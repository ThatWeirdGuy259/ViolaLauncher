import sys, os, json, threading, time
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtGui import QPainter, QFont
from PyQt6.QtCore import Qt
try:
    import keyboard
except ImportError:
    print("Missing dependency: pip install keyboard")
    sys.exit(1)

CONFIG_FILE = "config.json"

def load_hotkey():
    app_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    cfg_path = os.path.join(app_path, CONFIG_FILE)
    hk = "Right Shift"
    try:
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                hk = data.get("modules_hotkey", hk)
    except Exception:
        pass
    return hk

def normalize_for_keyboard_lib(hk_str: str) -> str:
    s = hk_str.strip().lower()
    mapping = {"right shift":"right shift","left shift":"left shift","shift":"shift",
               "right ctrl":"right ctrl","left ctrl":"left ctrl","ctrl":"ctrl",
               "right alt":"right alt","left alt":"left alt","alt":"alt","enter":"enter",
               "return":"enter","space":"space","tab":"tab","escape":"esc","esc":"esc",
               "backspace":"backspace","delete":"delete","insert":"insert","home":"home",
               "end":"end","page up":"page up","page down":"page down","up":"up","down":"down",
               "left":"left","right":"right","minus":"-","equals":"=","plus":"+","comma":",",
               "period":".","slash":"/","semicolon":";","apostrophe":"'","grave":"`","backtick":"`"}
    if s in mapping: return mapping[s]
    if s.startswith("f") and s[1:].isdigit(): return s
    if len(s)==1: return s
    return s

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
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
        self.items = ["• Keystrokes / CPS / FPS","• Coordinates HUD","• Zoom",
                      "• ToggleSprint / ToggleSneak","• Armor / Potions / Packs"]
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
        rect = self.rect().adjusted(0,0,-1,-1)
        painter.setBrush(Qt.GlobalColor.black)
        painter.setOpacity(0.65)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(rect, 20, 20)
        painter.setOpacity(1.0)

def hotkey_listener(toggle_callback, hk_display: str):
    hk = normalize_for_keyboard_lib(hk_display)
    print(f"[Viola Overlay] Listening for hotkey: {hk_display}  (normalized: '{hk}')")
    try:
        import keyboard
        keyboard.add_hotkey(hk, toggle_callback, suppress=False, trigger_on_release=False)
    except Exception as e:
        print("Failed to bind hotkey:", e)
    while True: time.sleep(0.25)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = OverlayWindow()
    overlay.hide()
    def toggle_overlay():
        if overlay.isVisible(): overlay.hide()
        else: overlay.show()
    chosen = load_hotkey()
    t = threading.Thread(target=hotkey_listener, args=(toggle_overlay, chosen), daemon=True)
    t.start()
    sys.exit(app.exec())
