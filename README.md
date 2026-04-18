# Otterdelete
A school garbage collector, oughta (otter) delete your old files!

## Overview
Otterdelete is a file management application built with PySide6 that helps users clean up old files from their folders. It allows users to scan directories recursively and filter files based on how long ago they were last modified, making it easy to identify and remove old files.

## Features
- **Recursive folder scanning** - Scans selected folders and all subdirectories
- **Time-based filtering** - Filter files by modification date (0, 1, 3, 6, or 12 months old)
- **Multi-file selection** - Select multiple files at once for batch operations
- **Confirmation dialog** - Confirms deletion before removing files
- **User-friendly GUI** - Built with Qt for an intuitive interface

## Application Components

### UI Elements
- **Folder Selection Button** (`Select Folder`) - Opens a file dialog to choose which folder to scan
- **Time Period Selector** (`Files modified past`) - Dropdown menu to choose the age threshold for files (0, 1, 3, 6, or 12 months)
- **File List** - Displays all files found in the scanned folder that match the time criteria
- **Select All Files Button** - Quickly select all files in the list with one click
- **Delete Selected Files Button** - Removes selected files after confirmation

### Core Classes & Methods

#### `FileCleanerApp(QWidget)`
Main application class that manages the UI and file operations.

**Key Attributes:**
- `selected_folder` - Path of the currently selected folder
- `selected_modified_past` - Currently selected time period in months

**Key Methods:**
- `select_folder()` - Handles folder selection and initiates scanning
- `scan_files()` - Prepares to scan the selected folder
- `scan_files_recursive(folder)` - Recursively traverses directories and identifies old files
- `on_time_period_changed()` - Updates the selected time period when user changes the dropdown
- `delete_files()` - Removes selected files with a confirmation dialog

### How It Works

1. **Select a Folder** - Click "Select Folder" to choose a directory to scan
2. **Choose Time Period** - Select how old files should be (0, 1, 3, 6, or 12 months)
3. **Scan** - The app automatically scans the folder and all subfolders
4. **Review Files** - Files matching the criteria are displayed in the list
5. **Select & Delete** - Choose files to delete and confirm removal

## Installation & Usage

### Requirements
- Python 3.x
- PySide6

### Running the Application
```bash
python main.py
```

The GUI will launch and you can begin selecting folders and cleaning up old files.
