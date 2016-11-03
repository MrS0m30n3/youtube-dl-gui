# -*- coding: UTF-8 -*-

from .utils import TwoWayOrderedDict as tdict


OUTPUT_FORMATS = tdict([
    (0, "ID"),
    (1, "Title"),
    (2, "Title + ID"),
    (3, "Custom")
])


DEFAULT_FORMATS = tdict([
    ("0", "default")
])


VIDEO_FORMATS = tdict([
    ("3gp", "3gp"),
    ("17", "3gp [176x144]"),
    ("36", "3gp [320x240]"),
    ("flv", "flv"),
    ("5", "flv [400x240]"),
    ("34", "flv [640x360]"),
    ("35", "flv [854x480]"),
    ("webm", "webm"),
    ("43", "webm [640x360]"),
    ("44", "webm [854x480]"),
    ("45", "webm [1280x720]"),
    ("46", "webm [1920x1080]"),
    ("mp4", "mp4"),
    ("18", "mp4 [640x360]"),
    ("22", "mp4 [1280x720]"),
    ("37", "mp4 [1920x1080]"),
    ("38", "mp4 [4096x3072]"),
    ("160", "mp4 144p (DASH)"),
    ("133", "mp4 240p (DASH)"),
    ("134", "mp4 360p (DASH)"),
    ("135", "mp4 480p (DASH)"),
    ("136", "mp4 720p (DASH)"),
    ("137", "mp4 1080p (DASH)"),
    ("264", "mp4 1440p (DASH)"),
    ("138", "mp4 2160p (DASH)"),
    ("242", "webm 240p (DASH)"),
    ("243", "webm 360p (DASH)"),
    ("244", "webm 480p (DASH)"),
    ("247", "webm 720p (DASH)"),
    ("248", "webm 1080p (DASH)"),
    ("271", "webm 1440p (DASH)"),
    ("272", "webm 2160p (DASH)"),
    ("82", "mp4 360p (3D)"),
    ("83", "mp4 480p (3D)"),
    ("84", "mp4 720p (3D)"),
    ("85", "mp4 1080p (3D)"),
    ("100", "webm 360p (3D)"),
    ("101", "webm 480p (3D)"),
    ("102", "webm 720p (3D)"),
    ("139", "m4a 48k (DASH AUDIO)"),
    ("140", "m4a 128k (DASH AUDIO)"),
    ("141", "m4a 256k (DASH AUDIO)"),
    ("171", "webm 48k (DASH AUDIO)"),
    ("172", "webm 256k (DASH AUDIO)")
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
