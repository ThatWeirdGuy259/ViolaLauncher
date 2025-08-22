import sys, os, glob
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QFont, QPainterPath, QRegion, QCursor, QIcon
from PyQt6.QtCore import Qt, QRectF

class NewPage(QWidget):
    def __init__(self, parent_launcher=None):
        super().__init__(parent_launcher)
        self.parent_launcher = parent_launcher
        self.setGeometry(0, 0, parent_launcher.width(), parent_launcher.height())
        self.setup_ui()

    def setup_ui(self):
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(app_path, "assets", "background.png")

        # Background same as main launcher
        self.bg_label = QLabel(self)
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path).scaled(
                self.width(),
                self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(bg_pixmap)
        else:
            self.bg_label.setStyleSheet("background-color: #1e1e1e;")  # fallback color
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        # Semi-transparent overlay
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 25px;")
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.raise_()

        # Page label
        label = QLabel("Welcome to Settings!", self)
        label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 0, self.width(), self.height())

        # Back button
        self.back_button = QPushButton("Back", self)
        self.back_button.setGeometry(self.width()//2 - 60, self.height() - 80, 120, 40)
        self.back_button.setStyleSheet("""
            QPushButton {
                background-color: #7C1FFF;
                color: white;
                border-radius: 15px;
                font: bold 16px "Segoe UI";
            }
            QPushButton:hover {
                background-color: #9B47FF;
            }
        """)
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.clicked.connect(lambda: self.parent_launcher.return_to_main())

class ViolaLauncher(QWidget):
    def __init__(self):
        super().__init__()

        # --- Set window icon with multiple fallbacks ---
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_paths = [
            os.path.join(app_path, "assets", "logo.ico"),  # primary
            os.path.join(app_path, "assets", "icon.ico"),  # backup
            os.path.join(app_path, "assets", "logo.png")   # final fallback
        ]
        for path in icon_paths:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break
        # --- End icon setup ---

        self.setWindowTitle("Viola Client")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.apply_rounded_corners()
        self.setup_ui()

        # For dragging
        self.drag_pos = None

    def apply_rounded_corners(self):
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        corner_radius = 25
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), corner_radius, corner_radius)
        polygon = path.toFillPolygon()
        region = QRegion(polygon.toPolygon())
        self.setMask(region)

    def setup_ui(self):
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(app_path, "assets", "background.png")
        logo_path = os.path.join(app_path, "assets", "logo.png")

        # Background
        bg_label = QLabel(self)
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            bg_label.setPixmap(bg_pixmap)
        else:
            bg_label.setStyleSheet("background-color: #1e1e1e;")
        bg_label.setGeometry(0, 0, self.width(), self.height())
        bg_label.lower()

        # Overlay
        overlay = QLabel(self)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 25px;")
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.raise_()

        # Logo
        logo_label = QLabel(self)
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(40, 40, Qt.AspectRatioMode.KeepAspectRatio,
                                                   Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        logo_label.setGeometry(20, 20, 40, 40)

        # Title
        title_label = QLabel("Viola Launcher", self)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setGeometry(70, 20, 300, 40)

        # Greeting
        hour = datetime.now().hour
        if 5 <= hour < 12:
            greeting = "Good Morning!"
        elif 12 <= hour < 18:
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        self.greeting_label = QLabel(greeting, self)
        self.greeting_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.greeting_label.setStyleSheet("color: white;")
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.greeting_label.setGeometry(0, 0, self.width(), self.height())

        # Launch button
        self.launch_button = QPushButton("Launch", self)
        self.launch_button.setGeometry(self.width()//2 - 100, self.height()//2 + 60, 200, 50)
        self.launch_button.setStyleSheet("""
            QPushButton {
                background-color: #7C1FFF;
                color: white;
                border-radius: 15px;
                font: bold 18px "Segoe UI";
            }
            QPushButton:hover {
                background-color: #9B47FF;
            }
        """)
        self.launch_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.launch_button.clicked.connect(self.launch_minecraft)

        # --- Settings button ---
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setGeometry(self.width()//2 - 100, self.height()//2 + 130, 200, 50)
        self.settings_button.setStyleSheet("""
            QPushButton {
                background-color: #818589;
                color: white;
                border-radius: 15px;
                font: bold 16px "Segoe UI";
            }
            QPushButton:hover {
                background-color: #9b9da0;
            }
        """)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.clicked.connect(self.open_settings)

        # Custom window buttons
        button_style = """
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                font: bold 20px "Segoe UI";
            }
            QPushButton:hover {
                color: #aaaaaa;
            }
        """
        self.min_button = QPushButton("–", self)
        self.min_button.setGeometry(self.width() - 80, 20, 30, 30)
        self.min_button.setStyleSheet(button_style)
        self.min_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.min_button.clicked.connect(self.showMinimized)

        self.close_button = QPushButton("×", self)
        self.close_button.setGeometry(self.width() - 40, 20, 30, 30)
        self.close_button.setStyleSheet(button_style)
        self.close_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_button.clicked.connect(self.close)

        # --- Create the settings page, hidden initially ---
        self.settings_page = NewPage(self)
        self.settings_page.hide()

    def open_settings(self):
        # Hide main page elements
        self.greeting_label.hide()
        self.launch_button.hide()
        self.settings_button.hide()
        # Show settings page
        self.settings_page.show()

    def return_to_main(self):
        # Show main page elements
        self.greeting_label.show()
        self.launch_button.show()
        self.settings_button.show()
        # Hide settings page
        self.settings_page.hide()

    def launch_minecraft(self):
        try:
            os.startfile("minecraft://")
        except Exception:
            possible_paths = glob.glob(r"C:\Program Files\WindowsApps\Microsoft.MinecraftUWP_*\Minecraft.Windows.exe")
            possible_paths.append(r"C:\Program Files\Microsoft Studios\Minecraft\Minecraft.Windows.exe")
            launched = False
            for path in possible_paths:
                if os.path.exists(path):
                    try:
                        os.startfile(path)
                        launched = True
                        break
                    except Exception:
                        continue
            if not launched:
                print("Failed to launch Minecraft. Please check your installation.")

    # Dragging
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ViolaLauncher()
    window.show()
    sys.exit(app.exec())
