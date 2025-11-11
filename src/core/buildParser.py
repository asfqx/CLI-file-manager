from argparse import ArgumentParser
from src.users.manager import userManager
from src.files.manager import fileManager
from src.system import cmd_disk_stats


def build_parser():
    p = ArgumentParser(prog="filemgr", description="Secure file manager CLI")
    sub = p.add_subparsers(dest="cmd")

    # disk stats
    sp = sub.add_parser("disk-stats", help="Show disk stats")
    sp.set_defaults(func=cmd_disk_stats)

    # list
    sp = sub.add_parser("list", help="List directory")
    sp.add_argument("path", nargs="?", default=".")
    sp.set_defaults(func=fileManager.list)

    # read
    sp = sub.add_parser("read", help="Read file")
    sp.add_argument("path")
    sp.add_argument(
        "--format", choices=["text", "json", "xml", "binary"], default="text"
    )
    sp.set_defaults(func=fileManager.read)

    # create-file
    sp = sub.add_parser(
        "create-file", help="Create a new file (optionally with content)"
    )
    sp.add_argument("path", help="Path to new file")
    sp.add_argument("--content", help="Optional text to write into file", default="")
    sp.set_defaults(func=fileManager.create_file)

    # write
    sp = sub.add_parser(
        "write", help="Write file (read data from stdin unless --from-file supplied)"
    )
    sp.add_argument("path")
    sp.add_argument(
        "--from-file", help="Read contents from local file instead of stdin"
    )
    sp.add_argument(
        "--user-id",
        type=int,
        dest="user_id",
        help="User ID to attach to metadata (optional)",
    )
    sp.set_defaults(func=fileManager.write)

    # delete
    sp = sub.add_parser("delete", help="Delete file")
    sp.add_argument("path")
    sp.set_defaults(func=fileManager.delete)

    # zip create
    sp = sub.add_parser("create-zip", help="Create zip from dir")
    sp.add_argument("src")
    sp.add_argument("dst")
    sp.set_defaults(func=fileManager.create_zip)

    # zip extract
    sp = sub.add_parser("extract-zip", help="Extract zip file safely")
    sp.add_argument("zip")
    sp.add_argument("--outdir", default=".")
    sp.set_defaults(func=fileManager.extract_zip)

    # auth
    sp = sub.add_parser("login", help="Login")
    sp.add_argument("username")
    sp.add_argument("password")
    sp.set_defaults(func=userManager.login)

    sp = sub.add_parser("logout", help="Logout")
    sp.set_defaults(func=userManager.logout)

    sp = sub.add_parser("create-user", help="Create user")
    sp.add_argument("username")
    sp.add_argument("password")
    sp.set_defaults(func=userManager.create_user)

    return p
