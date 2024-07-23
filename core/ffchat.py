from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor, QPainter
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy, QGraphicsOpacityEffect, QApplication, QLabel
from typing import Tuple, Optional, Union
import sys, os
from src.color_converter import ColorConverter, OutputColor

os.environ['QT_IM_MODULE'] = 'fcitx5'
N = ColorConverter.Num
ANY_RGB = Union[str, Tuple[N,N,N]]


class FloatingFFLabel(QLabel):
    def __init__(self, label: str, parent):
        super().__init__(label, parent)
        # self.adjustSize() 
        self.setVisible(False)

    def relocate(self, *, size: Optional[Tuple[int, int]] = None, pos: Optional[Tuple[int, int]] = None) -> None:
        if size is not None:
            self.setFixedSize(*size)
        if pos is not None:
            self.move(*pos)


class TranslucentWidget(QWidget):

    DEFAULT_ALPHA = 128

    def __init__(self, rgba: Union[str, Tuple[N,N,N,N], Tuple[N,N,N]], global_opacity: Union[float, int] = 1.0):
        super().__init__()

        if isinstance(global_opacity, int):
            global_opacity = ColorConverter.int_to_float(global_opacity)

        self._rgba = ColorConverter.convert(rgba, OutputColor.RGBA, "I")

        # Inicializar variables
        self._global_opacity = global_opacity

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Aplicar opacidad a todo el widget
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(opacity_effect)
        self.setAutoFillBackground(True)

    def paintEvent(self, event):
        # Draw translucent (or not) background
        painter = QPainter(self)
        painter.setBrush(QColor(*self._rgba))
        painter.drawRect(self.rect())

        # Call parent to draw everything else
        super().paintEvent(event)

    def relocate(self, size: Tuple[int, int], pos: Tuple[int, int]) -> None:
        self.setFixedSize(*size)
        self.move(*pos)


class FFChat(TranslucentWidget):
    def __init__(self):
        super().__init__((10,10,10,0.70), 1.0)
        self.initUI()

    def initUI(self):
        # Configuración de la ventana
        self.setWindowTitle('FFChat')

        # Input
        self.ff_input = QLineEdit(self)
        self.ff_input.setPlaceholderText('ここに入力してください')
        self.ff_input.setFixedHeight(80)
        self.ff_input.setFont(QFont("Noto Sans CJK", 16))
        self.ff_input.setStyleSheet("""
        QLineEdit
        {
            border: none;
            background: rgba(0,0,0,0.3);
            padding: 20px;
        }
        QLineEdit:hover {
            border: none;
        }
        QLineEdit:focus {
            border: none;
        }
        """)
        palette = self.ff_input.palette()
        palette.setColor(QPalette.ColorRole.PlaceholderText, QColor(190,190,190))
        palette.setColor(QPalette.ColorRole.Text, QColor(235,235,235))
        self.ff_input.setPalette(palette)

        # Label (la apendamos al input)
        self.ff_label = FloatingFFLabel("FFチャット (alpha 0.1)", self.ff_input)
        self.ff_label.setFont(QFont("Noto Sans CJK", 10))
        self.adjustSize() 
        self.ff_label.setVisible(True) 
        self.ff_label.setStyleSheet("""
        QLabel
        {
            color: rgba(230,230,230, 0.7);
        }
        """)

        # Layouts 
        layout = QVBoxLayout()
        layout_horizontal = QHBoxLayout()
        
        # layout secundario (horizontal)
        layout_horizontal.addItem(QSpacerItem(40, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout_horizontal.addWidget(self.ff_input)
        layout_horizontal.addItem(QSpacerItem(40, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        layout_horizontal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_horizontal.setContentsMargins(0, 0, 0, 0)
        layout_horizontal.setSpacing(0)
        
        # layout principal (vertical) 
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addLayout(layout_horizontal)

        self.setLayout(layout)

    def relocate(self, *, size: Optional[Tuple[int, int]] = None, pos: Optional[Tuple[int, int]] = None) -> None:
        if size is not None:
            self.setFixedSize(*size)
        if pos is not None:
            self.move(*pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        self.updateLabel()

    def updateLabel(self):
        # Hidde/Show
        ffsize = self.size()

        if ffsize.height() < 120:
            self.ff_label.setVisible(False)
            return
        else:
            self.ff_label.setVisible(True)

        # Position
        fflabelsize = self.ff_label.size()
        label_rtpos = (ffsize.width() - fflabelsize.width(), 0)
        label_pos = (label_rtpos[0] - 97, 6)
        self.ff_label.relocate(pos=label_pos)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    chat_window = FFChat()
    chat_window.relocate(pos=(510, 600), size=(900, 160))
    label_size = chat_window.ff_label.size()
    chat_window.show()
    sys.exit(app.exec())


