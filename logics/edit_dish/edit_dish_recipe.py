from forms.form_edit_dish_recipe import Ui_Dialog
from PyQt5.QtWidgets import QDialog
from sqlite3_requests import update_dish_recipe

from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from Custom_Widgets.Widgets import *


class Edit_dish_recipe(QDialog, Ui_Dialog):
    def __init__(self, parent, header, text, view_mode):
        super().__init__(parent)
        self.setupUi(self)

        self.label_text_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = 600
        dh = 600

        loadJsonStyle(self, self, "logics/edit_dish/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)
        self.label_2.setText("Изменение: " + header)
        # Отключение кнопки принять
        if view_mode:
            self.pushButton_11.hide()
            self.textBrowser.setReadOnly(True)
            dw = 970
            dh = 650
            self.label_2.setText("Просмотр: " + header)

        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.edit_recipe)
        self.pushButton_10.clicked.connect(self.close)

        # заполнение заголовка

        self.textBrowser.setText(text)

    def edit_recipe(self):
        # корректировка
        access = True
        if self.textBrowser.toPlainText() == "":
            self.textBrowser.setText("-")
        elif self.textBrowser.toPlainText()[0] == " ":
            self.textBrowser.setText("-")
        elif self.textBrowser.toPlainText()[0] == "\n":
            self.textBrowser.setText("-")
        elif self.textBrowser.toPlainText()[0] == "\\n":
            self.textBrowser.setText("-")

        # проверка
        if "'" in self.textBrowser.toPlainText():
            self.label_text_error.setText("Уберите ковычки!")
            self.label_text_error.show()
            access = False
        if access:
            update_dish_recipe(self.label_2.text()[11:], self.textBrowser.toPlainText())
            self.accept()
