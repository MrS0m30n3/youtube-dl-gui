## ADD SUPPORT FOR NEW LANGUAGE

**Requires**: [GNU GetText](https://www.gnu.org/software/gettext/) (Only if you want to build the MO files on your own)

1. Clone or Fork the repository
2. Copy **youtube-dl-gui/youtube_dl_gui/locale/en_US/LC_MESSAGES/youtube_dl_gui.po** to **youtube-dl-gui/locale_build/**
3. Go to **youtube-dl-gui/locale_build** directory
4. Edit the PO file with your favorite text editor (See *EDIT* section)
5. After you have finished the file editing save the file
6. Now you have two options
 1. Send me the translated PO file to this email address: ytubedlg@gmail.com
 2. Build the binary translation file (MO) on your own using the build scripts (See *BUILD* section)

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
   
   Usage: *build_locale.sh* <*language code*> <*translated PO file*>
   
   $ ./build_locale.sh *gr_GR* *gr.po*
   
2. Now you also need to add the corresponding language option under the options frame localization tab
 1. Open optionsframe.py
 2. Locate the LocalizationTab class
 3. Find the LOCALE_NAMES attribute
 4. Add your language to the LOCALE_NAMES 
  
  **Example**
  ``` python
  LOCALE_NAMES = twodict([
    ('en_US', 'English'),
    ('gr_GR', 'Greek')
  ])
  ```
  
3. Save the file and now you can make a new pull request after you push your changes to your remote
