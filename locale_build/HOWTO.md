## ADD SUPPORT FOR NEW LANGUAGE

**Requires**: [GNU GetText](https://www.gnu.org/software/gettext/) (If you want to build the MO files on your own)

###You have two options in order to add a new translation on youtube-dlg.

1. Translate the files and send them to me via email.
2. Fork youtube-dlg and push changes on your own.

####1st Way

1. Download the source code
 1. Either download & extract the source from [here](https://github.com/MrS0m30n3/youtube-dl-gui/archive/master.zip)
 2. Or run `git clone https://github.com/MrS0m30n3/youtube-dl-gui youtube-dl-gui-master`
2. Change directory into **youtube-dl-gui-master**
3. Copy **youtube_dl_gui/locale/en_US/LC_MESSAGES/youtube_dl_gui.po** -> **locale_build/**
4. Change directory into **locale_build**
5. Edit the PO file with your favorite text editor (See *EDIT* section)
6. Send me the translated PO file via email to: ytubedlg@gmail.com

####2nd Way

1. Fork youtube-dlg project (See [Fork A Repo](https://help.github.com/articles/fork-a-repo/))
2. Clone your repository `git clone https://github.com/<your-username>/youtube-dl-gui`
3. Change directory into **youtube-dl-gui**
4. Copy **youtube_dl_gui/locale/en_US/LC_MESSAGES/youtube_dl_gui.po** -> **locale_build/**
5. Change directory into **locale_build**
6. Edit the PO file with your favorite text editor (See *EDIT* section)
7. Build the binary translation file (MO) using the build scripts (See *BUILD* section)
8. Push changes: 
`git add -A; git commit -m "Your commit message here"; git push origin master`
9. Now you can open a new pull request

### EDIT
PO file headers informations:
https://www.gnu.org/software/gettext/manual/html_node/Header-Entry.html
  
To translate the PO file just edit the **msgstr** fields
  
**Example**
``` pot
#: mainframe.py:78
msgid "Download"
msgstr "Add the translation here"
```

### BUILD
1. To build the MO file you need to run the corresponding build script for your OS
   
   **Windows**: build_locale.**bat** 
   
   **Linux**: build_locale.**sh**

   **Example**
   
   Usage: `build_locale.sh <language code> <translated PO file>`
   
   `./build_locale.sh gr_GR gr.po`
   
2. Now you also need to add the corresponding language option under the options frame localization tab
 1. Open optionsframe.py
 2. Locate the LocalizationTab class
 3. Find the LOCALE_NAMES attribute
 4. Add your language to the LOCALE_NAMES 
  
  **Example**
  ``` python
  LOCALE_NAMES = twodict([
    ('en_US', 'English'),
   + ('gr_GR', 'Greek')
  ])
  ```
 
