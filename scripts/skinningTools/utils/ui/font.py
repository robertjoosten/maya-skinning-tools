from . import Qt

__all__ = [
    "FONT",
    "BOLT_FONT"
]


FONT = Qt.QFont()
FONT.setFamily("Consolas")

BOLT_FONT = Qt.QFont()
BOLT_FONT.setFamily("Consolas")
BOLT_FONT.setWeight(100)  