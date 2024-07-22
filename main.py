import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtSvg import QSvgWidget

class ThreeDotsMenu(QMenu):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dark_mode_action = QAction("Dark Mode", self, checkable=True)
        self.addAction(self.dark_mode_action)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.page().titleChanged.connect(self.update_title)
        self.browser.loadStarted.connect(self.clear_url_bar)
        self.browser.loadFinished.connect(self.update_url_bar_with_current_page_url)
        self.browser.setUrl(QUrl('https://duckduckgo.com/'))
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.addTab(self.browser, "New Tab")
        
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.tab_widget)
        
        navbar = QToolBar()
        navbar.setMovable(False)
        navbar.setIconSize(QSize(16, 16))
        layout.addWidget(navbar)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)
        self.showMaximized()

        back_btn = QAction(self.create_svg_icon("./icons/back.svg"), 'Back', self)
        back_btn.triggered.connect(lambda: self.current_web_view().back() if self.current_web_view() else None)
        navbar.addAction(back_btn)

        forward_btn = QAction(self.create_svg_icon("./icons/forward.svg"), 'Forward', self)
        forward_btn.triggered.connect(lambda: self.current_web_view().forward() if self.current_web_view() else None)
        navbar.addAction(forward_btn)

        refresh_btn = QAction(self.create_svg_icon("./icons/refresh.svg"), 'Refresh', self)
        refresh_btn.triggered.connect(lambda: self.current_web_view().reload() if self.current_web_view() else None)
        navbar.addAction(refresh_btn)

        home_btn = QAction(self.create_svg_icon("./icons/home.svg"), 'Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        navbar.addSeparator()

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search the web or type a URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        add_tab_btn = QAction(self.create_svg_icon("./icons/add_tab.svg"), 'New Tab', self)
        add_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(add_tab_btn)

        self.three_dots_menu = ThreeDotsMenu(self)
        three_dots_btn = QToolButton(self)
        three_dots_btn.setIcon(self.create_svg_icon("./icons/three_dots.svg"))
        three_dots_btn.setPopupMode(QToolButton.InstantPopup)
        three_dots_btn.setMenu(self.three_dots_menu)
        navbar.addWidget(three_dots_btn)

        self.three_dots_menu.dark_mode_action.triggered.connect(self.toggle_dark_mode)

        self.web_views = {0: self.browser}
        self.web_pages = {}

        self.setup_shortcuts()
        self.dark_mode = False

    def create_svg_icon(self, path):
        svg_widget = QSvgWidget(path)
        svg_widget.setFixedSize(QSize(16, 16))
        pixmap = QPixmap(svg_widget.size())
        pixmap.fill(Qt.transparent)
        svg_widget.render(pixmap)
        return QIcon(pixmap)

    def setup_shortcuts(self):
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(self.close_current_tab)

        open_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        open_tab_shortcut.activated.connect(self.add_new_tab)

    def navigate_home(self):
        self.current_web_view().setUrl(QUrl('https://duckduckgo.com/'))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            search_url = f"https://www.google.com/search?q={url}"
            self.current_web_view().setUrl(QUrl(search_url))
        else:
            self.current_web_view().setUrl(QUrl(url))

    def update_title(self, title):
        index = self.tab_widget.currentIndex()
        self.tab_widget.setTabText(index, title)

    def add_new_tab(self):
        new_web_view = QWebEngineView()
        new_page = QWebEnginePage(new_web_view)
        new_page.titleChanged.connect(self.update_title)
        new_web_view.setPage(new_page)
        index = self.tab_widget.addTab(new_web_view, "New Tab")
        self.tab_widget.setCurrentIndex(index)
        self.web_views[index] = new_web_view
        self.web_pages[index] = new_page
        new_web_view.setUrl(QUrl('https://duckduckgo.com/'))
        new_web_view.loadStarted.connect(self.clear_url_bar)
        new_web_view.loadFinished.connect(self.update_url_bar_with_current_page_url)

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
            del self.web_views[index]
            del self.web_pages[index]
        else:
            self.close()

    def close_current_tab(self):
        self.close_tab(self.tab_widget.currentIndex())

    def current_web_view(self):
        index = self.tab_widget.currentIndex()
        return self.web_views.get(index)

    def current_web_page(self):
        index = self.tab_widget.currentIndex()
        return self.web_pages.get(index)

    def clear_url_bar(self):
        self.url_bar.setText("")

    def update_url_bar_with_current_page_url(self, ok):
        url = self.current_web_view().url().toString()
        self.url_bar.setText(url)

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        self.apply_theme()

    def apply_theme(self):
        if self.dark_mode:
            self.setStyleSheet(self.get_dark_theme())
        else:
            self.setStyleSheet(self.get_light_theme())

    def get_light_theme(self):
        return """
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                color: #5f6368;
                min-width: 8ex;
                min-height: 2.5ex;
                padding: 6px 12px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #ffffff;
                color: #202124;
            }
            QTabBar::close-button {
                image: url(./icons/close.svg);
                subcontrol-position: right;
            }
            QToolBar {
                background-color: #ffffff;
                border: none;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QToolBar QToolButton:hover {
                background-color: #e0e0e0;
            }
            QLineEdit {
                background-color: #f1f3f4;
                border: 1px solid #f1f3f4;
                border-radius: 18px;
                padding: 5px 10px;
                selection-background-color: #cfe4fc;
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 1px solid #4285f4;
            }
        """

    def get_dark_theme(self):
        return """
            QMainWindow {
                background-color: #202124;
            }
            QTabWidget::pane {
                border: none;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar::tab {
                background-color: #3c4043;
                color: #9aa0a6;
                min-width: 8ex;
                min-height: 2.5ex;
                padding: 6px 12px;
                border: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                margin-right: 2px;
            }
            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #292b2e;
                color: #e8eaed;
            }
            QTabBar::close-button {
                image: url(./icons/close_dark.svg);
                subcontrol-position: right;
            }
            QToolBar {
                background-color: #292b2e;
                border: none;
                padding: 5px;
            }
            QToolBar QToolButton {
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QToolBar QToolButton:hover {
                background-color: #3c4043;
            }
            QLineEdit {
                background-color: #3c4043;
                border: 1px solid #3c4043;
                border-radius: 18px;
                padding: 5px 10px;
                color: #e8eaed;
                selection-background-color: #8ab4f8;
            }
            QLineEdit:focus {
                background-color: #202124;
                border: 1px solid #8ab4f8;
            }
        """

app = QApplication(sys.argv)

QApplication.setApplicationName("CrypBrowser")
window = MainWindow()
window.apply_theme()
app.exec_()