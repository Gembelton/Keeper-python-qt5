alf = 'abcdefghijklmnopqrstuvwxyz'
alf_main = []
for i in alf:
    alf_main.append(i)

while True:
    print("---------------")
    print("Выберите:")
    print("1.Зашифровать")
    print("2.Расшифровать")
    print("3.Выйти")
    print("---------------")
    user_input = int(input("Введите (1-3): "))
    if user_input == 1:
        print("Шифрование текста")
        print("---------------")
        text = input("Введите текст: ")
        new_text = ""
        for i in text:
            for j in range(len(alf_main)):
                if i==alf_main[j]:
                    if j == len(alf_main)-1:
                        new_text += "a"
                    else:
                        new_text+=alf_main[j+1]
                elif i == " ":
                    new_text += " "
                    break
        print(new_text)
    if user_input == 2:
        print("Расшифрование текста")
        print("---------------")
        text = input("Введите текст: ")
        new_text = ""
        for i in text:
            for j in range(len(alf_main)):
                if i == alf_main[j]:
                    if i == "z":
                        new_text += "a"
                    else:
                        new_text += alf_main[j - 1]
                elif i == " ":
                    new_text += " "
                    break
        print(new_text)
    if user_input == 3:
        break
