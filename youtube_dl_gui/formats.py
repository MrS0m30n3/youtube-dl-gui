# -*- coding: UTF-8 -*-

import gettext

from .utils import TwoWayOrderedDict as tdict


OUTPUT_FORMATS = tdict([
    (0, _("ID")),
    (1, _("Title")),
    (2, _("Title + ID")),
    (4, _("Title + Quality")),
    (5, _("Title + ID + Quality")),
    (3, _("Custom"))
])


DEFAULT_FORMATS = tdict([
    ("0", _("default"))
])


VIDEO_FORMATS = tdict([
    ("3gp", "3gp"),
    ("17", "3gp [144p]"),
    ("36", "3gp [240p]"),
    ("flv", "flv"),
    ("5", "flv [240p]"),
    ("34", "flv [360p]"),
    ("35", "flv [480p]"),
    ("webm", "webm"),
    ("43", "webm [360p]"),
    ("44", "webm [480p]"),
    ("45", "webm [720p]"),
    ("46", "webm [1080p]"),
    ("mp4", "mp4"),
    ("18", "mp4 [360p]"),
    ("22", "mp4 [720p]"),
    ("37", "mp4 [1080p]"),
    ("38", "mp4 [4K]"),
    ("160", "mp4 [144p] (DASH Video)"),
    ("133", "mp4 [240p] (DASH Video)"),
    ("134", "mp4 [360p] (DASH Video)"),
    ("135", "mp4 [480p] (DASH Video)"),
    ("136", "mp4 [720p] (DASH Video)"),
    ("137", "mp4 [1080p] (DASH Video)"),
    ("264", "mp4 [1440p] (DASH Video)"),
    ("138", "mp4 [2160p] (DASH Video)"),
    ("242", "webm [240p] (DASH Video)"),
    ("243", "webm [360p] (DASH Video)"),
    ("244", "webm [480p] (DASH Video)"),
    ("247", "webm [720p] (DASH Video)"),
    ("248", "webm [1080p] (DASH Video)"),
    ("271", "webm [1440p] (DASH Video)"),
    ("272", "webm [2160p] (DASH Video)"),
    ("82", "mp4 [360p] (3D)"),
    ("83", "mp4 [480p] (3D)"),
    ("84", "mp4 [720p] (3D)"),
    ("85", "mp4 [1080p] (3D)"),
    ("100", "webm [360p] (3D)"),
    ("101", "webm [480p] (3D)"),
    ("102", "webm [720p] (3D)"),
    ("139", "m4a 48k (DASH Audio)"),
    ("140", "m4a 128k (DASH Audio)"),
    ("141", "m4a 256k (DASH Audio)"),
    ("171", "webm 48k (DASH Audio)"),
    ("172", "webm 256k (DASH Audio)")
])


AUDIO_FORMATS = tdict([
    ("mp3", "mp3"),
    ("wav", "wav"),
    ("aac", "aac"),
    ("m4a", "m4a"),
    ("vorbis", "vorbis"),
    ("opus", "opus")
])


FORMATS = DEFAULT_FORMATS.copy()
FORMATS.update(VIDEO_FORMATS)
FORMATS.update(AUDIO_FORMATS)


def reload_strings():
    # IF YOU DONT WANT YOUR EYES TO BLEED STOP HERE
    # YOU HAVE BEEN WARNED
    # DO NOT LOOK THE CODE BELOW
    #
    #
    #
    #
    #
    #
    #
    #
    #NOTE Remove
    # Code is so messed up that i need to reload strings else
    # the translations wont work on the about gettext tags
    global OUTPUT_FORMATS
    global DEFAULT_FORMATS
    global VIDEO_FORMATS
    global AUDIO_FORMATS
    global FORMATS

    OUTPUT_FORMATS = tdict([
        (0, _("ID")),
        (1, _("Title")),
        (2, _("Title + ID")),
        (4, _("Title + Quality")),
        (5, _("Title + ID + Quality")),
        (3, _("Custom"))
    ])


    DEFAULT_FORMATS = tdict([
        ("0", _("default"))
    ])


    VIDEO_FORMATS = tdict([
        ("3gp", "3gp"),
        ("17", "3gp [144p]"),
        ("36", "3gp [240p]"),
        ("flv", "flv"),
        ("5", "flv [240p]"),
        ("34", "flv [360p]"),
        ("35", "flv [480p]"),
        ("webm", "webm"),
        ("43", "webm [360p]"),
        ("44", "webm [480p]"),
        ("45", "webm [720p]"),
        ("46", "webm [1080p]"),
        ("mp4", "mp4"),
        ("18", "mp4 [360p]"),
        ("22", "mp4 [720p]"),
        ("37", "mp4 [1080p]"),
        ("38", "mp4 [4K]"),
        ("160", "mp4 [144p] (DASH Video)"),
        ("133", "mp4 [240p] (DASH Video)"),
        ("134", "mp4 [360p] (DASH Video)"),
        ("135", "mp4 [480p] (DASH Video)"),
        ("136", "mp4 [720p] (DASH Video)"),
        ("137", "mp4 [1080p] (DASH Video)"),
        ("264", "mp4 [1440p] (DASH Video)"),
        ("138", "mp4 [2160p] (DASH Video)"),
        ("242", "webm [240p] (DASH Video)"),
        ("243", "webm [360p] (DASH Video)"),
        ("244", "webm [480p] (DASH Video)"),
        ("247", "webm [720p] (DASH Video)"),
        ("248", "webm [1080p] (DASH Video)"),
        ("271", "webm [1440p] (DASH Video)"),
        ("272", "webm [2160p] (DASH Video)"),
        ("82", "mp4 [360p] (3D)"),
        ("83", "mp4 [480p] (3D)"),
        ("84", "mp4 [720p] (3D)"),
        ("85", "mp4 [1080p] (3D)"),
        ("100", "webm [360p] (3D)"),
        ("101", "webm [480p] (3D)"),
        ("102", "webm [720p] (3D)"),
        ("139", "m4a 48k (DASH Audio)"),
        ("140", "m4a 128k (DASH Audio)"),
        ("141", "m4a 256k (DASH Audio)"),
        ("171", "webm 48k (DASH Audio)"),
        ("172", "webm 256k (DASH Audio)")
    ])


    AUDIO_FORMATS = tdict([
        ("mp3", "mp3"),
        ("wav", "wav"),
        ("aac", "aac"),
        ("m4a", "m4a"),
        ("vorbis", "vorbis"),
        ("opus", "opus")
    ])


    FORMATS = DEFAULT_FORMATS.copy()
    FORMATS.update(VIDEO_FORMATS)
    FORMATS.update(AUDIO_FORMATS)
