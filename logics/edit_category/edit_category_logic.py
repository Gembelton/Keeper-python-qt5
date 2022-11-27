from forms.form_edit_category import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor

from sqlite3_requests import update_category
from Custom_Widgets.Widgets import *
from simple_tools import check_text, get_en_color

class EditCategory(QDialog, Ui_Dialog):
    def __init__(self, parent, header, name, color):
        super().__init__(parent)
        self.setupUi(self)


        self.label_text_error.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/add_category/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)


        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.edit_category)
        self.pushButton_10.clicked.connect(self.close)

        # заполнение заголовка
        self.label.setText("Изменение: "+header)

        self.lineEdit.setText(name)

        # Цвета
        self.comboBox.addItem("Черный")
        self.comboBox.addItem("Серый")
        self.comboBox.addItem("Белый")

        self.comboBox.addItem("Коричневый")
        self.comboBox.addItem("Красный")
        self.comboBox.addItem("Оранжевый")
        self.comboBox.addItem("Желтый")

        self.comboBox.addItem("Зеленый")
        self.comboBox.addItem("Св.Зеленый")

        self.comboBox.addItem("Синий")
        self.comboBox.addItem("Голубой")
        self.comboBox.addItem("Бирюзовый")

        self.comboBox.addItem("Фиолетовый")
        self.comboBox.addItem("Розовый")

        self.comboBox.currentIndexChanged.connect(self.change_color)

        # задает текущую метрику
        self.comboBox.setCurrentText(color)
        if color == "Черный":
            self.frame.setStyleSheet("background-color:black;"
                                                                   "border: 2px solid gray;"
                                                                   "border-radius:11px;")

    def change_color(self):
        """Смена цвета"""
        color = get_en_color(self.comboBox.currentText())

        self.frame.setStyleSheet("background-color:" + color + ";"
                                                               "border: 2px solid gray;"
                                                               "border-radius:11px;")

    def edit_category(self):
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


            if access:
                name = self.lineEdit.text().strip()

                update_category(name.lower(), self.label.text()[11:], self.comboBox.currentText())
                self.accept()

        # нарушение требований БД
        except Exception as e:
            if str(e) == "UNIQUE constraint failed: product_category.pr_cat_name":
                self.label_text_error.setText("Название уже используется!")
                self.label_text_error.show()
            elif str(e)[:4] == "near" or str(e)[:4] == "unre":
                self.label_text_error.setText("Уберите символ одной ковычки!")
                self.label_text_error.show()

