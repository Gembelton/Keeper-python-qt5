from forms.form_add_dish import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor
from sqlite3_requests import add_dish
from Custom_Widgets.Widgets import *
from simple_tools import check_text, check_price


class Add_dish(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.label_text_error.hide()
        self.label_price_error.hide()
        self.label_recipe_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/add_dish/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.add_dish)
        self.pushButton_10.clicked.connect(self.close)

    def add_dish(self):
        try:
            access = True

            ###############
            """название"""
            ###############

            # проверка
            checked_text = check_text(self.lineEdit.text())
            if not checked_text[0]:
                self.label_text_error.setText(checked_text[1])
                self.label_text_error.show()
                access = False
            else:
                self.label_text_error.hide()
                self.label_text_error.clear()

            ###############
            """рецепт"""
            ###############

            # корректировка
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
                self.label_recipe_error.setText("Уберите ковычки!")
                self.label_recipe_error.show()
                access = False
            else:
                self.label_recipe_error.hide()
                self.label_recipe_error.clear()
            ###############
            """стоимость"""
            ###############

            # корректировка
            if self.lineEdit_2.text() == "":
                self.lineEdit_2.setText('0')
            elif self.lineEdit_2.text()[0] == " ":
                self.lineEdit_2.setText('0')

            # проверка
            checked_price = check_price(self.lineEdit_2.text())
            if not checked_price[0]:
                self.label_price_error.setText(checked_price[1])
                self.label_price_error.show()
                access = False
            else:
                self.label_price_error.hide()
                self.label_price_error.clear()

            if access:
                name = self.lineEdit.text().strip()
                add_dish(name.lower(), self.lineEdit_2.text(), self.textBrowser.toPlainText())
                self.accept()

        # нарушение требований БД
        except Exception as e:
            if str(e) == "UNIQUE constraint failed: dish.ds_name":
                self.label_text_error.show()
                self.label_text_error.setText("Название уже используется!")
            elif str(e)[:4] == "near" or str(e)[:4] == "unre":
                self.label_price_error.show()
                self.label_text_error.setText("Уберите символ одной ковычки!")
            print(e)