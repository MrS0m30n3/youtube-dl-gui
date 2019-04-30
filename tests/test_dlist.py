#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""Contains test cases for the DownloadList object."""

from __future__ import unicode_literals

import sys
import os.path
import unittest

PATH = os.path.realpath(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(PATH)))

try:
    import mock
    from youtube_dl_gui.downloadmanager import DownloadList, synchronized
except ImportError as error:
    print error
    sys.exit(1)


class TestInit(unittest.TestCase):

    """Test case for the DownloadList init."""

    def test_init(self):
        mocks = [mock.Mock(object_id=0), mock.Mock(object_id=1)]

        dlist = DownloadList(mocks)
        self.assertEqual(dlist._items_list, [0, 1])
        self.assertEqual(dlist._items_dict, {0: mocks[0], 1: mocks[1]})

    def test_init_empty(self):
        dlist = DownloadList()
        self.assertEqual(dlist._items_list, [])
        self.assertEqual(dlist._items_dict, {})

    def test_init_invalid_args(self):
        self.assertRaises(AssertionError, DownloadList, {})
        self.assertRaises(AssertionError, DownloadList, ())
        self.assertRaises(AssertionError, DownloadList, False)


class TestInsert(unittest.TestCase):

    """Test case for the DownloadList insert method."""

    def test_insert(self):
        mock_ditem = mock.Mock(object_id=0)

        dlist = DownloadList()
        dlist.insert(mock_ditem)

        self.assertEqual(dlist._items_list, [0])
        self.assertEqual(dlist._items_dict, {0: mock_ditem})


class TestRemove(unittest.TestCase):

    """Test case for the DownloadList remove method."""

    def setUp(self):
        self.mocks = [mock.Mock(object_id=0), mock.Mock(object_id=1), mock.Mock(object_id=2)]
        self.dlist = DownloadList(self.mocks)

    def test_remove(self):
        self.assertTrue(self.dlist.remove(1))

        self.assertEqual(self.dlist._items_list, [0, 2])
        self.assertEqual(self.dlist._items_dict, {0: self.mocks[0], 2: self.mocks[2]})

    def test_remove_not_exist(self):
        self.assertRaises(KeyError, self.dlist.remove, 3)

    def test_remove_active(self):
        self.mocks[1].stage = "Active"

        self.assertFalse(self.dlist.remove(1))
        self.assertEqual(self.dlist._items_list, [0, 1, 2])
        self.assertEqual(self.dlist._items_dict, {0: self.mocks[0], 1: self.mocks[1], 2: self.mocks[2]})


class TestFetchNext(unittest.TestCase):

    """Test case for the DownloadList fetch_next method."""

    def test_fetch_next(self):
        items_count = 3

        mocks = [mock.Mock(object_id=i, stage="Queued") for i in range(items_count)]

        dlist = DownloadList(mocks)

        for i in range(items_count):
            self.assertEqual(dlist.fetch_next(), mocks[i])
            mocks[i].stage = "Active"

        self.assertIsNone(dlist.fetch_next())

        for i in range(items_count):
            mocks[i].stage = "Completed"

        self.assertIsNone(dlist.fetch_next())

        mocks[1].stage = "Queued"  # Re-queue item
        self.assertEqual(dlist.fetch_next(), mocks[1])

    def test_fetch_next_empty_list(self):
        dlist = DownloadList()
        self.assertIsNone(dlist.fetch_next())


class TestMoveUp(unittest.TestCase):

    """Test case for the DownloadList move_up method."""

    def setUp(self):
        mocks = [mock.Mock(object_id=i, stage="Queued") for i in range(3)]
        self.dlist = DownloadList(mocks)

    def test_move_up(self):
        self.assertTrue(self.dlist.move_up(1))
        self.assertEqual(self.dlist._items_list, [1, 0, 2])

    def test_move_up_already_on_top(self):
        self.assertFalse(self.dlist.move_up(0))
        self.assertEqual(self.dlist._items_list, [0, 1, 2])

    def test_move_up_not_exist(self):
        self.assertRaises(ValueError, self.dlist.move_up, 666)


class TestMoveDown(unittest.TestCase):

    """Test case for the DownloadList move_down method."""

    def setUp(self):
        mocks = [mock.Mock(object_id=i, stage="Queued") for i in range(3)]
        self.dlist = DownloadList(mocks)

    def test_move_down(self):
        self.assertTrue(self.dlist.move_down(1))
        self.assertEqual(self.dlist._items_list, [0, 2, 1])

    def test_move_down_already_on_bottom(self):
        self.assertFalse(self.dlist.move_down(2))
        self.assertEqual(self.dlist._items_list, [0, 1, 2])

    def test_move_down_not_exist(self):
        self.assertRaises(ValueError, self.dlist.move_down, 666)


class TestGetItem(unittest.TestCase):

    """Test case for the DownloadList get_item method."""

    def test_get_item(self):
        mocks = [mock.Mock(object_id=i) for i in range(3)]
        dlist = DownloadList(mocks)

        self.assertEqual(dlist.get_item(0), mocks[0])
        self.assertEqual(dlist.get_item(2), mocks[2])

    def test_get_item_not_exist(self):
        dlist = DownloadList()
        self.assertRaises(KeyError, dlist.get_item, 0)


class TestGetLength(unittest.TestCase):

    """Test case for the DownloadList __len__ method."""

    def test_get_length(self):
        dlist = DownloadList([mock.Mock(), mock.Mock()])
        self.assertEqual(len(dlist), 2)

    def test_get_length_empty_list(self):
        dlist = DownloadList()
        self.assertEqual(len(dlist), 0)


class TestHasItem(unittest.TestCase):

    """Test case for the DownloadList has_item method."""

    def setUp(self):
        mock_ditem = mock.Mock(object_id=1337)
        self.dlist = DownloadList([mock_ditem])

    def test_has_item_true(self):
        self.assertTrue(self.dlist.has_item(1337))

    def test_has_item_false(self):
        self.assertFalse(self.dlist.has_item(1000))


class TestGetItems(unittest.TestCase):

    """Test case for the DownloadList get_items method."""

    def test_get_items(self):
        mocks = [mock.Mock() for _ in range(3)]
        dlist = DownloadList(mocks)

        self.assertEqual(dlist.get_items(), mocks)

    def test_get_items_empty_list(self):
        dlist = DownloadList()
        self.assertEqual(dlist.get_items(), [])


class TestClear(unittest.TestCase):

    """Test case for the DownloadList clear method."""

    def test_clear(self):
        dlist = DownloadList([mock.Mock() for _ in range(3)])

        self.assertEqual(len(dlist), 3)
        dlist.clear()
        self.assertEqual(len(dlist), 0)


class TestChangeStage(unittest.TestCase):

    """Test case for the DownloadList change_stage method."""

    def setUp(self):
        self.mocks = [mock.Mock(object_id=i, stage="Queued") for i in range(3)]
        self.dlist = DownloadList(self.mocks)

    def test_change_stage(self):
        self.dlist.change_stage(0, "Active")
        self.assertEqual(self.mocks[0].stage, "Active")

    def test_change_stage_id_not_exist(self):
        self.assertRaises(KeyError, self.dlist.change_stage, 3, "Active")


class TestIndex(unittest.TestCase):

    """Test case for the DownloadList index method."""

    def setUp(self):
        self.mocks = [mock.Mock(object_id=i) for i in range(3)]
        self.dlist = DownloadList(self.mocks)

    def test_index(self):
        self.assertEqual(self.dlist.index(2), 2)

    def test_index_not_exist(self):
        self.assertEqual(self.dlist.index(3), -1)


class TestSynchronizeDecorator(unittest.TestCase):

    def test_synchronize(self):
        mock_func = mock.Mock()
        mock_lock = mock.Mock()

        decorated_func = synchronized(mock_lock)(mock_func)

        self.assertEqual(decorated_func(1, a=2), mock_func.return_value)

        mock_func.assert_called_once_with(1, a=2)
        mock_lock.acquire.assert_called_once()
        mock_lock.release.assert_called_once()


def main():
    unittest.main()


if __name__ == '__main__':
    main()
