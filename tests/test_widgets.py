#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Contains test cases for the widgets.py module."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))


try:
    import wx
    import mock

    from youtube_dl_gui.widgets import (
        ListBoxWithHeaders,
        CustomComboBox,
        ListBoxPopup
    )
except ImportError as error:
    print error
    sys.exit(1)


class TestListBoxWithHeaders(unittest.TestCase):

    """Test cases for the ListBoxWithHeaders widget."""

    def setUp(self):
        self.app = wx.App()

        self.frame = wx.Frame(None)
        self.listbox = ListBoxWithHeaders(self.frame)

        self.listbox.add_header("Header")
        self.listbox.add_items(["item%s" % i for i in xrange(10)])

    def tearDown(self):
        self.frame.Destroy()

    def test_find_string_header_found(self):
        self.assertEqual(self.listbox.FindString("Header"), 0)

    def test_find_string_header_not_found(self):
        self.assertEqual(self.listbox.FindString("Header2"), wx.NOT_FOUND)

    def test_find_string_item_found(self):
        self.assertEqual(self.listbox.FindString("item1"), 2)

    def test_find_string_item_not_found(self):
        self.assertEqual(self.listbox.FindString("item"), wx.NOT_FOUND)

    def test_get_string_header(self):
        self.assertEqual(self.listbox.GetString(0), "Header")

    def test_get_string_item(self):
        self.assertEqual(self.listbox.GetString(10), "item9")

    def test_get_string_item_not_found(self):
        self.assertEqual(self.listbox.GetString(11), "")

    def test_get_string_item_negative_index(self):
        self.assertEqual(self.listbox.GetString(-1), "")

    def test_insert_items(self):
        self.listbox.SetSelection(1)

        self.listbox.InsertItems(["new_item1", "new_item2"], 1)
        self.assertEqual(self.listbox.GetString(1), "new_item1")
        self.assertEqual(self.listbox.GetString(2), "new_item2")
        self.assertEqual(self.listbox.GetString(3), "item0")

        self.assertTrue(self.listbox.IsSelected(3))  # Old selection + 2

    def test_set_selection_header(self):
        self.listbox.SetSelection(0)
        self.assertFalse(self.listbox.IsSelected(0))

    def test_set_selection_item_valid_index(self):
        self.listbox.SetSelection(1)
        self.assertEqual(self.listbox.GetSelection(), 1)

    def test_set_selection_item_invalid_index(self):
        self.listbox.SetSelection(1)
        self.assertEqual(self.listbox.GetSelection(), 1)

        self.listbox.SetSelection(wx.NOT_FOUND)
        self.assertEqual(self.listbox.GetSelection(), wx.NOT_FOUND)

    def test_set_string_item(self):
        self.listbox.SetString(1, "item_mod0")
        self.assertEqual(self.listbox.GetString(1), "item_mod0")

    def test_set_string_header(self):
        self.listbox.SetString(0, "New header")
        self.assertEqual(self.listbox.GetString(0), "New header")

        # Make sure that the header is not selectable
        self.listbox.SetSelection(0)
        self.assertFalse(self.listbox.IsSelected(0))

    def test_set_string_selection_header(self):
        self.assertFalse(self.listbox.SetStringSelection("Header"))
        self.assertFalse(self.listbox.IsSelected(0))

    def test_set_string_selection_item(self):
        self.assertTrue(self.listbox.SetStringSelection("item1"))
        self.assertTrue(self.listbox.IsSelected(2))

    def test_get_string_selection(self):
        self.listbox.SetSelection(1)
        self.assertEqual(self.listbox.GetStringSelection(), "item0")

    def test_get_string_selection_empty(self):
        self.assertEqual(self.listbox.GetStringSelection(), "")

    # wx.ItemContainer methods

    def test_append(self):
        self.listbox.Append("item666")
        self.assertEqual(self.listbox.GetString(11), "item666")

    def test_append_items(self):
        self.listbox.AppendItems(["new_item1", "new_item2"])
        self.assertEqual(self.listbox.GetString(11), "new_item1")
        self.assertEqual(self.listbox.GetString(12), "new_item2")

    def test_clear(self):
        self.listbox.Clear()
        self.assertEqual(self.listbox.GetItems(), [])

    def test_delete(self):
        self.listbox.Delete(0)
        self.assertEqual(self.listbox.GetString(0), "item0")

        # Test item selection
        self.listbox.SetSelection(0)
        self.assertTrue(self.listbox.IsSelected(0))

    # Test object extra methods

    def test_add_header(self):
        self.listbox.add_header("Header2")
        self.listbox.SetSelection(11)
        self.assertFalse(self.listbox.IsSelected(11))

    @mock.patch("wx.ListBox.Append")
    def test_add_item_with_prefix(self, mock_append):
        self.listbox.add_item("new_item")
        mock_append.assert_called_once_with(ListBoxWithHeaders.TEXT_PREFIX + "new_item")

    @mock.patch("wx.ListBox.Append")
    def test_add_item_without_prefix(self, mock_append):
        self.listbox.add_item("new_item", with_prefix=False)
        mock_append.assert_called_once_with("new_item")

    @mock.patch("wx.ListBox.AppendItems")
    def test_add_items_with_prefix(self, mock_append):
        self.listbox.add_items(["new_item1", "new_item2"])
        mock_append.assert_called_once_with([ListBoxWithHeaders.TEXT_PREFIX + "new_item1",
                                             ListBoxWithHeaders.TEXT_PREFIX + "new_item2"])
    @mock.patch("wx.ListBox.AppendItems")
    def test_add_items_without_prefix(self, mock_append):
        self.listbox.add_items(["new_item1", "new_item2"], with_prefix=False)
        mock_append.assert_called_once_with(["new_item1", "new_item2"])


class TestCustomComboBox(unittest.TestCase):

    """Test cases for the CustomComboBox widget."""

    def setUp(self):
        self.app = wx.App()

        self.frame = wx.Frame(None)
        self.combobox = CustomComboBox(self.frame)

        # Call directly the ListBoxWithHeaders methods
        self.combobox.listbox.GetControl().add_header("Header")
        self.combobox.listbox.GetControl().add_items(["item%s" % i for i in xrange(10)])

    def tearDown(self):
        self.frame.Destroy()

    def test_init(self):
        combobox = CustomComboBox(self.frame, -1, "item1", choices=["item0", "item1", "item2"])

        self.assertEqual(combobox.GetValue(), "item1")
        self.assertEqual(combobox.GetCount(), 3)
        self.assertEqual(combobox.GetSelection(), 1)

    # wx.ComboBox methods
    # Not all of them since most of them are calls to ListBoxWithHeaders
    # methods and we already have tests for those

    def test_is_list_empty_false(self):
        self.assertFalse(self.combobox.IsListEmpty())

    def test_is_list_empty_true(self):
        self.combobox.Clear()
        self.assertTrue(self.combobox.IsListEmpty())

    def test_is_text_empty_false(self):
        self.combobox.SetValue("somevalue")
        self.assertFalse(self.combobox.IsTextEmpty())

    def test_is_text_empty_true(self):
        self.assertTrue(self.combobox.IsTextEmpty())

    def test_set_selection_item(self):
        self.combobox.SetSelection(1)
        self.assertEqual(self.combobox.GetSelection(), 1)
        self.assertEqual(self.combobox.GetValue(), "item0")

    def test_set_selection_header(self):
        self.combobox.SetSelection(0)
        self.assertEqual(self.combobox.GetSelection(), wx.NOT_FOUND)
        self.assertEqual(self.combobox.GetValue(), "")

    def test_set_string_selection_item(self):
        self.combobox.SetStringSelection("item0")
        self.assertEqual(self.combobox.GetStringSelection(), "item0")
        self.assertEqual(self.combobox.GetValue(), "item0")

    def test_set_string_selection_header(self):
        self.combobox.SetStringSelection("Header")
        self.assertEqual(self.combobox.GetStringSelection(), "")
        self.assertEqual(self.combobox.GetValue(), "")

    def test_set_string_selection_invalid_string(self):
        self.combobox.SetStringSelection("abcde")
        self.assertEqual(self.combobox.GetStringSelection(), "")
        self.assertEqual(self.combobox.GetValue(), "")

    # wx.ItemContainer methods

    def test_clear(self):
        self.combobox.SetValue("value")

        self.combobox.Clear()
        self.assertEqual(self.combobox.GetCount(), 0)
        self.assertTrue(self.combobox.IsTextEmpty())

    def test_append(self):
        self.combobox.Append("item10")
        self.assertEqual(self.combobox.GetCount(), 12)

    def test_append_items(self):
        self.combobox.AppendItems(["item10", "item11"])
        self.assertEqual(self.combobox.GetCount(), 13)

    def test_delete(self):
        self.combobox.Delete(1)
        self.assertEqual(self.combobox.GetString(1), "item1")

    # wx.TextEntry methods

    def test_get_value(self):
        self.combobox.SetValue("value")
        self.assertEqual(self.combobox.GetValue(), "value")


def main():
    unittest.main()


if __name__ == '__main__':
    main()
