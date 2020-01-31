import wx
import wx.lib
import wx.richtext

from nzt import NZTFile

VERSION = "1.0.0"


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
        self.treeCtrl = wx.TreeCtrl(self.panel, wx.ID_ANY, )
        self.treeCtrl.AddRoot("<None>", self.packageImage)
        self.treeCtrl.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.open_item)

        self.treeCtrl.AssignImageList(image_list)

        self.panel.Bind(wx.EVT_SIZE, self.resize_tree)

        # self.sizer.Add(self.treeCtrl)

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
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_str, self.nodeValueStr)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_bool, self.nodeValueBool)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_int, self.nodeValueInt)
        self.nodeValueMenu.Bind(wx.EVT_MENU, self.new_float, self.nodeValueFloat)
        self.nodeValueMenu.Append(self.nodeValueStr)
        self.nodeValueMenu.Append(self.nodeValueBool)
        self.nodeValueMenu.Append(self.nodeValueInt)
        self.nodeValueMenu.Append(self.nodeValueFloat)
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
        print(data[path[0]])
        if len(path) > 1:
            return self._delete_item(item, path[1:], data[path[0]])
        elif len(path) == 1:
            del data[path[0]]

    def delete_item(self, evt: wx.CommandEvent):
        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]

        print(path)

        if len(path) == 0:
            return

        if self.get_type2(path[:-1], self.data) in [dict, list] and len(path) > 0:
            print(self.data[path[0]])
            if len(path) > 1:
                self._delete_item(selected_item, path[1:], self.data[path[0]])
            elif len(path) == 1:
                del self.data[path[0]]
        print("DATA:", self.data)
        self._refresh_tree_item(
            self.treeCtrl.GetItemParent(selected_item),
            self.get_value(path[:-1], self.data), path[:-1]
        )

    def about(self, evt: wx.MenuEvent):
        with wx.Dialog(self) as dialog:
            dialog: wx.Dialog

            main_button = wx.Button(self, id=wx.ID_OK, label="OK")
            dialog.AddMainButtonId(wx.ID_OK)

            richtext = wx.richtext.RichTextCtrl(dialog)
            richtext.AppendText(f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 26'>"
                                f"NZT Explorer"
                                f"</center>"
                                f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 12'>"
                                f"<br><br>Version: {VERSION}"
                                f"</center>"
                                f"<center style='font-family: \"Malgun Gothic Semilight\";font-size: 12'>"
                                f"<br>Website: "
                                f"<a href='https://quintenjungblut.wixsite.com/qplaysoftware'>"
                                f"'https://quintenjungblut.wixsite.com/qplaysoftware'"
                                f"</a>")
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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
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

        selected_item: wx.TreeItemId = self.treeCtrl.GetFocusedItem()
        if selected_item == self.treeCtrl.GetRootItem():
            path = []
        else:
            path: list = self.treeCtrl.GetItemData(selected_item)["path"]
        self.new_value(path, selected_item, name, value)

    def new_command(self, evt: wx.CommandEvent):
        self.new()

    def new(self):
        self.treeCtrl.DeleteChildren(self.treeCtrl.GetRootItem())
        self.treeCtrl.SetItemText(self.treeCtrl.GetRootItem(), "<None>")
        self.data = {}
        self.path = None

    def exit_command(self, evt: wx.CommandEvent):
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

        exit(0)

    def save_command(self, evt: wx.CommandEvent):
        if self.path:
            nzt_file = NZTFile(self.path, "w")
            nzt_file.data = self.data
            nzt_file.save()
            nzt_file.close()
            return
        self.saveas_command(evt)

    def saveas_command(self, evt: wx.CommandEvent):
        with wx.FileDialog(self, "Select NZT File",  wildcard="NZT files (*.nzt)|*.nzt",
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

        with wx.FileDialog(self, "Select NZT File",  wildcard="NZT files (*.nzt)|*.nzt",
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
        root_item: wx.TreeItemId = self.treeCtrl.GetRootItem()
        self.treeCtrl.SetItemImage(root_item, self.packageImage)
        self.treeCtrl.SetItemText(root_item, self.path)
        # print(self.data)

        for key, value in self.data.items():
            # print(f"{key}: {value}")
            item: wx.TreeItemId = self.treeCtrl.AppendItem(root_item, f"{key}: {value}",
                                                           data={"path": [key],
                                                                 "name": key,
                                                                 "value": value,
                                                                 "index": None})
            item.path = [key]
            item.name = key
            item.value = value
            item.index = None
            if type(value) in (dict, list, tuple):
                item.type = type(value)
                self.treeCtrl.SetItemText(item, f"{key}")
                self.treeCtrl.SetItemImage(item, self.packageImage if type(value) == dict else self.listImage)
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
        self.treeCtrl.DeleteChildren(tree_item)
        if type(data) == dict:
            for key, value in data.items():
                item: wx.TreeItemId = self.treeCtrl.AppendItem(tree_item, f"{key}: {value}",
                                                               data={"path": path + [key],
                                                                     "name": key,
                                                                     "value": value,
                                                                     "index": None})
                item.path = path + [key]
                item.name = key
                item.value = value
                item.index = None

                if type(value) in (dict, list, tuple):
                    item.type = type(value)
                    self.treeCtrl.SetItemText(item, f"{key}")
                    self.treeCtrl.SetItemImage(item, self.packageImage if type(value) == dict else self.listImage)
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
                item: wx.TreeItemId = self.treeCtrl.AppendItem(tree_item, f"{i}: {data[i]}",
                                                               data={"path": path + [i],
                                                                     "name": None,
                                                                     "value": data[i], "index": i})
                item.path = path + [i]

                item.name = None
                item.value = data[i]
                item.index = i

                if type(data[i]) in (dict, list, tuple):
                    item.type = type(data[i])
                    self.treeCtrl.SetItemText(item, f"{i}")
                    self.treeCtrl.SetItemImage(item, self.packageImage if type(data[i]) == dict else self.listImage)
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
                self.treeCtrl.SetItemText(item, f"{data['value']}")
            else:
                self.treeCtrl.SetItemText(item, f"{data['name']}: {data['value']}")

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
    Main().MainLoop()
