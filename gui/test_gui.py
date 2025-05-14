#!/usr/bin/env python3
import sys, time, serial
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel
from serial.tools import list_ports      

# ------------------------------------------------------------------ #
# 0. Sub‑class that re‑emits the moment the popup is about to open
class DynamicCombo(QComboBox):
    popupAboutToBeShown = pyqtSignal()          # <- custom signal

    # call order: Qt → showPopup() → (our emit) → super() → dropdown opens
    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super().showPopup()

###############################################################################
# 1. A tiny QThread that owns the pyserial object so the GUI never blocks
###############################################################################
class SerialWorker(QThread):
    list_received = pyqtSignal(list)        # emits ["A", "B", "C"]
    error        = pyqtSignal(str)

    def __init__(self, port=None, baudrate=115200, parent=None):   # port now defaults to None
        super().__init__(parent)

        # ---------- Pick the first port automatically ----------
        if port is None:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                raise RuntimeError("No serial ports found.")
            port = ports[0].device            # e.g. 'COM5' or '/dev/ttyUSB0'

        self._port     = port
        self._baudrate = baudrate
        self._ser      = None
        self._wanted_list  = False          # set True when GUI asks for list
        self._to_send      = None           # holds a str to send
        self._running      = True

    # --------------------------------------------------------------------- #
    # public slots callable from GUI thread
    @pyqtSlot()
    def request_list(self):
        self._wanted_list = True

    @pyqtSlot(str)
    def send_item(self, text):
        self._to_send = text

    # --------------------------------------------------------------------- #
    def run(self):
        try:
            self._ser = serial.Serial(self._port, self._baudrate, timeout=1)
        except serial.SerialException as e:
            self.error.emit(f"Serial open failed: {e}")
            return

        while self._running:
            # --------------------------------------------------------- #
            # 1) Was a list requested?
            if self._wanted_list:
                try:
                    self._ser.write(b"list_csv_files\n")
                except serial.SerialException as e:
                    self.error.emit(f"Write failed: {e}")
                self._wanted_list = False

            # --------------------------------------------------------- #
            # 2) Do we have data waiting?
            try:
                if self._ser.in_waiting:
                    line = self._ser.readline().decode(errors="ignore").strip()
                    # Expect a single comma‑separated line
                    if line:
                        items = [s.strip() for s in line.split(",") if s.strip()]
                        self.list_received.emit(items)
            except serial.SerialException as e:
                self.error.emit(f"Read failed: {e}")

            # --------------------------------------------------------- #
            # 3) Is there an item to echo back?
            if self._to_send:
                try:
                    self._ser.write((self._to_send + "\n").encode())
                except serial.SerialException as e:
                    self.error.emit(f"Write failed: {e}")
                self._to_send = None

            time.sleep(0.05)   # don’t burn CPU

        # graceful shutdown
        if self._ser and self._ser.is_open:
            self._ser.close()

    def stop(self):
        self._running = False
        self.wait()

###############################################################################
# 2. The simple GUI
###############################################################################
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arduino List Demo")
        self.resize(300, 120)

        self.combo  = DynamicCombo()
        self.combo.addItem("‑‑ click to load from Arduino ‑‑")
        self.combo.view().window().setWindowFlags(                     # optional:
            self.combo.view().window().windowFlags() | Qt.Popup)       # show as popup

        self.status = QLabel("Status: idle")
        self.status.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.combo)
        layout.addWidget(self.status)

        # ---------------- Serial thread ---------------- #
        self.worker = SerialWorker(port='/dev/ttyACM0', baudrate=115200)
        self.worker.list_received.connect(self.populate_combo)
        self.worker.error.connect(self.show_error)
        self.worker.start()

        # intercept “about to show” to trigger request_list()
        self.combo.popupAboutToBeShown.connect(self.ask_for_list)
        # send chosen item back
        self.combo.activated[str].connect(self.worker.send_item)

    # -------------------------------------------------- #
    @pyqtSlot()
    def ask_for_list(self):
        self.status.setText("Status: requesting list …")
        self.worker.request_list()

    # -------------------------------------------------- #
    @pyqtSlot(list)
    def populate_combo(self, items):
        self.combo.clear()
        self.combo.addItems(items)
        self.status.setText("Status: list updated")

    # -------------------------------------------------- #
    @pyqtSlot(str)
    def show_error(self, msg):
        self.status.setText(f"Error: {msg}")

    # -------------------------------------------------- #
    def closeEvent(self, event):
        self.worker.stop()
        event.accept()

###############################################################################
# 3. Run it
###############################################################################
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w   = MainWindow()
    w.show()
    sys.exit(app.exec_())
