# Localization Guide - [Transifex](https://www.transifex.com/youtube-dl-gui/public/)

## &#x1F534; DISCLAIMER
**By sending a translation you agree to publish your work under the [UNLICENSE](https://unlicense.org/) license!**

## Contents
  * [Translators](localization_howto.md#translators)
  * [Testers](localization_howto.md#testers)
  * [Devs](localization_howto.md#devs)
  * [FAQs](localization_howto.md#faqs)

## Translators

### Requirements
  * A modern browser
  * A Transifex account, [sign-up](https://www.transifex.com/signup/)

### Notes
  * If your language is currently not supported you can make a request for new language support.
  * When you request support for a new language, the language code should be in the format **en_US** and NOT just **en**.
  * Variables such as **{0}**, **{1}**, **{dir}**, **{0:.1f}**, etc should be copied exactly as they appear in the translation box.
  * Variables represent a word that will be replaced by real data (name, number, etc).
  * Variables can be moved around the string in order to make the most logical translation.
  * When new strings for translation are available you will get inbox notifications.
  * For help you can leave a comment with @username or send a direct message to one of the maintainers.
  * Maintainer usernames are: `MrS0m30n3`, `nodiscc`

### Gettings Started
  1. [Sign-in](https://www.transifex.com/signin/) to Transifex
  2. [Join a translation team](https://docs.transifex.com/getting-started/translators#joining-a-translation-team)
  3. [Start translating using the web editor](https://docs.transifex.com/translation/translating-with-the-web-editor)

### Help
  * [Translators getting started](https://docs.transifex.com/getting-started/translators)
  * [Translating offline](https://docs.transifex.com/translation/offline)
  * [Using the glossary](https://docs.transifex.com/translation/using-the-glossary)
  * For help you can [leave a comment or open an issue](https://docs.transifex.com/translation/tools-in-the-editor#comments-and-issues)

## Testers

### Requirements
  * Check [project requirements](../README.md#requirements)
  * [Git](https://git-scm.com/downloads)
  * [Transifex CLI client](https://docs.transifex.com/client/installing-the-client)
  * Some kind of text editor to edit some code (notepad++, nano, etc are sufficient)
  * A Transifex account, [sign-up](https://www.transifex.com/signup/)

### Notes
  * The instructions below assume basic knowledge of the command line (OS independent).
  * The **language code** being used should be in the format `<ISO 639-1>_<ISO 3166-1 alpha-2>` (e.g. en_US).
  * You can locally edit the translation file (PO) by opening it using a simple editor and editing the **msgstr** fields.
  * You can find the translation file (PO) after downloading it under the
    `youtube_dl_gui/locale/<LANG_CODE>/LC_MESSAGES/` directory.
  * In order to get the translations from Transifex **your account needs permissions to access the project**.

### Getting Started
  1. Open a terminal
  2. Test that Git works: `git --version`
  3. Test that Transifex CLI client works: `tx --version`
  4. Clone upstream using Git: `git clone https://github.com/MrS0m30n3/youtube-dl-gui`
  5. Change to project directory: `cd youtube-dl-gui`
  6. Pull the translation you want to test from Transifex (**Auth needed**): `tx pull --force -l <LANGUAGE_CODE_HERE>`
  7. Make the language appear under **Options>General** tab (only for new languages):
      1. Open the **optionsframe.py** under the **youtube_dl_gui** directory
      2. Search for the **LOCALE_NAMES** attribute
      3. Add the new language to it (in our example `('el_GR', 'Greek'),`)
      4. Don't forget to save your changes

  ```python
  LOCALE_NAMES = twodict([
    + ('el_GR', 'Greek'),   # language_code, language_name
      ('ar_SA', 'Arabic'),
      ('cs_CZ', 'Czech'),
        ...
  ```
  8. Build the binary translation files (MO): `python setup.py build_trans`
  9. Test the translations by running youtube-dl-gui and selecting your language: `python -m youtube_dl_gui`
  10. Make changes locally in your translation file (PO) and go back to step 8 to test them

### Help
  * [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
  * [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
  * [Command line basics Linux](https://lifehacker.com/5633909/who-needs-a-mouse-learn-to-use-the-command-line-for-almost-anything)

## Devs

### Requirements
  * See [Testers](localization_howto.md#testers) requirements

### Notes
  * Read [Testers](localization_howto.md#testers) notes first.
  * Binary translation files (MO) are ignored and you should not push them upstream.
  * Don't forget to update the [ChangeLog](../ChangeLog) after adding a new language.
  * You can gather all extra requirements below using **pip**.

### Getting Started

#### Add a new language under Options>General tab
  1. Open the **optionsframe.py** file
  2. Search for the **LOCALE_NAMES** attribute
  3. Add the new language to it and make sure to **sort alphabetically** based on the language name

  ```python
  LOCALE_NAMES = twodict([
    ('en_US', 'English'),
    ('fr_FR', 'French'),
  + ('el_GR', 'Greek'),
    ('it_IT', 'Italian'),
        ...
  ```

#### Build the binary translation files (MO)
  1. Just run the setup script: `python setup.py build_trans`

#### Automatically check translations using Google translate (Requires: polib & doodle_translate)
  1. Change directory to `devscripts`
  2. Run the check script: `python check-translation.py <LANGUAGE_CODE_HERE>`

#### Get translations from Transifex (Requires: Permissions to access project)
  * Pull everything: `tx pull -a`
  * Pull reviewed: `tx pull --mode reviewed -a`
  * Pull everything (force): `tx pull -a -f`
  * Pull specific language: `tx pull -l <LANGUAGE_CODE_HERE>`
  * Pull only completed translations (100%): `tx pull -a --minimum-perc=100`

#### Update source strings (Only Maintainers, Requires: python-gettext)
  1. Change directory to `devscripts`
  2. Run the `update-locales.sh` script (also builds MO files)
  3. Push changes to Transifex: `tx push --source --translations`

#### Add support for new language locally (DEPRECATED, ONLY TESTING)
  1. Change directory to `devscripts`
  2. Run the new locale script: `python new-locale.py <LANGUAGE_CODE_HERE>`

### Help
  * [ISO 639-1](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes)
  * [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2)
  * [PO file headers](https://www.gnu.org/software/gettext/manual/html_node/Header-Entry.html)
  * [GNU gettext manual](https://www.gnu.org/software/gettext/manual/html_node/index.html#SEC_Contents)
  * Transifex [user roles](https://docs.transifex.com/teams/understanding-user-roles)
  * Transifex [CLI client introduction](https://docs.transifex.com/client/introduction)

## FAQs

* **Translations unnecessarily having country codes?**:
Some languages have dialects in different countries. For example, `de_AT` is used for Austria, and `pt_BR` for Brazil. The country code serves to distinguish the dialects. Also, using a single format (*ll_CC*) instead of multiple for the locale name simplifies some implementation specific things.
