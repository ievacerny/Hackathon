# This file is generated by wxPython's SIP generator.  Do not edit by hand.
#
# Copyright: (c) 2017 by Total Control Software
# License:   wxWindows License

"""
The `wx.ribbon` module contains a set of classes for writing a ribbon-based user interface.

At the most generic level, this is a combination of a tab control with a
toolbar. At a more functional level, it is similar to the user interface
present in recent versions of Microsoft Office and in Windows 10.
"""

from ._ribbon import *

import wx

EVT_RIBBONPANEL_EXTBUTTON_ACTIVATED = wx.PyEventBinder(wxEVT_RIBBONPANEL_EXTBUTTON_ACTIVATED, 1)

EVT_RIBBONBAR_PAGE_CHANGED    = wx.PyEventBinder(wxEVT_RIBBONBAR_PAGE_CHANGED, 1)
EVT_RIBBONBAR_PAGE_CHANGING   = wx.PyEventBinder(wxEVT_RIBBONBAR_PAGE_CHANGING,1)
EVT_RIBBONBAR_TAB_MIDDLE_DOWN = wx.PyEventBinder(wxEVT_RIBBONBAR_TAB_MIDDLE_DOWN, 1)
EVT_RIBBONBAR_TAB_MIDDLE_UP   = wx.PyEventBinder(wxEVT_RIBBONBAR_TAB_MIDDLE_UP, 1)
EVT_RIBBONBAR_TAB_RIGHT_DOWN  = wx.PyEventBinder(wxEVT_RIBBONBAR_TAB_RIGHT_DOWN, 1)
EVT_RIBBONBAR_TAB_RIGHT_UP    = wx.PyEventBinder(wxEVT_RIBBONBAR_TAB_RIGHT_UP, 1)
EVT_RIBBONBAR_TAB_LEFT_DCLICK = wx.PyEventBinder(wxEVT_RIBBONBAR_TAB_LEFT_DCLICK, 1)
EVT_RIBBONBAR_TOGGLED         = wx.PyEventBinder(wxEVT_RIBBONBAR_TOGGLED, 1)
EVT_RIBBONBAR_HELP_CLICK      = wx.PyEventBinder(wxEVT_RIBBONBAR_HELP_CLICK, 1)

def _RibbonPageTabInfoArray___repr__(self):
    return "RibbonPageTabInfoArray: " + repr(list(self))
RibbonPageTabInfoArray.__repr__ = _RibbonPageTabInfoArray___repr__
del _RibbonPageTabInfoArray___repr__
if 'wxMSW' in wx.PlatformInfo:
    RibbonDefaultArtProvider = RibbonMSWArtProvider
else:
    RibbonDefaultArtProvider = RibbonAUIArtProvider

EVT_RIBBONBUTTONBAR_CLICKED = wx.PyEventBinder( wxEVT_RIBBONBUTTONBAR_CLICKED, 1 )
EVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED = wx.PyEventBinder( wxEVT_RIBBONBUTTONBAR_DROPDOWN_CLICKED, 1 )

EVT_RIBBONGALLERY_HOVER_CHANGED = wx.PyEventBinder( wxEVT_RIBBONGALLERY_HOVER_CHANGED, 1 )
EVT_RIBBONGALLERY_SELECTED = wx.PyEventBinder( wxEVT_RIBBONGALLERY_SELECTED, 1 )
EVT_RIBBONGALLERY_CLICKED = wx.PyEventBinder( wxEVT_RIBBONGALLERY_CLICKED, 1 )

EVT_RIBBONTOOLBAR_CLICKED = wx.PyEventBinder( wxEVT_RIBBONTOOLBAR_CLICKED, 1 )
EVT_RIBBONTOOLBAR_DROPDOWN_CLICKED = wx.PyEventBinder( wxEVT_RIBBONTOOLBAR_DROPDOWN_CLICKED, 1 )

