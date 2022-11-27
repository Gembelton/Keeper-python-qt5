from forms.form_yes_no import Ui_Dialog

from PyQt5.QtWidgets import QDialog,QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from Custom_Widgets.Widgets import *

class Dialog_yes_no(QDialog,Ui_Dialog):

    def __init__(self,parent,header,text):
        super().__init__(parent)
        self.setupUi(self)

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/yes_no/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        #Привязка к кнопкам "да" и "нет"
        self.pushButton_8.clicked.connect(self.accept)
        self.pushButton_9.clicked.connect(self.close)

        #заполнение заголовка
        self.label.setText(header)
        self.setWindowTitle(header)

        #заполнение текста
        self.label_2.setText(text)




