from forms.form_edit_ingr import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from sqlite3_requests import update_ingr_gramm_price
from simple_tools import check_price,check_mass
from Custom_Widgets.Widgets import *

class Edit_ingr(QDialog, Ui_Dialog):
    def __init__(self, parent, dish_name, pr_name, pr_gramm, pr_price):
        super().__init__(parent)
        self.setupUi(self)

        self.label_text_error.hide()
        self.label_price_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/edit_ingr/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.edit_ingr)
        self.pushButton_10.clicked.connect(self.close)

        # заполнение заголовка
        self.label.setText(dish_name+": "+pr_name)

        self.lineEdit.setText(pr_gramm[:pr_gramm.find(" ")])
        self.lineEdit_2.setText(pr_price)

        # запомнить переменные
        self.dish_name = dish_name
        self.pr_name = pr_name

        # измерение веса
        self.comboBox.addItem("гр.")
        self.comboBox.addItem("кг.")
        self.comboBox.addItem("мл.")
        self.comboBox.addItem("л.")
        self.comboBox.addItem("ч.л")
        self.comboBox.addItem("ст.л.")
        self.comboBox.addItem("щепотка")

        # задает текущую метрику
        self.comboBox.setCurrentText(pr_gramm[pr_gramm.find(" ") + 1:])

    def edit_ingr(self):

        access = True
        ################
        """стоимость"""
        ################

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

        ################
        """кол-во"""
        ################

        # корректировка
        if self.lineEdit.text() == "":
            self.lineEdit.setText('1')
        elif self.lineEdit.text()[0] == " ":
            self.lineEdit.setText('1')

        # проверка
        checked_mass = check_mass(self.lineEdit.text())
        if not checked_mass[0]:
            self.label_text_error.setText(checked_mass[1])
            self.label_text_error.show()
            access = False
        else:
            self.label_text_error.hide()
            self.label_text_error.clear()

        if access:
            update_ingr_gramm_price(self.dish_name, self.pr_name,
                                    self.lineEdit.text(), self.lineEdit_2.text(), self.comboBox.currentText())

            self.accept()
