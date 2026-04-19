import sys
import os
import time
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QHBoxLayout, QLineEdit, QComboBox,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QAbstractItemView,
    QRadioButton, QButtonGroup, QLineEdit, QCheckBox, 
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
    OLD_FILE_DAYS = 180
    BIG_FILE_BYTES = 50 * 1024 * 1024

    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 600, 700)

        self.selected_folder = ""

        layout = QVBoxLayout()

        self.label = QLabel("Choose a starting folder.")
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

        # Go through the folder and add all the files to the file list.
        for file_name in os.listdir(folder):
            full_path = os.path.join(folder, file_name)

            if os.path.isfile(full_path):
                self.file_list.addItem(full_path)
            elif(os.path.isdir(full_path)):
                # Add all the folders to rec_dir.
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
