from forms.form_insert_in_category import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from sqlite3_requests import update_product_cat, get_info_table,get_table_column
from Custom_Widgets.Widgets import *

from simple_tools import get_en_color

class InsertInCategory(QDialog, Ui_Dialog):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.name = name
        self.setupUi(self)

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/insert_pr_to_cat/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.edit_product)
        self.pushButton_10.clicked.connect(self.close)

        self.comboBox_2.currentIndexChanged.connect(self.change_color)

        # заполнение заголовка
        self.label.setText("Поместить: "+name)

        # измерение веса
        info_table = get_info_table("product_category")
        if info_table != []:
            for i, tuple in enumerate(info_table):
                self.comboBox_2.addItem(str(tuple[1]))

    def edit_product(self):
        update_product_cat(self.name, self.comboBox_2.currentText())
        self.accept()

    def change_color(self):
        """Смена цвета"""
        color = get_en_color(
            get_table_column(
                "product_category", "pr_cat_color", "pr_cat_name", self.comboBox_2.currentText()))

        self.frame_9.setStyleSheet("background-color:" + color + ";"
                                                                 "border: 2px solid gray;"
                                                                 "border-radius:11px;")