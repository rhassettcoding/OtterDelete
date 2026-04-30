import sys
import os
from fileObject import FileObject
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QAbstractItemView,
    QRadioButton, QButtonGroup, QLineEdit
)
from PySide6.QtGui import QIntValidator

class FileCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 600, 400)

        self.GLOBAL_FLAGS = {
            "checkAge": True,
            "checkDuplicate":True,
            "checkKeyword":True,
        }

        self.selected_folder = None


        """
            The below two folders are to organize what files are visible to the user and what isn't
            making it more efficient so we don't have to search through the entire folder each time
            to re-init ever file object over and over, these arrays are cleared when a new folder is selected
        
        """
        self.valid_files = [] #<-- to track all the visible files of the folder that folow criteria (deleted once new folder is selected)
        self.invalid_files = [] #<-- to track all invisible files of the folder that don't follow criteria but are in the selected folder

        self.selected_time_value = 1
        self.selected_time_unit = "month"

        layout = QVBoxLayout()

        self.label = QLabel("Choose a folder to scan for old school files.")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

        # Time period selector
        self.time_period_label = QLabel("Files modified past:")
        layout.addWidget(self.time_period_label)

        time_selector_layout = QHBoxLayout()
        self.time_value_input = QLineEdit()
        self.time_value_input.setValidator(QIntValidator(0, 9999, self))
        self.time_value_input.setText("1")
        self.time_value_input.setMaximumWidth(80)
        self.time_value_input.editingFinished.connect(self.on_time_value_changed)
        time_selector_layout.addWidget(QLabel("Amount:"))
        time_selector_layout.addWidget(self.time_value_input)

        self.day_radio = QRadioButton("Day")
        self.week_radio = QRadioButton("Week")
        self.month_radio = QRadioButton("Month")
        self.year_radio = QRadioButton("Year")
        self.month_radio.setChecked(True)

        self.time_unit_group = QButtonGroup(self)
        self.time_unit_group.addButton(self.day_radio)
        self.time_unit_group.addButton(self.week_radio)
        self.time_unit_group.addButton(self.month_radio)
        self.time_unit_group.addButton(self.year_radio)
        self.time_unit_group.buttonClicked.connect(self.on_time_unit_changed)

        time_selector_layout.addWidget(self.day_radio)
        time_selector_layout.addWidget(self.week_radio)
        time_selector_layout.addWidget(self.month_radio)
        time_selector_layout.addWidget(self.year_radio)
        layout.addLayout(time_selector_layout)

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

    def on_time_value_changed(self):
        value_text = self.time_value_input.text().strip()
        if value_text:
            self.selected_time_value = int(value_text)
        else:
            self.selected_time_value = 0

    def on_time_unit_changed(self):
        checked_button = self.time_unit_group.checkedButton()
        if checked_button:
            self.selected_time_unit = checked_button.text().lower()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder To Scan")
        if folder:
            # if there is pre-selected items remove them
            if(self.file_list):
                self.file_list.clear()
            self.selected_folder = folder
            self.label.setText(f"Selected Folder: {folder}")
            # --> remove the tracked files of the previous folder
            self.valid_files.clear()
            self.invalid_files.clear()
            #--> scan the folder after all items are cleared
            self.folder_scan() 

    def folder_scan(self):
        #when we select a folder we only want to initialize all the file Objects once ->
        # then we scan through the list of items that we have in the visible/invisible list

        #if a folder isn't chosen -->
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.file_list.clear()
        self.dir_list.clear()

        self.get_all_files_recursively(self.selected_folder)


    def check_file_criteria_on_init(self,FileObject): #<-- checks if the file is following the current flag criteria
        # check if file follows metrics
        # if self.GLOBAL_FLAGS['checkAge']:
            
        # if self.GLOBAL_FLAGS['checkDuplicate']:
            
        # if self.GLOBAL_FLAGS['checkKeyword']:

        return True #<-- file should be added to list

    # def get_all_files_from_folder(self, folder):
    #     if not self.selected_folder:
    #         QMessageBox.warning(self, "Warning", "Please select a folder first.")
    #         return

    #     self.file_list.clear()
    #     self.dir_list.clear()

    #     self.get_all_files(self.selected_folder)

    def get_all_files_recursively(self,folder):
        remaining_dir = []

        #Go through the folder and add all the files to the file list
        for file_name in os.listdir(folder):
            full_path = os.path.join(folder, file_name)

            if os.path.isfile(full_path):
                newFile = FileObject(full_path)
                if(self.check_file_criteria_on_init(newFile)):
                    # --> add to visible list
                    self.valid_files.append(newFile)
                    self.file_list.addItem(full_path)
                else:
                    # --> add to not visible list 
                    self.invalid_files.append(newFile)
            elif(os.path.isdir(full_path)):
                #add all the folders to remaining_dir
                remaining_dir.append(full_path)
        #If remaining_dir empty return
        if(len(remaining_dir) == 0):
            return

        #Then in a foreach loop call this on all the folders in remaining_dir
        for recFolder in remaining_dir:
            self.get_all_files_recursively(recFolder)


    # def scan_files_depricated(self):
    #     if not self.selected_folder:
    #         QMessageBox.warning(self, "Warning", "Please select a folder first.")
    #         return

    #     self.file_list.clear()
    #     self.dir_list.clear()

    #     self.scan_files_recursive(self.selected_folder)
        
    
    # def scan_files_recursive_depcrecated(self, folder): #<-- replaced with get_all_files_from_folder
    #     rec_dir = []

    #     #Go through the folder and add all the files to the file list
    #     for file_name in os.listdir(folder):
    #         full_path = os.path.join(folder, file_name)

    #         if os.path.isfile(full_path):
    #             self.file_list.addItem(full_path)
    #         elif(os.path.isdir(full_path)):
    #             #add all the folders to rec_dir
    #             rec_dir.append(full_path)
        
    #     #If rec_dir empty return
    #     if(len(rec_dir) == 0):
    #         return

    #     #Then in a foreach loop call this on all the folders in rec_dir
    #     for recFolder in rec_dir:
    #         self.scan_files_recursive(recFolder)


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