#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Responsible for handling keyboard shortcuts.

This implementation is based on the code obtained from here:
http://wiki.wxpython.org/Using%20Multi-key%20Shortcuts

"""

import wx

KEYMAP = {}


def gen_keymap():
    """The base wx.Menu classes do not support all of the keys that our
    keyboard support, so that a list of possible pulsations is performed."""
    keys = ("BACK", "TAB", "RETURN", "ESCAPE", "SPACE", "DELETE", "START",
            "LBUTTON", "RBUTTON", "CANCEL", "MBUTTON", "CLEAR", "PAUSE",
            "CAPITAL", "PRIOR", "NEXT", "END", "HOME", "LEFT", "UP", "RIGHT",
            "DOWN", "SELECT", "PRINT", "EXECUTE", "SNAPSHOT", "INSERT", "HELP",
            "NUMPAD0", "NUMPAD1", "NUMPAD2", "NUMPAD3", "NUMPAD4", "NUMPAD5",
            "NUMPAD6", "NUMPAD7", "NUMPAD8", "NUMPAD9", "MULTIPLY", "ADD",
            "SEPARATOR", "SUBTRACT", "DECIMAL", "DIVIDE", "F1", "F2", "F3",
            "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12", "F13",
            "F14", "F15", "F16", "F17", "F18", "F19", "F20", "F21", "F22",
            "F23", "F24", "NUMLOCK", "SCROLL", "PAGEUP", "PAGEDOWN",
            "NUMPAD_SPACE", "NUMPAD_TAB", "NUMPAD_ENTER", "NUMPAD_F1",
            "NUMPAD_F2", "NUMPAD_F3", "NUMPAD_F4", "NUMPAD_HOME", "NUMPAD_LEFT",
            "NUMPAD_UP", "NUMPAD_RIGHT", "NUMPAD_DOWN", "NUMPAD_PRIOR",
            "NUMPAD_PAGEUP", "NUMPAD_NEXT", "NUMPAD_PAGEDOWN", "NUMPAD_END",
            "NUMPAD_BEGIN", "NUMPAD_INSERT", "NUMPAD_DELETE", "NUMPAD_EQUAL",
            "NUMPAD_MULTIPLY", "NUMPAD_ADD", "NUMPAD_SEPARATOR",
            "NUMPAD_SUBTRACT", "NUMPAD_DECIMAL", "NUMPAD_DIVIDE")

    for i in keys:
        KEYMAP[getattr(wx, "WXK_" + i)] = i
    for i in ("SHIFT", "ALT", "CONTROL", "MENU"):
        KEYMAP[getattr(wx, "WXK_" + i)] = ''


def get_key_press(event):
    """Generate specific names for each keyboard keypress combination that we
    come upon in our event processing."""
    key_code = event.GetKeyCode()
    key_name = KEYMAP.get(key_code, None)
    modifiers = ""
    for mod, ch in ((event.ControlDown(), 'Ctrl+'),
                    (event.AltDown(), 'Alt+'),
                    (event.ShiftDown(), 'Shift+'),
                    (event.MetaDown(), 'Meta+')):
        if mod:
            modifiers += ch

    if key_name is None:
        if 27 < key_code < 256:
            key_name = chr(key_code)
        else:
            key_name = "(%s)unknown" % key_code
    return modifiers + key_name
