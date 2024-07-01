# prototype pynsource gui possibilities

import wx
from fbpyn1_gen import FramePyIdea_gen
import wx.lib.ogl as ogl
import wx.stc as stc
import secrets


class Node:
    def __init__(self, level, start, end, text, parent=None, styles=[]):
        """Folding node as data for tree item."""
        self.parent = parent
        self.level = level
        self.start = start
        self.end = end
        self.text = text
        self.styles = styles  # can be useful for icon detection
        self.children = []


class FramePyIdea(FramePyIdea_gen):
    def OnShowPane(self, event):
        # print frame.m_mgr.GetAllPanes()
        # print frame.m_mgr.GetPane('pane_code')
        frame.m_mgr.RestorePane(frame.m_mgr.GetPane("pane_code"))
        # print '-'*88
        # print frame.m_mgr.GetAllPanes()
        # frame.m_mgr.GetPane('pane_code').Float()
        # frame.m_mgr.AddPane( frame.m_code, wx.aui.AuiPaneInfo() .Name( u"pane_code" ).Right() .Caption( u"Source Code" ).MaximizeButton( False ).MinimizeButton( False ).PinButton( True ).Dock().Resizable().FloatingSize( wx.DefaultSize ).DockFixed( False ) )
        frame.m_mgr.Update()

    def addpane(self, dofloat=False):
        from fbpyn1_scintilla import PythonSTC

        m_code2 = PythonSTC(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.WANTS_CHARS)
        if dofloat:
            self.m_mgr.AddPane(
                m_code2,
                wx.aui.AuiPaneInfo()
                .Name("pane_code" + repr(secrets.SystemRandom().randint(1, 1000)))
                .Right()
                .Caption("Source Code" + repr(secrets.SystemRandom().randint(1, 1000)))
                .MaximizeButton(False)
                .MinimizeButton(False)
                .PinButton(True)
                .Float()
                .Resizable()
                .FloatingPosition((350, 100))
                .FloatingSize((350, 500))
                .DockFixed(False),
            )
        else:
            self.m_mgr.AddPane(
                m_code2,
                wx.aui.AuiPaneInfo()
                .Name("pane_code" + repr(secrets.SystemRandom().randint(1, 1000)))
                .Right()
                .Caption("Source Code" + repr(secrets.SystemRandom().randint(1, 1000)))
                .MaximizeButton(False)
                .MinimizeButton(False)
                .PinButton(True)
                .Dock()
                .Resizable()
                .FloatingSize(wx.DefaultSize)
                .DockFixed(False),
            )
        m_code2.SetText(open(r"fbpyn1.py").read())
        m_code2.Colourise(
            0, m_code2.GetTextLength()
        )  # make sure everything is lexed. or use (0, -1)
        self.andycollapsetodefs(m_code2)
        m_code2.SetReadOnly(False)
        frame.m_mgr.Update()

    def OnAddPane(self, event):
        self.addpane()

    def OnAddPaneFloat(self, event):
        self.addpane(True)

    def OnFold1(self, event):
        frame.m_code.ToggleFold(frame.m_code.GetCurrentLine())
        for i in range(0, 30):
            print(i, frame.m_code.GetLineVisible(i))

    def OnFoldAll(self, event):
        frame.m_code.FoldAll()

    def OnHier(self, event):
        self.andycollapsetodefs(frame.m_code)

    def andycollapsetodefs(self, ed):
        root = self.getHierarchy(ed)
        self.appendChildren(None, root, ed)  # Andy version

    def appendChildren(self, wxParent, nodeParent, ed):
        for nodeItem in nodeParent.children:
            # wxItem    = self.AppendItem(wxParent,nodeItem.text.strip())
            # self.SetPyData(wxItem,nodeItem)
            # print nodeItem.text.strip()
            # self.appendChildren(wxItem,nodeItem)
            self.appendChildren(None, nodeItem, ed)

            if "def " in nodeItem.text.strip():
                # print "start", nodeItem.start, "level", nodeItem.level
                if ed.GetFoldExpanded(nodeItem.start):
                    ed.ToggleFold(nodeItem.start)

    def getHierarchy(self, ed):
        import wx.stc as stc

        self = ed
        # [(level,line,text,parent,[children]),]
        n = self.GetLineCount() + 1
        prevNode = root = Node(level=0, start=0, end=n, text="root", parent=None)
        for line in range(n - 1):
            foldBits = self.GetFoldLevel(line)
            if foldBits & stc.STC_FOLDLEVELHEADERFLAG:
                # folding point
                prevLevel = prevNode.level
                level = foldBits & stc.STC_FOLDLEVELNUMBERMASK
                text = self.GetLine(line)
                node = Node(level=level, start=line, end=n, text=text)
                if level == prevLevel:
                    # say hello to new brother or sister
                    node.parent = prevNode.parent
                    node.parent.children.append(node)
                    prevNode.end = line
                elif level > prevLevel:
                    # give birth to child (only one level deep)
                    node.parent = prevNode
                    prevNode.children.append(node)
                else:
                    # find your uncles and aunts (can be several levels up)
                    while level < prevNode.level:
                        prevNode.end = line
                        prevNode = prevNode.parent
                    node.parent = prevNode.parent
                    node.parent.children.append(node)
                    prevNode.end = line
                prevNode = node
        prevNode.end = line
        return root


##class TreeCtrl(wx.TreeCtrl):
##    def __init__(self,*args,**keyw):
##        keyw['style'] = wx.TR_HIDE_ROOT|wx.TR_HAS_BUTTONS
##        wx.TreeCtrl.__init__(self,*args,**keyw)
##        self.root        = self.AddRoot('foldExplorer root')
##        self.hierarchy  = None
##        self.Bind(wx.EVT_RIGHT_UP, self.onRightUp)
##        self.Bind(wx.EVT_TREE_KEY_DOWN, self.update)
##
##    def update(self, event=None):
##        """Update tree with the source code of the editor"""
##        hierarchy   = self.editor.getHierarchy()
##        if hierarchy != self.hierarchy:
##            self.hierarchy = hierarchy
##            self.DeleteChildren(self.root)
##            self.appendChildren(self.root,self.hierarchy)
##
##    def appendChildren(self,wxParent,nodeParent):
##        for nodeItem in nodeParent.children:
##            wxItem    = self.AppendItem(wxParent,nodeItem.text.strip())
##            self.SetPyData(wxItem,nodeItem)
##            self.appendChildren(wxItem,nodeItem)
##
##    def onRightUp(self,event):
##        """If a tree item is right clicked select the corresponding code"""
##        pt              = event.GetPosition();
##        wxItem, flags   = self.HitTest(pt)
##        nodeItem        = self.GetPyData(wxItem)
##        self.editor.selectNode(nodeItem)

# class Frame(wx.Frame):
#    def __init__(self,title,size=(800,600)):
#        wx.Frame.__init__(self,None,-1,title,size=size)
#        splitter            = wx.SplitterWindow(self)
#        self.explorer       = TreeCtrl(splitter)
#        self.editor         = Editor(splitter)
#        splitter.SplitVertically(
#            self.explorer,
#            self.editor,
#            int(self.GetClientSize()[1]/3)
#        )
#        self.explorer.editor    = self.editor
#        self.editor.explorer    = self.explorer
#        self.Show()


import wx.lib.mixins.inspection


class MyApp(wx.App, wx.lib.mixins.inspection.InspectionMixin):
    def OnInit(self):
        self.Init()  # initialize the inspection tool
        return True


app = MyApp()
# app = wx.App()
ogl.OGLInitialize()
frame = FramePyIdea(None)

# line numbers in the margin
frame.m_code.SetMarginType(1, stc.STC_MARGIN_NUMBER)
frame.m_code.SetMarginWidth(1, 25)  # set width of margin

frame.m_code.SetText(open(r"fbpyn1_gen.py").read())
frame.m_code.EmptyUndoBuffer()
frame.Show()
frame.m_code.Colourise(0, -1)

frame.canvas.SetBackgroundColour("LIGHT BLUE")
# Optional - add a shape
shape = ogl.RectangleShape(60, 60)
shape.SetX(50)
shape.SetY(50)
frame.canvas.AddShape(shape)
frame.canvas.GetDiagram().ShowAll(True)

# inspection tool
# import wx.lib.inspection
# wx.lib.inspection.InspectionTool().Show()

app.MainLoop()
