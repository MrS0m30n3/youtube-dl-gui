# youtube-dlG
A cross platform front-end GUI of the popular [youtube-dl](https://rg3.github.io/youtube-dl/) media downloader written in wxPython. [Supported sites](https://rg3.github.io/youtube-dl/supportedsites.html)

## Screenshots
![youtube-dl-gui main window](https://raw.githubusercontent.com/MrS0m30n3/youtube-dl-gui/gh-pages/images/ydlg_ui.gif)

## Requirements
* [Python 3](https://www.python.org/downloads)
* [wxPython 4 Phoenix](https://wxpython.org/download.php)
* [TwoDict](https://pypi.org/project/twodict)
* [PyPubSub](https://pypi.org/project/PyPubSub)
* [polib](https://pypi.org/project/polib)
* [FFmpeg](https://ffmpeg.org/download.html) (optional, to postprocess video files)

### Requirement for build Binaries/Executables
* [PyInstaller](https://www.pyinstaller.org/)

### Optionals
* [GNU gettext](https://www.gnu.org/software/gettext/)

## Downloads
* [Source (.zip)](https://github.com/oleksis/youtube-dl-gui/archive/v1.1.0-alpha.zip)
* [Source (.tar.gz)](https://github.com/oleksis/youtube-dl-gui/archive/v1.1.0-alpha.tar.gz)

## Installation

### Install From Source
* Download & extract the source
* Change directory into *youtube-dl-gui-1.1.0-alpha*
* Create virtual environment 
```
python3 -m venv env
```
* Activate virtual environment
```
source env/bin/activate
```
* Install requirements, build translations and install
```
pip install -r requirements.txt
python setup.py build_trans
python setup.py install
```

## Binaries
Create binaries using [PyInstaller](https://www.pyinstaller.org/)
* Create virtual environment
```
python3 -m venv env
```
* Activate virtual environment
```
source env/bin/activate
```
* Install requirements, build translations and create binaries
```
pip install -r requirements.txt
python setup.py build_trans
python setup.py pyinstaller
```

## Run Youtube-DLG
* Activate virtual environment and run
```
source env/bin/activate
youtube-dl-gui
```

## Notes
An alternative to install wxPython 4 **Phoenix** from the Extras section

For Ubuntu 20.04

```
wget https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
pip3 install wxPython-4.1.0-cp38-cp38-linux_x86_64.whl 
```

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
