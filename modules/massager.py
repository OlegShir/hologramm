from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import QTimer

class MSGLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setGeometry(20,670,600,16)

        # Установка настроек таймера
        self.timer = QTimer()
        self.current_duration = 0
        self.timer.timeout.connect(self.hideText)
        
        self.color_codes:dict = {
                            "b": "black",
                            "r": "red",
                            "y": "yellow",
                           }


        # Установка настроек шрифта
        font = QFont()
        font.setPointSize(10)  # Размер шрифта
        font.setWeight(QFont.Bold)  # Жирность шрифта
        self.setFont(font)
    
    def set_text(self, text: str, color = "b", duration: int = 2000):
        # Преобразование цвета в формат QColor
        qcolor = QColor(self.color_codes.get(color, "b"))
        # Установка цвета текста
        self.setStyleSheet(f"color: {qcolor.name()};")
        self.setText(text)
        self.current_duration = duration
        self.timer.start(duration)
 
    def hideText(self):
        self.setText('')
        self.current_duration = 0
        self.timer.stop()