from forms.form_edit_dish import Ui_Dialog
from PyQt5.QtWidgets import QDialog,QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from sqlite3_requests import update_dish_name_price
from Custom_Widgets.Widgets import *
from simple_tools import check_price,check_text

class Edit_dish(QDialog, Ui_Dialog):
    def __init__(self, parent, header, ds_name, ds_price):
        super().__init__(parent)
        self.setupUi(self)

        self.label_text_error.hide()
        self.label_price_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/edit_dish/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)


        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.edit_dish)
        self.pushButton_10.clicked.connect(self.close)

        # заполнение заголовка
        self.label.setText("Изменение: "+header)

        self.lineEdit.setText(ds_name)
        self.lineEdit_2.setText(ds_price)

    def edit_dish(self):
        try:
            access = True

            ###############
            """стоимость"""
            ###############

            # корректировка
            if self.lineEdit_2.text() == "":
                self.lineEdit_2.setText('0')

            elif self.lineEdit_2.text()[0] == " ":
                self.lineEdit_2.setText('0')

            checked_price = check_price(self.lineEdit_2.text())
            if not checked_price[0]:
                self.label_price_error.setText(checked_price[1])
                self.label_price_error.show()
                access = False
            else:
                self.label_price_error.hide()
                self.label_price_error.clear()

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

            if access:
                name = self.lineEdit.text().strip()
                update_dish_name_price(self.label.text()[11:], self.lineEdit_2.text(), name.lower())
                self.accept()

        # нарушение требований БД
        except Exception as e:
            if str(e) == "UNIQUE constraint failed: dish.ds_name":
                self.label_text_error.show()
                self.label_text_error.setText("Название уже используется!")
            elif str(e)[:4] == "near" or str(e)[:4] == "unre":
                self.label_text_error.show()
                self.label_text_error.setText("Уберите символ одной ковычки!")
            elif str(e)[:2] == "ne" or str(e)[:2] == "no" or \
                            str(e)[:2] == "un":
                self.label_price_error.show()
                self.label_price_error.setText("Запрещен текст и запятые !")
