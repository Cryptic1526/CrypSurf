import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.browser = QWebEngineView()
        self.browser.page().titleChanged.connect(self.update_title)
        self.browser.loadStarted.connect(self.clear_url_bar)
        self.browser.loadFinished.connect(self.update_url_bar_with_current_page_url)
        self.browser.setUrl(QUrl('https://duckduckgo.com/'))
        
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.browser, "Loading...")
        
        layout = QVBoxLayout()
        layout.addWidget(self.tab_widget)
        
        navbar = QToolBar()
        navbar.setStyleSheet("padding-left: 10px; padding-right: 10px; padding-top: 5px; padding-bottom: 5px;")
        layout.addWidget(navbar)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        
        self.setCentralWidget(central_widget)
        self.showMaximized()

        back_btn = QAction('Back', self)
        back_btn.triggered.connect(lambda: self.current_web_view().back() if self.current_web_view() else None)
        navbar.addAction(back_btn)

        forward_btn = QAction('Forward', self)
        forward_btn.triggered.connect(lambda: self.current_web_view().forward() if self.current_web_view() else None)
        navbar.addAction(forward_btn)

        refresh_btn = QAction('Refresh', self)
        refresh_btn.triggered.connect(lambda: self.current_web_view().reload() if self.current_web_view() else None)
        navbar.addAction(refresh_btn)

        home_btn = QAction('Home', self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        add_tab_btn = QAction('Add Tab', self)
        add_tab_btn.triggered.connect(self.add_new_tab)
        navbar.addAction(add_tab_btn)

        remove_tab_btn = QAction('Remove Current Tab', self)
        remove_tab_btn.triggered.connect(self.remove_current_tab)
        navbar.addAction(remove_tab_btn)

        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter search query or URL")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)
        self.url_bar.setStyleSheet("padding: 5px; border: 1px solid black; border-radius: 10px;")

        self.web_views = {0: self.browser}
        self.web_pages = {}

        self.setup_shortcuts()

    def setup_shortcuts(self):
        close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        close_tab_shortcut.activated.connect(self.remove_current_tab)

        open_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        open_tab_shortcut.activated.connect(self.add_new_tab)

    def navigate_home(self):
        self.current_web_view().setUrl(QUrl('https://duckduckgo.com/'))

    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith(("http://", "https://")):
            search_url = f"https://duckduckgo.com/?q={url}"
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
        index = self.tab_widget.addTab(new_web_view, "+")
        self.tab_widget.setCurrentIndex(index)
        self.web_views[index] = new_web_view
        self.web_pages[index] = new_page
        new_web_view.setUrl(QUrl('https://duckduckgo.com/'))
        new_web_view.loadStarted.connect(self.clear_url_bar)
        new_web_view.loadFinished.connect(self.update_url_bar_with_current_page_url)

    def remove_current_tab(self):
        if self.tab_widget.count() > 1:
            index = self.tab_widget.currentIndex()
            self.tab_widget.removeTab(index)
            del self.web_views[index]
            del self.web_pages[index]
        else:
            sys.exit()

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

app = QApplication(sys.argv)

# app.setStyleSheet("""
#     QMainWindow {
#         background-color: #07090D; 
#         border-radius: 10px;
#     }
#     QToolBar {
#         background-color: #0E121B;
#         color: white;
#         border-radius: 5px; 
#     }
#     QPushButton, QLineEdit {
#         border: none;
#         color: white;
#         background-color: #1C2435; 
#         padding: 5px;
#         border-radius: 10px;
#     }
#     QPushButton:hover, QLineEdit:focus {
#         background-color: #2F3640;
#     }
#     QTabWidget {
#         background-color: #07090D;
#         color: white;
#     }
#     QTabBar::tab {
#         background-color: #07090D;
#         color: white;
#         padding: 10px;
#         border-width: 2px; 
#         border-style: solid;
#         border-color: #0E121B;
#         border-radius: 10px;
#     }
#     QTabBar::tab:selected {
#         background-color: #0E121B;
#     }
#     QToolBar::action {
#         color: white; 
#     }
#     QToolBar::action:hover {
#         background-color: #1C2435; /* Button color on hover */
#     }
# """)

QApplication.setApplicationName("CrypBrowser")
window = MainWindow()
app.exec_()