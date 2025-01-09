"""
Simple ogl scrolling canvas to test redraw algorithms.
"""

import wx
import wx.lib.ogl as ogl
import os, stat
import secrets

WINDOW_SIZE = (1024, 768)

# from gui.coord_utils import setpos, getpos


class Log:
    def WriteText(self, text):
        if text[-1:] == "\n":
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


# compensate for the fact that x, y for a ogl shape are the centre of the shape, not the top left
def setpos(shape, x, y):
    width, height = shape.GetBoundingBoxMax()
    shape.SetX(x + width / 2)
    shape.SetY(y + height / 2)


def getpos(shape):
    width, height = shape.GetBoundingBoxMax()
    x = shape.GetX()
    y = shape.GetY()
    return x - width / 2, y - height / 2


class UmlCanvas(ogl.ShapeCanvas):
    def __init__(self, parent, log, frame):
        ogl.ShapeCanvas.__init__(self, parent)
        maxWidth = 1000
        maxHeight = 1000
        self.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)

        self.log = log
        self.frame = frame
        self.SetBackgroundColour("LIGHT BLUE")  # wxWHITE)

        self.SetDiagram(ogl.Diagram())
        self.GetDiagram().SetCanvas(self)
        self.save_gdi = []
        wx.EVT_WINDOW_DESTROY(self, self.OnDestroy)

        self.Bind(wx.EVT_CHAR, self.onKeyChar)
        self.working = False

        self.font1 = wx.Font(14, wx.MODERN, wx.NORMAL, wx.NORMAL, False)
        self.font2 = wx.Font(10, wx.MODERN, wx.NORMAL, wx.NORMAL, False)

    def onKeyChar(self, event):
        if event.GetKeyCode() >= 256:
            event.Skip()
            return
        if self.working:
            event.Skip()
            return
        self.working = True

        keycode = chr(event.GetKeyCode())

        if keycode == "m":
            # print len(self.GetDiagram().GetShapeList())

            shape = self.GetDiagram().GetShapeList()[secrets.SystemRandom().randint(0, 17)]

            dc = wx.ClientDC(self)
            self.PrepareDC(dc)

            # V1
            # setpos(shape, random.randint(1,300), 0)
            # self.GetDiagram().Clear(dc)
            # self.GetDiagram().Redraw(dc)

            # V2 - duplicates cos no clear
            # shape.Move(dc, shape.GetX(), shape.GetY())

            # V3 - duplicates cos no clear
            # x = random.randint(1,300)
            # y = 0
            # width, height = shape.GetBoundingBoxMax()
            # x += width/2
            # y += height/2
            # shape.Move(dc, x, y)

            x = secrets.SystemRandom().randint(1, 600)
            y = shape.GetY()
            width, height = shape.GetBoundingBoxMax()
            x += width / 2
            # y += height/2
            shape.Move(dc, x, y, display=False)
            self.GetDiagram().Clear(dc)
            self.GetDiagram().Redraw(dc)

        elif keycode == "w":
            maxWidth = 1000
            maxHeight = 2000
            self.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)  # on Linux / GTK this expands virt area but ogl won't draw there!

            self.OnSize(evt=None)  # fix for GTK - will create a larger _buffer

        elif keycode == "W":
            maxWidth = 1000
            maxHeight = 1000
            self.SetScrollbars(20, 20, maxWidth / 20, maxHeight / 20)


        elif keycode in ["1", "2", "3", "4", "5", "6", "7", "8"]:
            pass

        elif keycode in ["b", "B"]:
            pass

        self.working = False
        event.Skip()

    def OnDestroy(self, evt):
        for shape in self.GetDiagram().GetShapeList():
            if shape.GetParent() == None:
                shape.SetCanvas(None)

    def OnLeftClick(self, x, y, keys):  # Override of ShapeCanvas method
        # keys is a bit list of the following: KEY_SHIFT  KEY_CTRL
        # self.app.run.CmdDeselectAllShapes()
        pass


class MainApp(wx.App):
    def OnInit(self):
        self.log = Log()
        self.working = False
        wx.InitAllImageHandlers()
        self.andyapptitle = "ogl scroll testPyNsource GUI - Python Code into UML"

        self.frame = wx.Frame(
            None,
            -1,
            self.andyapptitle,
            pos=(50, 50),
            size=(0, 0),
            style=wx.NO_FULL_REPAINT_ON_RESIZE | wx.DEFAULT_FRAME_STYLE,
        )
        self.frame.CreateStatusBar()

        self.umlwin = UmlCanvas(self.frame, Log(), self.frame)

        ogl.OGLInitialize()  # creates some pens and brushes that the OGL library uses.

        # Set the frame to a good size for showing stuff
        self.frame.SetSize(WINDOW_SIZE)
        self.umlwin.SetFocus()
        self.SetTopWindow(self.frame)

        self.frame.Show(True)
        wx.EVT_CLOSE(self.frame, self.OnCloseFrame)

        wx.CallAfter(self.BootStrap)  # doesn't make a difference calling this via CallAfter

        return True

    def BootStrap(self):
        y = 0
        # for x in range(0, 1200, 70):
        for x in range(0, 1200, 10):
            shape = ogl.RectangleShape(60, 60)
            shape.AddText("%d,%d" % (x, y))
            setpos(shape, x, y)
            self.umlwin.AddShape(shape)

            y += 70

        self.umlwin.GetDiagram().ShowAll(1)

    def OnButton(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.umlwin.ShutdownDemo()
        evt.Skip()


def main():
    application = MainApp(0)
    application.MainLoop()


if __name__ == "__main__":
    main()
