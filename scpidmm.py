#!/usr/bin/env python
# vim: syntax smartindent shiftwidth=2 tabstop=2 noexpandtab

import wx
import owon
from time import sleep


class MainWindow(wx.Frame):
	VOLT=0
	CURR=1
	RES=2
	CAP=3
	FREQ=4
	TEMP=5


	TIMER=6
	refresh=100
	frame=0
	hl=-1
	def __init__(self, parent, title):
		wx.Frame.__init__(self, parent, title=title, size=(-1,-1))
		hsizer = wx.BoxSizer(wx.HORIZONTAL)
		grid=wx.GridBagSizer(hgap=1, vgap=1)

		# keep this in sync with the class global variables, it will be
		# used to index the functions for acces to button properties
		self.buttons = [
			wx.Button(self, id=self.VOLT, label="≂ V"),
			wx.Button(self, id=self.CURR, label="≂ A"),
			wx.Button(self, id=self.RES, label="Ω 🔊"),
			wx.Button(self, id=self.CAP, label="CAP"),
			wx.Button(self, id=self.FREQ, label="FREQ"),
			wx.Button(self, id=self.TEMP, label="TEMP")
		]

		grid.Add(self.buttons[self.VOLT], pos=(0,0))
		grid.Add(self.buttons[self.CURR], pos=(0,1))
		grid.Add(self.buttons[self.RES], pos=(0,2))
		grid.Add(self.buttons[self.CAP], pos=(1,0))
		grid.Add(self.buttons[self.FREQ], pos=(1,1))
		grid.Add(self.buttons[self.TEMP], pos=(1,2))

		self.timer=wx.Timer(self,self.TIMER)
		self.Bind(wx.EVT_TIMER, self.OnTimer, id=self.TIMER)

		# Open the connection to the multimeter
		self.multimeter=owon.DMM()

		self.display=wx.StaticText(self, size=(600,-1), style=wx.ALIGN_CENTRE_HORIZONTAL)

		hsizer.Add(self.display)
		hsizer.Add(grid)
	
		self.SetSizerAndFit(hsizer)

		self.Bind(wx.EVT_BUTTON, self.OnClick)
		self.CreateStatusBar() # A Statusbar in the bottom of the window
		self.SetLabel(" ".join(["scpiDMM:"]+ self.multimeter.idn.split(",")[:2]))

		# Setting up the menu.
		filemenu=wx.Menu()

		# wx.ABOUT and wx.EXIT are standard IDs provided by wxWidgets.
		#filemenu.Append(wx.ABOUT, "&About"," Information about this program")
		filemenu.AppendSeparator()
		#filemenu.Append(wx.EXIT,"E&xit"," Terminate the program")
		filemenu.Append(15, "Preferences", "Multimeter configuration")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
		self.Show(True)
		self.timer.Start(self.refresh)

	def OnTimer(self,id):
		self.multimeter.get()
		if ( self.multimeter.function1.button() == -1 ):
			if ( self.timer.GetInterval() == self.refresh ):
				self.timer.Start(2000)
			self.display.SetLabelMarkup("<span size='40960' foreground='red' background='black'>OFFLINE</span>")
		else:
			if ( self.timer.GetInterval() != self.refresh ):
				self.timer.Start(self.refresh)
			hl = self.multimeter.function1.button()
#			output="{}{}".format(self.multimeter.value(), self.m[self.multimeter.function1][1])
			self.display.SetLabelMarkup("<span size='40960' foreground='red' background='black' font-family='ui-monospace'>{}</span>".format(self.multimeter.function1))
			if (self.hl != hl):
				self.buttons[self.hl].SetBackgroundColour(wx.NullColour)
				self.buttons[hl].SetBackgroundColour(wx.Colour(50,255,50))
				self.hl = hl

	def OnClick(self,event):
		btn=event.GetEventObject()
		button_id = btn.GetId()
		if ( button_id == self.VOLT ):
			if ( self.multimeter.function1 == "VOLT" ):
				self.multimeter.switch_mode("VOLT:AC")
			else:
				self.multimeter.switch_mode("VOLT:DC")
		if ( button_id == self.CURR ):
			if ( self.multimeter.function1 == "CURR" ):
				self.multimeter.switch_mode("CURR:AC")
			else:
				self.multimeter.switch_mode("CURR:DC")
		if ( button_id == self.RES ):
			match self.multimeter.function1:
				case 'RES':
					self.multimeter.switch_mode("CONT")
				case 'CONT':
					self.multimeter.switch_mode("DIOD")
				case 'DIOD':
					self.multimeter.switch_mode("RES")
				case _:
					self.multimeter.switch_mode("RES")
		if ( button_id == self.CAP ):
			self.multimeter.switch_mode("CAP")
		if ( button_id == self.FREQ ):
			self.multimeter.switch_mode("FREQ")
		if ( button_id == self.TEMP ):
			self.multimeter.switch_mode("TEMP")

		

app = wx.App()
frame = MainWindow(None, "HorroDMM")
frame.Show(True)
app.MainLoop()

