# youtube-dlG
A cross platform front-end GUI of the popular [youtube-dl](https://rg3.github.io/youtube-dl/) media downloader written in wxPython. [Supported sites](https://rg3.github.io/youtube-dl/supportedsites.html)

## Screenshots
![youtube-dl-gui main window](https://raw.githubusercontent.com/MrS0m30n3/youtube-dl-gui/gh-pages/images/ydlg_ui.gif)

## Requirements
* [Python 3](https://www.python.org/downloads)
* [wxPython Phoenix 4](https://wxpython.org/download.php)
* [TwoDict](https://pypi.python.org/pypi/twodict)
* [FFmpeg](https://ffmpeg.org/download.html) (optional, to postprocess video files)

### Requirement for build Binaries/Executables
* [PyInstaller](https://www.pyinstaller.org/)

### Optionals
* [GNU gettext](https://www.gnu.org/software/gettext/)

## Downloads
* [Source (.zip)](https://github.com/oleksis/youtube-dl-gui/archive/1.0.0.zip)
* [Source (.tar.gz)](https://github.com/oleksis/youtube-dl-gui/archive/1.0.0.tar.gz)

## Installation

### Install From Source
1. Download & extract the source
2. Change directory into *youtube-dl-gui-1.0*
3. Run `python setup.py build_trans`
4. Run `python setup.py install`

## Binaries
Create binaries using [PyInstaller](https://www.pyinstaller.org/)
1. Run `python setup.py pyinstaller`

## Contributing
* **Add support for new language:** See [localization howto](docs/localization_howto.md)
* **Report a bug:** See [issues](https://github.com/oleksis/youtube-dl-gui/issues)

## Authors
See [AUTHORS](AUTHORS) file

## License
The [Public Domain License](LICENSE)

## Frequently Asked Questions
See [FAQs](docs/faqs.md) file

## Thanks
Thanks to everyone who contributed to this project and to [@philipzae](https://github.com/philipzae) for designing the new UI layout.
