def remove_dot_zero_from_end(work_string):
    """Убирает .0 в строке"""
    if work_string[-2:len(work_string)] == ".0":
        return work_string[:-2]
    else:
        return work_string


def check_text(text: str) -> "bool" and str:
    """Проверка текста"""

    if text == "":
        return False, "Необходимо заполнить поле!"

    elif text[0] == " ":
        return False, "Запрещен пробел(ы) в начале!"

    elif not 3 <= len(text) <= 25:
        return False, "Разрешено от 3 символов до 25!"

    elif "'" in text:
        return False, "Уберите ковычки!"

    else:
        return True, ""


def check_price(text: str) -> "bool" and str:
    """Проверка стоимости"""
    try:
        b = float(text)
        if b < 0:
            return False, "Отрицательная стоимость!"

    except:
        return False, "Запрещен текст и запятые!"

    if len(text) > 10:
        return False, "Стоимость до 10 цифр!"

    elif "'" in text:
        return False, "Уберите ковычки!"

    else:
        return True, ""

def check_mass(text: str) -> "bool" and str:
    """Проверка стоимости"""
    try:
        b = float(text)
        if b < 0:
            return False, "Отрицательная масса!"

    except:
        return False, "Запрещен текст и запятые!"

    if len(text) > 10:
        return False, "Масса до 10 цифр!"

    elif "'" in text:
        return False, "Уберите ковычки!"

    else:
        return True, ""

def get_en_color(rus_name):
    if rus_name == "Черный":
        return "black"
    elif rus_name == "Серый":
        return "gray"
    elif rus_name == "Белый":
        return "white"
    elif rus_name == "Коричневый":
        return "brown"
    elif rus_name == "Красный":
        return "red"
    elif rus_name == "Оранжевый":
        return "orange"
    elif rus_name == "Желтый":
        return "yellow"
    elif rus_name == "Зеленый":
        return "green"
    elif rus_name == "Св.Зеленый":
        return "lightgreen"
    elif rus_name == "Синий":
        return "blue"
    elif rus_name == "Голубой":
        return "lightblue"
    elif rus_name == "Бирюзовый":
        return "#30d5c8"
    elif rus_name == "Фиолетовый":
        return "purple"
    elif rus_name == "Розовый":
        return "pink"

    else:
        return "#c8d0ab"


