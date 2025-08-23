import sys, os, glob, json, requests, zipfile, tempfile, subprocess, threading, time
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from PyQt6.QtGui import QPixmap, QFont, QPainterPath, QRegion, QCursor, QIcon, QPainter, QKeySequence
from PyQt6.QtCore import Qt, QRectF, QThread, pyqtSignal, QTimer

# ---------------- Paths & Config ----------------
CONFIG_FILENAME = "config.json"

def resource_dir():
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))

def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

def config_path():
    return os.path.join(app_dir(), CONFIG_FILENAME)

def read_json(path, default=None):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return default if default is not None else {}

def write_json(path, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print("Failed to write config:", e)
        return False

# ---------------- Worker Thread for Updater ----------------
class UpdateThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, url, dest):
        super().__init__()
        self.url = url
        self.dest = dest

    def run(self):
        try:
            r = requests.get(self.url, stream=True, timeout=30)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(self.dest, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            percent = int(downloaded / total * 100)
                            self.progress.emit(min(max(percent, 0), 100))
            if total == 0:
                self.progress.emit(100)
            self.finished.emit(True, self.dest)
        except Exception as e:
            print("Update Finished:", e)
            self.finished.emit(False, str(e))

# ---------------- Overlay Window ----------------
class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(500, 360)
        self.move(300, 200)

        self.title = QLabel("Viola Modules Menu", self)
        self.title.setStyleSheet("color: white; font: bold 20px 'Segoe UI';")
        self.title.adjustSize()
        self.title.move(30, 24)

        self.hint = QLabel("(Press hotkey again to hide)", self)
        self.hint.setStyleSheet("color: rgba(255,255,255,180); font: 12px 'Segoe UI';")
        self.hint.adjustSize()
        self.hint.move(30, 60)

        self.items = [
            "• Keystrokes / CPS / FPS",
            "• Coordinates HUD",
            "• Zoom",
            "• ToggleSprint / ToggleSneak",
            "• Armor / Potions / Packs",
        ]
        y = 100
        self.item_labels = []
        for txt in self.items:
            lab = QLabel(txt, self)
            lab.setStyleSheet("color: white; font: 14px 'Segoe UI';")
            lab.adjustSize()
            lab.move(40, y)
            y += 28
            self.item_labels.append(lab)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        rect = self.rect().adjusted(0, 0, -1, -1)
        painter.setBrush(Qt.GlobalColor.black)
        painter.setOpacity(0.65)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 20, 20)
        painter.setOpacity(1.0)

# ---------------- Hotkey helpers ----------------
def normalize_hotkey(hk_str: str) -> str:
    mapping = {
        "return": "enter",
        "escape": "esc",
        "backtick": "`",
        "plus": "+",
        "minus": "-",
        "equals": "=",
    }
    s = (hk_str or "").strip().lower()
    return mapping.get(s, s)

def load_hotkey():
    cfg = read_json(config_path(), {})
    return normalize_hotkey(cfg.get("modules_hotkey", "right shift"))

def save_hotkey(hk: str):
    cfg = read_json(config_path(), {})
    cfg["modules_hotkey"] = hk.strip()
    write_json(config_path(), cfg)

def hotkey_listener(toggle_callback, hk_display: str):
    try:
        import keyboard
    except ImportError:
        print("Missing dependency: pip install keyboard")
        return
    hk = normalize_hotkey(hk_display)
    print(f"[Viola Overlay] Listening for hotkey: {hk_display} (normalized: '{hk}')")
    try:
        keyboard.add_hotkey(hk, toggle_callback, suppress=False, trigger_on_release=False)
    except Exception as e:
        print("Failed to bind hotkey:", e)
    while True:
        time.sleep(0.25)

# ---------------- Settings Page ----------------
class SettingsPage(QWidget):
    def __init__(self, parent_launcher=None):
        super().__init__(parent_launcher)
        self.parent_launcher = parent_launcher
        self.setGeometry(0, 0, parent_launcher.width(), parent_launcher.height())
        self.waiting_for_key = False
        self.setup_ui()

    def setup_ui(self):
        rdir = resource_dir()
        bg_path = os.path.join(rdir, "assets", "background.png")

        self.bg_label = QLabel(self)
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path).scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )
            self.bg_label.setPixmap(bg_pixmap)
        else:
            self.bg_label.setStyleSheet("background-color: #1e1e1e;")
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
        self.bg_label.lower()

        self.overlay = QLabel(self)
        self.overlay.setStyleSheet("background-color: rgba(0,0,0,120); border-radius: 25px;")
        self.overlay.setGeometry(0, 0, self.width(), self.height())
        self.overlay.raise_()

        label = QLabel("Settings", self)
        label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        label.setStyleSheet("color: white;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setGeometry(0, 40, self.width(), 60)

        self.hotkey_button = QPushButton(load_hotkey(), self)
        self.hotkey_button.setGeometry(self.width()//2 - 120, 140, 240, 40)
        self.hotkey_button.setStyleSheet("""
            QPushButton {
                background-color: #2e2e2e;
                color: white;
                border-radius: 12px;
                font: bold 16px "Segoe UI";
            }
            QPushButton:hover {
                background-color: #454545;
            }
        """)
        self.hotkey_button.clicked.connect(self.wait_for_key)

        save_button = QPushButton("Save Hotkey", self)
        save_button.setGeometry(self.width() // 2 - 70, 200, 140, 40)
        save_button.setStyleSheet("""
            QPushButton { background-color: #7C1FFF; color: white; border-radius: 15px; font: bold 16px "Segoe UI"; }
            QPushButton:hover { background-color: #9B47FF; }
        """)
        save_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        save_button.clicked.connect(self.save_hotkey)

        self.back_button = QPushButton("Back", self)
        self.back_button.setGeometry(self.width() // 2 - 60, self.height() - 80, 120, 40)
        self.back_button.setStyleSheet("""
            QPushButton { background-color: #818589; color: white; border-radius: 15px; font: bold 16px "Segoe UI"; }
            QPushButton:hover { background-color: #9b9da0; }
        """)
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.back_button.clicked.connect(lambda: self.parent_launcher.return_to_main())

    def wait_for_key(self):
        if self.waiting_for_key:
            return
        self.waiting_for_key = True
        self.hotkey_button.setText("Press any key...")
        self.grabKeyboard()

    def keyPressEvent(self, event):
        if self.waiting_for_key:
            key = event.key()
            key_text = QKeySequence(key).toString()
            if key_text:
                self.hotkey_button.setText(key_text.lower())
            else:
                self.hotkey_button.setText("Unknown")
            self.waiting_for_key = False
            self.releaseKeyboard()

    def save_hotkey(self):
        new_hk = self.hotkey_button.text().strip()
        if new_hk:
            save_hotkey(new_hk)
            print(f"Hotkey saved: {new_hk}")
            self.parent_launcher.rebind_hotkey(new_hk)

# ---------------- Main Launcher ----------------
class ViolaLauncher(QWidget):
    CURRENT_VERSION = "1.0.28"

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Viola Launcher")
        self.setFixedSize(900, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        rdir = resource_dir()
        for p in [os.path.join(rdir, "assets", "logo.ico"), os.path.join(rdir, "assets", "logo.png")]:
            if os.path.exists(p):
                self.setWindowIcon(QIcon(p))
                break

        self.apply_rounded_corners()
        self.setup_ui()
        self.drag_pos = None

        self.overlay_window = OverlayWindow()
        self.overlay_window.hide()

        self._hotkey_thread = None
        self.rebind_hotkey(load_hotkey())

        self.update_overlay = QLabel(self)
        self.update_overlay.setStyleSheet("background-color: black; color: white; font: bold 24px 'Segoe UI';")
        self.update_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_overlay.setGeometry(0, 0, self.width(), self.height())
        self.update_overlay.hide()
        self.check_for_updates()

    def rebind_hotkey(self, hk):
        def run_listener():
            hotkey_listener(self.toggle_overlay, hk)
        t = threading.Thread(target=run_listener, daemon=True)
        t.start()
        self._hotkey_thread = t

    def toggle_overlay(self):
        if self.overlay_window.isVisible():
            self.overlay_window.hide()
        else:
            self.overlay_window.show()

    def apply_rounded_corners(self):
        path = QPainterPath()
        path.setFillRule(Qt.FillRule.WindingFill)
        corner_radius = 25
        path.addRoundedRect(QRectF(0, 0, self.width(), self.height()), corner_radius, corner_radius)
        polygon = path.toFillPolygon()
        region = QRegion(polygon.toPolygon())
        self.setMask(region)

    def setup_ui(self):
        rdir = resource_dir()
        bg_path = os.path.join(rdir, "assets", "background.png")
        logo_path = os.path.join(rdir, "assets", "logo.png")

        bg_label = QLabel(self)
        if os.path.exists(bg_path):
            bg_pixmap = QPixmap(bg_path).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation,
            )
            bg_label.setPixmap(bg_pixmap)
        else:
            bg_label.setStyleSheet("background-color: #1e1e1e;")
        bg_label.setGeometry(0, 0, self.width(), self.height())
        bg_label.lower()

        overlay = QLabel(self)
        overlay.setStyleSheet("background-color: rgba(0, 0, 0, 120); border-radius: 25px;")
        overlay.setGeometry(0, 0, self.width(), self.height())
        overlay.raise_()

        logo_label = QLabel(self)
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path).scaled(
                40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(logo_pixmap)
        logo_label.setGeometry(20, 20, 40, 40)

        title_label = QLabel("Viola Launcher", self)
        title_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setGeometry(70, 20, 300, 40)

        hour = datetime.now().hour
        greeting = "Good Morning!" if 5 <= hour < 12 else ("Good Afternoon!" if 12 <= hour < 18 else "Good Evening!")
        self.greeting_label = QLabel(greeting, self)
        self.greeting_label.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.greeting_label.setStyleSheet("color: white;")
        self.greeting_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.greeting_label.setGeometry(0, 0, self.width(), self.height())

        self.launch_button = QPushButton("Launch", self)
        self.launch_button.setGeometry(self.width() // 2 - 100, self.height() // 2 + 60, 200, 50)
        self.launch_button.setStyleSheet("""
            QPushButton { background-color: #7C1FFF; color: white; border-radius: 15px; font: bold 18px "Segoe UI"; }
            QPushButton:hover { background-color: #9B47FF; }
        """)
        self.launch_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.launch_button.clicked.connect(self.launch_minecraft)

        self.settings_button = QPushButton("Settings", self)
        self.settings_button.setGeometry(self.width() // 2 - 100, self.height() // 2 + 130, 200, 50)
        self.settings_button.setStyleSheet("""
            QPushButton { background-color: #818589; color: white; border-radius: 15px; font: bold 16px "Segoe UI"; }
            QPushButton:hover { background-color: #9b9da0; }
        """)
        self.settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.settings_button.clicked.connect(self.open_settings)

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

        self.settings_page = SettingsPage(self)
        self.settings_page.hide()

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
            return
        except Exception:
            pass
        possible_paths = glob.glob(r"C:\Program Files\WindowsApps\Microsoft.MinecraftUWP_*\Minecraft.Windows.exe")
        possible_paths.append(r"C:\Program Files\Microsoft Studios\Minecraft\Minecraft.Windows.exe")
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    os.startfile(path)
                    return
                except Exception:
                    continue
        print("Failed to launch Minecraft. Please check your installation.")

    def check_for_updates(self):
        try:
            r = requests.get(
                "https://github.com/ThatWeirdGuy259/ViolaLauncher/releases/latest/download/latest.json",
                timeout=5,
            )
            data = r.json()
            latest_version = str(data.get("version", "")).strip()
            url = data.get("url")
            if latest_version and latest_version != self.CURRENT_VERSION and url:
                self.launch_button.setEnabled(False)
                self.update_overlay.setText("Updating… 0%")
                self.update_overlay.show()
                dest_zip = os.path.join(tempfile.gettempdir(), "viola_update.zip")
                self.update_thread = UpdateThread(url, dest_zip)
                self.update_thread.progress.connect(self.update_progress)
                self.update_thread.finished.connect(self.update_finished)
                self.update_thread.start()
        except Exception as e:
            print("Failed to check updates:", e)

    def update_progress(self, percent):
        self.update_overlay.setText(f"Updating… {percent}%")

    def update_finished(self, success, path_or_err):
        if success and path_or_err and os.path.exists(path_or_err):
            try:
                with zipfile.ZipFile(path_or_err, "r") as zip_ref:
                    target_dir = app_dir()
                    zip_ref.extractall(target_dir)
                try:
                    os.remove(path_or_err)
                except Exception:
                    pass
                self.update_overlay.setText("Update complete!")
                QTimer.singleShot(1000, self.restart_launcher)
            except Exception as e:
                print("Update extraction failed:", e)
                self.update_overlay.setText("Update failed!")
                QTimer.singleShot(2000, self.update_overlay.hide)
                self.launch_button.setEnabled(True)
        else:
            print("Update failed:", path_or_err)
            self.update_overlay.setText("Update failed!")
            QTimer.singleShot(2000, self.update_overlay.hide)
            self.launch_button.setEnabled(True)

    def restart_launcher(self):
        exe = sys.executable if getattr(sys, "frozen", False) else os.path.join(app_dir(), "viola_launcher.exe")
        if os.path.exists(exe):
            try:
                subprocess.Popen([exe])
            except Exception as e:
                print("Failed to relaunch:", e)
        self.close()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.drag_pos:
            self.move(event.globalPosition().toPoint() - self.drag_pos)

    def mouseReleaseEvent(self, event):
        self.drag_pos = None

# ---------------- Entry ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ViolaLauncher()
    window.show()
    sys.exit(app.exec())
