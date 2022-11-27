from cgitb import text
import sys
import codecs


# 2.1
def task1():
    a = int(input('введите число: '))
    b = int(input('введите второе число: '))
    print('result: ', a ** b)
    print('первое число возведённое в степень равную воторому числу')
    print('-----------------------------------------------------------')
    return


# 2.2
def task2():
    a = float(input('enter number: '))
    print(int(a / 4))
    print(int(a % 5))
    print('----------------------------')
    return


# 2.3
def task3():
    a = float(input('enter number: '))
    b = float(input('enter next number: '))
    c = float(input('enter last number: '))
    d = a + b + c
    print(d / 3)
    print('-----------------------------------------------------------')
    return


# 2.4
def task4():
    a = int(input('введите двухзначное число: '))
    print(a / 10)
    print('-----------------------------------------------------------')
    return


# 2.5
def task5():
    a = int(input('введите двухзначное число: '))
    print(a % 10)
    print('-----------------------------------------------------------')
    return


# 2.6
def task6():
    b = float(input('введите дробное число: '))
    a = float(input('введите дробное число: '))
    s = float(input('введите дробное число: '))
    t = b ** a + a ** s + s ** b
    a_1 = b * a * s
    r = t / a_1
    d = r - b * a / s
    print(d)
    print('-----------------------------------------------------------')
    return


# 2.7
def task7():
    number = int(input('введите число: '))
    text = str(input('введите текст: '))
    print(text * number)
    print('-----------------------------------------------------------')
    return


# 2.8
def task8():
    f = str(input('введите текст 1: '))
    u = str(input('введите текст 2: '))
    c = str(input('введите текст 3: '))
    k = str(input('введите текст 4: '))
    print([k, c, u, f])
    print('-----------------------------------------------------------')
    return


def taskSelection():
    choise = int(input('\nselect task(1-8) press Enter to exit: '))
    try:
        if choise == 1:
            task1()
        if choise == 2:
            task2()
        if choise == 3:
            task3()
        if choise == 4:
            task4()
        if choise == 5:
            task5()
        if choise == 6:
            task6()
        if choise == 7:
            task7()
        if choise == 8:
            task8()
        else:
            print(' ')
        taskSelection()
    except ValueError:
        f = codecs.open("end_image.txt", "r", "utf_8_sig")
        print(f.read())
        # print('You entered invalid value, please try again.')
        sys.exit()


if __name__ == "__main__":
    taskSelection()





