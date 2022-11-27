import sys
import time

from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QGraphicsDropShadowEffect
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QColor, QGradient

from forms.form_main import Ui_MainWindow

from logics.yes_no.yes_no_logic import Dialog_yes_no
from logics.edit_dish.edit_dish_name_price import Edit_dish
from logics.edit_dish.edit_dish_recipe import Edit_dish_recipe
from logics.add_ingr.add_ingr_logic import Add_ingr
from logics.edit_ingr.edit_ingr_logic import Edit_ingr
from logics.add_dish.add_dish_logic import Add_dish
from logics.edit_product.edit_product_logic import EditProduct
from logics.add_product.add_product_logic import AddProduct
from logics.add_category.add_category_logic import AddCategory
from logics.edit_category.edit_category_logic import EditCategory
from logics.insert_pr_to_cat.insert_in_category_logic import InsertInCategory

from languages.Eng import Eng
from languages.Rus import Rus

from sqlite3_requests import get_info_table, \
    get_table_column, \
    get_all_pr_id_from_consistance_dish, \
    delete_table_row, \
    delete_ingridient_row, \
    get_consistance_dish, \
    get_all_ds_id_from_consistance_dish, \
    get_dishes_by_product, \
    update_product_cat

from simple_tools import remove_dot_zero_from_end, get_en_color
from Custom_Widgets.Widgets import *


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        # Подгрузка интерфейса
        self.setupUi(self)
        loadJsonStyle(self, self)

        # Корректировки перед запуском программы
        self.correct_ui_before_run()

        # Заполнение заголовков таблицы |блюд, продуктов, категории
        self.setTableHeaders_dish()
        self.setTableHeaders_product()
        self.setTableHeaders_category()

        # Добавление инфы в таблицу |блюд, продуктов, категории
        self.fillTable_dishes()
        self.fillTable_product()
        self.fillTable_category()

        # привязка к нажатию в таблице |блюд
        self.tableWidget_dishes.clicked.connect(self.change_dish_info)
        self.tableWidget_dishes.clicked.connect(lambda: self.enable_disable_dish_buttons(True))

        # QtGui.QFont().setBold(True)

        # self.tableWidget_dishes.clicked.connect(lambda: self.tableWidget_dishes.selectedItems()[0].setFont(QtGui.QFont().setBold(True)))

        # привязка к нажатию в таблице |продуктов
        self.tableWidget_products.clicked.connect(self.change_product_info)
        self.tableWidget_products.clicked.connect(lambda: self.enable_disable_product_buttons(True))

        # Привязка к нажатию в таблице |ингридиенты
        self.tableWidget_ingr.clicked.connect(lambda: self.enable_disable_ingr_buttons(True))
        self.tableWidget_dishes.clicked.connect(lambda: self.enable_disable_ingr_buttons(False))

        # Привязка к нажатию в таблице |продукты + вкл.блюда
        # !!!!
        self.tableWidget_products.clicked.connect(lambda: self.enable_disable_ds_buttons(False))
        self.tableWidget_ingr_in_dishes.clicked.connect(lambda: self.enable_disable_ds_buttons(True))

        # привязка к нажатию в таблице |Категория
        self.tableWidget_categories.clicked.connect(lambda: self.enable_disable_category_buttons(True))

        # текущий индекс выбранного элемента в таблицах
        self.tableWidget_current_index = 0
        self.tableWidget_ingr_current_index = 0
        self.tableWidget_products_current_index = 0
        self.tableWidget_ingr_in_dishes_current_index = 0
        self.tableWidget_categories_current_index = 0

        # Словарь виджетов для сохранния состояния ( морозка)
        self.active_items_dict = {}

        # Кнопка изменения, удаления и добавления |блюд
        self.pushButton_delete_dish.clicked.connect(self.delete_dish)
        self.pushButton_edit_dish.clicked.connect(self.edit_dish)
        self.pushButton_edit_recipe.clicked.connect(lambda: self.edit_dish_recipe(False))
        self.pushButton_look_recipe.clicked.connect(lambda: self.edit_dish_recipe(True))
        self.pushButton_add_dish.clicked.connect(self.add_dish)

        # Кнопка изменения и удаления |Ингридиентов
        self.pushButton_edit_ingr.clicked.connect(self.edit_ingr)
        self.pushButton_delete_ingr.clicked.connect(self.delete_ingridient)
        self.pushButton_add_ingr.clicked.connect(self.add_ingr)

        # кнопки добавления, изменения и удаления | Продуктов
        self.pushButton_delete_product.clicked.connect(self.delete_product)
        self.pushButton_edit_product.clicked.connect(self.edit_product)
        self.pushButton_add_product.clicked.connect(self.add_product)
        self.pushButton_add_to_cat.clicked.connect(self.add_replace_pr_to_cat)

        # кнопки добавления, изменения и удаления | Категории
        self.pushButton_add_category.clicked.connect(self.add_category)
        self.pushButton_edit_category.clicked.connect(self.edit_category)
        self.pushButton_delete_category.clicked.connect(self.delete_category)
        self.pushButton_remove_from_cat.clicked.connect(self.remove_pr_from_cat)

        # кнопки изменения и удаления | Продуктов в блюдах
        self.pushButton_delete_ingr_in_dish.clicked.connect(self.delete_product_from_dish)
        self.pushButton_edit_ingr_in_dish.clicked.connect(self.edit_product_in_dish)

        # Кнопка смены языка
        self.pushButton_info_3.clicked.connect(self.change_language)

        # обнулить на вкладках
        self.tabWidget.currentChanged.connect(self.pages_change)

        # включение сортировки по нажатию галочки | продукты, категория
        self.radioButton_enable_cat_filter.clicked.connect(self.enable_cat_sort)
        self.comboBox_categories.currentIndexChanged.connect(self.setTableHeaders_product)
        self.comboBox_categories.currentIndexChanged.connect(self.fillTable_product)
        self.comboBox_categories.currentIndexChanged.connect(lambda: self.enable_disable_product_buttons(False))

        # Кнопки вызова меню слева
        self.pushButton_dishes.clicked.connect(lambda: self.set_page("dishes"))
        self.pushButton_products.clicked.connect(lambda: self.set_page("product"))
        self.pushButton_categories.clicked.connect(lambda: self.set_page("category"))
        self.pushButton_info.clicked.connect(lambda: self.set_page("info"))

    def correct_ui_before_run(self):
        """Корректировка перед запуском программы"""
        self.tabWidget.tabBar().hide()
        self.set_page("dishes")

    def set_page(self, page_name):
        """меняет меню в соответствие с кнопкой"""
        glow = QGraphicsDropShadowEffect(self)
        glow.setYOffset(1)
        glow.setXOffset(1)
        glow.setBlurRadius(4)
        glow.setColor(QColor(0, 0, 0))

        self.pushButton_dishes.setGraphicsEffect(None)
        self.pushButton_products.setGraphicsEffect(None)
        self.pushButton_categories.setGraphicsEffect(None)
        self.pushButton_info.setGraphicsEffect(None)
        new_css = "*{background-color:" \
                  "#FBFFD8;" \
                  "border-radius: 20px;border:" \
                  " 0px solid black;Text-align:" \
                  "left;padding-left:10px;font-size:" \
                  " 12px;}"

        old_css = "*{background-color:" \
                  " qlineargradient(spread:pad, " \
                  "x1:0, y1:0, x2:1, y2:0, stop:0 " \
                  "rgba(207, 208, 176, 255), stop:1" \
                  " rgba(200, 207, 168, 255));" \
                  "border-radius: 20px;border:" \
                  " 0px solid black;Text-align:" \
                  "left;padding-left:10px;font-size:" \
                  " 12px;}:hover{background-color:" \
                  " #E1E5C3;border-radius: 20px;border:" \
                  " 0px solid black;Text-align:left;" \
                  "padding-left:10px;font-size: 12px;}"

        self.pushButton_categories.setStyleSheet(old_css)
        self.pushButton_dishes.setStyleSheet(old_css)
        self.pushButton_products.setStyleSheet(old_css)
        self.pushButton_info.setStyleSheet(old_css)

        if page_name == "dishes":
            self.tabWidget.setCurrentIndex(0)
            self.pushButton_dishes.setGraphicsEffect(glow)
            self.pushButton_dishes.setStyleSheet(new_css)

        elif page_name == "product":
            self.tabWidget.setCurrentIndex(1)
            self.pushButton_products.setGraphicsEffect(glow)
            self.pushButton_products.setStyleSheet(new_css)
        elif page_name == "category":
            self.tabWidget.setCurrentIndex(2)
            self.pushButton_categories.setGraphicsEffect(glow)
            self.pushButton_categories.setStyleSheet(new_css)

        elif page_name == "info":
            self.tabWidget.setCurrentIndex(3)
            self.pushButton_info.setGraphicsEffect(glow)
            self.pushButton_info.setStyleSheet(new_css)

    def remove_pr_from_cat(self):
        """Меняет категорию продукта"""
        cur_name = self.tableWidget_products.selectedItems()[0].text()
        if self.radioButton_enable_cat_filter.isChecked():
            cat = self.comboBox_categories.currentText()
        else:
            cat = self.tableWidget_products.selectedItems()[3].text()

        dialog = Dialog_yes_no(self, "Убрать", cur_name + " из " + cat)

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            update_product_cat(cur_name, None)
            self.setTableHeaders_product()
            self.fillTable_product()

        self.frozen(False)

    def enable_cat_sort(self):
        """Включение сортировки по категории"""
        if self.radioButton_enable_cat_filter.isChecked():
            # Очистка встречаний в блюдах ингридиента
            self.tableWidget_ingr_in_dishes.setColumnCount(0)
            self.tableWidget_ingr_in_dishes.setRowCount(0)
            self.tableWidget_ingr_in_dishes.clear()
            self.enable_disable_ds_buttons(False)

            # включение комбобокса
            self.comboBox_categories.setEnabled(True)

            info_table = get_info_table("product_category")
            if info_table != []:
                for i, tuple in enumerate(info_table):
                    self.comboBox_categories.addItem(str(tuple[1]))

        else:
            self.comboBox_categories.setEnabled(False)

            self.comboBox_categories.clear()

        self.setTableHeaders_product()
        self.fillTable_product()

        self.enable_disable_product_buttons(False)

    def pages_change(self):
        """Обновить таблицы !!!"""
        if self.tabWidget.currentIndex() == 1:

            self.tableWidget_ingr_in_dishes.setColumnCount(0)
            self.tableWidget_ingr_in_dishes.setRowCount(0)

            self.tableWidget_categories.setColumnCount(0)
            self.tableWidget_categories.setRowCount(0)

            self.enable_disable_category_buttons(False)
            self.enable_disable_product_buttons(False)
            self.enable_disable_ds_buttons(False)

            self.pushButton_delete_ingr.setEnabled(False)
            self.pushButton_edit_ingr.setEnabled(False)

            if get_info_table("product_category") == []:
                self.radioButton_enable_cat_filter.setEnabled(False)
            else:
                self.radioButton_enable_cat_filter.setEnabled(True)

            self.pushButton_add_to_cat.setEnabled(False)

            self.setTableHeaders_product()
            self.fillTable_product()

        elif self.tabWidget.currentIndex() == 2:
            self.tableWidget_ingr.setColumnCount(0)
            self.tableWidget_ingr.setRowCount(0)

            self.tableWidget_ingr_in_dishes.setColumnCount(0)
            self.tableWidget_ingr_in_dishes.setRowCount(0)

            self.enable_disable_dish_buttons(False)
            self.enable_disable_product_buttons(False)

            self.setTableHeaders_category()
            self.fillTable_category()

            self.pushButton_delete_ingr.setEnabled(False)
            self.pushButton_edit_ingr.setEnabled(False)
        else:
            self.textBrowser_recipe.clear()
            self.tableWidget_ingr.setColumnCount(0)
            self.tableWidget_ingr.setRowCount(0)

            self.tableWidget_categories.setColumnCount(0)
            self.tableWidget_categories.setRowCount(0)

            self.enable_disable_category_buttons(False)
            self.enable_disable_dish_buttons(False)

            self.pushButton_add_ingr.setEnabled(False)
            self.setTableHeaders_dish()
            self.fillTable_dishes()

            self.pushButton_delete_ingr.setEnabled(False)
            self.pushButton_edit_ingr.setEnabled(False)

    def change_dish_info(self):
        """Меняет описание рецепта и состава"""

        # очистить от старых записей + обнулить
        self.tableWidget_ingr.clear()
        self.tableWidget_ingr.setColumnCount(0)
        self.tableWidget_ingr.setRowCount(0)

        """Виджет рецепта"""
        # вынимает необходимую инфу из столбца с названием
        ds_name = self.tableWidget_dishes.selectedItems()[0].text()

        # вынимаем по названию
        about_dish = get_table_column("dish", "ds_about", "ds_name", ds_name)

        # помещаем в виджет описание рецепта
        self.textBrowser_recipe.setText(about_dish.replace('\\n', '\n'))

        """Таблица состава"""
        # получение id всех ингридиентов, и по ним остальной инфы
        list_of_lists = get_all_pr_id_from_consistance_dish(ds_name)
        if list_of_lists:
            for i, list in enumerate(list_of_lists):
                pr_names = list[1]
                pr_gramovka = list[2]
                pr_part_price = list[3]
                pr_metric = list[4]
                pr_cat_id = get_table_column("product", "pr_cat_id", "pr_id", list[0])

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

                # получаем длину строки и вычитаем 1 столбец (где айди) и описание

                columns_count = len(get_info_table("consistance_dish")[0]) - 2

                rows_count = len(list_of_lists)

                # задаем кол-во всех строк и столбцов
                self.tableWidget_ingr.setColumnCount(columns_count)
                self.tableWidget_ingr.setRowCount(rows_count)

                # нумерация рядом со строками
                item = QTableWidgetItem()
                self.tableWidget_ingr.setVerticalHeaderItem(i, item)
                self.tableWidget_ingr.verticalHeaderItem(i).setText(str(i + 1))

                # подпись заголовков
                item = QTableWidgetItem()
                self.tableWidget_ingr.setHorizontalHeaderItem(0, item)
                self.tableWidget_ingr.horizontalHeaderItem(0).setText("Название")

                item = QTableWidgetItem()
                self.tableWidget_ingr.setHorizontalHeaderItem(1, item)
                self.tableWidget_ingr.horizontalHeaderItem(1).setText("Масса")

                item = QTableWidgetItem()
                self.tableWidget_ingr.setHorizontalHeaderItem(2, item)

                self.tableWidget_ingr.horizontalHeaderItem(2).setText("Руб.")

                # заполняет первый столбец
                item = QTableWidgetItem()
                if color: item.setBackground(linear_gradient)
                self.tableWidget_ingr.setItem(i, 0, item)
                self.tableWidget_ingr.item(i, 0).setText(str(pr_names))

                # заполняет второй столбец
                item = QTableWidgetItem()
                if color: item.setBackground(linear_gradient)
                self.tableWidget_ingr.setItem(i, 1, item)
                self.tableWidget_ingr.item(i, 1).setText(
                    remove_dot_zero_from_end(str(pr_gramovka)) + " " + str(pr_metric))

                # заполняет третий столбец
                item = QTableWidgetItem()
                if color:
                    item.setBackground(linear_gradient)
                self.tableWidget_ingr.setItem(i, 2, item)
                self.tableWidget_ingr.item(i, 2).setText(remove_dot_zero_from_end(str(pr_part_price)))

            # подгон ширины столбцов под текст
            header = self.tableWidget_ingr.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)


        else:

            # очистка таблицы
            self.tableWidget_ingr.setColumnCount(0)
            self.tableWidget_ingr.setRowCount(0)

            # Отключение кнопок  кнопок ингридиентов
            self.enable_disable_ingr_buttons(False)

        # Если выбрали продукт, разрешить добавлять ингридиенты
        self.pushButton_add_ingr.setEnabled(True)

    def change_product_info(self):
        """Обновление информации о продукте"""

        # очистить от старых записей + обнулить
        self.tableWidget_ingr_in_dishes.clear()
        self.tableWidget_ingr_in_dishes.setColumnCount(0)
        self.tableWidget_ingr_in_dishes.setRowCount(0)
        self.pushButton_add_to_cat.setEnabled(True)
        # вынимает необходимую инфу из столбца с названием
        pr_name = self.tableWidget_products.selectedItems()[0].text()

        """Таблица блюд, которые включают продукт"""
        # получение id всех ингридиентов, и по ним остальной инфы
        id_s = get_all_ds_id_from_consistance_dish(pr_name)
        if id_s != []:

            for i, id in enumerate(id_s):
                ds_name = get_table_column("dish", "ds_name", "ds_id", id)

                tuple = get_dishes_by_product(pr_name, id)[0]

                columns_count = 3

                rows_count = len(id_s)

                # задаем кол-во всех строк и столбцов
                self.tableWidget_ingr_in_dishes.setColumnCount(columns_count)
                self.tableWidget_ingr_in_dishes.setRowCount(rows_count)

                # нумерация рядом со строками
                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setVerticalHeaderItem(i, item)
                self.tableWidget_ingr_in_dishes.verticalHeaderItem(i).setText(str(i + 1))

                # подпись заголовков
                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setHorizontalHeaderItem(0, item)
                self.tableWidget_ingr_in_dishes.horizontalHeaderItem(0).setText("Название")

                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setHorizontalHeaderItem(1, item)
                self.tableWidget_ingr_in_dishes.horizontalHeaderItem(1).setText("Масса")

                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setHorizontalHeaderItem(2, item)
                self.tableWidget_ingr_in_dishes.horizontalHeaderItem(2).setText("Ст.")

                # заполняет первый столбец
                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setItem(i, 0, item)
                self.tableWidget_ingr_in_dishes.item(i, 0).setText(str(ds_name))

                # заполняет второй столбец
                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setItem(i, 1, item)
                self.tableWidget_ingr_in_dishes.item(i, 1).setText(
                    remove_dot_zero_from_end(str(tuple[0])) + " " + str(tuple[1]))

                # заполняет третий столбец
                item = QTableWidgetItem()
                self.tableWidget_ingr_in_dishes.setItem(i, 2, item)
                self.tableWidget_ingr_in_dishes.item(i, 2).setText(remove_dot_zero_from_end(str(tuple[2])))

            # подгон ширины столбцов под текст
            header = self.tableWidget_ingr_in_dishes.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        else:
            # очистка таблицы
            self.tableWidget_ingr_in_dishes.setColumnCount(0)
            self.tableWidget_ingr_in_dishes.setRowCount(0)

            # Отключение кнопок  кнопок ингридиентов
            self.enable_disable_ds_buttons(False)
        self.pushButton_add_to_cat.setEnabled(True)

    def setTableHeaders_dish(self):
        # получаем длину строки и вычитаем 1 столбец (где айди) и описание
        # Получаем кол-во всех строк

        # обнуление
        self.tableWidget_dishes.clear()
        self.tableWidget_dishes.setColumnCount(0)
        self.tableWidget_dishes.setRowCount(0)
        info_table = get_info_table("dish")

        if info_table != []:
            columns_count = len(info_table[0]) - 3
            rows_count = len(info_table)

            # задаем строки и столбцы
            self.tableWidget_dishes.setColumnCount(columns_count)
            self.tableWidget_dishes.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)  # память !!!
                self.tableWidget_dishes.setVerticalHeaderItem(i, item)
                self.tableWidget_dishes.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget_dishes.setHorizontalHeaderItem(0, item)
            self.tableWidget_dishes.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget_dishes.setHorizontalHeaderItem(1, item)
            self.tableWidget_dishes.horizontalHeaderItem(1).setText("Руб.")

    def fillTable_dishes(self):
        info_table = get_info_table("dish")
        if info_table != []:
            for i, tuple in enumerate(info_table):
                # заполняет первый столбец
                item = QTableWidgetItem()

                self.tableWidget_dishes.setItem(i, 0, item)
                self.tableWidget_dishes.item(i, 0).setText(str(tuple[1]))

                # заполняет второй столбец
                item = QTableWidgetItem()
                # цвет стоимости - зеленый
                # item.setForeground(QBrush(QColor(0, 255, 0))) # память
                # item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter) #память 1
                self.tableWidget_dishes.setItem(i, 1, item)
                self.tableWidget_dishes.item(i, 1).setText(remove_dot_zero_from_end(str(tuple[2])))

            header = self.tableWidget_dishes.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)

    def setTableHeaders_product(self):
        """Задает заголовки таблице продуктов"""
        # обнуление
        self.tableWidget_products.clear()
        self.tableWidget_products.setColumnCount(0)
        self.tableWidget_products.setRowCount(0)

        info_table = get_info_table("product")

        if self.radioButton_enable_cat_filter.isChecked() and self.comboBox_categories.currentText():
            category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                           self.comboBox_categories.currentText())
        else:
            category_id = None
        count = 0
        for tuple in info_table:
            if tuple[5] == category_id:
                count += 1

        if info_table != []:
            columns_count = len(info_table[0])

            # Если включены категории
            if not self.radioButton_enable_cat_filter.isChecked():
                columns_count += 1
                rows_count = len(info_table)
            else:
                rows_count = count

            # задаем строки и столбцы

            self.tableWidget_products.setColumnCount(columns_count - 3)
            self.tableWidget_products.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                self.tableWidget_products.setVerticalHeaderItem(i, item)
                self.tableWidget_products.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget_products.setHorizontalHeaderItem(0, item)
            self.tableWidget_products.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget_products.setHorizontalHeaderItem(1, item)
            self.tableWidget_products.horizontalHeaderItem(1).setText("Масса")

            item = QTableWidgetItem()
            self.tableWidget_products.setHorizontalHeaderItem(2, item)
            self.tableWidget_products.horizontalHeaderItem(2).setText("Руб.")

            if not self.radioButton_enable_cat_filter.isChecked():
                # задаем строки и столбцы
                item = QTableWidgetItem()
                self.tableWidget_products.setHorizontalHeaderItem(3, item)
                self.tableWidget_products.horizontalHeaderItem(3).setText("Категория")

    def fillTable_product(self):
        info_table = get_info_table("product")
        category_id = ""
        if info_table != []:
            if self.radioButton_enable_cat_filter.isChecked() and self.comboBox_categories.currentText():
                category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                               self.comboBox_categories.currentText())
            f = 0
            for i, tuple in enumerate(info_table):
                if self.radioButton_enable_cat_filter.isChecked() and tuple[5] != category_id:

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
                    self.tableWidget_products.setItem(f, 0, item)
                    self.tableWidget_products.item(f, 0).setText(str(tuple[1]))

                    # заполняет второй столбец
                    item = QTableWidgetItem()
                    if color: item.setBackground(linear_gradient)
                    self.tableWidget_products.setItem(f, 2, item)
                    self.tableWidget_products.item(f, 2).setText(remove_dot_zero_from_end(str(tuple[2])))

                    # заполняет третий столбец
                    item = QTableWidgetItem()
                    if color: item.setBackground(linear_gradient)
                    self.tableWidget_products.setItem(f, 1, item)
                    self.tableWidget_products.item(f, 1).setText(
                        remove_dot_zero_from_end(str(tuple[3])) + " " + str(tuple[4]))

                    if not self.radioButton_enable_cat_filter.isChecked():
                        # заполняет четвертый столбец
                        item = QTableWidgetItem()
                        if color: item.setBackground(linear_gradient)
                        self.tableWidget_products.setItem(f, 3, item)
                        if not tuple[5]:

                            self.tableWidget_products.item(f, 3).setText("-")
                        else:
                            name = get_table_column("product_category", "pr_cat_name", "pr_cat_id", tuple[5])
                            self.tableWidget_products.item(f, 3).setText(str(name))
                    f += 1
            header = self.tableWidget_products.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)

    def setTableHeaders_category(self):
        """Задает заголовки таблице продуктов"""
        # обнуление
        self.tableWidget_categories.clear()
        self.tableWidget_categories.setColumnCount(0)
        self.tableWidget_categories.setRowCount(0)

        info_table = get_info_table("product_category")

        if info_table != []:
            columns_count = len(info_table[0])
            rows_count = len(info_table)

            # задаем строки и столбцы

            self.tableWidget_categories.setColumnCount(columns_count - 1)
            self.tableWidget_categories.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                self.tableWidget_categories.setVerticalHeaderItem(i, item)
                self.tableWidget_categories.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget_categories.setHorizontalHeaderItem(0, item)
            self.tableWidget_categories.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget_categories.setHorizontalHeaderItem(1, item)
            self.tableWidget_categories.horizontalHeaderItem(1).setText("Цвет")

    def fillTable_category(self):
        info_table = get_info_table("product_category")
        if info_table != []:
            for i, tuple in enumerate(info_table):

                linear_gradient = None

                try:
                    color = get_en_color(str(tuple[2]))
                    linear_gradient = QtGui.QLinearGradient()
                    linear_gradient.setStart(0, 0)
                    linear_gradient.setFinalStop(0, 150)

                    linear_gradient.setColorAt(0, QColor("Transparent"))
                    linear_gradient.setColorAt(1, QColor(color))
                except:
                    color = False

                # заполняет первый столбец
                item = QTableWidgetItem()
                if color: item.setBackground(linear_gradient)
                self.tableWidget_categories.setItem(i, 0, item)
                self.tableWidget_categories.item(i, 0).setText(str(tuple[1]))

                # заполняет второй столбец
                item = QTableWidgetItem()
                if color: item.setBackground(linear_gradient)
                self.tableWidget_categories.setItem(i, 1, item)
                self.tableWidget_categories.item(i, 1).setText(remove_dot_zero_from_end(str(tuple[2])))

            header = self.tableWidget_categories.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)

    def delete_dish(self):
        """Удаление блюда"""
        current_dish_name = self.tableWidget_dishes.selectedItems()[0].text()
        current_dish_price = self.tableWidget_dishes.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удаление блюда", current_dish_name + " " + current_dish_price)
        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:

            delete_table_row("dish", "ds_name", current_dish_name)

            # обновление заголовков, таблиц, рецепта+состава

            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # очистить от старых записей + обнулить
            self.tableWidget_ingr.clear()
            self.tableWidget_ingr.setColumnCount(0)
            self.tableWidget_ingr.setRowCount(0)
            self.textBrowser_recipe.clear()

            self.frozen(False)
            # Если ничего не выбрано
            if self.tableWidget_dishes.selectedItems() == []:
                self.enable_disable_dish_buttons(False)
                self.pushButton_add_ingr.setEnabled(False)
        else:
            self.frozen(False)

    def delete_product(self):
        """Удаление блюда"""
        current_pr_name = self.tableWidget_products.selectedItems()[0].text()
        current_pr_price = self.tableWidget_products.selectedItems()[2].text()
        current_pr_gramm = self.tableWidget_products.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_pr_name + " " + current_pr_gramm + " " + current_pr_price)

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            delete_table_row("product", "pr_name", current_pr_name)

            # обновление заголовков, таблиц

            self.setTableHeaders_product()
            self.fillTable_product()

            # очистить от старых записей + обнулить
            self.tableWidget_ingr_in_dishes.clear()
            self.tableWidget_ingr_in_dishes.setColumnCount(0)
            self.tableWidget_ingr_in_dishes.setRowCount(0)

            self.frozen(False)
            self.enable_disable_product_buttons(False)
            self.enable_disable_ds_buttons(False)
        else:
            self.frozen(False)

    def delete_ingridient(self):
        """Удаление ингридиента"""
        current_dish_name = self.tableWidget_dishes.selectedItems()[0].text()
        current_ingr_name = self.tableWidget_ingr.selectedItems()[0].text()

        self.tableWidget_current_index = self.tableWidget_dishes.currentRow()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_ingr_name + " из " + current_dish_name + " ?")

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            delete_ingridient_row(current_dish_name, current_ingr_name)

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # вернуть текущую строку
            self.tableWidget_dishes.selectRow(self.tableWidget_current_index)
            self.change_dish_info()

            self.frozen(False)
            # Если ничего не выбрано
            if self.tableWidget_ingr.selectedItems() == []:
                self.enable_disable_ingr_buttons(False)
        else:
            self.frozen(False)

    def delete_product_from_dish(self):
        """Удаление ингридиента"""
        current_dish_name = self.tableWidget_ingr_in_dishes.selectedItems()[0].text()
        current_ingr_name = self.tableWidget_products.selectedItems()[0].text()

        self.tableWidget_products_current_index = self.tableWidget_products.currentRow()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_ingr_name + " из " + current_dish_name + " ?")

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            delete_ingridient_row(current_dish_name, current_ingr_name)

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_product()
            self.fillTable_product()

            # вернуть текущую строку
            self.tableWidget_products.selectRow(self.tableWidget_products_current_index)
            self.change_product_info()

            self.frozen(False)
            # Если ничего не выбрано
            if self.tableWidget_ingr_in_dishes.selectedItems() == []:
                self.enable_disable_ds_buttons(False)

        else:
            self.frozen(False)

    def delete_category(self):
        """Удаление блюда"""
        cur_name = self.tableWidget_categories.selectedItems()[0].text()
        cur_color = self.tableWidget_categories.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", cur_name + "\nЦвет: " + cur_color)

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            delete_table_row("product_category", "pr_cat_name", cur_name)

            # обновление заголовков, таблиц

            self.setTableHeaders_category()
            self.fillTable_category()

            self.frozen(False)
            self.enable_disable_category_buttons(False)
        else:
            self.frozen(False)

    def edit_dish(self):
        """редактирование блюда |название,стоимость"""

        # запомнить текущую строку
        self.tableWidget_current_index = self.tableWidget_dishes.currentRow()

        current_dish_name = self.tableWidget_dishes.selectedItems()[0].text()
        current_dish_price = self.tableWidget_dishes.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Edit_dish(self, current_dish_name, current_dish_name, current_dish_price)
        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # вернуть текущую строку
            self.tableWidget_dishes.selectRow(self.tableWidget_current_index)

            # Если ничего не выбрано
            if self.tableWidget_dishes.selectedItems() == []:
                self.pushButton_edit_product.setEnabled(False)
                self.pushButton_edit_product.setEnabled(True)
        self.frozen(False)

    def edit_ingr(self):
        """Редактирование ингридиента"""

        # запомнить текущую строку
        self.tableWidget_ingr_current_index = self.tableWidget_ingr.currentRow()

        cur_dish_name = self.tableWidget_dishes.selectedItems()[0].text()
        cur_ingr_name = self.tableWidget_ingr.selectedItems()[0].text()
        cur_ingr_gramm = self.tableWidget_ingr.selectedItems()[1].text()
        cur_ingr_price = self.tableWidget_ingr.selectedItems()[2].text()

        # Подгрузка вспомогательной формы |"ред. Ингридиента"
        dialog = Edit_ingr(self, cur_dish_name, cur_ingr_name, cur_ingr_gramm, cur_ingr_price)
        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            self.change_dish_info()

            # вернуть текущую строку
            self.tableWidget_ingr.selectRow(self.tableWidget_ingr_current_index)
        self.frozen(False)

    def edit_product_in_dish(self):
        """Редактировать продукт в блюде | продукты"""

        # запомнить текущую строку
        self.tableWidget_ingr_in_dishes_current_index = self.tableWidget_ingr_in_dishes.currentRow()

        cur_pr_name = self.tableWidget_products.selectedItems()[0].text()
        cur_ds_name = self.tableWidget_ingr_in_dishes.selectedItems()[0].text()
        cur_pr_gramm = self.tableWidget_ingr_in_dishes.selectedItems()[1].text()
        cur_pr_price = self.tableWidget_ingr_in_dishes.selectedItems()[2].text()

        # Подгрузка вспомогательной формы |"ред. Ингридиента"
        dialog = Edit_ingr(self, cur_ds_name, cur_pr_name, cur_pr_gramm, cur_pr_price)

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            self.change_product_info()

            # вернуть текущую строку
            self.tableWidget_ingr_in_dishes.selectRow(self.tableWidget_ingr_in_dishes_current_index)
        self.frozen(False)

    def edit_product(self):
        """редактирование продукта"""

        # запомнить текущую строку
        self.tableWidget_products_current_index = self.tableWidget_products.currentRow()

        current_pr_name = self.tableWidget_products.selectedItems()[0].text()
        current_pr_price = self.tableWidget_products.selectedItems()[2].text()
        current_pr_gramm = self.tableWidget_products.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = EditProduct(self, current_pr_name, current_pr_name, current_pr_gramm, current_pr_price)
        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:

            # обновление заголовков, таблиц
            self.setTableHeaders_product()
            self.fillTable_product()

            # вернуть текущую строку
            self.tableWidget_products.selectRow(self.tableWidget_products_current_index)

            # Если ничего не выбрано
            if self.tableWidget_dishes.selectedItems() == []:
                self.pushButton_edit_product.setEnabled(False)
                self.pushButton_edit_product.setEnabled(True)

        self.frozen(False)

    def edit_category(self):
        """редактирование категории"""

        # запомнить текущую строку
        self.tableWidget_categories_current_index = self.tableWidget_categories.currentRow()

        cur_name = self.tableWidget_categories.selectedItems()[0].text()
        cur_color = self.tableWidget_categories.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"

        dialog = EditCategory(self, cur_name, cur_name, cur_color)
        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц
            self.setTableHeaders_category()
            self.fillTable_category()

            # вернуть текущую строку
            self.tableWidget_categories.selectRow(self.tableWidget_categories_current_index)

        self.frozen(False)

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
            self.minimize_window_button.setEnabled(False)
            self.restore_window_button.setEnabled(False)

        else:
            for obj in self.active_items_dict:
                obj.setEnabled(self.active_items_dict[obj])
            self.close_window_button.setEnabled(True)
            self.minimize_window_button.setEnabled(True)
            self.restore_window_button.setEnabled(True)

    def add_dish(self):
        """Добавление блюда """

        # Подгрузка вспомогательной формы
        dialog = Add_dish(self)

        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()
            self.tableWidget_dishes.selectRow(self.tableWidget_dishes.rowCount() - 1)
            self.change_dish_info()
        self.frozen(False)

    def add_product(self):
        """Добавление продукта """

        # Подгрузка вспомогательной формы
        dialog = AddProduct(self)
        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_product()
            self.fillTable_product()
            self.tableWidget_products.selectRow(self.tableWidget_products.rowCount() - 1)
            self.change_product_info()
            self.enable_disable_product_buttons(True)
        self.frozen(False)

    def add_category(self):
        """Добавление категории"""

        # Подгрузка вспомогательной формы
        dialog = AddCategory(self)

        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава

            self.setTableHeaders_category()

            self.fillTable_category()

            self.tableWidget_categories.selectRow(self.tableWidget_categories.rowCount() - 1)

            self.enable_disable_category_buttons(True)

        self.frozen(False)

    def add_ingr(self):
        """Добавление ингридиента (+)"""
        try:
            current_dish_name = self.tableWidget_dishes.selectedItems()[0].text()

            # получение уже использованных ингридиентов (названий)
            list_of_included_ingr = []

            # добавление их в список

            for i in range(self.tableWidget_ingr.rowCount()):
                list_of_included_ingr.append(self.tableWidget_ingr.item(i, 0).text())

            # Подгрузка вспомогательной формы |"да и нет"
            dialog = Add_ingr(self, current_dish_name, list_of_included_ingr)
            self.active_items_dict.clear()
            self.frozen(True)
            if dialog.exec_() and dialog.accept:

                # обновление заголовков, таблиц, рецепта+состава

                self.change_dish_info()
                self.tableWidget_ingr.selectRow(self.tableWidget_ingr.rowCount() - 1)

                # Если ничего не выбрано
                if self.tableWidget_ingr.selectedItems() == []:
                    self.enable_disable_ingr_buttons(False)

        except Exception as e:
            print(e)
        self.frozen(False)

    def add_replace_pr_to_cat(self):
        """Добавляет и перемещает из категории"""

        self.tableWidget_products_current_index = self.tableWidget_products.currentRow()
        cur_name = self.tableWidget_products.selectedItems()[0].text()

        dialog = InsertInCategory(self, cur_name)
        self.active_items_dict.clear()
        self.frozen(True)
        if dialog.exec_() and dialog.accept:
            self.setTableHeaders_product()
            self.fillTable_product()
            # вернуть текущую строку
            self.tableWidget_products.selectRow(self.tableWidget_products_current_index)

        self.frozen(False)

    def edit_dish_recipe(self, view_mode):
        """Редактирование рецепта блюда"""
        current_dish_name = self.tableWidget_dishes.selectedItems()[0].text()
        current_dish_recipe = self.textBrowser_recipe.toPlainText()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Edit_dish_recipe(self, current_dish_name, current_dish_recipe, view_mode)
        self.active_items_dict.clear()
        self.frozen(True)

        if dialog.exec_() and dialog.accept:
            self.change_dish_info()
        self.frozen(False)

    def enable_disable_dish_buttons(self, enable=True):
        """
        Включение и откючение кнопок удаления и изменения
        просмотра, редактирования рецепта
        """
        if enable:
            self.pushButton_delete_dish.setEnabled(True)
            self.pushButton_edit_dish.setEnabled(True)
            self.pushButton_edit_recipe.setEnabled(True)
            self.pushButton_look_recipe.setEnabled(True)
        else:
            self.pushButton_edit_dish.setEnabled(False)
            self.pushButton_delete_dish.setEnabled(False)
            self.pushButton_edit_recipe.setEnabled(False)
            self.pushButton_look_recipe.setEnabled(False)

    def enable_disable_ingr_buttons(self, enable=True):
        """Кнопки управления ингридиентами (вкл, выкл)"""
        if enable:

            self.pushButton_edit_ingr.setEnabled(True)
            self.pushButton_delete_ingr.setEnabled(True)
        else:
            self.pushButton_edit_ingr.setEnabled(False)
            self.pushButton_delete_ingr.setEnabled(False)

    def enable_disable_product_buttons(self, enable=True):
        """
        Включение и откючение кнопок удаления и изменения
        просмотра, редактирования рецепта
        """
        if enable:
            self.pushButton_edit_product.setEnabled(True)
            self.pushButton_delete_product.setEnabled(True)
            self.pushButton_add_to_cat.setEnabled(True)
            try:
                cat = self.tableWidget_products.selectedItems()[3].text()
            except:
                cat = "None"
            if str(cat) == '-':
                self.pushButton_remove_from_cat.setEnabled(False)
            else:
                self.pushButton_remove_from_cat.setEnabled(True)

        else:
            self.pushButton_edit_product.setEnabled(False)
            self.pushButton_delete_product.setEnabled(False)
            self.pushButton_add_to_cat.setEnabled(False)
            self.pushButton_remove_from_cat.setEnabled(False)

    def enable_disable_category_buttons(self, enable=True):
        """
        Включение и откючение кнопок
        """
        if enable:
            self.pushButton_delete_category.setEnabled(True)
            self.pushButton_edit_category.setEnabled(True)

        else:
            self.pushButton_delete_category.setEnabled(False)
            self.pushButton_edit_category.setEnabled(False)

    def enable_disable_ds_buttons(self, enable=True):
        """Кнопки управления продуктами (вкл, выкл)"""
        if enable:

            self.pushButton_delete_ingr_in_dish.setEnabled(True)
            self.pushButton_edit_ingr_in_dish.setEnabled(True)

        else:
            self.pushButton_delete_ingr_in_dish.setEnabled(False)
            self.pushButton_edit_ingr_in_dish.setEnabled(False)

        if get_info_table("product_category") == []:
            self.radioButton_enable_cat_filter.setEnabled(False)


        else:
            self.radioButton_enable_cat_filter.setEnabled(True)

    def change_language(self):
        """Переключалка языка"""
        if self.pushButton_info_3.text() == "   Rus":
            self.pushButton_info_3.setText("   Eng")
            self.change_page_language("Eng")
        else:
            self.pushButton_info_3.setText("   Rus")
            self.change_page_language("Rus")

    def change_page_language(self, current_language):
        if current_language == "Eng":
            cl = Eng()
        else:
            cl = Rus()
        self.label_2.setText(cl.label_2)
        self.label_3.setText(cl.label_3)
        self.label_4.setText(cl.label_4)


"""План"""

"""
1. Добавить комбобокс в добавление ингридиента

0.3 Смена цвета квадрата в категории ( добавление, изменение)

"""
