import sys

import wx
import wx.lib
import wx.richtext
import wx.dataview
from wx._dataview import TLI_LAST
from wx.html import HtmlWindow

from nzt import NZTFile

VERSION = "1.1.0"


# noinspection PyUnusedLocal
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None)

        self.data = {}
        self.path = None
        self.SetTitle(f"NZT Explorer {VERSION}")

        self.panel = wx.Panel(self)

        # self.valueImage = wx.Bitmap("file.png")
        # self.packageImage = wx.Bitmap("package.png")
        image_list = wx.ImageList(16, 16)
        self.valueImage = image_list.Add(
            wx.Image("icons/file.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.packageImage = image_list.Add(
            wx.Image("icons/package.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.listImage = image_list.Add(
            wx.Image("icons/list.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        self.dictImage = image_list.Add(
            wx.Image("icons/dict.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())

        self.valueImages = {
            str: image_list.Add(wx.Image("icons/files/string.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            int: image_list.Add(wx.Image("icons/files/integer.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            float: image_list.Add(wx.Image("icons/files/float.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            bytes: image_list.Add(wx.Image("icons/files/bytes.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            bytearray: image_list.Add(wx.Image("icons/files/bytearray.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            bool: image_list.Add(wx.Image("icons/files/boolean.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            object: image_list.Add(wx.Image("icons/files/object.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            type: image_list.Add(wx.Image("icons/files/type.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap()),
            None: image_list.Add(wx.Image("icons/file.png", wx.BITMAP_TYPE_PNG).ConvertToBitmap())
        }

        # Controls
        # self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.treeCtrl = wx.dataview.TreeListCtrl(self.panel, wx.ID_ANY, )
        self.nameColumn = self.treeCtrl.AppendColumn("Name")
        self.valueColumn = self.treeCtrl.AppendColumn("Value")
        self.treeCtrl.Bind(wx.dataview.EVT_TREELIST_ITEM_ACTIVATED, self.open_item)

        self.treeCtrl.AssignImageList(image_list)
        # self.rootItem = self.treeCtrl.AppendItem(self.treeCtrl.GetRootItem(), "")
        # self.treeCtrl.SetItemText(self.rootItem, self.nameColumn, "<None>")
        # self.treeCtrl.SetItemText(self.rootItem, self.valueColumn, "<None>")

        # self.sizer.Add(self.treeCtrl)

        root_item = self.treeCtrl.GetRootItem()
        item: wx.dataview.TreeListItem = self.treeCtrl.AppendItem(root_item, "")
        self.treeCtrl.SetItemText(item, self.nameColumn, f"<Not Opened Yet>")
        self.treeCtrl.SetItemText(item, self.valueColumn, f"")
        self.rootItem = item
        self.panel.Bind(wx.EVT_SIZE, self.resize_tree)

        # Menu Bar
        self.menuBar = wx.MenuBar(style=0)

        # File Menu
        self.fileMenu = wx.Menu()
        self.fileNewItem = wx.MenuItem(self.fileMenu, wx.ID_ANY, "&New file...")
        self.fileOpenItem = wx.MenuItem(self.fileMenu, wx.ID_ANY, "&Open file...")
        self.fileSep1 = wx.MenuItem(self.fileMenu, wx.ID_SEPARATOR, "")
        self.fileSaveItem = wx.MenuItem(self.fileMenu, wx.ID_ANY, "&Save")
        self.fileSaveAsItem = wx.MenuItem(self.fileMenu, wx.ID_ANY, "Save &As...")
        self.fileExitItem = wx.MenuItem(self.fileMenu, wx.ID_ANY, "E&xit")
        self.fileMenu.Bind(wx.EVT_MENU, self.new_command, self.fileNewItem)
        self.fileMenu.Bind(wx.EVT_MENU, self.open_command, self.fileOpenItem)
        self.fileMenu.Bind(wx.EVT_MENU, self.save_command, self.fileSaveItem)
        self.fileMenu.Bind(wx.EVT_MENU, self.saveas_command, self.fileSaveAsItem)
        self.fileMenu.Bind(wx.EVT_MENU, self.exit_command, self.fileExitItem)
        self.fileMenu.Append(self.fileOpenItem)
        self.fileMenu.Append(self.fileNewItem)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(self.fileSaveItem)
        self.fileMenu.Append(self.fileSaveAsItem)
        self.fileMenu.AppendSeparator()
        self.fileMenu.Append(self.fileExitItem)
        self.menuBar.Append(self.fileMenu, "&File")

        # Node Menu
        self.nodeMenu = wx.Menu()
        self.nodePackageMenu = wx.Menu()
        self.nodePackageDict = wx.MenuItem(self.nodePackageMenu, wx.ID_ANY, "New &Dictionary Package")
        self.nodePackageList = wx.MenuItem(self.nodePackageMenu, wx.ID_ANY, "New &List Package")
        self.nodePackageMenu.Bind(wx.EVT_MENU, self.new_dict_command, self.nodePackageDict)
        self.nodePackageMenu.Bind(wx.EVT_MENU, self.new_list_command, self.nodePackageList)
        self.nodePackageMenu.Append(self.nodePackageDict)
        self.nodePackageMenu.Append(self.nodePackageList)
        self.nodeMenu.AppendSubMenu(self.nodePackageMenu, "New &Package")

        self.nodeValueMenu = wx.Menu()
        self.nodeValueStr = wx.MenuItem(self.nodeValueMenu, wx.ID_ANY, "New &String Value")
        self.nodeValueBool = wx.MenuItem(self.nodeValueMenu, wx.ID_ANY, "New &Boolean Value")
        self.nodeValueInt = wx.MenuItem(self.nodeValueMenu, wx.ID_ANY, "New &Integer Value")
        self.nodeValueFloat = wx.MenuItem(self.nodeValueMenu, wx.ID_ANY, "New &Float Value")
        # self.nodeValueObject = wx.MenuItem(self.nodeValueMenu, wx.ID_ANY, "New &Object Value")
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_str, self.nodeValueStr)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_bool, self.nodeValueBool)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_int, self.nodeValueInt)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_float, self.nodeValueFloat)
        # self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_object, self.nodeValueObject)
        self.nodeValueMenu.Append(self.nodeValueStr)
        self.nodeValueMenu.Append(self.nodeValueBool)
        self.nodeValueMenu.Append(self.nodeValueInt)
        self.nodeValueMenu.Append(self.nodeValueFloat)
        # self.nodeValueMenu.Append(self.nodeValueObject)
        self.nodeMenu.AppendSubMenu(self.nodeValueMenu, "New &Value")

        self.nodeDeleteItem = wx.MenuItem(self.nodeMenu, wx.ID_ANY, "&Delete Value or Package")
        self.nodeMenu.Bind(wx.EVT_MENU, self.delete_item, self.nodeDeleteItem)
        self.nodeMenu.AppendSeparator()
        self.nodeMenu.Append(self.nodeDeleteItem)
        self.menuBar.Append(self.nodeMenu, "&Node")

        self.helpMenu = wx.Menu()
        self.aboutItem = wx.MenuItem(self.helpMenu, wx.ID_ANY, "&About...")
        self.helpMenu.Bind(wx.EVT_MENU, self.about, self.aboutItem)
        self.helpMenu.Append(self.aboutItem)
        self.menuBar.Append(self.helpMenu, "&Help")

        self.SetMenuBar(self.menuBar)

        self.new()

        # Set sizer
        # self.panel.SetSizer(self.sizer)

    def _delete_item(self, item, path, data):
        # print(data[path[0]])
        if len(path) > 1:
            return self._delete_item(item, path[1:], data[path[0]])
        elif len(path) == 1:
            del data[path[0]]

    def delete_item(self, evt: wx.CommandEvent):
        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]

        # print(path)

        if len(path) == 0:
            return

        if self.get_type2(path[:-1], self.data) in [dict, list] and len(path) > 0:
            # print(self.data[path[0]])
            if len(path) > 1:
                self._delete_item(selected_item, path[1:], self.data[path[0]])
            elif len(path) == 1:
                del self.data[path[0]]
        # print("DATA:", self.data)
        self._refresh_tree_item(
            self.treeCtrl.GetItemParent(selected_item),
            self.get_value(path[:-1], self.data), path[:-1]
        )

    def about(self, evt: wx.MenuEvent):
        with wx.Dialog(self) as dialog:
            def on_link_clicked(evt: wx.html.HtmlLinkEvent):
                print(f"CLicked on URL: {evt.GetLinkInfo().GetHref()}")
                os.startfile(evt.GetLinkInfo().GetHref())

            dialog: wx.Dialog

            richtext = HtmlWindow(dialog, size=(150, 150))
            richtext.Bind(wx.html.EVT_HTML_LINK_CLICKED, on_link_clicked)
            richtext.SetPage(f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 26'>"
                             f"NZT Explorer"
                             f"</center>"
                             f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 12'>"
                             f"<br><br>Version: {VERSION}"
                             f"</center>"
                             f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 12'>"
                             f"<br>Website: "
                             f"<a href='https://quintenjungblut.wixsite.com/qplaysoftware'>"
                             f"https://quintenjungblut.wixsite.com/qplaysoftware"
                             f"</a>")

            main_button = wx.Button(self, id=wx.ID_OK, label="OK")
            dialog.AddMainButtonId(wx.ID_OK)

            dialog.ShowModal()

    def new_float(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new float:", "New Float") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        with wx.TextEntryDialog(self, "Deciamal value (float) for the new float:", "New Float") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()

            try:
                value_ = float(dialog.GetValue())
            except ValueError:
                with wx.MessageDialog(self, "Invalid Value!", "Error",
                                      wx.OK | wx.CENTRE | wx.ICON_ERROR) as messageDialog:
                    messageDialog: wx.MessageDialog
                    messageDialog.ShowModal()
                return

            value = value_

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_bool(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new string:", "New Integer") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        with wx.SingleChoiceDialog(self, "Choose 'True' or 'False'", "Boolean", ["True", "False"]) as dialog:
            dialog: wx.SingleChoiceDialog
            dialog.ShowModal()
            choosen = dialog.GetStringSelection()
            if choosen == "True":
                value = True
            elif choosen == "False":
                value = False
            else:
                return

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_str(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new string:", "New String") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        with wx.TextEntryDialog(self, "Value for the new string", "New String") as dialog:
            dialog: wx.NumberEntryDialog
            dialog.ShowModal()
            value: str = dialog.GetValue()

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_object(self, evt: wx.CommandEvent):
        import wx

        app = wx.App()

        with wx.MessageDialog(self, "WARNING!", "Are you sure you want to create a new object?\n"
                                                "Don't use this feature unless you know what you are doing.", wx.YES_NO | wx.ICON_WARNING) as dialog:
            result = dialog.ShowModal()

        if result == wx.ID_YES:
            with wx.TextEntryDialog(self, "Name for the new string:", "New String") as dialog:
                dialog: wx.TextEntryDialog
                dialog.ShowModal()
                name: str = dialog.GetValue()

            with wx.TextEntryDialog(self, "Code for the new object", "New String") as dialog:
                dialog: wx.NumberEntryDialog
                dialog.ShowModal()
                code: str = dialog.GetValue()

            with wx.TextEntryDialog(self, "Filename for the new object", "New String") as dialog:
                dialog: wx.NumberEntryDialog
                dialog.ShowModal()
                file: str = dialog.GetValue()

            glob = {}
            loc = {}

            try:
                exec(compile(code, file, "exec"), glob, loc)
            except Exception as e:
                import traceback

                with wx.MessageDialog(self, "Error", traceback.format_exception(e.__class__, e, e.__traceback__),
                                      wx.OK | wx.CENTRE | wx.ICON_ERROR) as dialog:
                    dialog.ShowModal()

            with wx.SingleChoiceDialog(self, "Choose an local object to create", "Boolean", loc.keys()) as dialog:
                dialog: wx.SingleChoiceDialog
                dialog.ShowModal()
                choosen = dialog.GetStringSelection()

                if choosen:
                    value = loc[choosen]
                else:
                    return

            selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
            if selected_item == self.treeCtrl.GetRootItem():
                path = []
            else:
                path: list = self.treeCtrl.GetItemData(selected_item)["path"]
            self.new_value(path, selected_item, name, value)
        # evt.Destroy()

    def new_int(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new integer:", "New Integer") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        with wx.NumberEntryDialog(self, "Value for the new integer", "Value:", "New Integer",
                                  0, -99999999, +99999999) as dialog:
            dialog: wx.NumberEntryDialog
            dialog.ShowModal()
            value: int = dialog.GetValue()

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_list_command(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new list package:") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        value = []

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_dict_command(self, evt: wx.CommandEvent):
        with wx.TextEntryDialog(self, "Name for the new dictionary package:") as dialog:
            dialog: wx.TextEntryDialog
            dialog.ShowModal()
            name: str = dialog.GetValue()

        value = {}

        selected_item: wx.TreeItemId = self.treeCtrl.GetSelection()
        if selected_item == self.rootItem:
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_command(self, evt: wx.CommandEvent):
        self.new()

    def new(self):
        while self.treeCtrl.GetFirstChild(self.rootItem):
            self.treeCtrl.DeleteItem(self.treeCtrl.GetFirstChild(self.rootItem))
        self.treeCtrl.SetItemText(self.treeCtrl.GetRootItem(), "<None>")
        self.data = {}
        self.path = None

    def exit_command(self, evt: wx.CommandEvent):
        if self.path:
            nzt_file = NZTFile(self.path, "r")
            nzt_file.load()
            if nzt_file.data != self.data:
                with wx.MessageDialog(self, "Are you sure you want to quit?", "Question",
                                      wx.YES | wx.NO | wx.NO_DEFAULT | wx.CENTRE | wx.ICON_QUESTION) as messageDialog:
                    messageDialog: wx.MessageDialog
                    choice = messageDialog.ShowModal()
                    if choice == wx.ID_NO:
                        nzt_file.close()
                        return

            nzt_file.close()
        sys.exit(0)

    def save_command(self, evt: wx.CommandEvent):
        if self.path:
            nzt_file = NZTFile(self.path, "w")
            nzt_file.data = self.data
            nzt_file.save()
            nzt_file.close()
            return
        self.saveas_command(evt)

    def saveas_command(self, evt: wx.CommandEvent):
        with wx.FileDialog(self, "Select NZT File", wildcard="NZT files (*.nzt)|*.nzt",
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:
            fileDialog: wx.FileDialog
            fileDialog.ShowModal()
            path = fileDialog.GetPath()

        nzt_file = NZTFile(path, "w")
        nzt_file.data = self.data
        nzt_file.save()
        nzt_file.close()

        self.path = path

    def open_command(self, evt: wx.CommandEvent):
        # self.save()
        # self.close()

        # menu_item = evt.GetEventObject()
        # menu_item_id = evt.GetId()
        # menu_item = self.FindWindowById(menu_item_id)
        # print(menu_item)

        self.new()

        with wx.FileDialog(self, "Select NZT File", wildcard="NZT files (*.nzt)|*.nzt",
                           style=wx.FD_DEFAULT_STYLE) as fileDialog:
            fileDialog: wx.FileDialog
            fileDialog.ShowModal()
            path = fileDialog.GetPath()

        if path:
            nzt_file = NZTFile(path, "r")
            nzt_file.load()

            self.data = nzt_file.data
            self.path = nzt_file.zipFormatFile.path

            nzt_file.close()

            self.refresh_tree()

    def refresh_tree(self):
        print(self.rootItem)
        self.treeCtrl.SetItemImage(self.rootItem, self.packageImage)
        self.treeCtrl.SetItemText(self.rootItem, self.nameColumn, os.path.split(self.path)[-1])
        root_item = self.rootItem
        # print(self.data)

        for key, value in self.data.items():
            # print(f"{key}: {value}")
            item: wx.dataview.TreeListItem = self.treeCtrl.AppendItem(root_item, "",
                                                                      data={"path": [key],
                                                                            "name": key,
                                                                            "value": value,
                                                                            "index": None})
            print(item)
            item.path = [key]
            item.name = key
            item.value = value
            item.index = None
            self.treeCtrl.SetItemText(item, self.nameColumn, f"{repr(key)}")
            self.treeCtrl.SetItemText(item, self.valueColumn, f"{repr(value)}")
            if type(value) in (dict, list, tuple):
                item.type = type(value)
                self.treeCtrl.SetItemText(item, self.nameColumn, f"{key}")
                self.treeCtrl.SetItemText(item, self.valueColumn, f"")
                self.treeCtrl.SetItemImage(item, self.dictImage if type(value) == dict else self.listImage)
                self._refresh_tree_item(item, value, item.path)
            elif type(value) in (int, float, str, bool, bytes, bytearray, type):
                item.type = type(value)
                self.treeCtrl.SetItemImage(
                    item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                )
            elif value is None:
                item.type = None
                self.treeCtrl.SetItemImage(
                    item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                )
            else:
                item.type = object
                self.treeCtrl.SetItemImage(
                    item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                )

    def _refresh_tree_item(self, tree_item, data, path):
        while self.treeCtrl.GetFirstChild(tree_item):
            self.treeCtrl.DeleteItem(self.treeCtrl.GetFirstChild(tree_item))
        if type(data) == dict:
            for key, value in data.items():
                item: wx.TreeItemId = self.treeCtrl.AppendItem(tree_item, "",
                                                               data={"path": path + [key],
                                                                     "name": key,
                                                                     "value": value,
                                                                     "index": None})
                item.path = path + [key]
                item.name = key
                item.value = value
                item.index = None
                self.treeCtrl.SetItemText(item, self.nameColumn, f"{repr(key)}")
                self.treeCtrl.SetItemText(item, self.valueColumn, f"{repr(value)}")
                if type(value) in (dict, list, tuple):
                    item.type = type(value)
                    self.treeCtrl.SetItemText(item, self.nameColumn, f"{key}")
                    self.treeCtrl.SetItemText(item, self.valueColumn, f"")
                    self.treeCtrl.SetItemImage(item, self.dictImage if type(value) == dict else self.listImage)
                    self._refresh_tree_item(item, value, item.path)
                elif type(value) in (int, float, str, bool, bytes, bytearray, type):
                    item.type = type(value)
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )
                elif value is None:
                    item.type = None
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )
                else:
                    item.type = object
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )
        elif type(data) in [list, tuple]:
            for i in range(len(data)):
                item: wx.TreeItemId = self.treeCtrl.AppendItem(tree_item, "",  # f"{repr(i)}: {repr(data[i])}",
                                                               data={"path": path + [i],
                                                                     "name": None,
                                                                     "value": data[i], "index": i})
                item.path = path + [i]

                item.name = None
                item.value = data[i]
                item.index = i

                self.treeCtrl.SetItemText(item, self.nameColumn, f"{repr(i)}")
                self.treeCtrl.SetItemText(item, self.valueColumn, f"{repr(data[i])}")

                if type(data[i]) in (dict, list, tuple):
                    item.type = type(data[i])
                    self.treeCtrl.SetItemText(item, self.nameColumn, f"{i}")
                    self.treeCtrl.SetItemText(item, self.valueColumn, f"")
                    self.treeCtrl.SetItemImage(item, self.dictImage if type(data[i]) == dict else self.listImage)
                    self._refresh_tree_item(item, data[i], item.path)
                elif type(data[i]) in (int, float, str, bool, bytes, bytearray, type):
                    item.type = type(data[i])
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )
                elif data[i] is None:
                    item.type = None
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )
                else:
                    item.type = object
                    self.treeCtrl.SetItemImage(
                        item, self.valueImages[item.type] if item.type in self.valueImages else self.valueImage
                    )

    def resize_tree(self, event: wx.SizeEvent):
        self.treeCtrl.SetSize(event.GetSize())

    def get_value(self, path, data):
        if len(path) > 1:
            return self.get_value(path[1:], data[path[0]])
        elif len(path) == 1:
            return data[path[0]]
        else:
            return data

    def get_type(self, path, data):
        value = self.get_value(path, data)
        type_ = type(value)

        if type_ in (dict, list, tuple, bytes, bytearray, type):
            return None
        elif type_ in (int, float, str, bool):
            return type_

    def get_type2(self, path, data):
        value = self.get_value(path, data)
        type_ = type(value)

        if type_ in (tuple, bytes, bytearray, type):
            return None
        elif type_ in (dict, list, int, float, str, bool):
            return type_

    def new_value(self, path, item, name, value):
        parent_value = self.get_value(path, self.data)
        parent_type = self.get_type2(path, self.data)
        # print(parent_value, parent_type)
        if parent_type == dict:
            if name not in parent_value:
                parent_value[name] = value
                self._refresh_tree_item(item, parent_value, path)
            else:
                raise ValueError(f"Value '{name}' already in path")
        elif parent_type == list:
            parent_value.append(value)
            self._refresh_tree_item(item, parent_value, path)

    def change_value(self, path, item):
        value_ = self.get_value(path, self.data)
        type_ = self.get_type(path, self.data)
        # print(value_)
        # print(type_)
        if type_:
            if type_ == int:
                with wx.NumberEntryDialog(self, "Change integer", "Enter value without a dot", "Integer",
                                          value_, -99999999, +99999999) as dialog:
                    dialog: wx.NumberEntryDialog
                    dialog.ShowModal()
                    value_ = dialog.GetValue()

                data = self.treeCtrl.GetItemData(item)
                data["value"] = value_
                self.treeCtrl.SetItemData(item, data)
            elif type_ == str:
                with wx.TextEntryDialog(self, "Change integer", "Integer", value_) as dialog:
                    dialog: wx.TextEntryDialog
                    dialog.ShowModal()
                    value_ = dialog.GetValue()

                data = self.treeCtrl.GetItemData(item)
                data["value"] = value_
                self.treeCtrl.SetItemData(item, data)
            elif type_ == bool:
                with wx.SingleChoiceDialog(self, "Choose 'True' or 'False'", "Boolean", ["True", "False"]) as dialog:
                    dialog: wx.SingleChoiceDialog
                    dialog.ShowModal()
                    choosen = dialog.GetStringSelection()
                    if choosen == "True":
                        data = self.treeCtrl.GetItemData(item)
                        data["value"] = True
                        self.treeCtrl.SetItemData(item, data)
                    elif choosen == "False":
                        data = self.treeCtrl.GetItemData(item)
                        data["value"] = False
                        self.treeCtrl.SetItemData(item, data)
                    else:
                        data = self.treeCtrl.GetItemData(item)
                        data["value"] = False
                        self.treeCtrl.SetItemData(item, data)
            elif type_ == float:
                with wx.TextEntryDialog(self, "Enter a decimal value (float)", "Float", str(value_)) as dialog:
                    dialog: wx.TextEntryDialog
                    dialog.ShowModal()

                    try:
                        value_ = float(dialog.GetValue())
                    except ValueError:
                        with wx.MessageDialog(self, "Invalid Value!", "Error",
                                              wx.OK | wx.CENTRE | wx.ICON_ERROR) as messageDialog:
                            messageDialog: wx.MessageDialog
                            messageDialog.ShowModal()
                        return

                    data = self.treeCtrl.GetItemData(item)
                    data["value"] = value_
                    self.treeCtrl.SetItemData(item, data)
            else:
                return

            if data["index"]:
                self.treeCtrl.SetItemText(item, self.nameColumn, f"{repr(data['index'])}")
                self.treeCtrl.SetItemText(item, self.valueColumn, f"{repr(data['value'])}")
            else:
                self.treeCtrl.SetItemText(item, self.nameColumn, f"{repr(data['name'])}")
                self.treeCtrl.SetItemText(item, self.valueColumn, f"{repr(data['value'])}")

            self.set_value(path, self.data, data['value'])
            # print("Setted Value", data['value'])
            # print("Getted Value", self.get_value(path, self.data))

    def open_item(self, evt: wx.TreeEvent):
        item: wx.TreeItemId = evt.GetItem()
        path: list = self.treeCtrl.GetItemData(item)["path"]
        # print(self.get_value(path, self.data))
        self.change_value(path, item)

    def set_value(self, path, data, value_):
        if len(path) > 1:
            # print(path[0], path[1:], data[path[0]])
            return self.set_value(path[1:], data[path[0]], value_)
        else:
            # print(path[0], data[path[0]])
            data[path[0]] = value_

    def get_type3(self, path, data):
        value_ = self.get_value(path, data)
        type_ = type(value_)

        if type_ in (dict, list, int, float, str, bool):
            return type_


class Main(wx.App):
    def __init__(self):
        super().__init__(False)

        self.mainFrame = MainFrame()
        self.mainFrame.Show()


if __name__ == '__main__':
    import os

    import sys
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    os.chdir(os.path.abspath(os.getcwd()))
    Main().MainLoop()
