from forms.form_add_product import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from sqlite3_requests import add_product, get_info_table, get_table_column
from Custom_Widgets.Widgets import *
from simple_tools import check_text, check_price,get_en_color,check_mass


class AddProduct(QDialog, Ui_Dialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.label_text_error.hide()
        self.label_8.hide()
        self.label_price_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/add_product/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.add_product)
        self.pushButton_10.clicked.connect(self.close)

        # измерение веса
        self.comboBox.addItem("гр.")
        self.comboBox.addItem("кг.")
        self.comboBox.addItem("мл.")
        self.comboBox.addItem("л.")
        self.comboBox.addItem("ч.л")
        self.comboBox.addItem("ст.л.")
        self.comboBox.addItem("щепотка")
        self.comboBox_2.currentIndexChanged.connect(self.change_color)
        self.change_color()

        self.radioButton.clicked.connect(self.enable_categories)

        if get_info_table("product_category") == []:
            self.radioButton.setEnabled(False)

        else:
            self.radioButton.setEnabled(True)

    def change_color(self):
        """Смена цвета"""
        if self.radioButton.isChecked():
            color = get_en_color(
                get_table_column(
                    "product_category", "pr_cat_color", "pr_cat_name", self.comboBox_2.currentText()))


            self.frame_9.setStyleSheet("background-color:" + color + ";"
                                                                     "border: 2px solid gray;"
                                                                     "border-radius:11px;")


    def enable_categories(self):
        if self.radioButton.isChecked():
            self.comboBox_2.setEnabled(True)
            info_table = get_info_table("product_category")
            if info_table != []:
                for i, tuple in enumerate(info_table):
                    self.comboBox_2.addItem(str(tuple[1]))
        else:
            self.comboBox_2.setEnabled(False)
            self.comboBox_2.clear()
            self.frame_9.setStyleSheet("background-color:#c8d0ab;"
                                       "border: 2px solid gray;"
                                       "border-radius:11px;")

    def add_product(self):
        try:
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
            if self.lineEdit_3.text() == "":
                self.lineEdit_3.setText('1')
            elif self.lineEdit_3.text()[0] == " ":
                self.lineEdit_3.setText('1')

            # проверка
            checked_mass = check_mass(self.lineEdit_3.text())
            if not checked_mass[0]:
                self.label_8.setText(checked_mass[1])
                self.label_8.show()
                access = False
            else:
                self.label_8.hide()
                self.label_8.clear()

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
                cat = self.comboBox_2.currentText() if self.radioButton.isChecked() else False
                name = self.lineEdit.text().strip()

                add_product(name.lower(), self.lineEdit_2.text(), self.lineEdit_3.text(), self.comboBox.currentText(),
                            cat)
                self.accept()

        # нарушение требований БД
        except Exception as e:
            if str(e) == "UNIQUE constraint failed: product.pr_name":
                self.label_text_error.show()
                self.label_text_error.setText("Название уже используется!")
            elif str(e)[:4] == "near" or str(e)[:4] == "unre":
                self.label_text_error.show()
                self.label_text_error.setText("Уберите символ одной ковычки!")
