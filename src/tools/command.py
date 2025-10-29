def version(args, _):
    """显示版本信息
    """
    print(f"Version: {__version__}")
    if args.more:
        print(f"Author: {__author__}")
        print(f"Author_email: {__author_email__}")


def changelog(args, _):
    """显示变更日志
    """
    print("变更日志:")
    from pathlib import Path
    # 读取变更日志文件
    changelog_file = Path(__file__).parent.parent / "meta/changelog.md"
    with open(changelog_file, 'r') as f:
        for line in f:
            if line.strip() == "" and not args.more:
                break
            print(f"{line.strip()}")


def default(_, parser):
    """默认命令
    """
    parser.print_help()

commands = {
    "version": version,
    "changelog": changelog,
    "default": default
}

__all__ = [
    "commands"
]
