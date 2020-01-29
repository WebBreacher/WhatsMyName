'''
Created on Jan 22, 2020

@author: Bryan.GALBRAITH - Modification of an app written by Micah Hoffman (@webBreacher)
'''

import wx
import configParams
from pubsub import pub
from goFindThem import searchUsers


class tabUName(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        
        pub.subscribe(self.updOutText, 'O.Change')
        
        _UNameBox = wx.StaticBox(self, -1, 'Find Usernames: ', size = (800,800))
        _UNSizer = wx.StaticBoxSizer(_UNameBox, wx.VERTICAL)
        _UNSizer.AddSpacer(15)
        
        row01Sizer = wx.BoxSizer(wx.HORIZONTAL)
        row02Sizer = wx.BoxSizer(wx.HORIZONTAL)
        row03Sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # row 1
        _unLabel = wx.StaticText(self, label="User Name: ")
        self._unCtrl = wx.TextCtrl(self)
        self._unCtrl.Bind(wx.EVT_TEXT, self.nmKeyTyped) 
        
        # row 2

        self.conText = wx.TextCtrl(self, wx.ID_ANY, size = (620,300),
                                  style = wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RICH|wx.HSCROLL|wx.VSCROLL)
        self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(0,0,0)))

        # row 3
        self.srchButton = wx.Button(self, -1, " Search ")
        self.srchButton.Bind(wx.EVT_BUTTON, self.onSearch)
        self.cbDebug = wx.CheckBox(self, label = 'Debug On')
        self.Bind(wx.EVT_CHECKBOX, self.onChecked)
        
        
        row01Sizer.Add(_unLabel, 0, wx.ALL)
        row01Sizer.Add(self._unCtrl, 1, wx.ALL)
        row02Sizer.Add(self.conText, 0, wx.ALL)
        row03Sizer.Add(self.srchButton, 0)
        row03Sizer.AddSpacer(20)
        row03Sizer.Add(self.cbDebug, 1,wx.ALIGN_CENTER_VERTICAL)
        
        _UNSizer.Add(row01Sizer, 0, wx.ALL|wx.EXPAND, 2)
        _UNSizer.AddSpacer(8)
        _UNSizer.Add(row02Sizer, 0, wx.ALL|wx.EXPAND, 3)
        _UNSizer.AddSpacer(8)
        _UNSizer.Add(row03Sizer, 0, wx.ALL)
        self.SetSizer(_UNSizer)
        self.Show(show=True)
        
        # Setup status bar messages
        
    def nmKeyTyped(self, event):
        pub.sendMessage('F.Change', fobj = "Enter Username to Search For")
        
        # Grab username and see if we can locate them
        
    def onSearch(self, event):
        tmpMsg = self._unCtrl.GetValue()
        configParams.srchUserName = tmpMsg        
        searchUsers()
                
        # Updates the multi line text edit in the main panel, and checks to see if the 
        # text needs to be 'decorated' based on response codes
    
    def updOutText(self, fobj):
        tmpMsg = ((fobj)+'\n')
        self.bgColour = wx.WHITE
        self.conText.SetBackgroundColour(self.bgColour)        
        self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(0,0,0)))
        if configParams.bcolour == 'CYAN':
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(10,187,196)))
            self.conText.AppendText(tmpMsg)
        elif configParams.bcolour == 'GREEN':
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(12,133,35)))
            self.conText.AppendText(tmpMsg)
        elif configParams.bcolour == 'YELLOW':
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(209,209,15)))
            self.conText.AppendText(tmpMsg)
        elif configParams.bcolour == 'RED':
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(255,0,0)))
            self.conText.AppendText(tmpMsg)
        elif configParams.bcolour == 'ENDC':
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(0,0,0)))
            self.conText.AppendText(tmpMsg)
        else:
            self.conText.SetDefaultStyle(wx.TextAttr(wx.Colour(0,0,0)))

        return
        
        # Debug requested - then show all
        
    def onChecked(self, e):
        if self.cbDebug.IsChecked() == True:
            configParams.debug = True
        else:
            configParams.debug = False
            
            
    
        