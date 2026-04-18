import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QMessageBox,QAbstractItemView
)


class FileCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 600, 400)

        self.selected_folder = ""

        layout = QVBoxLayout()

        self.label = QLabel("Choose a folder to scan for old school files.")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

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

        self.file_list.clear()
        self.dir_list.clear()

        self.scan_files_recursive(self.selected_folder)
        # for file_name in os.listdir(self.selected_folder):
        #     full_path = os.path.join(self.selected_folder, file_name)

        #     if os.path.isfile(full_path):
        #         self.file_list.addItem(full_path)
            # else:
            #     self.dir_list.addItem(full_path)

    def scan_files_recursive(self, folder):
        rec_dir = []

        #Go through the folder and add all the files to the file list
        for file_name in os.listdir(folder):
            full_path = os.path.join(folder, file_name)

            if os.path.isfile(full_path):
                self.file_list.addItem(full_path)
            elif(os.path.isdir(full_path)):
                #add all the folders to rec_dir
                rec_dir.append(full_path)
        
        
        #If rec_dir empty return
        if(len(rec_dir) == 0):
            return

        #Then in a foreach loop call this on all the folders in rec_dir
        for recFolder in rec_dir:
            self.scan_files_recursive(recFolder)


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
                # replace with os.remove(file_path) when actually ready to delete files
                self.file_list.takeItem(self.file_list.row(item))

            QMessageBox.information(self, "Done", "Selected files removed from the list.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCleanerApp()
    window.show()
    sys.exit(app.exec())