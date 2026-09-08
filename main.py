import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMainWindow, QStackedWidget
from PyQt6.QtGui import QIcon
from database import Database
from ui.login import LoginWindow
from ui.dashboard import Dashboard

class MyTradeManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Trade Manager")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize database
        self.db = Database()
        self.db.create_tables()
        
        # Setup main widget
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Check if user exists
        if self.db.get_users():
            self.show_dashboard()
        else:
            self.show_login()
        
        self.show()
    
    def show_login(self):
        self.login_window = LoginWindow(self)
        self.stacked_widget.addWidget(self.login_window)
        self.stacked_widget.setCurrentWidget(self.login_window)
    
    def show_dashboard(self):
        self.dashboard = Dashboard(self.db, self)
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.setCurrentWidget(self.dashboard)

def main():
    app = QApplication(sys.argv)
    manager = MyTradeManager()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
