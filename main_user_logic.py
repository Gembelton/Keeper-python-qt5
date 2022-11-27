from forms.form_begin import Ui_MainWindow
from sqlite3_requests import get_info_table, \
    order_add_dish, \
    order_get_current_info, \
    order_get_current_dishes, \
    delete_dish_from_current_order, \
    order_get_list, \
    update_order_status, \
    order_get_info, \
    get_all_pr_id_from_consistance_dish, \
    order_modify_dish_ingr, \
    get_info_by_dict, \
    get_table_column

from functools import partial
from Custom_Widgets.Widgets import *

from simple_tools import remove_dot_zero_from_end


class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)

        # Подгрузка интерфейса
        self.setupUi(self)
        # loadJsonStyle(self, self)

        # режим приложения
        self.mode = "add to current"

        # Скидка всего чека и скидка на один продукт
        self.global_skidka = 0
        self.dish_skidka = 0

        # заполняет список имеющихся блюд
        self.fill_dishes_list()

        # заполняет текущий заказ
        self.refresh_current_order()

        # заполняет очередь заказов
        self.refresh_order_queue()

        # Привязка чекбоксов
        self.checkBox.clicked.connect(self.enable_disable_skidka)

        # привязка списка заказов (неготовые и готовые к выдаче)
        self.listWidget.itemClicked.connect(self.item_selected_in_listbox)
        self.listWidget_2.itemClicked.connect(self.item_selected_in_listbox)

        # прявязка исходных кнопок
        self.pushButton_9.clicked.connect(self.order_to_cook)
        self.pushButton_9.clicked.connect(self.give_check_to_client)
        self.pushButton_10.clicked.connect(self.cancel_order)

    @staticmethod
    def get_label_name_by_widget_name(button_name, layout):
        """Получает имя блюда по рядом стоящей кнопке или лэйблу и расположению"""
        index = ""
        if button_name[-2].isdigit():
            index += str(button_name[-2])
        index += str(button_name[-1])
        label = layout.itemAt(int(index)).itemAt(0).widget()
        text = label.text().partition(' ')  # после пробела элемент

        # Пример вывода ('2', ' ', 'Бургер')
        return text

    def cancel_order(self):
        """Отменить заказ"""
        if self.mode == "add to current":
            for l in reversed(range(self.verticalLayout_2.count())):
                if self.verticalLayout_2.itemAt(l) is not None:
                    layout = self.verticalLayout_2.itemAt(l).layout()
                    if type(layout) == type(QtWidgets.QHBoxLayout()):
                        object_name = layout.itemAt(0).widget().objectName()
                        normal_number = self.get_label_name_by_widget_name(object_name, self.verticalLayout_2)[0]
                        delete_dish_from_current_order(normal_number)

                        self.refresh_current_order()

    def item_selected_in_listbox(self):
        """При выборе заказа из первой очереди (неготовых)"""

        order_number = self.sender().currentItem().text().split(" ")[1]

        self.clear_current_order_panel()

        if self.sender().objectName() == "listWidget":
            self.label_current_order_number.setText("Готовящийся заказ " + str(order_number))
        elif self.sender().objectName() == "listWidget_2":
            self.label_current_order_number.setText("На выдачу заказ " + str(order_number))

        list_of_order_dishes_names = order_get_info(order_number)
        order_summ = 0
        # Добавление виджетов названий текста
        for i, tuple in enumerate(list_of_order_dishes_names):
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setObjectName("horizontalLayout_number_" + str(i))

            # Текст с нумерацией
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)
            self.label.setObjectName("label_text_number_" + str(i))
            self.label.setText(str(i + 1) + " " + str(tuple[0]))
            self.label.setFixedHeight(60)
            self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignTop)
            self.verticalLayout_2.addLayout(self.horizontalLayout)

            # Стоимость
            order_summ += tuple[1]
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setAlignment(QtCore.Qt.AlignLeading | QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            self.label.setObjectName("label_price_number_" + str(i))
            text = remove_dot_zero_from_end(str(tuple[1]))
            self.label.setText(text)
            self.label.setFixedHeight(60)
            self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignTop)
            self.verticalLayout_2.addLayout(self.horizontalLayout)

        # Костыль с пустым фреймом внутри layout который будет пододвигать
        # все horizontalLayout c кнопками вверх
        vertical = QtWidgets.QVBoxLayout()
        frame = QtWidgets.QFrame()
        frame.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        vertical.addWidget(frame)
        self.verticalLayout_2.addLayout(vertical)

        self.lineEdit.setText(str(order_summ))

        # Выбор режима в зависимости от источника нажатия
        if self.sender().objectName() == "listWidget":
            self.change_mode("view and accept")
        elif self.sender().objectName() == "listWidget_2":
            self.change_mode("view and finish")

    def change_mode(self, key):
        """Смена режима окна"""
        if key == "add to current":
            # Кнопка отмены, перезапись
            self.pushButton_10.setText("Отменить")
            self.pushButton_10.clicked.disconnect()
            self.pushButton_10.clicked.connect(self.cancel_order)

            # Кнопка оформить, перезапись
            self.pushButton_9.setText("Оформить")
            self.pushButton_9.clicked.disconnect()
            self.pushButton_9.clicked.connect(self.order_to_cook)
            self.pushButton_9.clicked.connect(self.give_check_to_client)

            # доступ к добавлению блюд в заказ
            self.scrollArea.setEnabled(True)

            # доступ к текущим блюдам заказа
            self.scrollArea_2.setEnabled(True)

            # Доступ к просмотру очередей
            self.listWidget.setEnabled(True)
            self.listWidget_2.setEnabled(True)

        elif key == "view and accept":
            # Кнопка возвращения к добавлению, перезапись
            self.pushButton_10.setText("Назад")
            self.pushButton_10.clicked.disconnect()
            self.pushButton_10.clicked.connect(self.go_to_current_order)

            # Кнопка добавления блюда в список готовых, перезапись
            self.pushButton_9.setText("Готов")
            self.pushButton_9.clicked.disconnect()
            self.pushButton_9.clicked.connect(self.order_to_ready_to_pick)

            # доступ к добавлению блюд в заказ
            self.scrollArea.setEnabled(False)



        elif key == "view and finish":
            # Кнопка возвращения к добавлению, перезапись
            self.pushButton_10.setText("Назад")
            self.pushButton_10.clicked.disconnect()
            self.pushButton_10.clicked.connect(self.go_to_current_order)

            # Кнопка выдачи блюда, перезапись
            self.pushButton_9.setText("Выдан")
            self.pushButton_9.clicked.disconnect()
            self.pushButton_9.clicked.connect(self.order_picked)

            # доступ к добавлению блюд в заказ
            self.scrollArea.setEnabled(False)

        elif key == "edit current dish":
            # Кнопка возвращения к текущему заказу
            self.pushButton_10.setText("Назад")
            self.pushButton_10.clicked.disconnect()
            self.pushButton_10.clicked.connect(self.fill_dishes_list)
            self.pushButton_10.clicked.connect(self.go_to_current_order)

            # Кнопка выдачи блюда, перезапись
            self.pushButton_9.setText("Подтвердить")
            self.pushButton_9.clicked.disconnect()
            self.pushButton_9.clicked.connect(self.accept_dish_changes)

            # доступ к текущим блюдам заказа
            self.scrollArea_2.setEnabled(False)

            # Доступ к просмотру очередей
            self.listWidget.setEnabled(False)
            self.listWidget_2.setEnabled(False)

        self.mode = key

    def accept_dish_changes(self):
        """Подтвердить изменения блюда"""
        self.pushButton_10.click()
        print("изменено!")

    def go_to_current_order(self):
        """Вернуться к текущему заказу"""

        # задание заголовка панели справа
        self.label_left_panel.setText("Меню")

        # Возврат к меню
        self.fill_dishes_list()

        self.refresh_current_order()

        self.change_mode("add to current")

    def refresh_order_queue(self):
        """Обновляет список заказов"""
        list_of_orders = order_get_list()

        self.listWidget.clear()
        self.listWidget_2.clear()
        for row in list_of_orders:
            text = str(row[-1][0]) + " " + str(row[1])
            item = QtWidgets.QListWidgetItem(text)
            if str(row[-1][0]) == 'c':
                self.listWidget.addItem(item)
            elif str(row[-1][0]) == 'r':
                self.listWidget_2.addItem(item)

    def order_to_cook(self):
        """меняет статус заказу, очищает, добавляет в очередь"""
        current_number = int(self.label_current_order_number.text().split(" ")[2])
        update_order_status('not ready to cooking')
        self.label_current_order_number.setText("Текущий заказ " + str(current_number + 1))
        self.refresh_order_queue()
        self.refresh_current_order()

    def give_check_to_client(self):
        """Логика работы с кассовым аппаратом"""
        print("выдается чек")

    def order_to_ready_to_pick(self):
        """Переместить выбранный заказ в готовые к выдаче"""
        order_number = self.label_current_order_number.text().split(" ")[-1]

        update_order_status("cooking to ready", order_number)
        self.refresh_order_queue()
        self.pushButton_10.click()

    def order_picked(self):
        """Закрыть заказ"""
        order_number = self.label_current_order_number.text().split(" ")[-1]

        update_order_status("finished", order_number)
        self.refresh_order_queue()
        self.pushButton_10.click()

    def enable_disable_skidka(self):
        """Выключение и включение кнопок скидок"""
        for i, panel in enumerate(self.verticalLayout_2.children()):
            if panel is not None and panel.itemAt(2) is not None:
                if not self.checkBox.isChecked():
                    panel.itemAt(2).widget().hide()
                else:
                    panel.itemAt(2).widget().show()

    def get_dish_skidka_current_order(self):
        """Добавление блюду в текущем заказе скидки"""
        pass

    def edit_dish_current_order(self):
        """Редактирование блюда в текущем заказе"""
        info = self.get_label_name_by_widget_name(self.sender().objectName(), self.verticalLayout_2)
        dish_number = info[0]
        dish_name = info[2]

        # Очистка правой панели
        for l in reversed(range(self.verticalLayout.count())):
            if self.verticalLayout.itemAt(l) is not None:
                layout = self.verticalLayout.itemAt(l).layout()
                for w in range(layout.count()):
                    layout.itemAt(w).widget().deleteLater()
                self.verticalLayout.removeItem(layout)

        # Добавление панелей топингов и состава
        list_of_products = get_all_pr_id_from_consistance_dish(dish_name)

        # для проверок
        or_normal_number = self.label_current_order_number.text().split(" ")[-1]
        or_id = get_table_column("order_check","or_id","or_normal_number",or_normal_number)

        dict = {"or_normal_number": or_normal_number, "or_id": int(or_id)}
        print(dict)
        # or_ds_id по номеру заказу и по or_id
        # pr_id в цикле по получению стобца
        get_info_by_dict("consistance_order", dict)

        for i, row in enumerate(list_of_products):
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setObjectName("horizontalLayout_edit_number_" + str(i))

            # Текст с нумерацией
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.label.setObjectName("label_edit_name_number_" + str(i))
            self.label.setText(str(i + 1) + " " + str(row[1]))
            self.label.setFixedHeight(30)
            self.label.setFixedWidth(150)
            self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            # граммы
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.label.setObjectName("label_edit_gramm_number_" + str(i))
            text = remove_dot_zero_from_end(str(row[2])) + " " + row[-1]
            self.label.setText(text)
            self.label.setFixedHeight(30)
            self.label.setFixedWidth(50)

            self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            # кнопка убрать ингридиент
            self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
            self.pushButton.setFixedHeight(30)
            self.pushButton.setFixedWidth(60)
            self.pushButton.setObjectName("pushButton_remove_ingr_number_" + str(i))

            # проверка на то, есть ли этот ингридиент или нет уже
            self.pushButton.setText("Убрать")

            self.horizontalLayout.addWidget(self.pushButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            self.verticalLayout.addLayout(self.horizontalLayout)

        # Костыль с пустым фреймом внутри layout который будет пододвигать
        # чтобы все horizontalLayout c кнопками вверх поджались
        vertical = QtWidgets.QVBoxLayout()
        frame = QtWidgets.QFrame()
        frame.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        vertical.addWidget(frame)
        self.verticalLayout.addLayout(vertical)

        # смена заголовка
        self.label_left_panel.setText("Редактирование")
        self.label_secret_save.setText(dish_number + " " + dish_name)
        self.change_mode("edit current dish")

        # обработчик событий нажатий кнопки
        for i, panel in enumerate(self.verticalLayout.children()):
            # pushbutton object
            if type(panel) == type(QtWidgets.QHBoxLayout()):
                panel.itemAt(2).widget().clicked.connect(self.remove_or_add_ingr_from_dish)

    def remove_or_add_ingr_from_dish(self):
        """Удаляет выбранный ингридиент, или восстанавливает"""

        # проверка на долбоеба, который все ингридиенты убрал
        count_ingr = 0
        for l in reversed(range(self.verticalLayout.count())):
            if self.verticalLayout.itemAt(l) is not None:
                layout = self.verticalLayout.itemAt(l).layout()
                if type(layout) == type(QtWidgets.QHBoxLayout()):
                    text = layout.itemAt(2).widget().text()
                    if text == "Убрать":
                        count_ingr += 1
        for l in reversed(range(self.verticalLayout.count())):
            if self.verticalLayout.itemAt(l) is not None:
                layout = self.verticalLayout.itemAt(l).layout()
                if type(layout) == type(QtWidgets.QHBoxLayout()):
                    if count_ingr == 3:

                        layout.itemAt(2).widget().setEnabled(False)
                    else:
                        layout.itemAt(2).widget().setEnabled(True)

        # основная логика
        button_name = self.sender().objectName()
        ingr_name = self.get_label_name_by_widget_name(button_name, self.verticalLayout)[-1]
        ds_normal_number = self.label_secret_save.text().partition(" ")[0]
        or_normal_number = self.label_current_order_number.text().split(" ")[-1]
        order_modify_dish_ingr(or_normal_number, ds_normal_number, ingr_name)

        if self.sender().text() == "Убрать":
            self.sender().setText("Вернуть")
        else:
            self.sender().setText("Убрать")

    def remove_dish_current_order(self):
        """Удаляет блюдо из текущего заказа"""
        normal_number = self.get_label_name_by_widget_name(self.sender().objectName(), self.verticalLayout_2)[0]
        delete_dish_from_current_order(int(normal_number))
        self.refresh_current_order()

    def add_dish_to_order(self):
        """Добавление блюда"""
        dish_name = self.get_label_name_by_widget_name(self.sender().objectName(), self.verticalLayout)[2]

        if self.label_current_order_number.text()[-1].isdigit() and "Текущий" in self.label_current_order_number.text():
            # во всех остальных случаях берем оттуда номер заказа
            order_add_dish(dish_name, self.label_current_order_number.text().split(" ")[2])
        else:
            # При старте, заранее задаем первый заказ
            self.label_current_order_number.setText("Текущий заказ 1")
            order_add_dish(dish_name, 1)

        self.refresh_current_order()

    def clear_current_order_panel(self):
        """Очистка области средней панели"""
        for l in reversed(range(self.verticalLayout_2.count())):
            if self.verticalLayout_2.itemAt(l) is not None:
                layout = self.verticalLayout_2.itemAt(l).layout()
                for w in range(layout.count()):
                    layout.itemAt(w).widget().deleteLater()
                self.verticalLayout_2.removeItem(layout)

    def refresh_current_order(self):
        """Обновить текущий заказ"""
        current_order_info = order_get_current_info()

        # удаление блюд
        for l in reversed(range(self.verticalLayout_2.count())):
            if self.verticalLayout_2.itemAt(l) is not None:
                layout = self.verticalLayout_2.itemAt(l).layout()
                for w in range(layout.count()):
                    layout.itemAt(w).widget().deleteLater()
                self.verticalLayout_2.removeItem(layout)

        # Очиста общей суммы заказа
        self.lineEdit.clear()

        if current_order_info:
            # задаем номер заказа в лэйбле
            self.label_current_order_number.setText("Текущий заказ " + str(current_order_info[0][1]))
            current_order_dishes = order_get_current_dishes(current_order_info[0][1])

            order_summ = 0

            # Создание динамических панелей
            for i, tuple in enumerate(current_order_dishes):
                self.horizontalLayout = QtWidgets.QHBoxLayout()
                self.horizontalLayout.setObjectName("horizontalLayout_current_number_" + str(i))

                # Текст с нумерацией
                self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
                self.label.setObjectName("label_current_name_number_" + str(i))
                self.label.setText(str(i + 1) + " " + str(tuple[0]))
                self.label.setFixedHeight(60)
                self.label.setFixedWidth(150)
                self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

                # стоимость
                self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
                self.label.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                self.label.setObjectName("label_current_price_number_" + str(i))
                text = remove_dot_zero_from_end(str(tuple[1]))
                self.label.setText(text)
                self.label.setFixedHeight(60)
                self.label.setFixedWidth(20)

                self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
                order_summ += tuple[1]

                # кнопка скидка
                self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
                self.pushButton.setFixedHeight(60)
                self.pushButton.setFixedWidth(60)
                self.pushButton.setObjectName("pushButton_current_skidka_number_" + str(i))
                self.pushButton.setText("skidka")
                if not self.checkBox.isChecked():
                    self.pushButton.hide()

                self.horizontalLayout.addWidget(self.pushButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

                # кнопка редактировать
                self.pushButton = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
                self.pushButton.setFixedHeight(60)
                self.pushButton.setFixedWidth(60)
                self.pushButton.setObjectName("pushButton_current_edit_number_" + str(i))
                self.pushButton.setText("edit")
                self.horizontalLayout.addWidget(self.pushButton, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

                # кнопка убрать
                self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
                self.pushButton_2.setFixedHeight(60)
                self.pushButton_2.setFixedWidth(60)
                self.pushButton_2.setObjectName("pushButton_current_remove_number_" + str(i))
                self.pushButton_2.setText("remove")
                self.horizontalLayout.addWidget(self.pushButton_2, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

                self.verticalLayout_2.addLayout(self.horizontalLayout)

            # Костыль с пустым фреймом внутри layout который будет пододвигать
            # чтобы все horizontalLayout c кнопками вверх поджались
            vertical = QtWidgets.QVBoxLayout()
            frame = QtWidgets.QFrame()
            frame.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
            vertical.addWidget(frame)
            self.verticalLayout_2.addLayout(vertical)

            # задание суммы заказа
            self.lineEdit.setText(str(order_summ))

            # обработчик на нажатие кнопок: skidka,edit,remove | центральная панель
            for i, panel in enumerate(self.verticalLayout_2.children()):
                # pushbutton object

                if type(panel) == type(QtWidgets.QHBoxLayout()):
                    panel.itemAt(2).widget().clicked.connect(self.get_dish_skidka_current_order)
                    panel.itemAt(3).widget().clicked.connect(self.edit_dish_current_order)
                    panel.itemAt(4).widget().clicked.connect(self.remove_dish_current_order)
        else:
            self.label_current_order_number.setText("Текущего заказа нет")

    def fill_dishes_list(self):
        """Заполняет главный список имеющихся блюд"""

        # Очистка правой панели
        for l in reversed(range(self.verticalLayout.count())):
            if self.verticalLayout.itemAt(l) is not None:
                layout = self.verticalLayout.itemAt(l).layout()
                for w in range(layout.count()):
                    layout.itemAt(w).widget().deleteLater()
                self.verticalLayout.removeItem(layout)

        list_of_dishes = get_info_table("dish")
        for i, value in enumerate(list_of_dishes):
            # панелька
            self.horizontalLayout = QtWidgets.QHBoxLayout()
            self.horizontalLayout.setObjectName("horizontalLayout_number_" + str(i))

            # Текст с нумерацией
            self.label = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
            self.label.setObjectName("label_name_number_" + str(i))

            self.label.setText(str(i + 1) + " " + str(value[1]))
            self.label.setFixedHeight(60)
            self.label.setFixedWidth(150)

            self.horizontalLayout.addWidget(self.label, 0, QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

            # Стоимость
            self.label_2 = QtWidgets.QLabel(self.scrollAreaWidgetContents)
            self.label_2.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.label_2.setObjectName("label_price_number_" + str(i))
            text = remove_dot_zero_from_end(str(value[2]))
            self.label_2.setText(text)
            self.label_2.setFixedHeight(60)
            self.label_2.setFixedWidth(15)
            self.horizontalLayout.addWidget(self.label_2, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

            # кнопка добавить
            self.pushButton_2 = QtWidgets.QPushButton(self.scrollAreaWidgetContents)
            self.pushButton_2.setFixedHeight(60)
            self.pushButton_2.setFixedWidth(60)
            self.pushButton_2.setObjectName("pushButton_add_number_" + str(i))
            self.pushButton_2.setText("add")

            self.horizontalLayout.addWidget(self.pushButton_2, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
            self.verticalLayout.addLayout(self.horizontalLayout)

        # обработчик на нажатие кнопки add | левая панель
        for i, panel in enumerate(self.verticalLayout.children()):
            # pushbutton object
            if type(panel) == type(QtWidgets.QHBoxLayout()):
                panel.itemAt(2).widget().clicked.connect(self.add_dish_to_order)

        # Костыль с пустым фреймом внутри layout который будет пододвигать
        # чтобы все horizontalLayout c кнопками вверх поджались
        vertical = QtWidgets.QVBoxLayout()
        frame = QtWidgets.QFrame()
        frame.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        vertical.addWidget(frame)
        self.verticalLayout.addLayout(vertical)

# 1. функционал "забыли доложить к заказу продукт, поэтому просто достали и положили, а он обманул нас покупатель блин"
