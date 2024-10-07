import argparse
import sys

from utils.LuaScripts import LuaScripts
from utils.Version import VerMgr


class Options:
    def __init__(self, args=None):
        parser = argparse.ArgumentParser(description="Process Lua files.")

        parser.add_argument('-i', '--infile', required=True, help='Input lua file to be processed.')
        parser.add_argument('-o', '--outfile', required=True, help='Output processed lua file.')
        parser.add_argument('-e', '--encrypt', action='store_true', default=False, help='Encrypt the lua file.')
        parser.add_argument('-d', '--decrypt', action='store_true', default=False, help='Decrypt the lua file.')
        parser.add_argument('-p', '--platform', default='Android', help='Platform(Android/iOS).')
        parser.add_argument('--nofix', action='store_true', default=False, help='Do not fix the file.')
        # parser.add_argument('--ver-bytes', action='store_true', default=False, help='Read version data from file.')
        # parser.add_argument('-h', '--help', action='help', help='Show help.')

        # 如果未传递参数，则默认使用 sys.argv
        if args is None:
            self.args = parser.parse_args()
        else:
            self.args = parser.parse_args(args)


def utils_main(args=None):
    options = Options(args).args

    if options.encrypt:
        platform = options.platform.lower()
        if platform == 'android':
            result = LuaScripts.GenEncryptABData(options.infile, options.outfile, True, not options.nofix)
            if isinstance(result, bool):
                # 如果 result 是布尔值，表示成功与否
                return result
            else:
                # 如果 result 不是布尔值，按你需要的逻辑处理，这里假设成功
                return True
        elif platform == 'ios':
            LuaScripts.GenEncryptABData(options.infile, options.outfile, False, not options.nofix)
        else:
            raise Exception(f"Invalid platform: {options.platform}")
    elif options.decrypt:
        LuaScripts.GenDecryptABData(options.infile, options.outfile)
    # elif options.ver_bytes:
    #     verMgr = VerMgr()
    #     verMgr.load_ver_info(options.infile, options.outfile)
    # elif options.help:
    #     print("Help")


if __name__ == "__main__":
    utils_main()
