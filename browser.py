import sys
import os
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QPushButton, QToolBar, QAction, QTabWidget, QLabel, QCheckBox, QListWidget, QListWidgetItem, QInputDialog, QComboBox, QFormLayout, QMessageBox, QFileDialog, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt, QTranslator, QLocale
from PyQt5.QtGui import QClipboard

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fast Browser')
        self.setGeometry(100, 100, 1200, 800)

        self.config_path = os.path.join(os.getenv('APPDATA'), 'dxddy', 'ent')
        os.makedirs(self.config_path, exist_ok=True)
        self.config_file = os.path.join(self.config_path, 'config.json')
        self.log_file = os.path.join(self.config_path, 'browser.log')
        self.error_log_file = os.path.join(self.config_path, 'error.log')
        self.tabs_file = os.path.join(self.config_path, 'tabs.json')
        self.history_file = os.path.join(self.config_path, 'history.json')

        logging.basicConfig(filename=self.log_file, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.error_logger = logging.getLogger('error_logger')
        error_handler = logging.FileHandler(self.error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        self.error_logger.addHandler(error_handler)

        self.translator = QTranslator()
        self.load_settings()

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.setStyleSheet("QTabBar::tab { height: 30px; width: 150px; }")
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)

        self.restore_tabs()

        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)

        self.back_button = QAction('⟵', self)
        self.back_button.triggered.connect(lambda: self.tabs.currentWidget().back())

        self.forward_button = QAction('⟶', self)
        self.forward_button.triggered.connect(lambda: self.tabs.currentWidget().forward())

        self.reload_button = QAction('⟳', self)
        self.reload_button.triggered.connect(lambda: self.tabs.currentWidget().reload())

        self.new_tab_button = QAction('✚', self)
        self.new_tab_button.triggered.connect(lambda: self.add_new_tab())

        self.translate_button = QAction('Перевести', self)
        self.translate_button.triggered.connect(self.translate_page)

        self.settings_button = QAction('⚙', self)
        self.settings_button.triggered.connect(self.show_settings)

        self.toolbar = QToolBar()
        self.toolbar.addAction(self.settings_button)
        self.toolbar.addAction(self.back_button)
        self.toolbar.addAction(self.forward_button)
        self.toolbar.addAction(self.reload_button)
        self.toolbar.addAction(self.new_tab_button)
        self.toolbar.addAction(self.translate_button)
        self.toolbar.addWidget(self.url_bar)

        self.addToolBar(self.toolbar)

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        self.apply_theme()

    def load_settings(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    config = json.load(file)
                    self.default_search_engine = config.get('default_search_engine', 'http://www.google.com')
                    self.theme = config.get('theme', 'Светлая')
                    self.download_path = config.get('download_path', os.path.expanduser('~'))
                    self.language = config.get('language', 'ru')
            else:
                self.default_search_engine = 'http://www.google.com'
                self.theme = 'Светлая'
                self.download_path = os.path.expanduser('~')
                self.language = 'ru'
            self.apply_language()
            logging.info('Settings loaded')
        except Exception as e:
            self.error_logger.error(f'Error loading settings: {e}')

    def save_settings(self):
        try:
            self.default_search_engine = self.search_engine_input.text()
            self.theme = self.theme_selector.currentText()
            self.download_path = self.download_path_input.text()
            self.language = self.language_selector.currentText()
            self.apply_theme()
            self.apply_language()
            config = {
                'default_search_engine': self.default_search_engine,
                'theme': self.theme,
                'download_path': self.download_path,
                'language': self.language
            }
            with open(self.config_file, 'w') as file:
                json.dump(config, file)
            logging.info('Settings saved')
            print(f"Поисковая система сохранена: {self.default_search_engine}")
            print(f"Тема сохранена: {self.theme}")
            print(f"Путь загрузки сохранен: {self.download_path}")
            print(f"Язык сохранен: {self.language}")
        except Exception as e:
            self.error_logger.error(f'Error saving settings: {e}')

    def apply_theme(self):
        try:
            if self.theme == "Светлая":
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: #ffffff;
                    }
                    QToolBar {
                        background-color: #f0f0f0;
                        spacing: 10px;
                    }
                    QLineEdit {
                        padding: 5px;
                        border-radius: 5px;
                        border: 1px solid #ccc;
                        background-color: #ffffff;
                        color: #000000;
                    }
                    QPushButton, QAction {
                        background-color: #e0e0e0;
                        color: #000000;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 10px;
                    }
                    QPushButton:hover, QAction:hover {
                        background-color: #d0d0d0;
                    }
                    QLabel {
                        font-size: 14px;
                        color: #000000;
                    }
                    QCheckBox {
                        font-size: 14px;
                        color: #000000;
                    }
                    QWidget#settings_widget {
                        background-color: #ffffff;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 20px;
                    }
                    QTabBar::tab {
                        background: #e0e0e0;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 2px;
                    }
                    QTabBar::tab:selected {
                        background: #d0d0d0;
                    }
                    QTabBar::close-button {
                        image: url(close-icon.png);
                        subcontrol-position: right;
                        subcontrol-origin: padding;
                    }
                    QTabBar::close-button:hover {
                        image: url(close-icon-hover.png);
                    }
                    QTabBar::tab:!selected {
                        margin-top: 2px;
                    }
                    QToolBar QToolButton {
                        background-color: #e0e0e0;
                        border: 1px solid #ccc;
                        border-radius: 10px;
                        padding: 5px 10px;
                    }
                    QToolBar QToolButton:hover {
                        background-color: #d0d0d0;
                    }
                    QVBoxLayout {
                        spacing: 15px;
                    }
                    QHBoxLayout {
                        spacing: 10px;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QMainWindow {
                        background-color: #1e1e1e;
                    }
                    QToolBar {
                        background-color: #2e2e2e;
                        spacing: 10px;
                    }
                    QLineEdit {
                        padding: 5px;
                        border-radius: 5px;
                        border: 1px solid #555;
                        background-color: #3e3e3e;
                        color: #ffffff;
                    }
                    QPushButton, QAction {
                        background-color: #4e4e4e;
                        color: #ffffff;
                        border: none;
                        padding: 5px 10px;
                        border-radius: 10px;
                    }
                    QPushButton:hover, QAction:hover {
                        background-color: #5e5e5e;
                    }
                    QLabel {
                        font-size: 14px;
                        color: #ffffff;
                    }
                    QCheckBox {
                        font-size: 14px;
                        color: #ffffff;
                    }
                    QWidget#settings_widget {
                        background-color: #2e2e2e;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 20px;
                    }
                    QTabBar::tab {
                        background: #4e4e4e;
                        border: 1px solid #555;
                        border-radius: 10px;
                        padding: 10px;
                        margin: 2px;
                    }
                    QTabBar::tab:selected {
                        background: #5e5e5e;
                    }
                    QTabBar::close-button {
                        image: url(close-icon.png);
                        subcontrol-position: right;
                        subcontrol-origin: padding;
                    }
                    QTabBar::close-button:hover {
                        image: url(close-icon-hover.png);
                    }
                    QTabBar::tab:!selected {
                        margin-top: 2px;
                    }
                    QToolBar QToolButton {
                        background-color: #4e4e4e;
                        border: 1px solid #555;
                        border-radius: 10px;
                        padding: 5px 10px;
                    }
                    QToolBar QToolButton:hover {
                        background-color: #5e5e5e;
                    }
                    QVBoxLayout {
                        spacing: 15px;
                    }
                    QHBoxLayout {
                        spacing: 10px;
                    }
                """)
        except Exception as e:
            self.error_logger.error(f'Error applying theme: {e}')

    def apply_language(self):
        try:
            if self.language == "ru":
                self.translator.load("ru.qm")
            else:
                self.translator.load("en.qm")
            QApplication.instance().installTranslator(self.translator)
            self.retranslate_ui()
        except Exception as e:
            self.error_logger.error(f'Error applying language: {e}')

    def retranslate_ui(self):
        self.setWindowTitle(self.tr("Fast Browser"))
        self.back_button.setText(self.tr("⟵"))
        self.forward_button.setText(self.tr("⟶"))
        self.reload_button.setText(self.tr("⟳"))
        self.new_tab_button.setText(self.tr("✚"))
        self.translate_button.setText(self.tr("Перевести"))
        self.settings_button.setText(self.tr("⚙"))

    def add_new_tab(self, qurl=None, label="Новая вкладка"):
        try:
            if qurl is None:
                qurl = QUrl(self.default_search_engine)
            browser = QWebEngineView()
            browser.setUrl(qurl)
            browser.page().profile().downloadRequested.connect(self.on_download_requested)
            browser.setContextMenuPolicy(Qt.CustomContextMenu)
            browser.customContextMenuRequested.connect(self.show_context_menu)
            i = self.tabs.addTab(browser, label)
            self.tabs.setCurrentIndex(i)
            browser.urlChanged.connect(lambda qurl, browser=browser: self.update_tab_title(browser))
            browser.loadFinished.connect(lambda _, browser=browser: self.update_tab_title(browser))
            browser.iconChanged.connect(lambda _, browser=browser: self.update_tab_icon(browser))
            logging.info(f'New tab added: {qurl.toString()}')
            self.add_to_history(qurl.toString())
        except Exception as e:
            self.error_logger.error(f'Error adding new tab: {e}')

    def show_context_menu(self, pos):
        try:
            context_menu = QMenu(self)
            back_action = context_menu.addAction(self.tr("Назад"))
            forward_action = context_menu.addAction(self.tr("Вперед"))
            reload_action = context_menu.addAction(self.tr("Перезагрузить"))
            save_page_action = context_menu.addAction(self.tr("Сохранить страницу"))
            open_link_in_new_tab_action = context_menu.addAction(self.tr("Открыть ссылку в новой вкладке"))
            open_link_in_new_window_action = context_menu.addAction(self.tr("Открыть ссылку в новом окне"))
            save_link_action = context_menu.addAction(self.tr("Сохранить ссылку"))
            copy_link_address_action = context_menu.addAction(self.tr("Копировать адрес ссылки"))

            action = context_menu.exec_(self.mapToGlobal(pos))

            if action == back_action:
                self.tabs.currentWidget().back()
            elif action == forward_action:
                self.tabs.currentWidget().forward()
            elif action == reload_action:
                self.tabs.currentWidget().reload()
            elif action == save_page_action:
                self.save_page()
            elif action == open_link_in_new_tab_action:
                self.open_link_in_new_tab()
            elif action == open_link_in_new_window_action:
                self.open_link_in_new_window()
            elif action == save_link_action:
                self.save_link()
            elif action == copy_link_address_action:
                self.copy_link_address()
        except Exception as e:
            self.error_logger.error(f'Error showing context menu: {e}')

    def save_page(self):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                download_path, _ = QFileDialog.getSaveFileName(self, self.tr("Сохранить страницу"), os.path.join(self.download_path, "page.html"))
                if download_path:
                    browser.page().save(download_path, QWebEngineDownloadItem.CompleteHtmlSaveFormat)
                    logging.info(f'Page saved: {download_path}')
        except Exception as e:
            self.error_logger.error(f'Error saving page: {e}')

    def open_link_in_new_tab(self):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                page = browser.page()
                context_menu_data = page.contextMenuData()
                link_url = context_menu_data.linkUrl()
                if link_url.isValid():
                    self.add_new_tab(link_url)
        except Exception as e:
            self.error_logger.error(f'Error opening link in new tab: {e}')

    def open_link_in_new_window(self):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                page = browser.page()
                context_menu_data = page.contextMenuData()
                link_url = context_menu_data.linkUrl()
                if link_url.isValid():
                    new_browser = Browser()
                    new_browser.add_new_tab(link_url)
                    new_browser.show()
        except Exception as e:
            self.error_logger.error(f'Error opening link in new window: {e}')

    def save_link(self):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                page = browser.page()
                context_menu_data = page.contextMenuData()
                link_url = context_menu_data.linkUrl()
                if link_url.isValid():
                    download_path, _ = QFileDialog.getSaveFileName(self, self.tr("Сохранить ссылку"), os.path.join(self.download_path, link_url.fileName()))
                    if download_path:
                        self.download_file(link_url.toString(), download_path)
        except Exception as e:
            self.error_logger.error(f'Error saving link: {e}')

    def copy_link_address(self):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                page = browser.page()
                context_menu_data = page.contextMenuData()
                link_url = context_menu_data.linkUrl()
                if link_url.isValid():
                    clipboard = QApplication.clipboard()
                    clipboard.setText(link_url.toString())
                    logging.info(f'Link address copied: {link_url.toString()}')
        except Exception as e:
            self.error_logger.error(f'Error copying link address: {e}')

    def download_file(self, url, path):
        try:
            browser = self.tabs.currentWidget()
            if isinstance(browser, QWebEngineView):
                page = browser.page()
                profile = page.profile()
                download_manager = profile.downloadManager()
                download_manager.downloadRequested.connect(lambda download: self.on_download_requested(download, path))
                page.setUrl(QUrl(url))
        except Exception as e:
            self.error_logger.error(f'Error downloading file: {e}')

    def on_download_requested(self, download, path=None):
        try:
            if path is None:
                path, _ = QFileDialog.getSaveFileName(self, self.tr("Сохранить файл"), os.path.join(self.download_path, download.suggestedFileName()))
            if path:
                download.setPath(path)
                download.accept()
                logging.info(f'File download started: {path}')
        except Exception as e:
            self.error_logger.error(f'Error downloading file: {e}')

    def close_current_tab(self, i):
        try:
            if self.tabs.count() > 1:
                self.tabs.removeTab(i)
                logging.info(f'Tab closed: {i}')
        except Exception as e:
            self.error_logger.error(f'Error closing tab: {e}')

    def update_url_bar(self, i):
        try:
            if hasattr(self, 'url_bar'):  # Проверка существования url_bar
                current_widget = self.tabs.currentWidget()
                if isinstance(current_widget, QWebEngineView):  # Проверка типа текущей вкладки
                    qurl = current_widget.url()
                    self.url_bar.setText(qurl.toString())
                    self.url_bar.setCursorPosition(0)
                else:
                    self.url_bar.setText("")
        except Exception as e:
            self.error_logger.error(f'Error updating URL bar: {e}')

    def navigate_to_url(self):
        try:
            url = self.url_bar.text()
            if not url.startswith("http"):
                url = self.default_search_engine + "/search?q=" + url
            self.tabs.currentWidget().setUrl(QUrl(url))
            logging.info(f'Navigated to URL: {url}')
            self.add_to_history(url)
        except Exception as e:
            self.error_logger.error(f'Error navigating to URL: {e}')

    def update_tab_title(self, browser):
        try:
            i = self.tabs.indexOf(browser)
            title = browser.page().title()
            self.tabs.setTabText(i, title)
        except Exception as e:
            self.error_logger.error(f'Error updating tab title: {e}')

    def update_tab_icon(self, browser):
        try:
            i = self.tabs.indexOf(browser)
            icon = browser.icon()
            self.tabs.setTabIcon(i, icon)
        except Exception as e:
            self.error_logger.error(f'Error updating tab icon: {e}')

    def translate_page(self):
        try:
            current_widget = self.tabs.currentWidget()
            if isinstance(current_widget, QWebEngineView):
                current_url = current_widget.url().toString()
                translate_url = f"https://translate.google.com/translate?hl=&sl=auto&tl=ru&u={current_url}"
                current_widget.setUrl(QUrl(translate_url))
                logging.info(f'Page translated: {current_url}')
        except Exception as e:
            self.error_logger.error(f'Error translating page: {e}')

    def show_settings(self):
        try:
            settings_widget = QWidget()
            settings_widget.setObjectName("settings_widget")
            layout = QVBoxLayout()

            search_engine_label = QLabel("Поисковая страница:")
            self.search_engine_input = QLineEdit()
            self.search_engine_input.setText(self.default_search_engine)

            theme_label = QLabel("Тема:")
            self.theme_selector = QComboBox()
            self.theme_selector.addItems(["Светлая", "Темная"])
            self.theme_selector.setCurrentText(self.theme)

            download_path_label = QLabel("Путь загрузки:")
            self.download_path_input = QLineEdit()
            self.download_path_input.setText(self.download_path)
            download_path_button = QPushButton("Выбрать")
            download_path_button.clicked.connect(self.select_download_path)

            language_label = QLabel("Язык:")
            self.language_selector = QComboBox()
            self.language_selector.addItems(["ru", "en"])
            self.language_selector.setCurrentText(self.language)

            version_label = QLabel("Бета 0.1v")
            version_label.setAlignment(Qt.AlignCenter)

            author_label = QLabel("Автор: dxddy")
            author_label.setAlignment(Qt.AlignCenter)

            save_button = QPushButton("Сохранить")
            save_button.clicked.connect(self.save_settings)

            update_button = QPushButton("Обновить браузер")
            update_button.clicked.connect(self.update_browser)

            history_button = QPushButton("История")
            history_button.clicked.connect(self.show_history)

            form_layout = QFormLayout()
            form_layout.addRow(search_engine_label, self.search_engine_input)
            form_layout.addRow(theme_label, self.theme_selector)
            form_layout.addRow(download_path_label, self.download_path_input)
            form_layout.addRow("", download_path_button)
            form_layout.addRow(language_label, self.language_selector)

            layout.addLayout(form_layout)
            layout.addWidget(version_label)
            layout.addWidget(author_label)
            layout.addWidget(save_button, alignment=Qt.AlignCenter)
            layout.addWidget(update_button, alignment=Qt.AlignCenter)
            layout.addWidget(history_button, alignment=Qt.AlignCenter)

            settings_widget.setLayout(layout)
            i = self.tabs.addTab(settings_widget, "Настройки")
            self.tabs.setCurrentIndex(i)
        except Exception as e:
            self.error_logger.error(f'Error showing settings: {e}')

    def select_download_path(self):
        try:
            path = QFileDialog.getExistingDirectory(self, "Выбрать папку для загрузок", self.download_path)
            if path:
                self.download_path_input.setText(path)
        except Exception as e:
            self.error_logger.error(f'Error selecting download path: {e}')

    def update_browser(self):
        try:
            # Логика обновления браузера
            logging.info('Browser updated')
            QMessageBox.information(self, 'Обновление', 'Браузер успешно обновлен.')
        except Exception as e:
            self.error_logger.error(f'Error updating browser: {e}')
            QMessageBox.critical(self, 'Ошибка', 'Произошла ошибка при обновлении браузера.')

    def show_history(self):
        try:
            history_widget = QWidget()
            history_widget.setObjectName("history_widget")
            layout = QVBoxLayout()

            history_list = QListWidget()
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as file:
                    history = json.load(file)
                    for item in history:
                        list_item = QListWidgetItem(f"{item['url']} - {item['timestamp']}")
                        history_list.addItem(list_item)

            history_list.itemDoubleClicked.connect(self.open_history_item)
            history_list.itemClicked.connect(self.delete_history_item)

            layout.addWidget(history_list)

            history_widget.setLayout(layout)
            i = self.tabs.addTab(history_widget, "История")
            self.tabs.setCurrentIndex(i)
        except Exception as e:
            self.error_logger.error(f'Error showing history: {e}')

    def open_history_item(self, item):
        try:
            url = item.text().split(" - ")[0]
            self.add_new_tab(QUrl(url))
        except Exception as e:
            self.error_logger.error(f'Error opening history item: {e}')

    def delete_history_item(self, item):
        try:
            url = item.text().split(" - ")[0]
            reply = QMessageBox.question(self, 'Удалить историю', f'Вы уверены, что хотите удалить {url} из истории?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                history_list = item.listWidget()
                history_list.takeItem(history_list.row(item))
                self.remove_from_history(url)
        except Exception as e:
            self.error_logger.error(f'Error deleting history item: {e}')

    def add_to_history(self, url):
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as file:
                    history = json.load(file)
            else:
                history = []
            if url not in [item['url'] for item in history]:
                history.append({'url': url, 'timestamp': timestamp})
                with open(self.history_file, 'w') as file:
                    json.dump(history, file)
            logging.info(f'Added to history: {url}')
        except Exception as e:
            self.error_logger.error(f'Error adding to history: {e}')

    def remove_from_history(self, url):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as file:
                    history = json.load(file)
                history = [item for item in history if item['url'] != url]
                with open(self.history_file, 'w') as file:
                    json.dump(history, file)
            logging.info(f'Removed from history: {url}')
        except Exception as e:
            self.error_logger.error(f'Error removing from history: {e}')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Сохранить вкладки', 'Вы хотите сохранить открытые вкладки для следующего сеанса?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.save_tabs()
        else:
            if os.path.exists(self.tabs_file):
                os.remove(self.tabs_file)
        event.accept()

    def save_tabs(self):
        try:
            tabs = []
            for i in range(self.tabs.count()):
                browser = self.tabs.widget(i)
                if isinstance(browser, QWebEngineView):
                    tabs.append(browser.url().toString())
            with open(self.tabs_file, 'w') as file:
                json.dump(tabs, file)
            logging.info('Tabs saved')
        except Exception as e:
            self.error_logger.error(f'Error saving tabs: {e}')

    def restore_tabs(self):
        try:
            if os.path.exists(self.tabs_file):
                with open(self.tabs_file, 'r') as file:
                    tabs = json.load(file)
                    for tab in tabs:
                        self.add_new_tab(QUrl(tab))
                logging.info('Tabs restored')
            else:
                self.add_new_tab(QUrl(self.default_search_engine))
        except Exception as e:
            self.error_logger.error(f'Error restoring tabs: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    browser = Browser()
    browser.show()
    sys.exit(app.exec_())
