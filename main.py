import sys
import os
import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QAbstractItemView,
    QLineEdit, QFrame, QListWidgetItem
)


class FileCleanerApp(QWidget):
    OLD_FILE_DAYS = 180
    BIG_FILE_BYTES = 50 * 1024 * 1024

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 600, 400)

        self.selected_folder = ""
        self.all_files = []

        layout = QVBoxLayout()

        self.label = QLabel("Choose a folder to scan for old school files.")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

        button_row = QHBoxLayout()

        self.or_button = QPushButton("Include any keywords")
        self.or_button.setCheckable(True)
        self.or_button.clicked.connect(self.toggle_or)

        self.and_button = QPushButton("Include all keywords")
        self.and_button.setCheckable(True)
        self.and_button.clicked.connect(self.toggle_and)

        self.include_keywords = set()
        self.exclude_keywords = set()

        button_row.addWidget(self.or_button)
        button_row.addWidget(self.and_button)

        layout.addLayout(button_row)

        
        self.keyword_container = QWidget()
        self.keyword_layout = QHBoxLayout()
        self.keyword_container.setLayout(self.keyword_layout)


        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Search by keyword in file names")
        self.keyword_input.returnPressed.connect(self.add_keyword_include)
        self.keyword_layout.addWidget(self.keyword_input)
        layout.addWidget(self.keyword_container)

        self.exclude_container = QWidget()
        self.exclude_layout = QHBoxLayout()
        self.exclude_container.setLayout(self.exclude_layout)

        self.exclude_button = QPushButton("Excluded keywords")
        self.exclude_button.clicked.connect(self.exclude_init)
        self.exclude_layout.addWidget(self.exclude_button)

        layout.addWidget(self.exclude_container)


        # self.scan_button = QPushButton("Scan Files")
        # self.scan_button.clicked.connect(self.scan_files)
        # layout.addWidget(self.scan_button)
        self.file_list_label = QLabel("Files")
        layout.addWidget(self.file_list_label)
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.MultiSelection) #allows us to select multiple files
        layout.addWidget(self.file_list)

        # Set up for the directory list
        self.dir_list_label = QLabel("Directories")
        layout.addWidget(self.dir_list_label)
        self.dir_list = QListWidget()
        self.dir_list.setSelectionMode(QAbstractItemView.MultiSelection) #allows us to select multiple files
        # layout.addWidget(self.dir_list)

        self.select_all_button = QPushButton("Select All Files")
        self.select_all_button.clicked.connect(self.file_list.selectAll)
        layout.addWidget(self.select_all_button)
        

        self.delete_button = QPushButton("Delete Selected Files")
        self.delete_button.clicked.connect(self.delete_files)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder To Scan")
        if folder:
            # if there is pre-selected items remove them
            if(self.file_list):
                self.file_list.clear()
            self.selected_folder = folder
            self.label.setText(f"Selected Folder: {folder}")
            #scan the files directly after selecting a folder
            self.scan_files() 


    def scan_files(self):
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.all_files.clear()
        self.dir_list.clear()

        self.scan_files_recursive(self.selected_folder)
        self.filter_files()

    def scan_files_recursive(self, folder):
        rec_dir = []

        # Go through the folder and add all the files to the file list.
        for file_name in os.listdir(folder):
            full_path = os.path.join(folder, file_name)

            if os.path.isfile(full_path):
                self.all_files.append(self.build_file_object(full_path))
            elif(os.path.isdir(full_path)):
                # Add all the folders to rec_dir.
                rec_dir.append(full_path)
        
        
        #If rec_dir empty return
        if(len(rec_dir) == 0):
            return

        #Then in a foreach loop call this on all the folders in rec_dir
        for recFolder in rec_dir:
            self.scan_files_recursive(recFolder)

    def build_file_object(self, path):
        stats = os.stat(path)
        file_obj = {
            "name": os.path.basename(path),
            "path": path,
            "size": stats.st_size,
            "last_modified": stats.st_mtime,
            "last_accessed": stats.st_atime,
            "extension": os.path.splitext(path)[1].lower(),
            "flags": {
                "is_old": False,
                "is_forgotten": False,
                "is_big": False
            },
            "reasons": []
        }
        self.apply_heuristics(file_obj)
        return file_obj

    def apply_heuristics(self, file_obj):
        current_time = time.time()
        old_file_seconds = self.OLD_FILE_DAYS * 24 * 60 * 60

        if current_time - file_obj["last_modified"] > old_file_seconds:
            file_obj["flags"]["is_old"] = True
            file_obj["reasons"].append(
                f"Last modified over {self.OLD_FILE_DAYS} days ago"
            )

        if current_time - file_obj["last_accessed"] > old_file_seconds:
            file_obj["flags"]["is_forgotten"] = True
            file_obj["reasons"].append(
                f"Last accessed over {self.OLD_FILE_DAYS} days ago"
            )

        if file_obj["size"] > self.BIG_FILE_BYTES:
            file_obj["flags"]["is_big"] = True
            file_obj["reasons"].append("File larger than 50 MB")

    def is_flagged(self, file_obj):
        return any(file_obj["flags"].values())

    def format_file_display(self, file_obj):
        tags = []

        if file_obj["flags"]["is_old"]:
            tags.append("[OLD]")
        if file_obj["flags"]["is_forgotten"]:
            tags.append("[FORGOTTEN]")
        if file_obj["flags"]["is_big"]:
            tags.append("[BIG]")

        if tags:
            return f'{file_obj["name"]} {" ".join(tags)}'
        return file_obj["name"]

    def refresh_file_list(self, files_to_show):
        self.file_list.clear()
        for file_obj in files_to_show:
            item = QListWidgetItem(self.format_file_display(file_obj))
            item.setData(Qt.UserRole, file_obj["path"])
            item.setToolTip("\n".join(file_obj["reasons"]) or file_obj["path"])
            self.file_list.addItem(item)

    def filter_files(self):
        filtered_files = [
            file_obj for file_obj in self.all_files
            if self.is_flagged(file_obj)
        ]

        if len(self.include_keywords) == 1:
            keyword = next(iter(self.include_keywords))
            filtered_files = [
                file_obj for file_obj in filtered_files
                if keyword in file_obj["name"].lower()
            ]
        elif len(self.include_keywords) > 1:
            if self.or_button.isChecked():
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if any(
                        keyword in file_obj["name"].lower()
                        for keyword in self.include_keywords
                    )
                ]
            elif self.and_button.isChecked():
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if all(
                        keyword in file_obj["name"].lower()
                        for keyword in self.include_keywords
                    )
                ]

        if self.exclude_keywords:
            filtered_files = [
                file_obj for file_obj in filtered_files
                if not any(
                    keyword in file_obj["name"].lower()
                    for keyword in self.exclude_keywords
                )
            ]

        
        self.refresh_file_list(filtered_files)


    def delete_files(self):
        selected_items = self.file_list.selectedItems()

        if not selected_items:
            QMessageBox.information(self, "Info", "No files selected.")
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Delete {len(selected_items)} selected file(s)?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for item in selected_items:
                file_path = item.data(Qt.UserRole)
                self.all_files = [
                    file_obj for file_obj in self.all_files
                    if file_obj["path"] != file_path
                ]
                self.file_list.takeItem(self.file_list.row(item))

            QMessageBox.information(self, "Done", "Selected files removed from the list.")

    def toggle_or(self):
        if self.or_button.isChecked():
            self.and_button.setEnabled(False)
        else:
            self.and_button.setEnabled(True)

        self.filter_files()
    
    def toggle_and(self):
        if self.and_button.isChecked():
            self.or_button.setEnabled(False)
        else:
            self.or_button.setEnabled(True)

        self.filter_files()

    def add_keyword_include(self):
        keyword = self.keyword_input.text().strip().lower()

        if not keyword:
            return

        if keyword in self.include_keywords:
            self.keyword_input.clear()
            return
        
        if len(self.include_keywords) >=1:
            if not self.or_button.isChecked() and not self.and_button.isChecked():
                QMessageBox.information(
                    self,
                    "Choose Search Mode",
                    "Select either 'Include any keywords' or 'Include all keywords' before adding any more keywords"
                )
                return
        

        self.include_keywords.add(keyword)
        self.create_keyword_chip(keyword)
        self.keyword_input.clear()
        self.filter_files()

    def create_keyword_chip(self, keyword):
        chip = QFrame()
        chip_layout = QHBoxLayout(chip)
        chip_layout.setContentsMargins(10,4,10,4)

        label = QLabel(keyword)
        remove_button = QPushButton("X")
        remove_button.clicked.connect(lambda: self.remove_keyword(keyword, chip))

        chip_layout.addWidget(label)
        chip_layout.addWidget(remove_button)

        chip.setStyleSheet("""
            QFrame {
                border: 1px solid #999999;
                border-radius: 12px;
                background-color: #e8f0fe;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-weight: bold;
            }
        """)

        input_index = self.keyword_layout.indexOf(self.keyword_input)
        self.keyword_layout.insertWidget(input_index, chip)
    
    def remove_keyword(self, keyword, chip):
        if keyword in self.include_keywords:
            self.include_keywords.remove(keyword)

        self.keyword_layout.removeWidget(chip)
        chip.deleteLater()
        self.filter_files()

    def exclude_init(self):
        self.exclude_layout.removeWidget(self.exclude_button)
        self.exclude_button.deleteLater()

        self.exclude_input = QLineEdit()
        self.exclude_input.setPlaceholderText("Add keywords to exclude from file names")
        self.exclude_input.returnPressed.connect(self.add_exclude_keyword)
        self.exclude_layout.addWidget(self.exclude_input)
    
    def add_exclude_keyword(self):
        keyword = self.exclude_input.text().strip().lower()

        if not keyword:
            return

        if keyword in self.exclude_keywords:
            self.exclude_input.clear()
            return
        

        self.exclude_keywords.add(keyword)
        self.create_exclude_chip(keyword)
        self.exclude_input.clear()
        self.filter_files()

    def create_exclude_chip(self, keyword):
        chip = QFrame()
        chip_exclude_layout = QHBoxLayout(chip)
        chip_exclude_layout.setContentsMargins(10,4,10,4)

        label = QLabel(keyword)
        remove_button = QPushButton("X")
        remove_button.clicked.connect(lambda: self.remove_exclude_keyword(keyword, chip))

        chip_exclude_layout.addWidget(label)
        chip_exclude_layout.addWidget(remove_button)

        chip.setStyleSheet("""
            QFrame {
                border: 1px solid #999999;
                border-radius: 12px;
                background-color: #e8f0fe;
            }
            QPushButton {
                border: none;
                background: transparent;
                font-weight: bold;
            }
        """)

        input_index = self.exclude_layout.indexOf(self.exclude_input)
        self.exclude_layout.insertWidget(input_index, chip)

    def remove_exclude_keyword(self, keyword, chip):
        if keyword in self.exclude_keywords:
            self.exclude_keywords.remove(keyword)

        self.exclude_layout.removeWidget(chip)
        chip.deleteLater()
        self.filter_files()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCleanerApp()
    window.show()
    sys.exit(app.exec())
