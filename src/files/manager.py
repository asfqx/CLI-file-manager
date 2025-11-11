import sys
import os
import json
import zipfile
from pathlib import Path
from src.cli import (
    resolve_secure_path,
    acquire_lock_for_path,
    AtomicWriter,
    ensure_valid_filename,
    safe_load_json,
    safe_load_xml,
    MAX_UPLOAD_SIZE,
    ZIP_MAX_FILES,
    inspect_zip_safety,
)
from src.operations.operations import Operations
from src.operations.enum import OperationType
from src.files.accessor import fileAccessor
from src.core.auth import is_authenticated
from src.operations.accessor import operationsAccessor
from src.files.files import Files


class FileManager:
    async def list(self, args=None):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        p = resolve_secure_path(args.path or ".")
        if p.is_dir():
            for child in sorted(p.iterdir()):
                stat = child.stat()
                tag = "[DIR]" if child.is_dir() else "     "
                print(f"{tag} {child.name:40} {stat.st_size:10}")

        else:
            print("Not a directory:", p)

    async def read(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        p = resolve_secure_path(args.path)
        if not p.exists():
            print("File not found")
            return
        if p.stat().st_size > MAX_UPLOAD_SIZE:
            print("File too large")
            return
        async with acquire_lock_for_path(p):
            with open(p, "rb") as f:
                data = f.read()
            if args.format == "text":
                print(data.decode(errors="replace"))
            elif args.format == "json":
                print(json.dumps(safe_load_json(data.decode()), indent=2))
            elif args.format == "xml":
                el = safe_load_xml(data.decode())
                import xml.etree.ElementTree as ET

                print(ET.tostring(el, encoding="unicode"))
            else:
                print(f"Binary file, {len(data)} bytes")

    async def write(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        p = resolve_secure_path(args.path)
        ensure_valid_filename(p.name)
        file_name = p.name
        file = await fileAccessor.fetch_by_name(file_name)
        if file and file.user_id != user:
            print("Permission denied: you can only modify your own files")
            return

        if args.from_file:
            src = Path(args.from_file)
            if not src.exists():
                print("Source file not found")
                return
            data = src.read_bytes()
        else:
            data = sys.stdin.buffer.read()

        if len(data) > MAX_UPLOAD_SIZE:
            print("Data too large")
            return

        async with acquire_lock_for_path(p):
            with AtomicWriter(p, "wb") as f:
                f.write(data)

        print("Wrote:", p)
        file_size = p.stat().st_size
        if file:
            file = await fileAccessor.update(file_size, file_name)
            if file:
                operation = Operations(
                    type=OperationType.UPDATE, file_id=file.id, user_id=user
                )
                await operationsAccessor.create(operation)
        else:
            file_in = Files(file_name=file_name, file_size=file_size, user_id=user)
            file = await fileAccessor.create(file_in)
            if file:
                operation = Operations(
                    type=OperationType.CREATE, file_id=file.id, user_id=user
                )
                await operationsAccessor.create(operation)

    async def delete(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        p = resolve_secure_path(args.path)
        if not p.exists():
            print("File not found")
            return

        async with acquire_lock_for_path(p):
            try:
                file_name = p.name
                files = await fileAccessor.fetch_by_name(file_name)

                if not files:
                    print("No file records found in DB")
                    return
                files_to_delete = [f for f in files if f.user_id == user]
                if not files_to_delete:
                    print("Permission denied: you can only delete your own files")
                    return

                for file in files_to_delete:
                    operation = Operations(
                        type=OperationType.DELETE, file_id=file.id, user_id=user
                    )
                    await operationsAccessor.create(operation)
                await fileAccessor.delete(file_name, user_id=user)

                os.remove(p)
                print("Deleted", p)

            except Exception as e:
                print("Error deleting file:", e)

    async def create_zip(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        src = resolve_secure_path(args.src)
        dst = resolve_secure_path(args.dst)
        if dst.exists():
            print("Destination already exists")
            return
        if not src.exists():
            print("Source not found")
            return

        with zipfile.ZipFile(dst, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            nfiles = 0
            for root, dirs, files in os.walk(src):
                for fname in files:
                    full = Path(root) / fname
                    rel = full.relative_to(src)
                    if full.stat().st_size > MAX_UPLOAD_SIZE:
                        raise ValueError(f"File {full} too large to include")
                    zf.write(full, arcname=str(rel))
                    nfiles += 1
                    if nfiles > ZIP_MAX_FILES:
                        raise ValueError("Too many files to archive")
        with zipfile.ZipFile(dst, "r") as zf:
            inspect_zip_safety(zf)
        print("Created zip", dst)

    async def extract_zip(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        zipp = resolve_secure_path(args.zip)
        outdir = resolve_secure_path(args.outdir or ".")
        if not zipp.exists():
            print("Zip not found")
            return
        with zipfile.ZipFile(zipp, "r") as zf:
            try:
                inspect_zip_safety(zf)
            except Exception as e:
                print("Refusing to extract zip:", e)
                return
            for info in zf.infolist():
                member_path = Path(info.filename)
                if member_path.is_absolute():
                    print("Unsafe entry in zip (absolute path):", info.filename)
                    return
                target = (outdir / member_path).resolve()
                if not str(target).startswith(str(outdir)):
                    print("Unsafe entry in zip (path traversal):", info.filename)
                    return
            zf.extractall(path=outdir)
        print("Extracted zip to", outdir)

    async def create_file(self, args):
        user = is_authenticated()
        if not user:
            print("Not authenticated")
            return

        p = resolve_secure_path(args.path)
        ensure_valid_filename(p.name)

        if p.exists():
            print("Error: file already exists.")
            return

        data = (args.content or "").encode()

        lock = acquire_lock_for_path(p)
        async with lock:
            with AtomicWriter(p, mode="wb") as fh:
                fh.write(data)

        print(f"Created file: {p}")
        file_name = p.name
        file_size = p.stat().st_size
        file_in = Files(file_name=file_name, file_size=file_size, user_id=user)
        file = await fileAccessor.create(file_in)
        if file:
            operation = Operations(
                type=OperationType.CREATE, file_id=file.id, user_id=user
            )
            await operationsAccessor.create(operation)


fileManager = FileManager()
