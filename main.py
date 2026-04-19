import sys
import os
import time
from datetime import datetime
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QProgressDialog,
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QListWidget, QFileDialog, QMessageBox, QAbstractItemView,
    QRadioButton, QButtonGroup, QLineEdit, QCheckBox, QProgressDialog, 
    QRadioButton, QButtonGroup, QCheckBox, QListWidgetItem, QFrame, QSplitter,
    QDialog, QDialogButtonBox, QFormLayout
)
from PySide6.QtGui import QIntValidator
from PySide6.QtCore import Qt

SEARCH_PARAMS = {
    "CHECK_AGE": False,
    "CHECK_SIZE": False,
}


file_size = {"kb": 1024, "mb": 1024 * 1024, "gb": 1024 * 1024 * 1024}
file_size_a = ["kb", "mb", "gb"]

class FileCleanerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OtterDelete")
        self.setGeometry(100, 100, 1100, 725)
        self.setMinimumSize(900, 720)

        self.selected_folder = ""
        self.all_files = []
        self.selected_time_value = 1
        self.selected_time_unit = "month"
        self.max_size = 0
        self.current_displayed_files = []
        self.confidence_filter = "ALL"

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(5, 5, 5, 5)
        root_layout.setSpacing(10)

        self.setStyleSheet("""
            QWidget {
                background-color: #EEF2F6;
                color: #1F2933;
                font-size: 13px;
            }
            QWidget#sidebar {
                background-color: #F0F2F5;
                border: 1px solid #D8E1EB;
                border-radius: 16px;
            }
            QWidget#resultsCanvas {
                background-color: #FFFFFF;
                border: 1px solid #D8E1EB;
                border-radius: 16px;
            }
            QFrame#card {
                background-color: #FFFFFF;
                border: 1px solid #D8E1EB;
                border-radius: 16px;
            }
            QLabel#pageTitle {
                font-size: 28px;
                font-weight: 700;
                color: #102A43;
            }
            QLabel#pageSubtitle {
                color: #52606D;
                font-size: 14px;
            }
            QLabel#sidebarHeader {
                color: #52606D;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#sectionTitle {
                font-size: 16px;
                font-weight: 700;
                color: #102A43;
            }
            QLabel#sectionHint {
                color: #52606D;
            }
            QLineEdit, QComboBox, QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #C9D6E2;
                border-radius: 10px;
                padding: 8px 10px;
            }
            QLineEdit[readOnly="true"] {
                background-color: #F8FAFC;
                color: #52606D;
            }
            QListWidget {
                border-radius: 14px;
                padding: 10px;
            }
            QListWidget::item {
                margin: 4px 0px;
            }
            QPushButton {
                background-color: #E7EEF7;
                border: 1px solid #C9D6E2;
                border-radius: 10px;
                padding: 5px 5px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #D9E7F5;
            }
            QPushButton#primaryButton {
                background-color: #4A90E2;
                color: white;
                border: none;
            }
            QPushButton#primaryButton:hover {
                background-color: #397DCE;
            }
            QPushButton#dangerButton {
                background-color: #E02020;
                color: white;
                border: none;
                min-width: 180px;
            }
            QPushButton#dangerButton:hover {
                background-color: #C81E1E;
            }
            QPushButton:checked {
                background-color: #D6E6FA;
                border-color: #4A90E2;
            }
            QRadioButton {
                spacing: 4px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                border: 2px solid #9FB3C8;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:checked {
                border: 2px solid #4A90E2;
                background-color: #4A90E2;
            }
            QLabel#summaryLabel {
                color: #52606D;
                font-weight: 600;
            }
            QLabel#emptyState {
                color: #7B8794;
                border: 1px dashed #C9D6E2;
                border-radius: 12px;
                padding: 26px;
                background-color: #F9FBFD;
            }
            QLabel#pillOld {
                background-color: #FEF3C7;
                color: #92400E;
                border-radius: 9px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#pillBig {
                background-color: #FEE2E2;
                color: #B91C1C;
                border-radius: 9px;
                padding: 2px 8px;
                font-size: 11px;
                font-weight: 700;
            }
            QLabel#fileName {
                color: #102A43;
                font-weight: 600;
            }
            QLabel#fileMeta {
                color: #52606D;
                font-size: 12px;
            }
            QLabel#scoreLabel {
                color: #4A90E2;
                font-size: 12px;
                font-weight: 700;
                min-width: 120px;
            }
            QPushButton#infoButton {
                min-width: 28px;
                max-width: 28px;
                min-height: 28px;
                max-height: 28px;
                border-radius: 14px;
                padding: 0px;
                font-weight: 700;
            }
            QSplitter::handle {
                background-color: #D8E1EB;
                width: 2px;
            }
        """)

        header_widget = QWidget()
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(4)
        header_widget.setLayout(header_layout)

        page_title = QLabel("OtterDelete")
        page_title.setObjectName("pageTitle")
        header_layout.addWidget(page_title)

        page_subtitle = QLabel("Review cleanup candidates with clear reasons before deleting anything.")
        page_subtitle.setObjectName("pageSubtitle")
        header_layout.addWidget(page_subtitle)
        root_layout.addWidget(header_widget)

        splitter = QSplitter(Qt.Horizontal)
        root_layout.addWidget(splitter, 1)

        sidebar_widget = QWidget()
        sidebar_widget.setObjectName("sidebar")
        sidebar_widget.setMinimumWidth(350)
        sidebar_widget.setMaximumWidth(410)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.setContentsMargins(18, 18, 18, 18)
        sidebar_layout.setSpacing(14)
        sidebar_widget.setLayout(sidebar_layout)

        self.add_sidebar_header(sidebar_layout, "TARGET FOLDER")
        self.label = QLabel("Choose a starting folder.")
        self.label.setObjectName("sectionHint")
        sidebar_layout.addWidget(self.label)

        self.folder_path_display = QLineEdit()
        self.folder_path_display.setReadOnly(True)
        self.folder_path_display.setPlaceholderText("No folder selected")
        sidebar_layout.addWidget(self.folder_path_display)

        self.select_button = QPushButton("Browse Folder")
        self.select_button.clicked.connect(self.select_folder)
        self.select_button.setObjectName("primaryButton")
        sidebar_layout.addWidget(self.select_button)

        self.add_sidebar_header(sidebar_layout, "FILTERS")

        button_row = QHBoxLayout()

        self.or_button = QPushButton("Any keywords")
        self.or_button.setCheckable(True)
        self.or_button.clicked.connect(self.toggle_or)

        self.and_button = QPushButton("All keywords")
        self.and_button.setCheckable(True)
        self.and_button.clicked.connect(self.toggle_and)

        self.include_keywords = set()
        self.exclude_keywords = set()

        button_row.addWidget(self.or_button)
        button_row.addWidget(self.and_button)

        sidebar_layout.addLayout(button_row)

        
        self.keyword_container = QWidget()
        self.keyword_layout = QHBoxLayout()
        self.keyword_layout.setContentsMargins(0, 0, 0, 0)
        self.keyword_container.setLayout(self.keyword_layout)


        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("Search by keyword in file names")
        self.keyword_input.returnPressed.connect(self.add_keyword_include)
        self.keyword_layout.addWidget(self.keyword_input)
        sidebar_layout.addWidget(self.keyword_container)

        self.exclude_container = QWidget()
        self.exclude_layout = QHBoxLayout()
        self.exclude_layout.setContentsMargins(0, 0, 0, 0)
        self.exclude_container.setLayout(self.exclude_layout)

        self.exclude_button = QPushButton("Excluded keywords")
        self.exclude_button.clicked.connect(self.exclude_init)
        self.exclude_layout.addWidget(self.exclude_button)

        sidebar_layout.addWidget(self.exclude_container)

        search_options_layout = QHBoxLayout()
        self.check_age_cb = QCheckBox("Check Age")
        self.check_age_cb.setChecked(SEARCH_PARAMS["CHECK_AGE"])
        self.check_age_cb.toggled.connect(self.on_check_age_toggled)
        
        search_options_layout.addWidget(self.check_age_cb)

        self.check_size_cb = QCheckBox("Check Size")
        self.check_size_cb.setChecked(SEARCH_PARAMS["CHECK_SIZE"])
        self.check_size_cb.toggled.connect(self.on_check_size_toggled)
        
        search_options_layout.addWidget(self.check_size_cb)

        sidebar_layout.addLayout(search_options_layout)

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

        sidebar_layout.addLayout(self.sizeSelectorLayout)

        self.time_period_label = QLabel("Files modified past:")
        sidebar_layout.addWidget(self.time_period_label)

        self.time_selector_layout = QHBoxLayout()
        self.time_selector_layout.setSpacing(6)
        self.time_value_input = QLineEdit()
        self.time_value_input.setValidator(QIntValidator(0, 9999, self))
        self.time_value_input.setText("1")
        self.time_value_input.setMaximumWidth(56)
        self.time_value_input.editingFinished.connect(self.on_time_value_changed)
        self.time_selector_layout.addWidget(QLabel("Age:"))
        self.time_selector_layout.addWidget(self.time_value_input)

        self.day_radio = QRadioButton("D")
        self.week_radio = QRadioButton("W")
        self.month_radio = QRadioButton("M")
        self.year_radio = QRadioButton("Y")
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
        sidebar_layout.addLayout(self.time_selector_layout)

        

        self.add_sidebar_header(sidebar_layout, "SCORE FILTERS")

        confidence_filter_label = QLabel("Confidence level:")
        confidence_filter_label.setObjectName("sectionHint")
        sidebar_layout.addWidget(confidence_filter_label)

        self.confidence_filter_dropdown = QComboBox()
        self.confidence_filter_dropdown.addItems([
            "All",
            "Low Confidence",
            "Medium Confidence",
            "High Confidence"
        ])
        self.confidence_filter_dropdown.currentIndexChanged.connect(
            self.on_confidence_filter_changed
        )
        sidebar_layout.addWidget(self.confidence_filter_dropdown)

        sidebar_layout.addStretch()

        self.scan_button = QPushButton("Scan Files")
        self.scan_button.clicked.connect(self.scan_files)
        self.scan_button.setObjectName("primaryButton")
        sidebar_layout.addWidget(self.scan_button)

        results_widget = QWidget()
        results_widget.setObjectName("resultsCanvas")
        results_layout = QVBoxLayout()
        results_layout.setContentsMargins(18, 18, 18, 18)
        results_layout.setSpacing(12)
        results_widget.setLayout(results_layout)

        results_header = QHBoxLayout()
        self.file_list_label = QLabel("Review Candidates")
        self.file_list_label.setObjectName("sectionTitle")
        results_header.addWidget(self.file_list_label)

        self.summary_label = QLabel("No scan results yet.")
        self.summary_label.setObjectName("summaryLabel")
        self.summary_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        results_header.addWidget(self.summary_label, 1)
        results_layout.addLayout(results_header)

        self.empty_state_label = QLabel("Click Scan Files to find cleanup candidates.")
        self.empty_state_label.setObjectName("emptyState")
        self.empty_state_label.setAlignment(Qt.AlignCenter)
        results_layout.addWidget(self.empty_state_label)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.file_list.itemSelectionChanged.connect(self.update_selection_summary)
        results_layout.addWidget(self.file_list, 1)
        self.file_list_string = []

        # Set up for the directory list
        self.dir_list_label = QLabel("Directories")
        # layout.addWidget(self.dir_list_label)

        self.dir_list = QListWidget()
        self.dir_list.setSelectionMode(QAbstractItemView.MultiSelection) #allows us to select multiple files
        # layout.addWidget(self.dir_list)

        self.select_all_button = QPushButton("Select All Files")
        self.select_all_button.clicked.connect(self.file_list.selectAll)

        self.clear_button = QPushButton("Clear Selection")
        self.clear_button.clicked.connect(self.file_list.clearSelection)
        
        action_row = QHBoxLayout()
        self.selection_summary_label = QLabel("Select files to see potential space savings.")
        self.selection_summary_label.setObjectName("summaryLabel")
        action_row.addWidget(self.selection_summary_label, 1)
        action_row.addWidget(self.select_all_button)
        action_row.addWidget(self.clear_button)

        self.delete_button = QPushButton("Delete Selected Files")
        self.delete_button.clicked.connect(self.delete_files)
        self.loading_dialog = None

    
        action_row.addWidget(self.delete_button)

        results_layout.addLayout(action_row)

        splitter.addWidget(sidebar_widget)
        splitter.addWidget(results_widget)
        splitter.setSizes([370, 710])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        self.on_check_age_toggled(SEARCH_PARAMS["CHECK_AGE"])
        self.on_check_size_toggled(SEARCH_PARAMS["CHECK_SIZE"])

        self.setLayout(root_layout)
        self.update_selection_summary()

    def show_loading(self, title, message):
        self.loading_dialog = QProgressDialog(message, "Cancel", 0, 0, self)
        self.loading_dialog.setWindowTitle(title)
        self.loading_dialog.setWindowModality(Qt.WindowModal)
        self.loading_dialog.setMinimumDuration(0)
        self.loading_dialog.setValue(0)
        self.loading_dialog.show()
        QApplication.processEvents()

    def hide_loading(self):
        if self.loading_dialog:
            self.loading_dialog.close()
            self.loading_dialog = None
            QApplication.processEvents()
        self.delete_button.setObjectName("dangerButton")
        self.delete_button.setEnabled(False)

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
        self.max_size = sizeText * mult
        self.refresh_heuristics()
        return

    def on_time_value_changed(self):
        value_text = self.time_value_input.text().strip()
        if value_text:
            self.selected_time_value = int(value_text)
        else:
            self.selected_time_value = 0
        self.refresh_heuristics()

    def on_time_unit_changed(self):
        checked_button = self.time_unit_group.checkedButton()
        if checked_button:
            self.selected_time_unit = checked_button.text().lower()
            self.refresh_heuristics()

    def on_check_age_toggled(self, checked):
        SEARCH_PARAMS["CHECK_AGE"] = checked
        # Show/hide time period selector based on CHECK_AGE state
        self.time_period_label.setVisible(checked)
        for i in range(self.time_selector_layout.count()):
            self.time_selector_layout.itemAt(i).widget().setVisible(checked)
        if(not checked):
            self.max_size = 0
        if(self.file_list):
            self.refresh_heuristics()

    def on_check_size_toggled(self, checked):
        SEARCH_PARAMS["CHECK_SIZE"] = checked
        self.is_big_label.setVisible(checked)
        for i in range(self.sizeSelectorLayout.count()):
            self.sizeSelectorLayout.itemAt(i).widget().setVisible(checked)
        if(self.file_list):
            self.refresh_heuristics()

    def on_confidence_filter_changed(self):
        text = self.confidence_filter_dropdown.currentText()

        if text == "Low Confidence":
            self.confidence_filter = "LOW"
        elif text == "Medium Confidence":
            self.confidence_filter = "MEDIUM"
        elif text == "High Confidence":
            self.confidence_filter = "HIGH"
        else:
            self.confidence_filter = "ALL"

        self.filter_files()
        
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder To Scan")
        if folder:
            # if there is pre-selected items remove them
            if(self.file_list):
                self.file_list.clear()
            self.selected_folder = folder
            self.folder_path_display.setText(folder)
            self.label.setText(f"Selected Folder: {folder}")
            #scan the files directly after selecting a folder
            self.scan_files() 

    #Deprecated to be replaced with getDuplicates
    def isDuplicate(self, file):
        return True
    
    def build_file_object(self, full_path):
        stats = os.stat(full_path)
        file_obj = {
            "name": os.path.basename(full_path),
            "path": full_path,
            "size": stats.st_size,
            "last_modified": stats.st_mtime,
            "last_accessed": stats.st_atime,
            "extension": os.path.splitext(full_path)[1].lower(),
            "flags": {
                "is_old": False,
                "is_big": False,
            },
            "reasons": [],
            "score": 0,
            "confidence_label": "Low Confidence",
        }
        self.apply_heuristics(file_obj)
        return file_obj

    def get_age_threshold_seconds(self):
        unit_to_seconds = {
            "day": 24 * 60 * 60,
            "week": 7 * 24 * 60 * 60,
            "month": 30 * 24 * 60 * 60,
            "year": 365 * 24 * 60 * 60,
        }
        return self.selected_time_value * unit_to_seconds.get(self.selected_time_unit, 30 * 24 * 60 * 60)

    def isBig(self, file_obj):
        if self.max_size < 0:
            return False
        return file_obj["size"] > self.max_size

    def isOld(self, file_obj):
        age_seconds = time.time() - file_obj["last_modified"]
        return age_seconds > self.get_age_threshold_seconds()

    def apply_heuristics(self, file_obj):
        file_obj["flags"]["is_old"] = self.isOld(file_obj)
        file_obj["flags"]["is_big"] = self.isBig(file_obj)
        file_obj["reasons"] = []

        if file_obj["flags"]["is_old"]:
            file_obj["reasons"].append("Last modified older than selected threshold")

        if file_obj["flags"]["is_big"]:
            file_obj["reasons"].append("File size exceeds selected threshold")

        self.apply_scoring(file_obj)

    def apply_scoring(self, file_obj):
        score = 0

        if file_obj["flags"]["is_old"]:
            score += 60

        if file_obj["flags"]["is_big"]:
            score += 40

        score = max(0, min(score, 100))
        file_obj["score"] = score

        if score <= 50:
            file_obj["confidence_label"] = "Low Confidence"
        elif score <= 80:
            file_obj["confidence_label"] = "Medium Confidence"
        else:
            file_obj["confidence_label"] = "Very Confident"

    def add_sidebar_header(self, layout, text):
        header = QLabel(text)
        header.setObjectName("sidebarHeader")
        layout.addWidget(header)

    def create_card(self):
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(18, 18, 18, 18)
        card_layout.setSpacing(12)
        card.setLayout(card_layout)
        return card, card_layout

    def format_size(self, size_bytes):
        if size_bytes >= file_size["gb"]:
            return f"{size_bytes / file_size['gb']:.1f} GB"
        if size_bytes >= file_size["mb"]:
            return f"{size_bytes / file_size['mb']:.1f} MB"
        if size_bytes >= file_size["kb"]:
            return f"{size_bytes / file_size['kb']:.1f} KB"
        return f"{size_bytes} B"

    def create_tag_label(self, text, object_name):
        tag_label = QLabel(text)
        tag_label.setObjectName(object_name)
        return tag_label

    def format_timestamp(self, timestamp):
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M")

    def create_result_row(self, file_obj):
        row_widget = QWidget()
        row_layout = QHBoxLayout()
        row_layout.setContentsMargins(14, 12, 14, 12)
        row_layout.setSpacing(12)
        row_widget.setLayout(row_layout)
        row_widget.setMinimumHeight(56)

        name_label = QLabel(file_obj["name"])
        name_label.setObjectName("fileName")
        row_layout.addWidget(name_label, 1)

        score_label = QLabel(
            f'{file_obj["score"]}% {file_obj["confidence_label"]}'
        )
        score_label.setObjectName("scoreLabel")
        row_layout.addWidget(score_label)

        size_label = QLabel(self.format_size(file_obj["size"]))
        size_label.setObjectName("fileMeta")
        row_layout.addWidget(size_label)

        if file_obj["flags"]["is_old"]:
            row_layout.addWidget(self.create_tag_label("OLD", "pillOld"))
        if file_obj["flags"]["is_big"]:
            row_layout.addWidget(self.create_tag_label("BIG", "pillBig"))

        info_button = QPushButton("i")
        info_button.setObjectName("infoButton")
        info_button.clicked.connect(
            lambda _, current_file=file_obj: self.show_file_details(current_file)
        )
        row_layout.addWidget(info_button)

        return row_widget

    def show_file_details(self, file_obj):
        dialog = QDialog(self)
        dialog.setWindowTitle("OtterDelete - File Details")
        dialog.setModal(True)
        dialog.resize(560, 420)

        layout = QVBoxLayout()

        title_label = QLabel("File Details")
        title_label.setObjectName("sectionTitle")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        active_flags = []
        if file_obj["flags"]["is_old"]:
            active_flags.append("OLD")
        if file_obj["flags"]["is_big"]:
            active_flags.append("BIG")

        form_layout.addRow("Name:", QLabel(file_obj["name"]))
        form_layout.addRow("Full Path:", QLabel(file_obj["path"]))
        form_layout.addRow("Size:", QLabel(self.format_size(file_obj["size"])))
        form_layout.addRow("Extension:", QLabel(file_obj["extension"] or "None"))
        form_layout.addRow("Last Modified:", QLabel(self.format_timestamp(file_obj["last_modified"])))
        form_layout.addRow("Last Accessed:", QLabel(self.format_timestamp(file_obj["last_accessed"])))
        form_layout.addRow("Score:", QLabel(f'{file_obj["score"]}%'))
        form_layout.addRow("Confidence:", QLabel(file_obj["confidence_label"]))
        form_layout.addRow(
            "Flags:",
            QLabel(", ".join(active_flags) if active_flags else "No active flags")
        )

        layout.addLayout(form_layout)

        reasons_title = QLabel("Reasons")
        reasons_title.setObjectName("sectionHint")
        layout.addWidget(reasons_title)

        reasons_text = "\n".join(f"• {reason}" for reason in file_obj["reasons"])
        reasons_label = QLabel(reasons_text or "No reasons recorded")
        reasons_label.setWordWrap(True)
        layout.addWidget(reasons_label)

        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(dialog.reject)
        button_box.accepted.connect(dialog.accept)
        layout.addWidget(button_box)

        dialog.setLayout(layout)
        dialog.exec()

    def update_results_summary(self, files_to_show):
        self.current_displayed_files = files_to_show
        file_count = len(files_to_show)
        total_size = sum(file_obj["size"] for file_obj in files_to_show)

        if file_count == 0:
            self.summary_label.setText("0 files flagged")
            self.empty_state_label.show()
        else:
            self.summary_label.setText(
                f"{file_count} file(s) flagged | {self.format_size(total_size)} potential cleanup"
            )
            self.empty_state_label.hide()

    def update_selection_summary(self):
        selected_items = self.file_list.selectedItems()

        if not selected_items:
            self.selection_summary_label.setText("Potential space savings.")
            self.delete_button.setText("Delete Selected Files")
            self.delete_button.setEnabled(False)
            return

        selected_size = sum(item.data(Qt.UserRole + 1) for item in selected_items)
        self.selection_summary_label.setText(
            f"Selecting {len(selected_items)} file(s) will free up {self.format_size(selected_size)}."
        )
        self.delete_button.setText(f"Delete {len(selected_items)} File(s)")
        self.delete_button.setEnabled(True)

    def refresh_heuristics(self):
        for file_obj in self.all_files:
            self.apply_heuristics(file_obj)
        self.filter_files()

    def format_file_display(self, file_obj):
        tags = []
        if file_obj["flags"]["is_old"]:
            tags.append("[OLD]")
        if file_obj["flags"]["is_big"]:
            tags.append("[BIG]")

        if tags:
            return f'{file_obj["name"]} {" ".join(tags)}'
        return file_obj["name"]


    def is_file_old(self, full_path):
        # --> returns true if the file has aged past selected time stamp #
        file_last_modified = os.path.getmtime(full_path)
        
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
    
    def scan_files(self):
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.file_list.clear()
        self.file_list_string.clear()
        self.dir_list.clear()

        self.show_loading("Scanning", "Scanning files. Please wait...")
        self.file_list.setUpdatesEnabled(False)
        try:
            self.scan_files_recursive(self.selected_folder)
        finally:
            self.file_list.setUpdatesEnabled(True)
            self.hide_loading()
    

    def scan_files(self):
        if not self.selected_folder:
            QMessageBox.warning(self, "Warning", "Please select a folder first.")
            return

        self.file_list.clear()
        self.dir_list.clear()
        self.all_files.clear()

        self.scan_files_recursive(self.selected_folder)
        self.filter_files()

    def scan_files_recursive(self, folder):
        for root, dirs, files in os.walk(folder):
            if self.loading_dialog and self.loading_dialog.wasCanceled():
                return

            QApplication.processEvents()

            for file_name in files:
                full_path = os.path.join(root, file_name)
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

    def is_candidate(self, file_obj):
        checks = []

        if SEARCH_PARAMS["CHECK_AGE"]:
            checks.append(file_obj["flags"]["is_old"])

        if SEARCH_PARAMS["CHECK_SIZE"]:
            checks.append(file_obj["flags"]["is_big"])

        if not checks:
            return True

        return any(checks)

    def refresh_file_list(self, files_to_show):
        self.file_list.clear()
        for file_obj in files_to_show:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, file_obj["path"])
            item.setData(Qt.UserRole + 1, file_obj["size"])
            item.setToolTip("\n".join(file_obj["reasons"]) or file_obj["path"])
            self.file_list.addItem(item)
            row_widget = self.create_result_row(file_obj)
            item.setSizeHint(row_widget.sizeHint())
            self.file_list.setItemWidget(item, row_widget)

        self.update_results_summary(files_to_show)
        self.update_selection_summary()

    def filter_files(self):
        filtered_files = [
            file_obj for file_obj in self.all_files
            if self.is_candidate(file_obj)
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
                    if any(keyword in file_obj["name"].lower() for keyword in self.include_keywords)
                ]
            elif self.and_button.isChecked():
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if all(keyword in file_obj["name"].lower() for keyword in self.include_keywords)
                ]

        if self.exclude_keywords:
            filtered_files = [
                file_obj for file_obj in filtered_files
                if not any(keyword in file_obj["name"].lower() for keyword in self.exclude_keywords)
            ]

        if self.confidence_filter != "ALL":
            if self.confidence_filter == "LOW":
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if file_obj["score"] <= 50
                ]
            elif self.confidence_filter == "MEDIUM":
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if 50 < file_obj["score"] <= 80
                ]
            elif self.confidence_filter == "HIGH":
                filtered_files = [
                    file_obj for file_obj in filtered_files
                    if file_obj["score"] > 80
                ]

        # filtered_files.sort(key=lambda file_obj: file_obj["score"], reverse=True)

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
            failed_deletes = []
            for item in selected_items:
                file_path = file_path = item.data(Qt.UserRole)
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


                file_path = item.data(Qt.UserRole)
                self.all_files = [
                    file_obj for file_obj in self.all_files
                    if file_obj["path"] != file_path
                ]
            self.filter_files()

            QMessageBox.information(self, "Done", "Selected Files Deleted")

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

