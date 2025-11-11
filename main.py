from src.core.buildParser import build_parser
from src.core.databaseAccessor import db

import asyncio


async def main():
    await db.connect()
    try:
        parser = build_parser()
        args = parser.parse_args()

        if not hasattr(args, "func"):
            parser.print_help()
            return

        fn = args.func
        if asyncio.iscoroutinefunction(fn):
            await fn(args)
        else:
            r = fn(args)
            if asyncio.iscoroutine(r):
                await r
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
