from argparse import ArgumentParser
from . import __version__, __author__, __author_email__
from .command import commands

def parse_args():
    """初始化命令行参数解析器
    """
    parser = ArgumentParser(description="工具集合，用于各种任务。")

    sub_cmd = parser.add_subparsers(title="subcommands", dest="subcommand", description="可用子命令", help="显示子命令的帮助信息。")
    sc_version = sub_cmd.add_parser(name="version", help="显示版本信息。") # 版本信息子命令
    sc_version.add_argument("-m", "--more", action="store_true", default=False, help="显示更多版本信息。")

    sc_changelog = sub_cmd.add_parser(name="changelog", help="显示变更日志信息。") # 变更日志子命令
    sc_changelog.add_argument("-m", "--more", action="store_true", default=False, help="显示更多变更日志信息。")

    return parser.parse_args(), parser

def cli():
    """命令行接口
    """
    
    args, parser = parse_args()
    if args.subcommand is None:
        args.subcommand = "default"
    commands[args.subcommand](args, parser)

    
