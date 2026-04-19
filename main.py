import sys
import os
import time
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QAbstractItemView,
    QRadioButton, QButtonGroup, QLineEdit, QCheckBox, QProgressDialog 
)
from PySide6.QtGui import QIntValidator

SEARCH_PARAMS = {
    "CHECK_DUPLICATES":True,
    "CHECK_AGE":True,
    "CHECK_SIZE":True,
}


from PySide6.QtGui import QIntValidator

file_size = {"kb":1024, "mb":1024000, "gb":1024000000}
file_size_a = ["kb", "mb", "gb"]
max_size = -1

class FileCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 600, 700)

        self.selected_folder = ""
        self.selected_time_value = 1
        self.selected_time_unit = "month"

        layout = QVBoxLayout()

        self.label = QLabel("Choose a starting folder.")
        layout.addWidget(self.label)

        self.select_button = QPushButton("Select Folder")
        self.select_button.clicked.connect(self.select_folder)
        layout.addWidget(self.select_button)

        self.scan_button = QPushButton("Scan Files")
        self.scan_button.clicked.connect(self.scan_files)
        layout.addWidget(self.scan_button)

        self.search_options_label = QLabel("Search Options:")
        layout.addWidget(self.search_options_label)

        search_options_layout = QHBoxLayout()
        self.check_duplicates_cb = QCheckBox("Check Duplicates")
        self.check_duplicates_cb.setChecked(SEARCH_PARAMS["CHECK_DUPLICATES"])
        self.check_duplicates_cb.toggled.connect(self.on_check_duplicates_toggled)
        search_options_layout.addWidget(self.check_duplicates_cb)

        self.check_age_cb = QCheckBox("Check Age")
        self.check_age_cb.setChecked(SEARCH_PARAMS["CHECK_AGE"])
        self.check_age_cb.toggled.connect(self.on_check_age_toggled)
        search_options_layout.addWidget(self.check_age_cb)

        self.check_size_cb = QCheckBox("Check Size")
        self.check_size_cb.setChecked(SEARCH_PARAMS["CHECK_SIZE"])
        self.check_size_cb.toggled.connect(self.on_check_size_toggled)
        search_options_layout.addWidget(self.check_size_cb)

        layout.addLayout(search_options_layout)

        self.sizeSelectorLayout = QHBoxLayout()

        self.is_big_label = QLabel("Size: ")

        #Add a textbox
        self.size_text = QLineEdit()
        self.size_text.setValidator(QIntValidator(0, 9999, self))

        #Add a drop down
        self.size_scale = QComboBox()
        for k in file_size.keys():
            self.size_scale.addItem(k)

        #Add a button to confirm
        self.size_confirm_button = QPushButton("Confirm")
        self.size_confirm_button.clicked.connect(self.changeMaxSize)

        #Add all the widgets in order
        self.sizeSelectorLayout.addWidget(self.is_big_label)
        self.sizeSelectorLayout.addWidget(self.size_text)
        self.sizeSelectorLayout.addWidget(self.size_scale)
        self.sizeSelectorLayout.addWidget(self.size_confirm_button)

        layout.addLayout(self.sizeSelectorLayout)

        # Time period selector --------------->
        self.time_period_label = QLabel("Files modified past:")
        layout.addWidget(self.time_period_label)

        self.time_selector_layout = QHBoxLayout()
        self.time_value_input = QLineEdit()
        self.time_value_input.setValidator(QIntValidator(0, 9999, self))
        self.time_value_input.setText("1")
        self.time_value_input.setMaximumWidth(80)
        self.time_value_input.editingFinished.connect(self.on_time_value_changed)
        self.time_selector_layout.addWidget(QLabel("Amount:"))
        self.time_selector_layout.addWidget(self.time_value_input)

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

        self.time_selector_layout.addWidget(self.day_radio)
        self.time_selector_layout.addWidget(self.week_radio)
        self.time_selector_layout.addWidget(self.month_radio)
        self.time_selector_layout.addWidget(self.year_radio)
        layout.addLayout(self.time_selector_layout)
        
        

        self.file_list_label = QLabel("Files")
        layout.addWidget(self.file_list_label)
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.MultiSelection) #allows us to select multiple files
        layout.addWidget(self.file_list)
        self.file_list_string = []

        # Set up for the directory list
        self.dir_list_label = QLabel("Directories")
        # layout.addWidget(self.dir_list_label)

        self.dir_list = QListWidget()
        self.dir_list.setSelectionMode(QAbstractItemView.MultiSelection) #allows us to select multiple files
        # layout.addWidget(self.dir_list)

        #This lets everything start out selected so as few clicks as possible to delete things
        self.file_list.selectAll()

        self.select_all_button = QPushButton("Select All Files")
        self.select_all_button.clicked.connect(self.file_list.selectAll)
        layout.addWidget(self.select_all_button)

        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.file_list.clearSelection)
        layout.addWidget(self.clear_button)
        

        self.delete_button = QPushButton("Delete Selected Files")
        self.delete_button.clicked.connect(self.delete_files)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

    def changeMaxSize(self):
        newSize = self.size_text.text()
        newScale = self.size_scale.currentIndex()
        format = file_size_a[newScale]
        
        mult = file_size[format]
        # print("In Max Size")
        # print(format)
        # print(file_size[format])

        sizeText = newSize.strip()
        if(sizeText):
            sizeText = int(sizeText)
        else:
            sizeText = 0
        global max_size
        max_size = sizeText*mult
        # print(max_size)
        return

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

    def on_check_duplicates_toggled(self, checked):
        SEARCH_PARAMS["CHECK_DUPLICATES"] = checked

    def on_check_age_toggled(self, checked):
        SEARCH_PARAMS["CHECK_AGE"] = checked
        # Show/hide time period selector based on CHECK_AGE state
        self.time_period_label.setVisible(checked)
        for i in range(self.time_selector_layout.count()):
            self.time_selector_layout.itemAt(i).widget().setVisible(checked)

    def on_check_size_toggled(self, checked):
        SEARCH_PARAMS["CHECK_SIZE"] = checked
        self.is_big_label.setVisible(checked)
        for i in range(self.sizeSelectorLayout.count()):
            self.sizeSelectorLayout.itemAt(i).widget().setVisible(checked)
        

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

    #Deprecated to be replaced with getDuplicates
    def isDuplicate(self, file):
        # if(self.is_duplicate_checkbox):
        #     #Check the file_list does anything have the same suffix, minus the numbers?
        #     #if there is return false
        #     for check in self.file_list_string:
        #         if(check == file):
        #             return False
        return True
    
    def isBig(self, file):
        # print(file)
        # print("Size: " + str(os.path.getsize(file)))
        # print("Max Size: " + str(max_size))
        if(os.path.getsize(file) > max_size):
            return True
        else:
            return False


    def scan_files(self):
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.file_list.clear()
        self.file_list_string.clear()
        self.dir_list.clear()

        self.scan_files_recursive(self.selected_folder)


    def is_file_old(self, full_path):
        # --> returns true if the file has aged past selected time stamp #
        file_last_modified = os.path.getmtime(full_path)
        file_created = os.path.getctime(full_path)
        
        # Check if file was modified past the selected time threshold
        current_time = time.time()
        unit_seconds = {
            "day": 24 * 60 * 60,
            "week": 7 * 24 * 60 * 60,
            "month": 30 * 24 * 60 * 60,
            "year": 365 * 24 * 60 * 60,
        }.get(self.selected_time_unit, 0)
        cutoff_time = current_time - (self.selected_time_value * unit_seconds)
        if file_last_modified < cutoff_time:
            return True
        else:
            return False
    
    def scan_files_recursive(self, folder):
        rec_dir = []

        #Go through the folder and add all the files to the file list
        try:
            entries = os.listdir(folder)
        except OSError:
            return

        for file_name in entries:
            full_path = os.path.join(folder, file_name)

            if os.path.isfile(full_path):
                big = True
                dupe = True
                old = True
                if(SEARCH_PARAMS["CHECK_SIZE"]):
                    big = self.isBig(full_path)
                if(SEARCH_PARAMS["CHECK_DUPLICATES"]):
                    dupe = self.isDuplicate(full_path)
                if(SEARCH_PARAMS["CHECK_AGE"]):
                    old = self.is_file_old(full_path)


                if(big and dupe and old):
                   self.file_list.addItem(full_path)
                   self.file_list_string.append(full_path)
                
                
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
            failed_deletes = []
            for item in selected_items:
                file_path = item.text()
                try:
                    os.remove(file_path)
                    self.file_list_string = [p for p in self.file_list_string if p != file_path]
                    self.file_list.takeItem(self.file_list.row(item))
                except OSError as error:
                    failed_deletes.append(f"{file_path}: {error}")

            if failed_deletes:
                QMessageBox.warning(
                    self,
                    "Partial Delete",
                    "Some files could not be deleted:\n\n" + "\n".join(failed_deletes),
                )
            else:
                QMessageBox.information(self, "Done", "Selected files removed from the list.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileCleanerApp()
    window.show()
    sys.exit(app.exec())
