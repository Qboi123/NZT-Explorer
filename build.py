import os

from compiler import Compiler

if __name__ == '__main__':
    # Get main folder
    main_folder_ = os.getcwd()

    # Compiler class
    compiler = Compiler(
        exclude=[".idea", ".gitattributes", ".gitignore", "build.py", "README.md",
                 "obj", "icon.png", ".git", "compiler.py", "dll", "logs", "fatcow-hosting-icons-3000.zip",
                 "fatcow-hosting-icons-3000", "Save-TEST.nzt", "Save-TEST-new.nzt",
                 "Test.nzt", "Test2.nzt", "Test3.nzt", "log.txt"],
        icon=None, main_folder=os.getcwd(), main_file="main.py",
        hidden_imports=["wx", "wx._core", "wx.core", "wx._adv", "wx._media", "wx._msw", "wx._propgrid", "wx._ribbon",
                        "wx._aui", "wx._dataview", "wx._glcanvas", "wx._grid", "wx._html", "wx._html2", "wx._richtext",
                        "wx._stc", "wx._xml", "wx._xrc", "_sys", "sys"],
        log_level="INFO", app_name="NZT-Explorer", clean=True, hide_console=False,
        dlls=[])
    compiler.reindex()

    # Get argument and command
    args = compiler.get_args()
    command = compiler.get_command(args)

    # Compile workspace
    compiler.compile(command)
