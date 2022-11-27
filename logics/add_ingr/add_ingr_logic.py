from forms.form_add_ingr import Ui_Dialog
from PyQt5.QtWidgets import QDialog, QGraphicsDropShadowEffect, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QColor

from sqlite3_requests import get_info_table, add_dish_ingr, get_table_column

from logics.add_product.add_product_logic import AddProduct

from simple_tools import remove_dot_zero_from_end, check_price, get_en_color, check_mass
from Custom_Widgets.Widgets import *


class Add_ingr(QDialog, Ui_Dialog):
    def __init__(self, parent, header, list_of_included_ingr):
        super().__init__(parent)
        self.setupUi(self)

        self.label_8.hide()
        self.label_9.hide()

        ph = self.parent().geometry().height()
        pw = self.parent().geometry().width()
        dw = self.width()
        dh = self.height()
        self.setGeometry(int((pw - dw) / 2), int((ph - dh) / 2), dw, dh)
        loadJsonStyle(self, self, "logics/add_ingr/")

        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(2)
        glow.setXOffset(2)
        glow.setBlurRadius(25)
        glow.setColor(QColor(0, 0, 0))

        self.setGraphicsEffect(glow)

        # Список ингр., которые надо вычесть
        # чтобы не добавить, что уже есть
        self.list_of_included_ingr = list_of_included_ingr

        # Словарь заморозки состояний
        self.active_items_dict = {}

        # Подготовить заголовки таблицы продуктов

        self.set_product_table_headers()

        # Заполнить таблицу продуктов
        self.fill_product_table()

        # заполнить заголовок
        self.label_5.setText(header)

        # При выборе продукта
        self.tableWidget.clicked.connect(self.change_pr_info)

        # Привязка к кнопкам "да" и "нет"
        self.pushButton_11.clicked.connect(self.add_ingr)
        self.pushButton_10.clicked.connect(self.close)

        # Привязка к новой форме | быстрое добавление блюда
        self.pushButton_12.clicked.connect(self.fast_add_pr)

        # измерение веса
        self.comboBox.addItem("гр.")
        self.comboBox.addItem("кг.")
        self.comboBox.addItem("мл.")
        self.comboBox.addItem("л.")
        self.comboBox.addItem("ч.л")
        self.comboBox.addItem("ст.л.")
        self.comboBox.addItem("щепотка")

        self.comboBox_2.currentIndexChanged.connect(self.set_product_table_headers)
        self.comboBox_2.currentIndexChanged.connect(self.fill_product_table)

        self.radioButton.clicked.connect(self.enable_cat_sort)

        if get_info_table("product_category") == []:
            self.radioButton.setEnabled(False)

        else:
            self.radioButton.setEnabled(True)

    def enable_cat_sort(self):
        """Включение сортировки по категории"""
        if self.radioButton.isChecked():
            self.comboBox_2.setEnabled(True)

            info_table = get_info_table("product_category")

            if info_table != []:

                for tuple in info_table:
                    self.comboBox_2.addItem(str(tuple[1]))

        else:
            self.comboBox_2.setEnabled(False)

            self.comboBox_2.clear()

        self.set_product_table_headers()
        self.fill_product_table()

    def set_product_table_headers(self):
        # получаем длину строки и вычитаем 1 столбец (где айди) и описание
        # Получаем кол-во всех строк минус кол-во повторений

        # обнуление
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)

        info_table = get_info_table("product")

        if self.radioButton.isChecked() and self.comboBox_2.currentText():
            category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                           self.comboBox_2.currentText())
        else:
            category_id = None

        count = 0  # кол-во блюд по категории
        for tuple in info_table:
            if tuple[5] == category_id:
                count += 1

        if info_table != []:
            columns_count = len(info_table[0])
            if not self.radioButton.isChecked():
                columns_count += 1
                rows_count = len(info_table) - len(self.list_of_included_ingr)
            else:

                new_count = 0

                for name in self.list_of_included_ingr:
                    # берем по имени все включенные продукты

                    pr_cat_id = get_table_column("product", "pr_cat_id", "pr_name", name)
                    if pr_cat_id:
                        pr_cat_name = get_table_column("product_category", "pr_cat_name", "pr_cat_id", pr_cat_id)
                    else:
                        pr_cat_name = ""
                    # получаем категорию каждого продукта
                    if pr_cat_name == self.comboBox_2.currentText():
                        new_count += 1  # считаю совпадения с текущей категорией в имеющихся ингридиентах

                rows_count = count - new_count
                columns_count = len(info_table[0])

            # задаем строки и столбцы
            self.tableWidget.setColumnCount(columns_count - 3)
            self.tableWidget.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                self.tableWidget.setVerticalHeaderItem(i, item)
                self.tableWidget.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(0, item)
            self.tableWidget.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(2, item)
            self.tableWidget.horizontalHeaderItem(2).setText("Руб.")

            item = QTableWidgetItem()
            self.tableWidget.setHorizontalHeaderItem(1, item)
            self.tableWidget.horizontalHeaderItem(1).setText("Масса")

            if not self.radioButton.isChecked():
                # задаем строки и столбцы
                item = QTableWidgetItem()
                self.tableWidget.setHorizontalHeaderItem(3, item)
                self.tableWidget.horizontalHeaderItem(3).setText("Категория")

    def frozen(self, freeze):
        """Заморозка элементов главной формы"""
        if freeze:
            for name, obj in dict(self.__dict__).items():
                if (name[:10] == 'pushButton' or
                            name[:11] == 'tableWidget' or
                            name[:11] == "radioButton" or
                            name[:8] == "lineEdit" or
                            name[:8] == "comboBox") \
                        and type(obj) != int:
                    self.active_items_dict[obj] = obj.isEnabled()
                    obj.setEnabled(False)
            self.close_window_button.setEnabled(False)
            # Логика окраски формы
            # !!!!
        else:
            for obj in self.active_items_dict:
                obj.setEnabled(self.active_items_dict[obj])
            self.close_window_button.setEnabled(True)

    def fast_add_pr(self):
        """Быстрое добавление продукта"""
        dialog = AddProduct(self)

        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            # Подготовить заголовки таблицы продуктов
            self.set_product_table_headers()

            # Заполнить таблицу продуктов
            self.fill_product_table()

            # Выделить новый продукт
            self.tableWidget.selectRow(self.tableWidget.rowCount() - 1)

            self.change_pr_info()
        self.frozen(False)

    def fill_product_table(self):
        """Заполняет таблицу"""

        list_of_new_ingr = get_info_table("product")
        category_id = ""

        if list_of_new_ingr != []:
            # вычитает повторяющие элементы
            list_of_new_ingr = [tuple for tuple in list_of_new_ingr
                                if str(tuple[1]) not in self.list_of_included_ingr]  # память 2

            if self.radioButton.isChecked():
                category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                               self.comboBox_2.currentText())
            # заполняет по порядку
            f = 0

            for i, tuple in enumerate(list_of_new_ingr):
                if self.radioButton.isChecked() and tuple[5] != category_id:

                    continue
                else:

                    id = tuple[0]
                    pr_cat_id = get_table_column("product", "pr_cat_id", "pr_id", id)

                    linear_gradient = None

                    try:
                        color = get_table_column("product_category", "pr_cat_color", "pr_cat_id", pr_cat_id)
                        linear_gradient = QtGui.QLinearGradient()
                        linear_gradient.setStart(0, 0)
                        linear_gradient.setFinalStop(0, 150)

                        linear_gradient.setColorAt(0, QColor("Transparent"))
                        linear_gradient.setColorAt(1, QColor(get_en_color(color)))
                    except:
                        color = False

                    # заполняет первый столбец
                    item = QTableWidgetItem()
                    if color: item.setBackground(linear_gradient)
                    self.tableWidget.setItem(f, 0, item)
                    self.tableWidget.item(f, 0).setText(str(tuple[1]))

                    # заполняет третий столбец
                    item = QTableWidgetItem()
                    if color: item.setBackground(linear_gradient)
                    self.tableWidget.setItem(f, 1, item)
                    self.tableWidget.item(f, 1).setText(remove_dot_zero_from_end(str(tuple[3])) + " " + str(tuple[4]))

                    # заполняет второй столбец
                    item = QTableWidgetItem()
                    if color: item.setBackground(linear_gradient)
                    self.tableWidget.setItem(f, 2, item)
                    self.tableWidget.item(f, 2).setText(remove_dot_zero_from_end(str(tuple[2])))

                    if not self.radioButton.isChecked():
                        # заполняет четвертый столбец
                        item = QTableWidgetItem()
                        if color: item.setBackground(linear_gradient)
                        self.tableWidget.setItem(f, 3, item)
                        if not tuple[5]:

                            self.tableWidget.item(f, 3).setText("-")
                        else:
                            name = get_table_column("product_category", "pr_cat_name", "pr_cat_id", tuple[5])
                            self.tableWidget.item(f, 3).setText(str(name))
                    f += 1

            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)

    def add_ingr(self):
        try:
            access = True
            ################
            """стоимость"""
            ################

            # корректировка
            if self.lineEdit_3.text() == "":
                self.lineEdit_3.setText('0')
            elif self.lineEdit_3.text()[0] == " ":
                self.lineEdit_3.setText('0')

            # проверка
            checked_price = check_price(self.lineEdit_3.text())
            if not checked_price[0]:
                self.label_9.setText(checked_price[1])
                self.label_9.show()
                access = False
            else:
                self.label_9.hide()
                self.label_9.clear()

            ################
            """кол-во"""
            ################

            # корректировка
            if self.lineEdit_2.text() == "":
                self.lineEdit_2.setText('1')
            elif self.lineEdit_2.text()[0] == " ":
                self.lineEdit_2.setText('1')

            # проверка
            checked_mass = check_mass(self.lineEdit_2.text())
            if not checked_mass[0]:
                self.label_8.setText(checked_mass[1])
                self.label_8.show()
                access = False
            else:
                self.label_8.hide()
                self.label_8.clear()

            if access:
                add_dish_ingr(self.label_5.text(), self.label_4.text(),
                              self.lineEdit_3.text(), self.lineEdit_2.text(), self.comboBox.currentText())
                self.accept()

        # нарушение требований БД
        except Exception as e:
            print(e, "dada", "add_ingr_logic_bug")

    def change_pr_info(self):
        """Меняет содержание под продукт"""
        # вынимает необходимую инфу из столбца с названием
        pr_name = self.tableWidget.selectedItems()[0].text()
        self.label_4.setText(pr_name)

        # включение кнопок и полей
        self.pushButton_10.setEnabled(True)
        self.pushButton_11.setEnabled(True)
        self.lineEdit_2.setEnabled(True)
        self.lineEdit_3.setEnabled(True)
