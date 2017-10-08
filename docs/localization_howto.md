## ADD SUPPORT FOR NEW LANGUAGE

### Requirements
- [GNU gettext](https://www.gnu.org/software/gettext) (To build the .MO files)

### Notes
- Do **NOT** send me the PO files via email since i'm not looking at them anymore
- See the **Help** & **Helpful links** sections below for help
- The instructions below assume basic knowledge of the command line (OS independent)
- Binary translation files (.MO) built during step 7 are only for the translator to test his work (in step 8) and you should **NOT** force push them
- Make sure to update the following headers in the **PO** file:
  - **PO-Revision-Date** - update the revision date
  - **Last-Translator** - provide valid contact information

---

### Getting started
1. Fork the project
2. Create a local clone of your fork repo
3. Change directory into **youtube-dl-gui**
4. Run the **new-locale.py** script under the **devscripts** directory: 
`python new-locale.py language_code_here`
5. Edit the created **PO** file with your favorite editor
6. Add the new language in the **optionsframe.py** file
7. Build the binary translation files (.MO) using the **setup.py** script:
`python setup.py build_trans`
8. Test the translations by running youtube-dl-gui:
`python -m youtube_dl_gui`
9. Push your changes:
```
git add -A
git commit -m "Your commit message here"
git push origin master
```
10. Open a new pull request

---

### Help
- The **language code** being used should be in the format `<ISO 639-1>_<ISO 3166-1 alpha-2>` (e.g. en_US)

- To translate the PO file just edit the **msgstr** fields as shown below:

 ``` pot
 msgid "Download"
 msgstr "ダウンロード"
 ```

- In order for youtube-dl-gui to display the new language you must add it to the **optionsframe.py** file:

 1. Open **optionsframe.py** with your favorite editor
 2. Locate the **LOCALE_NAMES** attribute
 3. Add your language to it (make sure to **sort alphabetically** based on the language name)

  ``` python
  LOCALE_NAMES = twodict([
    ('en_US', 'English'),
  + ('ja_JP', 'Japanese')
  ])
  ```

---

### Helpful links

- [Creating a pull request](https://help.github.com/articles/creating-a-pull-request)
- [Fork A Repo](https://help.github.com/articles/fork-a-repo)
- [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
- [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
- [PO file headers](https://www.gnu.org/software/gettext/manual/html_node/Header-Entry.html)
