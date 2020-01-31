import os

from compiler import Compiler

if __name__ == '__main__':
    # Get main folder
    main_folder_ = os.getcwd()

    # Compiler class
    compiler = Compiler(
        exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
                 "obj", "icon.png", ".git", "compiler.py", "dll", "logs"],
        icon="icon.ico", main_folder=os.getcwd(), main_file="__main__.py",
        hidden_imports=["wx", "wx._core", "wx.core"],
        log_level="INFO", app_name="Qplay Bubbles", clean=True, hide_console=True,
        dlls=["dll/avcodec.dll", "dll/avcodec-58.dll", "dll/avutil-56.dll"])
    compiler.reindex()

    # Get argument and command
    args = compiler.get_args()
    command = compiler.get_command(args)

    # Compile workspace
    compiler.compile(command)
