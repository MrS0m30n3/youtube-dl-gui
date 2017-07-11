# youtube-dlG
A cross platform front-end GUI for the popular [youtube-dl](https://rg3.github.io/youtube-dl/) media downloader written in wxPython. [Supported sites](https://rg3.github.io/youtube-dl/supportedsites.html)

## Screenshots
![youtube-dl-gui main window](https://raw.githubusercontent.com/MrS0m30n3/youtube-dl-gui/gh-pages/images/ydlg_ui.gif)

## Requirements
* [Python 2.7.3+](https://www.python.org/downloads)
* [wxPython 3](https://wxpython.org/download.php)
* [TwoDict](https://pypi.python.org/pypi/twodict)
* [GNU gettext](https://www.gnu.org/software/gettext/) (to build the package)
* [FFmpeg](https://ffmpeg.org/download.html) (optional, to post process video files)

## Downloads
* [Source (.zip)](https://github.com/MrS0m30n3/youtube-dl-gui/archive/0.4.zip)
* [Source (.tar.gz)](https://github.com/MrS0m30n3/youtube-dl-gui/archive/0.4.tar.gz)
* [PyPi](https://pypi.python.org/pypi/youtube-dlg/0.4)
* [Ubuntu PPA](http://ppa.launchpad.net/nilarimogard/webupd8/ubuntu/pool/main/y/youtube-dlg/)
* [Arch AUR](https://aur.archlinux.org/packages/youtube-dl-gui-git/)
* [Slackware SlackBuild](https://slackbuilds.org/repository/14.2/network/youtube-dl-gui/)
* [openSUSE](https://software.opensuse.org/package/youtube-dl-gui)
* [Windows Installer](https://github.com/MrS0m30n3/youtube-dl-gui/releases/download/0.4/youtube-dl-gui-0.4-win-setup.zip)
* [Windows Portable](https://github.com/MrS0m30n3/youtube-dl-gui/releases/download/0.4/youtube-dl-gui-0.4-win-portable.zip)

## Installation

### Install From Source
1. Download & extract the source
2. Change directory into *youtube-dl-gui-0.4*
3. Run `python setup.py install`

### Install from PyPi
1. Run `pip install youtube-dlg`

### Windows Installer
1. Download & extract the Windows installer
2. Run the `setup.exe` file

### Building the Debian package

1. Download & extract the source
2. Open a shell in the source directory
3. Run `cd .. && tar -cJvf youtube-dl-gui_0.4.0.orig.tar.xz youtube-dl-gui && cd youtube-dl-gui && dpkg-buildpackage -rfakeroot`
4. The debian package will be available in the parent directory, install it using `gdebi` or `dpkg -i`

## Contributing
* **Add support for new language:** See [localization howto](docs/localization_howto.md)
* **Report a bug:** See [issues](https://github.com/MrS0m30n3/youtube-dl-gui/issues)

## Authors
See [AUTHORS](AUTHORS) file

## License
The [Public Domain License](LICENSE)

## Frequently Asked Questions
See [FAQs](docs/faqs.md) file

## Thanks
Thanks to everyone who contributed to this project and to [@philipzae](https://github.com/philipzae) for designing the new UI layout.
