import sqlite3
from datetime import *


def set_connection_to_db():
    """Установка соединения с бд"""

    current_path = "P:\soft\SQLiteStudio"
    #conn = sqlite3.connect(current_path + '\money_base')
    conn = sqlite3.connect('money_base')
    conn.execute("PRAGMA foreign_keys = ON")
    cursor = conn.cursor()
    return conn, cursor


def get_info_table(table: str) -> "list of tuples":
    """Получает всю инфу из бд"""

    conn, cursor = set_connection_to_db()
    res = cursor.execute("SELECT * FROM " + table).fetchall()
    conn.commit()
    conn.close()
    return res


def get_table_column(table: str, column: str, first_arg: str, second_arg: str) -> str:
    """Получает значение столбца"""

    conn, cursor = set_connection_to_db()
    sql = "SELECT {} FROM {} WHERE {} LIKE '{}'".format(column, table, first_arg, second_arg)
    res = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return res[0][0]


def get_all_from_table(table: str, first_arg: str, second_arg: str) -> list:
    """Получает всю инфу из таблицы по одному критерию"""
    conn, cursor = set_connection_to_db()
    sql = "SELECT * FROM {} WHERE {} = {}".format(table, first_arg, second_arg)

    res = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return res


def get_info_by_dict(table, dict):
    """Получает по таблице и словарю аргументов"""
    sql_begin = "select * from {} where ".format(table)
    i = 0

    for key, value in dict.items():
        i += 1
        arg_before = key
        arg_after = value
        sql_begin += "{} = {}".format(arg_before, arg_after)
        if i != len(dict):
            sql_begin += " and "

    print(sql_begin)


def get_consistance_dish(column: str, ds_name, pr_id) -> str:
    """Получает значение столбца"""

    conn, cursor = set_connection_to_db()
    ds_id = cursor.execute("SELECT ds_id FROM dish WHERE ds_name LIKE '{}'".format(ds_name)).fetchall()

    sql = "SELECT {} FROM consistance_dish WHERE ds_id = {} AND pr_id = {}".format(column, ds_id[0][0], pr_id)

    res = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return res[0][0]


def get_dishes_by_product(pr_name, ds_id) -> list:
    """Получает значение столбца"""

    conn, cursor = set_connection_to_db()
    pr_id = cursor.execute("SELECT pr_id FROM product WHERE pr_name LIKE '{}'".format(pr_name)).fetchall()

    sql = "SELECT pr_gramm, pr_metric, pr_part_price FROM consistance_dish WHERE pr_id = {} and ds_id = {}".format(
        pr_id[0][0], ds_id)

    res = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()
    return res


def get_all_pr_id_from_consistance_dish(ds_name: str) -> list:
    """Получает все ингридиенты блюда"""

    conn, cursor = set_connection_to_db()
    ds_id = cursor.execute("SELECT ds_id FROM dish WHERE ds_name = '{}'".format(ds_name)).fetchall()

    sql = "SELECT * from consistance_dish where ds_id = {}".format(ds_id[0][0])
    list_of_tuples = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()

    for i in range(len(list_of_tuples)):
        list_of_tuples[i] = list(list_of_tuples[i])
        pr_name = get_table_column("product", "pr_name", "pr_id", list_of_tuples[i][1])
        list_of_tuples[i][0] = list_of_tuples[i][1]
        list_of_tuples[i][1] = pr_name

    return list_of_tuples


def get_all_ds_id_from_consistance_dish(pr_name: str) -> list:
    """Получает все блюда ингридиента"""

    conn, cursor = set_connection_to_db()
    pr_id = cursor.execute("SELECT pr_id FROM product WHERE pr_name LIKE '{}'".format(pr_name)).fetchall()

    sql = "SELECT ds_id from consistance_dish where pr_id LIKE '{}'".format(pr_id[0][0])
    list_of_tuples = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()

    # преобразование в нормальный список
    res = []
    for tuple in list_of_tuples:
        res.append(tuple[0])
    return res


def insert_product(name, price):
    """Добавление продукта"""
    conn, cursor = set_connection_to_db()

    sql = "INSERT INTO product VALUES (NULL, '{}', '{}')".format(name, price)

    res = cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def delete_table_row(table: str, first_arg: str, second_arg: str) -> str:
    """удаляет строку"""

    conn, cursor = set_connection_to_db()
    sql = "DELETE FROM {} WHERE {} = '{}'".format(table, first_arg, second_arg)
    cursor.execute(sql).fetchall()

    conn.commit()
    conn.close()


def order_get_list():
    """Получение статусов cooking и ready"""
    conn, cursor = set_connection_to_db()
    list_of_orders = cursor.execute("SELECT * FROM order_check "
                                    "WHERE or_status = 'cooking' "
                                    "or or_status = 'ready'").fetchall()
    conn.commit()
    conn.close()
    return list_of_orders


def delete_dish_from_current_order(normal_number):
    """Удаляет блюдо из текущего заказа"""

    conn, cursor = set_connection_to_db()

    # получение or_id по текущему заказу
    sql_help = "select or_id from order_check where or_status = 'not ready'"
    or_id = cursor.execute(sql_help).fetchall()[0][0]

    # Получение по номеру or_ds_id
    sql_0 = "select or_ds_id from consistance_order where or_ds_normal_number  = {} and or_id  = {}".format(
        normal_number, or_id)
    or_ds_id = cursor.execute(sql_0).fetchall()[0][0]

    # удаление из таблицы заказа
    sql_1 = "DELETE FROM consistance_order " \
            "WHERE or_ds_normal_number = {} and or_id  = {}".format(normal_number, or_id)
    cursor.execute(sql_1).fetchall()

    # передвинуть нумерацию на пункт ниже
    sql_2 = "Update consistance_order set " \
            "or_ds_normal_number = or_ds_normal_number - 1 where or_ds_normal_number>{} and or_id  = {}".format(
        normal_number, or_id)
    cursor.execute(sql_2).fetchall()

    # удаление заказанного продукта order_dish
    sql_3 = "DELETE FROM order_dish " \
            "WHERE or_ds_id = {}".format(or_ds_id)
    cursor.execute(sql_3).fetchall()

    # удаление заказанных граммовок
    sql_4 = "DELETE FROM consistance_order_dish_products " \
            "WHERE or_ds_id = {}".format(or_ds_id)
    cursor.execute(sql_4).fetchall()

    # проверка на удаление чека, если не заказали ничего, то и чек не надо
    sql_6 = "select * from consistance_order where or_id = {}".format(or_id)
    res = cursor.execute(sql_6).fetchall()

    if not res:
        sql_7 = "delete from order_check where or_status = 'not ready'"
        cursor.execute(sql_7).fetchall()

    conn.commit()
    conn.close()


def delete_ingridient_row(ds_name: str, pr_name: str) -> str:
    """удаляет строку ингридиента"""

    ds_id = get_table_column("dish", "ds_id", "ds_name", ds_name)
    pr_id = get_table_column("product", "pr_id", "pr_name", pr_name)

    conn, cursor = set_connection_to_db()
    sql = "DELETE FROM consistance_dish WHERE ds_id = {} AND pr_id = {}".format(ds_id, pr_id)
    cursor.execute(sql).fetchall()

    conn.commit()
    conn.close()


def add_product(pr_name, pr_price, pr_ves, pr_metric, pr_cat=False):
    """"Добавление продукта"""
    conn, cursor = set_connection_to_db()
    if not pr_cat:
        sql = "INSERT INTO product " \
              "(pr_name,pr_price,pr_ves,pr_kg)" \
              " VALUES('{}',{},{},'{}')".format(pr_name, pr_price, pr_ves, pr_metric)
    else:
        cat_id = get_table_column("product_category", "pr_cat_id", "pr_cat_name", pr_cat)
        sql = "INSERT INTO product " \
              "(pr_name,pr_price,pr_ves,pr_kg,pr_cat_id)" \
              " VALUES('{}',{},{},'{}',{})".format(pr_name, pr_price, pr_ves, pr_metric, cat_id)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def add_category(name, color):
    """"Добавление категории"""
    conn, cursor = set_connection_to_db()
    sql = "INSERT INTO product_category " \
          "(pr_cat_name,pr_cat_color)" \
          " VALUES('{}','{}')".format(name, color)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def update_dish_name_price(name, new_price, new_name):
    """изменение стоимости и названия продукта"""
    conn, cursor = set_connection_to_db()

    sql = "UPDATE dish SET ds_name = '{}', ds_price= {} WHERE ds_name LIKE '{}'".format(new_name, new_price, name)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def update_product(pr_name, pr_price, pr_ves, pr_kg, old_name):
    """изменение стоимости и названия продукта"""
    conn, cursor = set_connection_to_db()

    sql = "UPDATE product SET " \
          "pr_name = '{}', pr_price = {},pr_ves={},pr_kg='{}'" \
          " WHERE pr_name LIKE '{}'".format(pr_name, pr_price, pr_ves, pr_kg, old_name)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def update_category(new_name, old_name, color):
    """изменение стоимости и названия продукта"""
    conn, cursor = set_connection_to_db()

    sql = "UPDATE product_category SET " \
          "pr_cat_name = '{}', pr_cat_color= '{}'" \
          " WHERE pr_cat_name LIKE '{}'".format(new_name, color, old_name)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def update_product_cat(name, category):
    """Изменение категории (помещение)"""
    conn, cursor = set_connection_to_db()
    if not category == None:
        id_cat = get_table_column("product_category", "pr_cat_id", "pr_cat_name", category)
    else:
        id_cat = 'NULL'

    sql = "UPDATE product SET " \
          "pr_cat_id = {}" \
          " WHERE pr_name LIKE '{}'".format(id_cat, name)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def update_ingr_gramm_price(ds_name, pr_name, pr_gramm, pr_price, pr_metric):
    """грамовки и стоимости ингридиента в блюде"""
    conn, cursor = set_connection_to_db()

    ds_id = get_table_column("dish", "ds_id", "ds_name", ds_name)
    pr_id = get_table_column("product", "pr_id", "pr_name", pr_name)

    sql = "UPDATE consistance_dish SET pr_gramm = {}, pr_part_price= {},pr_metric = '{}'" \
          " WHERE ds_id = {} and pr_id = {}".format(pr_gramm, pr_price, pr_metric, ds_id, pr_id)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def add_dish(ds_name, ds_price, ds_recipe):
    """добавление блюда"""
    conn, cursor = set_connection_to_db()

    sql = "INSERT INTO dish " \
          "(ds_name,ds_price,ds_about)" \
          " VALUES('{}',{},'{}')".format(ds_name, ds_price, ds_recipe)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


def order_get_current_info():
    """Находит заказ not ready (текущий)"""
    conn, cursor = set_connection_to_db()
    sql_check = "select * from order_check where or_status = 'not ready'"
    res_1 = cursor.execute(sql_check).fetchall()
    conn.commit()
    conn.close()

    return res_1


def order_get_info(normal_number):
    """получает всю информацию о заказе"""
    conn, cursor = set_connection_to_db()

    # информация о заказе order_check
    sql_check = "select * from order_check where or_normal_number = {}".format(normal_number)
    res_1 = cursor.execute(sql_check).fetchall()

    # информация о блюдах заказа consistance_order
    sql_dishes = "select or_ds_id from consistance_order where or_id = {}".format(res_1[0][0])
    res_2 = cursor.execute(sql_dishes).fetchall()

    # получение имен блюд order_dish
    list_of_names = []
    for dish in res_2:
        sql = "select ds_id from order_dish where or_ds_id = {}".format(dish[0])
        res_3 = cursor.execute(sql).fetchall()

        sql = "select ds_name,ds_price from dish where ds_id = {}".format(res_3[0][0])
        res_4 = cursor.execute(sql).fetchall()
        list_of_names.append(res_4[0])

    conn.commit()
    conn.close()

    return list_of_names


def update_order_status(key, normal_number=None):
    """Обновляет статус заказу"""
    conn, cursor = set_connection_to_db()

    if key == "not ready to cooking":  # not ready -> cooking

        sql = "UPDATE order_check SET " \
              "or_status = 'cooking'" \
              " WHERE or_status = 'not ready'"
        cursor.execute(sql).fetchall()

    elif key == "cooking to ready":  # cooking -> ready
        ch_time_end = datetime.now().strftime("%H:%M")
        sql = "UPDATE order_check SET " \
              "or_status = 'ready', or_time_end_cooking = '{}'" \
              " WHERE or_status = 'cooking'and or_normal_number = {}".format(ch_time_end, normal_number)
        cursor.execute(sql).fetchall()

    elif key == "finished":  # cooking -> ready

        sql = "UPDATE order_check SET " \
              "or_status = 'finished'" \
              " WHERE or_status = 'ready'and or_normal_number = {}".format(normal_number)
        cursor.execute(sql).fetchall()

    conn.commit()
    conn.close()


def order_get_current_dishes(or_normal_number):
    """Получает список блюд"""
    conn, cursor = set_connection_to_db()

    # получаем заказ по нормальному номеру
    sql_check = "select or_id from order_check where or_normal_number = " + str(or_normal_number)
    res_1 = cursor.execute(sql_check).fetchall()
    list_of_dishes = []
    if res_1:
        # получаем блюда по номеру чека
        sql_dishes = "select * from consistance_order where or_id = " + str(res_1[0][0])
        res_2 = cursor.execute(sql_dishes).fetchall()

        for row in res_2:
            ds_id = cursor.execute("select ds_id from order_dish where or_ds_id = " + str(row[1])).fetchall()[0][0]
            ds_name = cursor.execute("select ds_name,ds_price from dish where ds_id = " + str(ds_id)).fetchall()[0]
            list_of_dishes.append(ds_name)
    conn.commit()
    conn.close()

    return list_of_dishes


def order_modify_dish_ingr(or_normal_number, ds_normal_number, ingr_name):
    # Добавляет в таблицу состава блюда изменения, где убирается ингридиент
    conn, cursor = set_connection_to_db()

    # Получаем айди заказа
    sql_0 = "select or_id from order_check where or_normal_number = {} and or_status = 'not ready'".format(
        or_normal_number)
    or_id = cursor.execute(sql_0).fetchall()[0][0]

    # получаем модифицируемое заказанное блюдо, его айди
    sql_1 = "select or_ds_id from consistance_order where or_ds_normal_number  = {} and or_id  = {}".format(
        ds_normal_number, or_id)
    or_ds_id = cursor.execute(sql_1).fetchall()[0][0]

    # получает айди блюда
    sql_2 = "select ds_id from order_dish where or_ds_id = {}".format(or_ds_id)
    ds_id = cursor.execute(sql_2).fetchall()[0][0]

    # получаем айди продукта, который изменяется
    sql_3 = "select pr_id from product where pr_name = '{}'".format(ingr_name)
    pr_id = cursor.execute(sql_3).fetchall()[0][0]

    # есть ли уже модификация в заказанном блюде или нет
    sql_check = " select * from consistance_order_dish_products" \
                " where or_ds_id = {} and pr_id = {}".format(or_ds_id, pr_id)
    is_there = cursor.execute(sql_check).fetchall()

    if not is_there:
        # Получаем составной компонент
        sql_4 = "select pr_gramm, pr_part_price, pr_metric from consistance_dish " \
                "where ds_id = {} and pr_id = {}".format(ds_id, pr_id)

        pr_gramm, pr_part_price, pr_metric = cursor.execute(sql_4).fetchall()[0]

        # Задаем новый атрибут в таблицу состава продукта заказанного блюда
        sql_add = "insert into consistance_order_dish_products " \
                  "(or_ds_id,pr_id,or_pr_gramm,or_pr_part_price,or_pr_metric) " \
                  "values ({},{},{},{},'{}')".format(or_ds_id, pr_id, pr_gramm * -1, pr_part_price * -1, pr_metric)

        cursor.execute(sql_add).fetchall()

    else:
        sql_remove = "delete from consistance_order_dish_products" \
                     " where or_ds_id = {} and pr_id = {}".format(or_ds_id, pr_id)
        cursor.execute(sql_remove).fetchall()

    conn.commit()
    conn.close()


def order_add_dish(dish_name, normal_number):
    """добавление блюда в текущий заказ"""
    # статусы: not ready,cooking,ready,finished,not picked up
    conn, cursor = set_connection_to_db()
    ch_date = datetime.today().strftime('%d.%m.%Y')
    ch_time = datetime.now().strftime("%H:%M")
    # логика нормальной нумерации заказа
    # проверка на наличие текущего заказа в бд
    res_1 = order_get_current_info()

    if not res_1:
        # нормальная нумерация заказа
        current_number = cursor.execute("select MAX(or_normal_number) from order_check").fetchall()[0][0]
        current_number = 1 if not current_number else current_number + 1

        sql_1 = "INSERT INTO order_check " \
                "(or_normal_number,or_date,or_time,or_status)" \
                " VALUES({},'{}','{}','{}')".format(current_number, ch_date, ch_time, "not ready")

        cursor.execute(sql_1).fetchall()
        # получение нового айди чека
        or_id = cursor.lastrowid
    else:
        or_id = cursor.execute("select * from order_check where or_normal_number = " + normal_number).fetchall()[0][0]

    # получение блюда
    ds_id = get_table_column("dish", "ds_id", "ds_name", dish_name)

    # создание заказанного блюда
    sql_2 = "INSERT INTO order_dish " \
            "(ds_id)" \
            " VALUES({})".format(ds_id)
    cursor.execute(sql_2).fetchall()

    # получение нового айди заказанного блюда
    or_ds_id = cursor.lastrowid

    # нормальная нумерация блюда в заказе
    current_ds_number = cursor.execute("select MAX(or_ds_normal_number) "
                                       "from consistance_order where or_id = {}".format(or_id)).fetchall()[0][0]
    current_ds_number = 1 if not current_ds_number else current_ds_number + 1

    # добавление блюда в заказ
    sql_3 = "INSERT INTO consistance_order " \
            "(or_id,or_ds_id,ds_count,or_ds_normal_number)" \
            " VALUES({},{},{},{})".format(or_id, or_ds_id, 1, current_ds_number)

    cursor.execute(sql_3).fetchall()

    conn.commit()
    conn.close()


def add_dish_ingr(ds_name, pr_name, pr_part_price, pr_gramm, pr_metric):
    """добавление продукта в блюдо"""
    conn, cursor = set_connection_to_db()

    ds_id = get_table_column("dish", "ds_id", "ds_name", ds_name)
    pr_id = get_table_column("product", "pr_id", "pr_name", pr_name)

    sql = "INSERT INTO consistance_dish " \
          "(ds_id,pr_id,pr_gramm,pr_part_price,pr_metric)" \
          " VALUES({},{},{},{},'{}')".format(ds_id, pr_id, pr_gramm, pr_part_price, pr_metric)

    cursor.execute(sql).fetchall()
    conn.commit()

    conn.close()


def update_dish_recipe(name, new_recipe):
    """изменение стоимости и названия продукта"""
    conn, cursor = set_connection_to_db()

    sql = "UPDATE dish SET ds_about = '{}' WHERE ds_name LIKE '{}'".format(new_recipe, name)

    cursor.execute(sql).fetchall()
    conn.commit()
    conn.close()


if __name__ == '__main__':
    # start

    # test
    # insert_product('ки233ви',15.5)
    # rint(get_info_table("product"))
    # print(get_table_column("dish", "ds_about", "ds_name", "шава с хлопьями"))
    id_s = get_all_pr_id_from_consistance_dish("шава с хлопьями")
    for id in id_s:
        pr_names = get_table_column("product", "pr_name", "pr_id", id)
        pr_gramovka = get_table_column("consistance_dish", "pr_gramm", "pr_id", id)
        pr_part_price = get_table_column("consistance_dish", "pr_part_price", "pr_id", id)

        # end
