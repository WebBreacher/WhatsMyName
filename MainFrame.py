'''
Created on Jan 22, 2020

@author: Bryan.GALBRAITH (@carbonUnit42)
Original Author - Micah Hoffman (@webBreacher) 
Modified his original WhatsMyName script from a command line
interface to a wxPython GUI
'''

import wx
from pubsub import pub
from UName import tabUName


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Who Am I", size=(630,720))
        
        self.statBar = self.CreateStatusBar(2)
        self.statBar.SetStatusWidths([300,-1])
        
        pub.subscribe(self.chStatBarTxt, 'F.Change') # Status Bar 1
        pub.subscribe(self.chStatBarTxt02, 'G.Change') # Status Bar 2
        
        _pnl = wx.Panel(self)
        _nb = wx.Notebook(_pnl)
        
        _pgOne = tabUName(_nb)
        
        _nb.AddPage(_pgOne, "User Names")
        
        sizer = wx.BoxSizer()
        sizer.Add(_nb, 1, wx.EXPAND)
        
        _pnl.SetSizer(sizer)
        
    def chStatBarTxt(self, fobj):
        self.SetStatusText(fobj)
        
    def chStatBarTxt02(self, fobj):
        self.SetStatusText(fobj,1)

        
if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
        