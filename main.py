import fileInit
import sys


if __name__ == "__main__":
    try:
        file_path = input("[OS]创建文件:")
        author = input("[OS]作者名称:")

        func_tools = fileInit.FileInit(file_path=file_path, author=author, reWrite=True)
        func_tools.userCmd()
    except KeyboardInterrupt:
        print ("\n[+] user exit")
        sys.exit(1)
