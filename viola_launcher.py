import sys, os, glob, json, requests, zipfile, shutil
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QFont, QPainterPath, QRegion, QCursor, QIcon
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal

# --- Worker thread to download update ---
class UpdateThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest

    def run(self):
        try:
            r = requests.get(self.url, stream=True)
            total = int(r.headers.get('content-length', 0))
            with open(self.dest, 'wb') as f:
                downloaded = 0
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        percent = int(downloaded / total * 100)
                        self.progress.emit(percent)
            self.finished.emit(self.dest)
        except Exception as e:
            print("Update failed:", e)
            self.finished.emit(None)

# --- Settings page (unchanged) ---
class NewPage(QWidget):
    def __init__(self, parent_launcher=None):
        super().__init__(parent_launcher)
        self.parent_launcher = parent_launcher
        self.setGeometry(0, 0, parent_launcher.width(), parent_launcher.height())
        self.setup_ui()

    def setup_ui(self):
        # Your existing settings UI here...
        pass

# --- Launcher ---
class ViolaLauncher(QWidget):
    CURRENT_VERSION = "1.0.0"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viola Launcher")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.apply_rounded_corners()
        self.setup_ui()
        self.drag_pos = None

        # --- Updater overlay ---
        self.update_overlay = QLabel(self)
        self.update_overlay.setStyleSheet(
            "background-color: black; color: white; font: bold 24px 'Segoe UI';"
        )
        self.update_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_overlay.setGeometry(0, 0, self.width(), self.height())
        self.update_overlay.hide()

        # Check for updates
        self.check_for_updates()

    # --- Rounded corners ---
    def apply_rounded_corners(self):
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        corner_radius = 25
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), corner_radius, corner_radius)
        polygon = path.toFillPolygon()
        region = QRegion(polygon.toPolygon())
        self.setMask(region)

    # --- UI setup ---
    def setup_ui(self):
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(app_path, "assets", "background.png")
        logo_path = os.path.join(app_path, "assets", "logo.png")

        # Background
        bg_label = QLabel(self)
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path).scaled(
                self.size(), Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation
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
            QPushButton { background-color: #7C1FFF; color: white; border-radius: 15px; font: bold 18px "Segoe UI"; }
            QPushButton:hover { background-color: #9B47FF; }
        """)
        self.launch_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.launch_button.clicked.connect(self.launch_minecraft)

        # Settings button
        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setGeometry(self.width()//2 - 100, self.height()//2 + 130, 200, 50)
        self.settings_button.setStyleSheet("""
            QPushButton { background-color: #818589; color: white; border-radius: 15px; font: bold 16px "Segoe UI"; }
            QPushButton:hover { background-color: #9b9da0; }
        """)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.clicked.connect(self.open_settings)

        # Custom window buttons
        button_style = """
            QPushButton { color: white; background: transparent; border: none; font: bold 20px "Segoe UI"; }
            QPushButton:hover { color: #aaaaaa; }
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

        # Settings page
        self.settings_page = NewPage(self)
        self.settings_page.hide()

    # --- Updater ---
    def check_for_updates(self):
        try:
            r = requests.get("https://raw.githubusercontent.com/ThatWeirdGuy259/ViolaLauncher/main/latest.json", timeout=5)
            data = r.json()
            latest_version = data.get("version")
            url = data.get("url")
            if latest_version != self.CURRENT_VERSION:
                self.update_overlay.setText("Updating… 0%")
                self.update_overlay.show()
                dest_zip = os.path.join(os.path.dirname(os.path.abspath(__file__)), "update.zip")
                self.update_thread = UpdateThread(url, dest_zip)
                self.update_thread.progress.connect(self.update_progress)
                self.update_thread.finished.connect(self.update_finished)
                self.update_thread.start()
        except Exception as e:
            print("Failed to check updates:", e)

    def update_progress(self, percent):
        self.update_overlay.setText(f"Updating… {percent}%")

    def update_finished(self, path):
        if path:
            try:
                current_folder = os.path.dirname(os.path.abspath(__file__))
                with zipfile.ZipFile(path, 'r') as zip_ref:
                    zip_ref.extractall(current_folder)
                os.remove(path)
                self.update_overlay.setText("Update complete!")
                QThread.sleep(1)
                self.update_overlay.hide()
                print("Update applied successfully.")
            except Exception as e:
                self.update_overlay.setText("Update failed!")
                print("Update failed:", e)
                QThread.sleep(2)
                self.update_overlay.hide()
        else:
            self.update_overlay.setText("Update failed!")
            QThread.sleep(2)
            self.update_overlay.hide()

    # --- Settings navigation ---
    def open_settings(self):
        self.greeting_label.hide()
        self.launch_button.hide()
        self.settings_button.hide()
        self.settings_page.show()

    def return_to_main(self):
        self.greeting_label.show()
        self.launch_button.show()
        self.settings_button.show()
        self.settings_page.hide()

    # --- Launch Minecraft ---
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

    # --- Dragging ---
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
