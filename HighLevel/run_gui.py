import wx
from painter_gui.painter_gui import *

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = PainterGUI()
    frame.Show()
    app.MainLoop()