import sys

from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QHeaderView

from forms.form_main import Ui_MainWindow

from yes_no_logic import Dialog_yes_no
from edit_dish_name_price import Edit_dish
from edit_dish_recipe import Edit_dish_recipe
from add_ingr_logic import Add_ingr
from edit_ingr_logic import Edit_ingr
from add_dish_logic import Add_dish
from edit_product_logic import EditProduct
from add_product_logic import AddProduct
from add_category_logic import AddCategory
from edit_category_logic import EditCategory
from insert_in_category_logic import InsertInCategory
from replace_pr_cat_logic import ReplaceCategory

from sqlite3_requests import get_info_table, \
    get_table_column, \
    get_all_pr_id_from_consistance_dish, \
    delete_table_row, \
    delete_ingridient_row, \
    get_consistance_dish, \
    get_all_ds_id_from_consistance_dish, \
    get_dishes_by_product, \
    update_product_cat

from simple_tools import remove_dot_zero_from_end
from Custom_Widgets.Widgets import *

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        # Подгрузка интерфейса
        self.setupUi(self)
        loadJsonStyle(self, self)
        self.tabWidget_3.tabBar().hide()

        # Заполнение заголовков таблицы |блюд, продуктов, категории
        self.setTableHeaders_dish()
        self.setTableHeaders_product()
        self.setTableHeaders_category()

        # Добавление инфы в таблицу |блюд, продуктов, категории
        self.fillTable_dishes()
        self.fillTable_product()
        self.fillTable_category()

        # привязка к нажатию в таблице |блюд
        self.tableWidget.clicked.connect(self.change_dish_info)
        self.tableWidget.clicked.connect(lambda: self.enable_disable_dish_buttons(True))

        # привязка к нажатию в таблице |продуктов
        self.tableWidget_3.clicked.connect(self.change_product_info)
        self.tableWidget_3.clicked.connect(lambda: self.enable_disable_product_buttons(True))

        # Привязка к нажатию в таблице |ингридиенты
        self.tableWidget_2.clicked.connect(lambda: self.enable_disable_ingr_buttons(True))
        self.tableWidget.clicked.connect(lambda: self.enable_disable_ingr_buttons(False))

        # Привязка к нажатию в таблице |продукты + вкл.блюда
        self.tableWidget_4.clicked.connect(lambda: self.enable_disable_ds_buttons(True))
        self.tableWidget_3.clicked.connect(lambda: self.enable_disable_ds_buttons(False))

        # привязка к нажатию в таблице |Категория
        self.tableWidget_5.clicked.connect(lambda: self.enable_disable_category_buttons(True))

        # текущий индекс выбранного элемента в таблицах
        self.tableWidget_current_index = 0
        self.tableWidget_2_current_index = 0
        self.tableWidget_3_current_index = 0
        self.tableWidget_4_current_index = 0
        self.tableWidget_5_current_index = 0

        # Кнопка изменения, удаления и добавления |блюд
        self.pushButton_4.clicked.connect(self.delete_dish)
        self.pushButton_5.clicked.connect(self.edit_dish)
        self.pushButton_10.clicked.connect(lambda: self.edit_dish_recipe(False))
        self.pushButton_12.clicked.connect(lambda: self.edit_dish_recipe(True))
        self.pushButton_13.clicked.connect(self.add_dish)

        # Кнопка изменения и удаления |Ингридиентов
        self.pushButton_8.clicked.connect(self.edit_ingr)
        self.pushButton_9.clicked.connect(self.delete_ingridient)
        self.pushButton_11.clicked.connect(self.add_ingr)

        # кнопки добавления, изменения и удаления | Продуктов
        self.pushButton_7.clicked.connect(self.delete_product)
        self.pushButton_6.clicked.connect(self.edit_product)
        self.pushButton_19.clicked.connect(self.add_product)
        self.pushButton_16.clicked.connect(self.add_replace_pr_to_cat)

        # кнопки добавления, изменения и удаления | Категории
        self.pushButton_31.clicked.connect(self.add_category)
        self.pushButton_33.clicked.connect(self.edit_category)
        self.pushButton_32.clicked.connect(self.delete_category)
        self.pushButton_17.clicked.connect(self.remove_pr_from_cat)

        # кнопки изменения и удаления | Продуктов в блюдах
        self.pushButton_3.clicked.connect(self.delete_product_from_dish)
        self.pushButton_15.clicked.connect(self.edit_product_in_dish)

        # обнулить на вкладках
        self.tabWidget_3.currentChanged.connect(self.pages_change)

        # включение сортировки по нажатию галочки | продукты, категория
        self.radioButton.clicked.connect(self.enable_cat_sort)
        self.comboBox.currentIndexChanged.connect(self.setTableHeaders_product)
        self.comboBox.currentIndexChanged.connect(self.fillTable_product)
        self.comboBox.currentIndexChanged.connect(lambda: self.enable_disable_product_buttons(False))

    def remove_pr_from_cat(self):
        """Меняет категорию продукта"""
        cur_name = self.tableWidget_3.selectedItems()[0].text()
        if self.radioButton.isChecked():
            cat = self.comboBox.currentText()
        else:
            cat = self.tableWidget_3.selectedItems()[3].text()

        dialog = Dialog_yes_no(self, "Убрать", cur_name + " из " + cat)
        if dialog.exec_() and dialog.accept:
            update_product_cat(cur_name, None)
            self.setTableHeaders_product()
            self.fillTable_product()

    def enable_cat_sort(self):
        """Включение сортировки по категории"""
        if self.radioButton.isChecked():
            self.comboBox.setEnabled(True)

            info_table = get_info_table("product_category")
            if info_table != []:
                for i, tuple in enumerate(info_table):
                    self.comboBox.addItem(str(tuple[1]))

        else:
            self.comboBox.setEnabled(False)

            self.comboBox.clear()


        self.setTableHeaders_product()
        self.fillTable_product()

        self.enable_disable_product_buttons(False)

    def pages_change(self):
        """Обновить таблицы !!!"""
        if self.tabWidget_3.currentIndex() == 1:

            self.tableWidget_4.setColumnCount(0)
            self.tableWidget_4.setRowCount(0)

            self.tableWidget_5.setColumnCount(0)
            self.tableWidget_5.setRowCount(0)

            self.enable_disable_category_buttons(False)
            self.enable_disable_product_buttons(False)
            self.enable_disable_ds_buttons(False)

            if get_info_table("product_category") == []:
                self.radioButton.setEnabled(False)
                self.pushButton_16.setEnabled(False)
            else:
                self.radioButton.setEnabled(True)
                self.pushButton_16.setEnabled(True)

            self.setTableHeaders_product()
            self.fillTable_product()

        elif self.tabWidget_3.currentIndex() == 2:
            self.tableWidget_2.setColumnCount(0)
            self.tableWidget_2.setRowCount(0)

            self.tableWidget_4.setColumnCount(0)
            self.tableWidget_4.setRowCount(0)

            self.enable_disable_dish_buttons(False)
            self.enable_disable_product_buttons(False)

            self.setTableHeaders_category()
            self.fillTable_category()

        else:
            self.textBrowser.clear()
            self.tableWidget_2.setColumnCount(0)
            self.tableWidget_2.setRowCount(0)

            self.tableWidget_5.setColumnCount(0)
            self.tableWidget_5.setRowCount(0)

            self.enable_disable_category_buttons(False)
            self.enable_disable_dish_buttons(False)

            self.pushButton_11.setEnabled(False)
            self.setTableHeaders_dish()
            self.fillTable_dishes()

    def change_dish_info(self):
        """Меняет описание рецепта и состава"""

        # очистить от старых записей + обнулить
        self.tableWidget_2.clear()
        self.tableWidget_2.setColumnCount(0)
        self.tableWidget_2.setRowCount(0)

        """Виджет рецепта"""
        # вынимает необходимую инфу из столбца с названием
        ds_name = self.tableWidget.selectedItems()[0].text()

        # вынимаем по названию
        about_dish = get_table_column("dish", "ds_about", "ds_name", ds_name)

        # помещаем в виджет описание рецепта
        self.textBrowser.setText(about_dish.replace('\\n', '\n'))

        """Таблица состава"""
        # получение id всех ингридиентов, и по ним остальной инфы
        id_s = get_all_pr_id_from_consistance_dish(ds_name)
        if id_s != []:
            for i, id in enumerate(id_s):
                pr_names = get_table_column("product", "pr_name", "pr_id", id)

                pr_gramovka = get_consistance_dish("pr_gramm", ds_name, id)

                pr_part_price = get_consistance_dish("pr_part_price", ds_name, id)

                pr_metric = get_consistance_dish("pr_metric", ds_name, id)

                # получаем длину строки и вычитаем 1 столбец (где айди) и описание

                columns_count = len(get_info_table("consistance_dish")[0]) - 2

                rows_count = len(id_s)

                # задаем кол-во всех строк и столбцов
                self.tableWidget_2.setColumnCount(columns_count)
                self.tableWidget_2.setRowCount(rows_count)

                # нумерация рядом со строками
                item = QTableWidgetItem()
                self.tableWidget_2.setVerticalHeaderItem(i, item)
                self.tableWidget_2.verticalHeaderItem(i).setText(str(i + 1))

                # подпись заголовков
                item = QTableWidgetItem()
                self.tableWidget_2.setHorizontalHeaderItem(0, item)
                self.tableWidget_2.horizontalHeaderItem(0).setText("Название")

                item = QTableWidgetItem()
                self.tableWidget_2.setHorizontalHeaderItem(1, item)
                self.tableWidget_2.horizontalHeaderItem(1).setText("Масса")

                item = QTableWidgetItem()
                self.tableWidget_2.setHorizontalHeaderItem(2, item)
                self.tableWidget_2.horizontalHeaderItem(2).setText("стоимость")

                # заполняет первый столбец
                item = QTableWidgetItem()
                self.tableWidget_2.setItem(i, 0, item)
                self.tableWidget_2.item(i, 0).setText(str(pr_names))

                # заполняет второй столбец
                item = QTableWidgetItem()
                self.tableWidget_2.setItem(i, 1, item)
                self.tableWidget_2.item(i, 1).setText(remove_dot_zero_from_end(str(pr_gramovka)) + " " + str(pr_metric))

                # заполняет третий столбец
                item = QTableWidgetItem()
                self.tableWidget_2.setItem(i, 2, item)
                self.tableWidget_2.item(i, 2).setText(remove_dot_zero_from_end(str(pr_part_price)))

            # подгон ширины столбцов под текст
            header = self.tableWidget_2.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)

        else:

            # очистка таблицы
            self.tableWidget_2.setColumnCount(0)
            self.tableWidget_2.setRowCount(0)

            # Отключение кнопок  кнопок ингридиентов
            self.enable_disable_ingr_buttons(False)

        # Если выбрали продукт, разрешить добавлять ингридиенты
        self.pushButton_11.setEnabled(True)

    def change_product_info(self):
        """Обновление информации о продукте"""

        # очистить от старых записей + обнулить
        self.tableWidget_4.clear()
        self.tableWidget_4.setColumnCount(0)
        self.tableWidget_4.setRowCount(0)

        # вынимает необходимую инфу из столбца с названием
        pr_name = self.tableWidget_3.selectedItems()[0].text()

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
                self.tableWidget_4.setColumnCount(columns_count)
                self.tableWidget_4.setRowCount(rows_count)

                # нумерация рядом со строками
                item = QTableWidgetItem()
                self.tableWidget_4.setVerticalHeaderItem(i, item)
                self.tableWidget_4.verticalHeaderItem(i).setText(str(i + 1))

                # подпись заголовков
                item = QTableWidgetItem()
                self.tableWidget_4.setHorizontalHeaderItem(0, item)
                self.tableWidget_4.horizontalHeaderItem(0).setText("Название")

                item = QTableWidgetItem()
                self.tableWidget_4.setHorizontalHeaderItem(1, item)
                self.tableWidget_4.horizontalHeaderItem(1).setText("Масса")

                item = QTableWidgetItem()
                self.tableWidget_4.setHorizontalHeaderItem(2, item)
                self.tableWidget_4.horizontalHeaderItem(2).setText("стоимость")

                # заполняет первый столбец
                item = QTableWidgetItem()
                self.tableWidget_4.setItem(i, 0, item)
                self.tableWidget_4.item(i, 0).setText(str(ds_name))

                # заполняет второй столбец
                item = QTableWidgetItem()
                self.tableWidget_4.setItem(i, 1, item)
                self.tableWidget_4.item(i, 1).setText(
                    remove_dot_zero_from_end(str(tuple[0])) + " " + str(tuple[1]))

                # заполняет третий столбец
                item = QTableWidgetItem()
                self.tableWidget_4.setItem(i, 2, item)
                self.tableWidget_4.item(i, 2).setText(remove_dot_zero_from_end(str(tuple[2])))

            # подгон ширины столбцов под текст
            header = self.tableWidget_4.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        else:
            # очистка таблицы
            self.tableWidget_4.setColumnCount(0)
            self.tableWidget_4.setRowCount(0)

            # Отключение кнопок  кнопок ингридиентов
            self.enable_disable_ds_buttons(False)

    def setTableHeaders_dish(self):
        # получаем длину строки и вычитаем 1 столбец (где айди) и описание
        # Получаем кол-во всех строк

        # обнуление
        self.tableWidget.clear()
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        info_table = get_info_table("dish")
        if info_table != []:
            columns_count = len(info_table[0]) - 2
            rows_count = len(info_table)

            # задаем строки и столбцы
            self.tableWidget.setColumnCount(columns_count)
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
            self.tableWidget.setHorizontalHeaderItem(1, item)
            self.tableWidget.horizontalHeaderItem(1).setText("Стоимость")

    def fillTable_dishes(self):
        info_table = get_info_table("dish")
        if info_table != []:
            for i, tuple in enumerate(info_table):
                # заполняет первый столбец
                item = QTableWidgetItem()
                self.tableWidget.setItem(i, 0, item)
                self.tableWidget.item(i, 0).setText(str(tuple[1]))

                # заполняет второй столбец
                item = QTableWidgetItem()
                # item.setTextAlignment(Qt.AlignTrailing | Qt.AlignVCenter) #память 1
                self.tableWidget.setItem(i, 1, item)
                self.tableWidget.item(i, 1).setText(remove_dot_zero_from_end(str(tuple[2])))

            header = self.tableWidget.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)

    def setTableHeaders_product(self):
        """Задает заголовки таблице продуктов"""
        # обнуление
        self.tableWidget_3.clear()
        self.tableWidget_3.setColumnCount(0)
        self.tableWidget_3.setRowCount(0)

        info_table = get_info_table("product")

        if self.radioButton.isChecked() and self.comboBox.currentText():
            category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                           self.comboBox.currentText())
        else:
            category_id = None
        count = 0
        for tuple in info_table:
            if tuple[5] == category_id:
                count += 1

        if info_table != []:
            columns_count = len(info_table[0])

            # Если включены категории
            if not self.radioButton.isChecked():
                columns_count += 1
                rows_count = len(info_table)
            else:
                rows_count = count

            # задаем строки и столбцы

            self.tableWidget_3.setColumnCount(columns_count - 3)
            self.tableWidget_3.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                self.tableWidget_3.setVerticalHeaderItem(i, item)
                self.tableWidget_3.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget_3.setHorizontalHeaderItem(0, item)
            self.tableWidget_3.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget_3.setHorizontalHeaderItem(1, item)
            self.tableWidget_3.horizontalHeaderItem(1).setText("Масса")

            item = QTableWidgetItem()
            self.tableWidget_3.setHorizontalHeaderItem(2, item)
            self.tableWidget_3.horizontalHeaderItem(2).setText("Стоимость")

            if not self.radioButton.isChecked():
                # задаем строки и столбцы
                item = QTableWidgetItem()
                self.tableWidget_3.setHorizontalHeaderItem(3, item)
                self.tableWidget_3.horizontalHeaderItem(3).setText("Категория")

    def fillTable_product(self):
        info_table = get_info_table("product")
        category_id = ""
        if info_table != []:
            if self.radioButton.isChecked() and self.comboBox.currentText():
                category_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name",
                                               self.comboBox.currentText())
            f = 0
            for i, tuple in enumerate(info_table):
                if self.radioButton.isChecked() and tuple[5] != category_id:

                    continue
                else:

                    # заполняет первый столбец
                    item = QTableWidgetItem()

                    self.tableWidget_3.setItem(f, 0, item)
                    self.tableWidget_3.item(f, 0).setText(str(tuple[1]))

                    # заполняет второй столбец
                    item = QTableWidgetItem()
                    self.tableWidget_3.setItem(f, 2, item)
                    self.tableWidget_3.item(f, 2).setText(remove_dot_zero_from_end(str(tuple[2])))

                    # заполняет третий столбец
                    item = QTableWidgetItem()
                    self.tableWidget_3.setItem(f, 1, item)
                    self.tableWidget_3.item(f, 1).setText(remove_dot_zero_from_end(str(tuple[3])) + " " + str(tuple[4]))

                    if not self.radioButton.isChecked():
                        # заполняет четвертый столбец
                        item = QTableWidgetItem()
                        self.tableWidget_3.setItem(f, 3, item)
                        if not tuple[5]:

                            self.tableWidget_3.item(f, 3).setText("-")
                        else:
                            name = get_table_column("product_category", "pr_cat_name", "pr_cat_id", tuple[5])
                            self.tableWidget_3.item(f, 3).setText(str(name))
                    f += 1
            header = self.tableWidget_3.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.Stretch)

    def setTableHeaders_category(self):
        """Задает заголовки таблице продуктов"""
        # обнуление
        self.tableWidget_5.clear()
        self.tableWidget_5.setColumnCount(0)
        self.tableWidget_5.setRowCount(0)

        info_table = get_info_table("product_category")

        if info_table != []:
            columns_count = len(info_table[0])
            rows_count = len(info_table)

            # задаем строки и столбцы

            self.tableWidget_5.setColumnCount(columns_count - 1)
            self.tableWidget_5.setRowCount(rows_count)

            # нумерация рядом со строками
            for i in range(rows_count):
                item = QTableWidgetItem()
                self.tableWidget_5.setVerticalHeaderItem(i, item)
                self.tableWidget_5.verticalHeaderItem(i).setText(str(i + 1))

            # подпись заголовков
            item = QTableWidgetItem()
            self.tableWidget_5.setHorizontalHeaderItem(0, item)
            self.tableWidget_5.horizontalHeaderItem(0).setText("Название")

            item = QTableWidgetItem()
            self.tableWidget_5.setHorizontalHeaderItem(1, item)
            self.tableWidget_5.horizontalHeaderItem(1).setText("Цвет")

    def fillTable_category(self):
        info_table = get_info_table("product_category")
        if info_table != []:
            for i, tuple in enumerate(info_table):
                # заполняет первый столбец
                item = QTableWidgetItem()
                self.tableWidget_5.setItem(i, 0, item)
                self.tableWidget_5.item(i, 0).setText(str(tuple[1]))

                # заполняет третий столбец
                item = QTableWidgetItem()
                self.tableWidget_5.setItem(i, 1, item)
                self.tableWidget_5.item(i, 1).setText(remove_dot_zero_from_end(str(tuple[2])))

            header = self.tableWidget_5.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Stretch)

    def delete_dish(self):
        """Удаление блюда"""
        current_dish_name = self.tableWidget.selectedItems()[0].text()
        current_dish_price = self.tableWidget.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_dish_name + " " + current_dish_price)

        if dialog.exec_() and dialog.accept:

            delete_table_row("dish", "ds_name", current_dish_name)

            # обновление заголовков, таблиц, рецепта+состава

            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # очистить от старых записей + обнулить
            self.tableWidget_2.clear()
            self.tableWidget_2.setColumnCount(0)
            self.tableWidget_2.setRowCount(0)
            self.textBrowser.clear()

            # Если ничего не выбрано
            if self.tableWidget.selectedItems() == []:
                self.enable_disable_dish_buttons(False)

    def delete_product(self):
        """Удаление блюда"""
        current_pr_name = self.tableWidget_3.selectedItems()[0].text()
        current_pr_price = self.tableWidget_3.selectedItems()[2].text()
        current_pr_gramm = self.tableWidget_3.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_pr_name + " " + current_pr_gramm + " " + current_pr_price)

        if dialog.exec_() and dialog.accept:
            delete_table_row("product", "pr_name", current_pr_name)

            # обновление заголовков, таблиц

            self.setTableHeaders_product()
            self.fillTable_product()

            # очистить от старых записей + обнулить
            self.tableWidget_4.clear()
            self.tableWidget_4.setColumnCount(0)
            self.tableWidget_4.setRowCount(0)

            self.enable_disable_product_buttons(False)
            self.enable_disable_ds_buttons(False)

    def delete_ingridient(self):
        """Удаление ингридиента"""
        current_dish_name = self.tableWidget.selectedItems()[0].text()
        current_ingr_name = self.tableWidget_2.selectedItems()[0].text()

        self.tableWidget_current_index = self.tableWidget.currentRow()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_ingr_name + " из " + current_dish_name + " ?")

        if dialog.exec_() and dialog.accept:
            delete_ingridient_row(current_dish_name, current_ingr_name)

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # вернуть текущую строку
            self.tableWidget.selectRow(self.tableWidget_current_index)
            self.change_dish_info()

            # Если ничего не выбрано
            if self.tableWidget_2.selectedItems() == []:
                self.enable_disable_ingr_buttons(False)

    def delete_product_from_dish(self):
        """Удаление ингридиента"""
        current_dish_name = self.tableWidget_4.selectedItems()[0].text()
        current_ingr_name = self.tableWidget_3.selectedItems()[0].text()

        self.tableWidget_3_current_index = self.tableWidget_3.currentRow()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", current_ingr_name + " из " + current_dish_name + " ?")

        if dialog.exec_() and dialog.accept:
            delete_ingridient_row(current_dish_name, current_ingr_name)

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_product()
            self.fillTable_product()

            # вернуть текущую строку
            self.tableWidget_3.selectRow(self.tableWidget_3_current_index)
            self.change_product_info()

            # Если ничего не выбрано
            if self.tableWidget_4.selectedItems() == []:
                self.enable_disable_ds_buttons(False)

    def delete_category(self):
        """Удаление блюда"""
        cur_name = self.tableWidget_5.selectedItems()[0].text()
        cur_color = self.tableWidget_5.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Dialog_yes_no(self, "Удалить", cur_name + "\nЦвет: " + cur_color)

        if dialog.exec_() and dialog.accept:
            delete_table_row("product_category", "pr_cat_name", cur_name)

            # обновление заголовков, таблиц

            self.setTableHeaders_category()
            self.fillTable_category()

            self.enable_disable_category_buttons(False)

    def edit_dish(self):
        """редактирование блюда |название,стоимость"""

        # запомнить текущую строку
        self.tableWidget_current_index = self.tableWidget.currentRow()

        current_dish_name = self.tableWidget.selectedItems()[0].text()
        current_dish_price = self.tableWidget.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Edit_dish(self, current_dish_name, current_dish_name, current_dish_price)

        if dialog.exec_() and dialog.accept:

            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()

            # вернуть текущую строку
            self.tableWidget.selectRow(self.tableWidget_current_index)

            # Если ничего не выбрано
            if self.tableWidget.selectedItems() == []:
                self.pushButton_4.setEnabled(False)
                self.pushButton_4.setEnabled(True)

    def edit_ingr(self):
        """Редактирование ингридиента"""

        # запомнить текущую строку
        self.tableWidget_2_current_index = self.tableWidget_2.currentRow()

        cur_dish_name = self.tableWidget.selectedItems()[0].text()
        cur_ingr_name = self.tableWidget_2.selectedItems()[0].text()
        cur_ingr_gramm = self.tableWidget_2.selectedItems()[1].text()
        cur_ingr_price = self.tableWidget_2.selectedItems()[2].text()

        # Подгрузка вспомогательной формы |"ред. Ингридиента"
        dialog = Edit_ingr(self, cur_dish_name, cur_ingr_name, cur_ingr_gramm, cur_ingr_price)

        if dialog.exec_() and dialog.accept:
            self.change_dish_info()

            # вернуть текущую строку
            self.tableWidget_2.selectRow(self.tableWidget_2_current_index)

    def edit_product_in_dish(self):
        """Редактировать продукт в блюде | продукты"""

        # запомнить текущую строку
        self.tableWidget_4_current_index = self.tableWidget_4.currentRow()

        cur_pr_name = self.tableWidget_3.selectedItems()[0].text()
        cur_ds_name = self.tableWidget_4.selectedItems()[0].text()
        cur_pr_gramm = self.tableWidget_4.selectedItems()[1].text()
        cur_pr_price = self.tableWidget_4.selectedItems()[2].text()

        # Подгрузка вспомогательной формы |"ред. Ингридиента"
        dialog = Edit_ingr(self, cur_ds_name, cur_pr_name, cur_pr_gramm, cur_pr_price)

        if dialog.exec_() and dialog.accept:
            self.change_product_info()

            # вернуть текущую строку
            self.tableWidget_4.selectRow(self.tableWidget_4_current_index)

    def edit_product(self):
        """редактирование продукта"""

        # запомнить текущую строку
        self.tableWidget_3_current_index = self.tableWidget_3.currentRow()

        current_pr_name = self.tableWidget_3.selectedItems()[0].text()
        current_pr_price = self.tableWidget_3.selectedItems()[2].text()
        current_pr_gramm = self.tableWidget_3.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = EditProduct(self, current_pr_name, current_pr_name, current_pr_gramm, current_pr_price)

        if dialog.exec_() and dialog.accept:

            # обновление заголовков, таблиц
            self.setTableHeaders_product()
            self.fillTable_product()

            # вернуть текущую строку
            self.tableWidget_3.selectRow(self.tableWidget_3_current_index)

            # Если ничего не выбрано
            if self.tableWidget.selectedItems() == []:
                self.pushButton_4.setEnabled(False)
                self.pushButton_4.setEnabled(True)

    def edit_category(self):
        """редактирование категории"""

        # запомнить текущую строку
        self.tableWidget_5_current_index = self.tableWidget_5.currentRow()

        cur_name = self.tableWidget_5.selectedItems()[0].text()
        cur_color = self.tableWidget_5.selectedItems()[1].text()

        # Подгрузка вспомогательной формы |"да и нет"

        dialog = EditCategory(self, cur_name, cur_name, cur_color)

        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц
            self.setTableHeaders_category()
            self.fillTable_category()

            # вернуть текущую строку
            self.tableWidget_5.selectRow(self.tableWidget_5_current_index)

    def add_dish(self):
        """Добавление блюда """

        # Подгрузка вспомогательной формы
        dialog = Add_dish(self)

        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_dish()
            self.fillTable_dishes()
            self.tableWidget.selectRow(self.tableWidget.rowCount() - 1)
            self.change_dish_info()

    def add_product(self):
        """Добавление продукта """

        # Подгрузка вспомогательной формы
        dialog = AddProduct(self)

        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава
            self.setTableHeaders_product()
            self.fillTable_product()
            self.tableWidget_3.selectRow(self.tableWidget_3.rowCount() - 1)
            self.change_product_info()
            self.enable_disable_product_buttons(True)

    def add_category(self):
        """Добавление категории"""

        # Подгрузка вспомогательной формы

        dialog = AddCategory(self)

        if dialog.exec_() and dialog.accept:
            # обновление заголовков, таблиц, рецепта+состава

            self.setTableHeaders_category()

            self.fillTable_category()

            self.tableWidget_5.selectRow(self.tableWidget_5.rowCount() - 1)

            self.enable_disable_category_buttons(True)

    def add_ingr(self):
        """Добавление ингридиента (+)"""
        try:
            current_dish_name = self.tableWidget.selectedItems()[0].text()

            # получение уже использованных ингридиентов (названий)
            list_of_included_ingr = []

            # добавление их в список

            for i in range(self.tableWidget_2.rowCount()):
                list_of_included_ingr.append(self.tableWidget_2.item(i, 0).text())

            # Подгрузка вспомогательной формы |"да и нет"
            dialog = Add_ingr(self, current_dish_name, list_of_included_ingr)

            if dialog.exec_() and dialog.accept:

                # обновление заголовков, таблиц, рецепта+состава

                self.change_dish_info()
                self.tableWidget_2.selectRow(self.tableWidget_2.rowCount() - 1)

                # Если ничего не выбрано
                if self.tableWidget_2.selectedItems() == []:
                    self.enable_disable_ingr_buttons(False)
        except Exception as e:
            print(e)

    def add_replace_pr_to_cat(self):
        """Добавляет и перемещает из категории"""

        self.tableWidget_3_current_index = self.tableWidget_3.currentRow()
        cur_name = self.tableWidget_3.selectedItems()[0].text()

        if self.radioButton.isChecked():
            cur_name = self.tableWidget_3.selectedItems()[0].text()
            dialog = ReplaceCategory(self, cur_name)
            if dialog.exec_() and dialog.accept:
                self.setTableHeaders_product()
                self.fillTable_product()
        else:
            # Подгрузка вспомогательной формы
            dialog = InsertInCategory(self, cur_name)
            if dialog.exec_() and dialog.accept:
                # обновление заголовков, таблиц
                self.setTableHeaders_product()
                self.fillTable_product()

                # вернуть текущую строку
                self.tableWidget_3.selectRow(self.tableWidget_3_current_index)

    def edit_dish_recipe(self, view_mode):
        """Редактирование рецепта блюда"""
        current_dish_name = self.tableWidget.selectedItems()[0].text()
        current_dish_recipe = self.textBrowser.toPlainText()

        # Подгрузка вспомогательной формы |"да и нет"
        dialog = Edit_dish_recipe(self, current_dish_name, current_dish_recipe, view_mode)

        if dialog.exec_() and dialog.accept:
            self.change_dish_info()

    def enable_disable_dish_buttons(self, enable=True):
        """
        Включение и откючение кнопок удаления и изменения
        просмотра, редактирования рецепта
        """
        if enable:
            self.pushButton_5.setEnabled(True)
            self.pushButton_4.setEnabled(True)
            self.pushButton_10.setEnabled(True)
            self.pushButton_12.setEnabled(True)
        else:
            self.pushButton_4.setEnabled(False)
            self.pushButton_5.setEnabled(False)
            self.pushButton_10.setEnabled(False)
            self.pushButton_12.setEnabled(False)

    def enable_disable_ingr_buttons(self, enable=True):
        """Кнопки управления ингридиентами (вкл, выкл)"""
        if enable:

            self.pushButton_8.setEnabled(True)
            self.pushButton_9.setEnabled(True)
        else:
            self.pushButton_8.setEnabled(False)
            self.pushButton_9.setEnabled(False)

    def enable_disable_product_buttons(self, enable=True):
        """
        Включение и откючение кнопок удаления и изменения
        просмотра, редактирования рецепта
        """
        if enable:
            self.pushButton_6.setEnabled(True)
            self.pushButton_7.setEnabled(True)

            try:
                cat = self.tableWidget_3.selectedItems()[3].text()
            except:
                cat = "None"
            if str(cat) == '-':
                self.pushButton_17.setEnabled(False)
            else:
                self.pushButton_17.setEnabled(True)

        else:
            self.pushButton_6.setEnabled(False)
            self.pushButton_7.setEnabled(False)

            self.pushButton_17.setEnabled(False)

    def enable_disable_category_buttons(self, enable=True):
        """
        Включение и откючение кнопок
        """
        if enable:
            self.pushButton_32.setEnabled(True)
            self.pushButton_33.setEnabled(True)

        else:
            self.pushButton_32.setEnabled(False)
            self.pushButton_33.setEnabled(False)

    def enable_disable_ds_buttons(self, enable=True):
        """Кнопки управления продуктами (вкл, выкл)"""
        if enable:

            self.pushButton_3.setEnabled(True)
            self.pushButton_15.setEnabled(True)

        else:
            self.pushButton_3.setEnabled(False)
            self.pushButton_15.setEnabled(False)

        if get_info_table("product_category") == []:
            self.radioButton.setEnabled(False)
            self.pushButton_16.setEnabled(False)
        else:
            self.radioButton.setEnabled(True)
            self.pushButton_16.setEnabled(True)

"""План"""

"""
1. Добавить комбобокс в добавление ингридиента

0.3 Смена цвета квадрата в категории ( добавление, изменение)

"""
