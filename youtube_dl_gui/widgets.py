#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import unicode_literals

import sys

try:
    import wx
except ImportError as error:
    print error
    sys.exit(1)


def crt_command_event(event_type, event_id=0):
    """Shortcut to create command events."""
    return wx.CommandEvent(event_type.typeId, event_id)


class ListBoxWithHeaders(wx.ListBox):

    """Custom ListBox object that supports 'headers'.

    Attributes:
        NAME (string): Default name for the name argument of the __init__.

        TEXT_PREFIX (string): Text to add before normal items in order to
            distinguish them (normal items) from headers.

        EVENTS (list): List with events to overwrite to avoid header selection.

    """

    NAME = "listBoxWithHeaders"

    TEXT_PREFIX = "    "

    EVENTS = [
        wx.EVT_LEFT_DOWN,
        wx.EVT_LEFT_DCLICK,
        wx.EVT_RIGHT_DOWN,
        wx.EVT_RIGHT_DCLICK,
        wx.EVT_MIDDLE_DOWN,
        wx.EVT_MIDDLE_DCLICK
    ]

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator, name=NAME):
        super(ListBoxWithHeaders, self).__init__(parent, id, pos, size, [], style, validator, name)
        self.__headers = set()

        # Ignore all key events i'm bored to handle the header selection
        self.Bind(wx.EVT_KEY_DOWN, lambda event: None)

        # Make sure that a header is never selected
        self.Bind(wx.EVT_LISTBOX, self._on_listbox)
        for event in self.EVENTS:
            self.Bind(event, self._disable_header_selection)

        # Append the items in our own way in order to add the TEXT_PREFIX
        self.AppendItems(choices)

    def _disable_header_selection(self, event):
        """Stop event propagation if the selected item is a header."""
        row = self.HitTest(event.GetPosition())
        event_skip = True

        if row != wx.NOT_FOUND and self.GetString(row) in self.__headers:
            event_skip = False

        event.Skip(event_skip)

    def _on_listbox(self, event):
        """Make sure no header is selected."""
        if event.GetString() in self.__headers:
            self.Deselect(event.GetSelection())
        event.Skip()

    def _add_prefix(self, string):
        return self.TEXT_PREFIX + string

    def _remove_prefix(self, string):
        if string[:len(self.TEXT_PREFIX)] == self.TEXT_PREFIX:
            return string[len(self.TEXT_PREFIX):]
        return string

    # wx.ListBox methods

    def FindString(self, string):
        index = super(ListBoxWithHeaders, self).FindString(string)

        if index == wx.NOT_FOUND:
            # This time try with prefix
            index = super(ListBoxWithHeaders, self).FindString(self._add_prefix(string))

        return index

    def GetStringSelection(self):
        return self._remove_prefix(super(ListBoxWithHeaders, self).GetStringSelection())

    def GetString(self, index):
        if index < 0 or index >= self.GetCount():
            # Return empty string based on the wx.ListBox docs
            # for some reason parent GetString does not handle
            # invalid indices
            return ""

        return self._remove_prefix(super(ListBoxWithHeaders, self).GetString(index))

    def InsertItems(self, items, pos):
        items = [self._add_prefix(item) for item in items]
        super(ListBoxWithHeaders, self).InsertItems(items, pos)

    def SetSelection(self, index):
        if index == wx.NOT_FOUND:
            self.Deselect(self.GetSelection())
        elif self.GetString(index) not in self.__headers:
            super(ListBoxWithHeaders, self).SetSelection(index)

    def SetString(self, index, string):
        old_string = self.GetString(index)

        if old_string in self.__headers and string != old_string:
            self.__headers.remove(old_string)
            self.__headers.add(string)

        super(ListBoxWithHeaders, self).SetString(index, string)

    def SetStringSelection(self, string):
        if string in self.__headers:
            return False

        self.SetSelection(self.FindString(string))
        return True

    # wx.ItemContainer methods

    def Append(self, string):
        super(ListBoxWithHeaders, self).Append(self._add_prefix(string))

    def AppendItems(self, strings):
        strings = [self._add_prefix(string) for string in strings]
        super(ListBoxWithHeaders, self).AppendItems(strings)

    def Clear(self):
        self.__headers.clear()
        super(ListBoxWithHeaders, self).Clear()

    def Delete(self, index):
        string = self.GetString(index)

        if string in self.__headers:
            self.__headers.remove(string)

        super(ListBoxWithHeaders, self).Delete(index)

    # Extra methods

    def add_header(self, header_string):
        self.__headers.add(header_string)
        super(ListBoxWithHeaders, self).Append(header_string)

    def add_item(self, item, with_prefix=True):
        if with_prefix:
            item = self._add_prefix(item)

        super(ListBoxWithHeaders, self).Append(item)

    def add_items(self, items, with_prefix=True):
        if with_prefix:
            items = [self._add_prefix(item) for item in items]

        super(ListBoxWithHeaders, self).AppendItems(items)


class ListBoxPopup(wx.PopupTransientWindow):

    """ListBoxWithHeaders as a popup.

    This class uses the wx.PopupTransientWindow to create the popup and the
    API is based on the wx.combo.ComboPopup class.

    Attributes:
        EVENTS_TABLE (dict): Dictionary that contains all the events
            that this class emits.

    """

    EVENTS_TABLE = {
        "EVT_COMBOBOX": crt_command_event(wx.EVT_COMBOBOX),
        "EVT_COMBOBOX_DROPDOWN" : crt_command_event(wx.EVT_COMBOBOX_DROPDOWN),
        "EVT_COMBOBOX_CLOSEUP": crt_command_event(wx.EVT_COMBOBOX_CLOSEUP)
    }

    def __init__(self, parent=None, flags=wx.BORDER_NONE):
        super(ListBoxPopup, self).__init__(parent, flags)
        self.__listbox = None

    def _on_motion(self, event):
        row = self.__listbox.HitTest(event.GetPosition())

        if row != wx.NOT_FOUND:
            self.__listbox.SetSelection(row)

            if self.__listbox.IsSelected(row):
                self.curitem = row

    def _on_left_down(self, event):
        self.value = self.curitem
        self.Dismiss()

        # Send EVT_COMBOBOX to inform the parent for changes
        wx.PostEvent(self, self.EVENTS_TABLE["EVT_COMBOBOX"])

    def Popup(self):
        super(ListBoxPopup, self).Popup()
        wx.PostEvent(self, self.EVENTS_TABLE["EVT_COMBOBOX_DROPDOWN"])

    def OnDismiss(self):
        wx.PostEvent(self, self.EVENTS_TABLE["EVT_COMBOBOX_CLOSEUP"])

    # wx.combo.ComboPopup methods

    def Init(self):
        self.value = self.curitem = -1

    def Create(self, parent):
        self.__listbox = ListBoxWithHeaders(parent, style=wx.LB_SINGLE)

        self.__listbox.Bind(wx.EVT_MOTION, self._on_motion)
        self.__listbox.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)

        sizer = wx.BoxSizer()
        sizer.Add(self.__listbox, 1, wx.EXPAND)
        self.SetSizer(sizer)
        return True

    def GetAdjustedSize(self, min_width, pref_height, max_height):
        width, height = self.GetBestSize()

        if width < min_width:
            width = min_width

        if pref_height != -1:
            height = pref_height * self.__listbox.GetCount() + 5

        if height > max_height:
            height = max_height

        return wx.Size(width, height)

    def GetControl(self):
        return self.__listbox

    def GetStringValue(self):
        return self.__listbox.GetString(self.value)

    #def SetStringValue(self, string):
        #self.__listbox.SetStringSelection(string)


class CustomComboBox(wx.Panel):

    """Custom combobox.

    Attributes:
        CB_READONLY (long): Read-only style. The only one supported from the
            wx.ComboBox styles.

        NAME (string): Default name for the name argument of the __init__.

    """
    #NOTE wx.ComboBox does not support EVT_MOTION inside the popup
    #NOTE Tried with ComboCtrl but i was not able to draw the button

    CB_READONLY = wx.TE_READONLY

    NAME = "customComboBox"

    def __init__(self, parent, id=wx.ID_ANY, value="", pos=wx.DefaultPosition,
            size=wx.DefaultSize, choices=[], style=0, validator=wx.DefaultValidator, name=NAME):
        super(CustomComboBox, self).__init__(parent, id, pos, size, 0, name)

        assert style == self.CB_READONLY or style == 0

        # Create components
        self.textctrl = wx.TextCtrl(self, wx.ID_ANY, style=style, validator=validator)
        tc_height = self.textctrl.GetSize()[1]

        self.button = wx.Button(self, wx.ID_ANY, "▾", size=(tc_height, tc_height))

        # Create the ListBoxPopup in two steps
        self.listbox = ListBoxPopup(self)
        self.listbox.Init()
        self.listbox.Create(self.listbox)

        # Set layout
        sizer = wx.BoxSizer()
        sizer.Add(self.textctrl, 1, wx.ALIGN_CENTER_VERTICAL)
        sizer.Add(self.button)
        self.SetSizer(sizer)

        # Bind events
        self.button.Bind(wx.EVT_BUTTON, self._on_button)

        for event in ListBoxPopup.EVENTS_TABLE.values():
            self.listbox.Bind(wx.PyEventBinder(event.GetEventType()), self._propagate)

        # Append items since the ListBoxPopup does not have the 'choices' arg
        self.listbox.GetControl().AppendItems(choices)
        self.SetStringSelection(value)

    def _propagate(self, event):
        if event.GetEventType() == wx.EVT_COMBOBOX.typeId:
            self.textctrl.SetValue(self.listbox.GetStringValue())

        wx.PostEvent(self, event)

    def _on_button(self, event):
        self.Popup()

    def _calc_popup_position(self):
        tc_x_axis, tc_y_axis = self.textctrl.ClientToScreen((0, 0))
        _, tc_height = self.textctrl.GetSize()

        return tc_x_axis, tc_y_axis + tc_height

    def _calc_popup_size(self):
        me_width, _ = self.GetSize()
        _, tc_height = self.textctrl.GetSize()
        _, screen_height = wx.DisplaySize()

        _, me_y_axis = self.GetScreenPosition()

        available_height = screen_height - (me_y_axis + tc_height)
        sug_width, sug_height = self.listbox.GetAdjustedSize(me_width, tc_height, available_height)

        return me_width, sug_height

    # wx.ComboBox methods

    def Dismiss(self):
        self.listbox.Dismiss()

    def FindString(self, string, caseSensitive=False):
        #TODO handle caseSensitive
        return self.listbox.GetControl().FindString(string)

    def GetCount(self):
        return self.listbox.GetControl().GetCount()

    def GetCurrentSelection(self):
        return self.GetSelection()

    def GetInsertionPoint(self):
        return self.textctrl.GetInsertionPoint()

    def GetSelection(self):
        return self.listbox.value

    def GetTextSelection(self):
        return self.textctrl.GetSelection()

    def GetString(self, index):
        return self.listbox.GetControl().GetString(index)

    def GetStringSelection(self):
        return self.listbox.GetStringValue()

    def IsListEmpty(self):
        return self.listbox.GetControl().GetCount() == 0

    def IsTextEmpty(self):
        return not self.textctrl.GetValue()

    def Popup(self):
        self.listbox.SetPosition(self._calc_popup_position())
        self.listbox.SetSize(self._calc_popup_size())

        self.listbox.Popup()

    def SetSelection(self, index):
        self.listbox.GetControl().SetSelection(index)
        if self.listbox.GetControl().IsSelected(index):
            self.listbox.value = index
            self.textctrl.SetValue(self.listbox.GetStringValue())

    def SetString(self, index, string):
        self.listbox.GetControl().SetString(index, string)

    def SetTextSelection(self, from_, to_):
        self.textctrl.SetSelection(from_, to_)

    def SetStringSelection(self, string):
        index = self.listbox.GetControl().FindString(string)
        self.listbox.GetControl().SetSelection(index)

        if index != wx.NOT_FOUND and self.listbox.GetControl().GetSelection() == index:
            self.listbox.value = index
            self.textctrl.SetValue(string)

    def SetValue(self, value):
        self.textctrl.SetValue(value)

    # wx.ItemContainer methods

    def Clear(self):
        self.textctrl.Clear()
        self.listbox.GetControl().Clear()

    def Append(self, item):
        self.listbox.GetControl().Append(item)

    def AppendItems(self, items):
        self.listbox.GetControl().AppendItems(items)

    def Delete(self, index):
        self.listbox.GetControl().Delete(index)

    # wx.TextEntry methods

    def GetValue(self):
        return self.textctrl.GetValue()

    # ListBoxWithHeaders methods

    def add_header(self, header):
        self.listbox.GetControl().add_header(header)

    def add_item(self, item, with_prefix=True):
        self.listbox.GetControl().add_item(item, with_prefix)

    def add_items(self, items, with_prefix=True):
        self.listbox.GetControl().add_items(items, with_prefix)
