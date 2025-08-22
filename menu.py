import sys, os, glob, subprocess, shutil, tempfile, hashlib, zipfile, requests
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QMessageBox
from PyQt6.QtGui import QPixmap, QFont, QPainterPath, QRegion, QCursor, QIcon
from PyQt6.QtCore import Qt, QRectF

CURRENT_VERSION = "1.0.0"  # must match your GitHub release tag (without "v")

class NewPage(QWidget):
    def __init__(self, parent_launcher=None):
        super().__init__(parent_launcher)
        self.parent_launcher = parent_launcher
        self.setGeometry(0, 0, parent_launcher.width(), parent_launcher.height())
        self.setup_ui()

    def setup_ui(self):
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        bg_path = os.path.join(app_path, "assets", "background.png")

        # Background
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
            self.bg_label.setStyleSheet("background-color: #1e1e1e;")
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        # Overlay
        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 25px;")
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.raise_()

        # Label
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

        # --- Icon setup ---
        app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        icon_paths = [
            os.path.join(app_path, "assets", "logo.ico"),
            os.path.join(app_path, "assets", "icon.ico"),
            os.path.join(app_path, "assets", "logo.png")
        ]
        for path in icon_paths:
            if os.path.exists(path):
                self.setWindowIcon(QIcon(path))
                break

        self.setWindowTitle("Viola Client")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.apply_rounded_corners()
        self.setup_ui()

        self.drag_pos = None

        # 🔄 Check for updates right away
        self.check_for_updates_on_startup()

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
        greeting = "Good Morning!" if 5 <= hour < 12 else "Good Afternoon!" if 12 <= hour < 18 else "Good Evening!"
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

        # Settings button
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

        # Settings page
        self.settings_page = NewPage(self)
        self.settings_page.hide()

        # Update overlay
        self.update_overlay = QLabel(self)
        self.update_overlay.setGeometry(0, 0, self.width(), self.height())
        self.update_overlay.setStyleSheet("background-color: black;")
        self.update_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_overlay.hide()

        self.update_label = QLabel("Updating... 0%", self.update_overlay)
        self.update_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.update_label.setStyleSheet("color: white;")
        self.update_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_label.setGeometry(0, 0, self.width(), self.height())

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
                        subprocess.Popen([path], shell=True)
                        launched = True
                        break
                    except Exception:
                        continue
            if not launched:
                QMessageBox.critical(self, "Launch Failed", "Failed to launch Minecraft.\nPlease check your installation.")

    # --- Updater ---
    def check_for_updates_on_startup(self):
        try:
            url = "https://raw.githubusercontent.com/ThatWeirdGuy259/ViolaLauncher/main/latest.json"
            r = requests.get(url, timeout=10)
            r.raise_for_status()
            latest = r.json()

            latest_version = latest["version"]
            download_url = latest["url"]
            expected_sha256 = latest["sha256"]

            if latest_version != CURRENT_VERSION:
                self.start_update(download_url, expected_sha256, latest_version)
        except Exception as e:
            print(f"[Updater] Failed to check for updates: {e}")

    def start_update(self, url, expected_sha256, latest_version):
        try:
            # Hide UI
            self.greeting_label.hide()
            self.launch_button.hide()
            self.settings_button.hide()
            self.update_overlay.show()

            tmpdir = tempfile.mkdtemp()
            zip_path = os.path.join(tmpdir, "update.zip")

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get("Content-Length", 0))
                downloaded = 0

                with open(zip_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int(downloaded * 100 / total_size)
                            self.update_label.setText(f"Updating... {percent}%")
                            QApplication.processEvents()

            # Verify SHA256
            sha256 = hashlib.sha256()
            with open(zip_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256.update(chunk)

            if sha256.hexdigest().lower() != expected_sha256.lower():
                self.update_label.setText("Update failed: checksum mismatch")
                return

            # Extract and replace exe
            extract_path = os.path.join(tmpdir, "extracted")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)

            current_exe = sys.argv[0]
            new_exe_path = os.path.join(extract_path, os.path.basename(current_exe))
            shutil.copy2(new_exe_path, current_exe)

            self.update_label.setText("Update complete! Restarting...")
            QApplication.processEvents()

            os.execv(current_exe, sys.argv)

        except Exception as e:
            self.update_label.setText(f"Update failed: {e}")

    # --- Dragging window ---
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
