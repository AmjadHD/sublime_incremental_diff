# Incremental Diff

A plugin to quickly diff two views through Sublime text's built-in Incremental Diff.

![usage](screen_cast.gif)

## Usage

The plugin provides these commands:
- `set_reference_document` available in the context and tab context menus and the command palette: opens a quick panel with all suitable open views (excluding images and possibly binary files) to set the contents as a reference for the incremental diff.

- `set_reference_document_from_file` available in the Side Bar context menu, when exactly two files are selected, the file on which the menu is invoked will be opened if not already open, and the other file's contents will be used as a reference for incremental diff.

- `toggle_all_diffs` bonus command, available in the context menu, shows/hides all diff hunks in the view.

## Installation

Open the Command Palette and select `Package Control: Install Package` and search for `IncrementalDiff`.