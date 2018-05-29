import wx
'''
import wx.lib.platebtn as platebtn
 
class MyForm(wx.Frame):
 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Plate Button Tutorial")
 
        # Add a panel so it looks the correct on all platforms
        panel = wx.Panel(self, wx.ID_ANY)
 
        menu = wx.Menu()
        for url in ['http://wxpython.org', 'http://slashdot.org',
                    'http://editra.org', 'http://xkcd.com']:
            menu.Append(wx.NewId(), url, "Open %s in your browser" % url)
 
        btn = platebtn.PlateButton(panel, label="Menu", size=None, style=platebtn.PB_STYLE_DEFAULT)
        btn.SetMenu(menu)
 
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(btn, 0, wx.ALL, 5)
        panel.SetSizer(sizer)
 
# Run the program
if __name__ == "__main__":
    app = wx.PySimpleApp()
    frame = MyForm().Show()
    app.MainLoop()
'''

#!/usr/bin/python
 
def onButton(event):
    print("Button pressed.")
 
app = wx.App()
 
frame = wx.Frame(None, -1, 'win.py')
frame.SetDimensions(0,0,200,50)
 
# Create open file dialog
openFileDialog = wx.FileDialog(frame, "Open", "", "", 
                                      "Python files (*.py)|*.py", 
                                       wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
 
openFileDialog.ShowModal()
print(openFileDialog.GetPath())
openFileDialog.Destroy()