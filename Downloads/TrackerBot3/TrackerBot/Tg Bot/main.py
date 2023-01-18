from typing import List, Any

import telebot
import sqlite3
from telebot import types
from time import sleep
from sheet import users
from Dicts import main2
main_dict = {}
main2()

from Dicts import lessons_dict, mentors_dict, participation_stage_dict
lessons = []
def main():
    token = '5846254841:AAE9hO3V9sbtkOYZeODrCdoYKvVB1FscC1I'  # Токен бота
    bot = telebot.TeleBot(token)

    db = sqlite3.connect("Data_Bases//Users.db",
                         check_same_thread=False)  # Создаём бд с id чатов и какие имена к ним привязаны
    cursor = db.cursor()


    db_olympiad = sqlite3.connect("Data_Bases//RsOS.db",
                                  check_same_thread=False)  # Создаём бд с именами пользователей,
    # олимпиадой, которую он написал, предметом по которой писал олимпиаду, этап олимпиады и его наставником
    cursor_olymp = db_olympiad.cursor()

    olympiad_lst = []  # Список всех олимпиад
    olympiad_dict = {}  # Словарь, где ключ это индекс олимпиады, а значение это название олимпиады
    c = 0

    olympiad = users("ROWS", "A1:B500", "read")
    for i in olympiad:
        if len(i[0]) == 1:
            i[0] = "0" + i[0]
        if i[0] not in olympiad_dict:
            olympiad_dict[i[0]] = [i[1]]
        else:
            olympiad_dict[i[0]].append([i[1]])
    olympiad = sorted(olympiad, key=lambda x: x[1])
    string = ''
    for i in olympiad:
        if "НТО:" not in i[1]:
            i[0] += ":"
        if c <= 15:
            string += " ".join(i)
            c += 1
        else:
            olympiad_lst.append(string)
            string, c = " ".join(i), 0
        string += "\n" + " " + "\n"
    olympiad_lst.append(string)



    @bot.message_handler(commands=['start'])  # Обрабатываем команду start
    def start_message(message):
        global user_chat_id
        user_chat_id = message.chat.id
        cursor.execute(f"SELECT chat_id FROM user WHERE chat_id = '{message.chat.id}'")
        # Ищем id чата с которого нам написали

        if cursor.fetchone() is None:  # Если такой человек нам не писал, то к id его чата не привязано имя,
            # а значит мы не сможем заносить в бд его по имени,
            # тогда нам надо спросить его имя и привязать его к id его чата
            bot.send_message(message.chat.id,
                             "✌Привет\n"
                             "Я бот для заполнения РсОШ трекера\n\n"
                             "🔎Для начала надо зарегистрироваться")  # Основное приветствие
            bot.send_message(message.chat.id, "Напиши своё ФИО в формате:\n"
                                              "'ФИО: *твоё ФИО*'")  # Запрос ФИО

        else:  # Если id чата уже есть в бд, значит пользователь уже зарегистрирован, тогда
            bot.send_message(message.chat.id, "Привет, ты уже зарегистрирован")  # Приветствуем его и
            button_message(message)  # Выводим ему основное меню кнопок

    def name(message):  # Функция для регистрации пользователя
        fio = message.text.split(': ')[1]  # Получаем ФИО пользователя

        cursor.execute(
            f"SELECT user_name FROM user WHERE user_name = '{fio}'")  # Проверяем, есть ли написанное имя в бд
        if cursor.fetchone() is None:  # Если его нет, тогда идём дальше
            cursor.execute('INSERT INTO user VALUES (?, ?, ?, ?)',
                           (None, message.chat.id, fio, 0))
            # Вписываем id чата пользователя и ФИО которое он написал
            db.commit()  # Сохраняем изменения в бд

            bot.send_message(message.chat.id,
                             "✅Ты успешно зарегистрировался")  # Оповещаем пользователя, что регистрация прошла успешно
            cursor_olymp.execute("""INSERT INTO olympiad_rating VALUES (?, ?, ?)""", (None, fio, 0))
            db_olympiad.commit()
            button_message(message)  # Выводим основное меню с кнопками
        else:  # Если имя уже есть, тогда
            bot.send_message(message.chat.id,
                             "❗️Пользователь с таким именем уже зарегистрирован")  # Говорим, что такое имя уже есть и
            button_message(message)  # Выводим основное меню с кнопками

    def button_message(message):  # Функция для вывода основного меню кнопок
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)  # Создаём меню

        new_olymp_register = types.KeyboardButton("✏️Зарегистрироваться на олимпиаду")
        del_olympiad = types.KeyboardButton("🗑Удалить олимпиаду")
        my_olymp = types.KeyboardButton("📄Мои олимпиады")
        my_place = types.KeyboardButton("🏆Моё место в рейтинге")
        rename_user = types.KeyboardButton("🔃Поменять имя")
        olymp_statick = types.KeyboardButton("📊Статистика олимпиад")
        # new_register = types.KeyboardButton("Зарегистрировать нового пользователя")

        # Создаём основные кнопки

        markup.add(new_olymp_register, del_olympiad, my_olymp, my_place, rename_user,
                   olymp_statick)  # Добавляем кнопки в меню
        bot.send_message(message.chat.id, '❔Что тебя интересует?',
                         reply_markup=markup)  # Отправляем сообщение и выводим основное меню

    def receive_user_name(message):
        cursor.execute(f"SELECT user_name FROM user WHERE chat_id = '{message.chat.id}'")
        user_name = cursor.fetchone()[0]
        return user_name

    def send_olympiad_list(message, ind):  # Функция для вывода списка олимпиад
        keyboard = types.InlineKeyboardMarkup()
        next_15 = types.InlineKeyboardButton(text="➡️Следующие 15", callback_data='next_15')
        past_15 = types.InlineKeyboardButton(text="⬅️Прошлые 15", callback_data='past_15')
        pick_olympiad = types.InlineKeyboardButton(text="✍️Выбрать олимпиаду", callback_data='pick_olympiad')

        # print(ind, len(olympiad_lst) - 1)
        if ind != len(olympiad_lst) - 1 and ind != 0:
            keyboard.add(past_15, next_15)
        elif ind == 0:
            keyboard.add(next_15)
        elif ind == len(olympiad_lst) - 1:
            keyboard.add(past_15)

        keyboard.add(pick_olympiad)

        bot.send_message(message.chat.id, olympiad_lst[ind], reply_markup=keyboard)

    def pick_olymp(message):
        name_user = receive_user_name(message)
        try:
            olympiad_name = olympiad_dict[message.text][0]

            if len(message.text.split('_')) == 1:
                main_dict[message.chat.id] = [name_user, olympiad_name]
                pick_lesson(message)
            else:
                main_dict[message.chat.id] = [name_user, olympiad_name]
                pick_participation_stage(message)
        except KeyError:
            print('ОШибка')
            bot.send_message(message.chat.id, f'Олимпиады под номером {message.text} нет в списке')
            button_message(message)

    def pick_lesson(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        list_of_subjects = []
        schet = 1
        for i in lessons_dict:
            list_of_subjects.append(
                types.InlineKeyboardButton(text=f"‍👨‍🏫{lessons_dict[i]}", callback_data=f'lesson{schet}'))
            schet += 1
        keyboard.add(*list_of_subjects)
        olympiad_name = main_dict[message.chat.id][1]
        bot.send_message(message.chat.id, f'📌Выбери предмет, по которому пишешь {olympiad_name}', reply_markup=keyboard)

    def pick_participation_stage(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        passed_registration = types.InlineKeyboardButton(text="✏️Прошёл регистрацию",
                                                         callback_data='passed_registration')
        wrote_qualifying = types.InlineKeyboardButton(text="📝Написал отборочный этап", callback_data='wrote_qualifying')
        passed_final = types.InlineKeyboardButton(text="🔝Прошёл на заключительный этап", callback_data='passed_final')
        took_final = types.InlineKeyboardButton(text="🏅Принял участие в финале(участник)", callback_data='took_final')
        final_prize_winner = types.InlineKeyboardButton(text="🥈🥉Призёр финала(диплом 2 или 3 степени)",
                                                        callback_data='final_prize_winner')
        winner_of_final = types.InlineKeyboardButton(text="🥇Победитель финала(диплом 1 степени)",
                                                     callback_data='winner_of_final')

        keyboard.add(passed_registration, wrote_qualifying, passed_final, took_final, final_prize_winner,
                     winner_of_final)

        olympiad_name = main_dict[message.chat.id][1]
        bot.send_message(message.chat.id,
                         "☑️Вы выбрали олимпиаду: " + olympiad_name +
                         '\n 📚Укажите этап участия в олимпиаде в данный момент', reply_markup=keyboard)

    def pick_mentor(message):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        schet = 1
        list_of_mentors = []
        for i in mentors_dict:
            list_of_mentors.append(
                types.InlineKeyboardButton(text=f"‍👨‍🏫{mentors_dict[i]}", callback_data=f'mentor{schet}'))
            schet += 1
        keyboard.add(*list_of_mentors)
        bot.send_message(message.chat.id, '📌Выбери своего наставника', reply_markup=keyboard)

    def correct_chak_olymp(message):
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        yes_button = types.InlineKeyboardButton(text="Да", callback_data='correct')
        no_button = types.InlineKeyboardButton(text="Нет", callback_data='not_correct')
        keyboard.add(yes_button, no_button)

        name_user = main_dict[message.chat.id][0]
        olympiad_name = main_dict[message.chat.id][1]

        if 'НТО' in olympiad_name:
            part_stage = main_dict[message.chat.id][2]
            mentor = main_dict[message.chat.id][3]
            bot.send_message(message.chat.id,
                             f'👦Имя: {name_user}\n'
                             f'🏆Олимпиада: {olympiad_name}\n'
                             f'📚Предмет: -\n'
                             f'📎Этап: {part_stage}\n'
                             f"📌Наставник: {mentor}", reply_markup=keyboard)
        else:
            lesson = main_dict[message.chat.id][2]
            part_stage = main_dict[message.chat.id][3]
            mentor = main_dict[message.chat.id][4]
            bot.send_message(message.chat.id,
                             f'👦Имя: {name_user}\n'
                             f'🏆Олимпиада: {olympiad_name}\n'
                             f'📚Предмет: {lesson}\n'
                             f'📎Этап: {part_stage}\n'
                             f"📌Наставник: {mentor}", reply_markup=keyboard)

    def new_olymp_reg(message):
        name_user = main_dict[message.chat.id][0]
        olympiad_name = main_dict[message.chat.id][1]

        if 'НТО' in olympiad_name:
            part_stage = main_dict[message.chat.id][2]
            mentor = main_dict[message.chat.id][3]
            cursor_olymp.execute('INSERT INTO olympiad VALUES (?, ?, ?, ?, ?, ?)',
                                 (None, name_user, olympiad_name, '-', part_stage, mentor))
        else:
            lesson = main_dict[message.chat.id][2]
            part_stage = main_dict[message.chat.id][3]
            mentor = main_dict[message.chat.id][4]
            cursor_olymp.execute('INSERT INTO olympiad VALUES (?, ?, ?, ?, ?, ?)',
                                 (None, name_user, olympiad_name, lesson, part_stage, mentor))
        db_olympiad.commit()

    def user_olympiad_list(message):
        user_name = receive_user_name(message)
        cursor_olymp.execute("SELECT * FROM olympiad")
        massive_big = cursor_olymp.fetchall()
        user_olympiad_string = '<b>📄Список ваших олимпиад:</b>\n\n'
        schet = 1
        for i in range(len(massive_big)):
            if massive_big[i][1] == user_name:
                if 'НТО' in massive_big[i][2]:
                    user_olympiad_string += f'<b>{schet})🎯Олимпиада:</b> {massive_big[i][2]}\n' \
                                            f'<b>Предмет:</b> -\n' \
                                            f'<b>Этап:</b> {massive_big[i][4]}\n' \
                                            f'<b>Наставник:</b> {massive_big[i][5]}\n' \
                                            f'<b>Индекс:</b> {massive_big[i][0]}\n\n'
                else:
                    user_olympiad_string += f'<b>{schet}) 🎯Олимпиада:</b> {massive_big[i][2]}\n' \
                                            f'<b>Предмет:</b> {massive_big[i][3]}\n' \
                                            f'<b>Этап:</b> {massive_big[i][4]}\n' \
                                            f'<b>Наставник:</b> {massive_big[i][5]}\n' \
                                            f'<b>Индекс:</b> {massive_big[i][0]}\n\n'
                    schet += 1

        bot.send_message(message.chat.id, user_olympiad_string, parse_mode="HTML")

    def my_rating_place(message):
        name_user = receive_user_name(message)
        olympiad_counter_list = cursor_olymp.execute(f"SELECT * FROM olympiad_rating").fetchall()
        olympiad_counter_dict = {}

        for i in range(len(olympiad_counter_list)):
            olympiad_counter_dict[olympiad_counter_list[i][1]] = olympiad_counter_list[i][2]

        olympiad_counter_dict = {k: v for k, v in
                                 sorted(olympiad_counter_dict.items(), key=lambda item: item[1], reverse=True)}
        try:
            bot.send_message(message.chat.id, f'{name_user}:\n'
                                              f'Место в рейтинге: {list(olympiad_counter_dict.keys()).index(name_user) + 1}\n'
                                              f'Количество олимпиад: {olympiad_counter_dict[name_user]}')
        except Exception:
            fio = cursor.execute(
                f"SELECT user_name FROM user WHERE chat_id = '{message.chat.id}'")
            cursor_olymp.execute("""INSERT INTO olympiad_rating VALUES (?, ?, ?)""", (None, fio, 0))
            db_olympiad.commit()
            my_rating_place(message)
        del olympiad_counter_dict
        button_message(message)

    def olympiad_rating(message):
        olympiad_counter_list = cursor_olymp.execute(f"SELECT * FROM olympiad_rating").fetchall()
        olympiad_counter_dict = {}

        for i in range(len(olympiad_counter_list)):
            olympiad_counter_dict[olympiad_counter_list[i][1]] = olympiad_counter_list[i][2]

        olympiad_counter_dict = {k: v for k, v in
                                 sorted(olympiad_counter_dict.items(), key=lambda item: item[1], reverse=True)}
        rating = ''
        schet = 1
        for k, v in olympiad_counter_dict.items():
            rating += f'<b>{schet}) {k}\n</b>' \
                      f'Количество олимпиад: {v}\n'
            schet += 1

        bot.send_message(message.chat.id, rating, parse_mode='HTML')
        del olympiad_counter_dict
        button_message(message)

    def rename_user(message):
        past_user_name = receive_user_name(message)
        global new_user_name
        new_user_name = message.text

        cursor.execute(
            f"SELECT user_name FROM user WHERE user_name = '{new_user_name}'")  # Проверяем, есть ли написанное имя в бд
        if cursor.fetchone() is None:  # Если его нет, тогда идём дальше
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            yes_button = types.InlineKeyboardButton(text="Да", callback_data='yes_rename')
            no_button = types.InlineKeyboardButton(text="Нет", callback_data='no_not_rename')
            keyboard.add(yes_button, no_button)

            bot.send_message(message.chat.id,
                             f'‼️ВНИМАНИЕ‼️\nЕсли вы смените своё ФИО, все олимпиады, которые были записаны будут записаны '
                             f'на новое введённое ФИО\n\nТекущее ФИО:{past_user_name}\nНовое ФИО: {new_user_name}\n\n'
                             f'Вы уверены, что хотите поменять текущее имя на новое?',
                             reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id,
                             'Такое имя пользователя, уже зарегистрировано. Если вы хотите поменять ваше ФИО на другое,'
                             'то попробуйте заново')
            button_message(message)

    def end_rename_user(message):
        past_user_name = receive_user_name(message)

        result_user = cursor.execute(f'SELECT id FROM user WHERE user_name="{past_user_name}"').fetchall()
        result_olympiad = cursor_olymp.execute(f'SELECT id FROM olympiad WHERE user_name="{past_user_name}"').fetchall()

        for user_id in result_user:  # перебираем результаты
            cursor.execute('UPDATE user SET user_name=? WHERE id=?',
                           (new_user_name, user_id[0]))  # обновляем записи в таблице user
            db.commit()

        for olympiad_id in result_olympiad:
            cursor_olymp.execute('UPDATE olympiad SET user_name=? WHERE id=?',
                                 (new_user_name, olympiad_id[0]))  # обновляем записи в таблице.
            db_olympiad.commit()

        bot.send_message(message.chat.id, 'Ваше ФИО обновлено')
        cursor_olymp.execute(
            'UPDATE olympiad_rating SET user_name=? WHERE user_name=?',
            (new_user_name, past_user_name))
        db_olympiad.commit()

    def del_olympiad(message):
        name_user = receive_user_name(message)
        len_do = cursor_olymp.execute('SELECT olympiad FROM olympiad WHERE user_name=?', (name_user,)).fetchall()
        cursor_olymp.execute("DELETE FROM olympiad WHERE id=?", (message.text,))
        db_olympiad.commit()

        len_posle = cursor_olymp.execute('SELECT olympiad FROM olympiad WHERE user_name=?', (name_user,)).fetchall()
        if len_do != len_posle:
            cursor_olymp.execute(
                'UPDATE olympiad_rating SET olympiad_counter=olympiad_counter - ? WHERE user_name=?',
                (1, name_user))
            db_olympiad.commit()
            bot.send_message(message.chat.id, f'Олимпиада под номером {message.text} успешно удалена')
        else:
            bot.send_message(message.chat.id, f'Олимпиады под индексом {message.text} нет в списке ваших олимпиад')
        button_message(message)

    @bot.callback_query_handler(func=lambda call: True)
    def answer(call):
        cursor.execute(f"SELECT olympiad_index FROM user WHERE chat_id = '{call.message.chat.id}'")
        olympiad_index = int(cursor.fetchone()[0])

        if call.data == 'next_15':
            bot.delete_message(call.message.chat.id, call.message.id)
            olympiad_index += 1
            cursor.execute(
                f"UPDATE user set olympiad_index = '{olympiad_index}' WHERE chat_id = '{call.message.chat.id}'")
            send_olympiad_list(call.message, olympiad_index)

        elif call.data == 'past_15':
            bot.delete_message(call.message.chat.id, call.message.id)
            olympiad_index -= 1
            cursor.execute(
                f"UPDATE user set olympiad_index = '{olympiad_index}' WHERE chat_id = '{call.message.chat.id}'")
            send_olympiad_list(call.message, olympiad_index)

        elif call.data == 'pick_olympiad':
            msg = bot.send_message(call.message.chat.id,
                                   '📋Выбери номер нужной тебе олимпиады\n\nЕсли ты выбираешь какой то из профилей НТО, '
                                   'не забудь указать через нижнее подчёркивание второе число')
            bot.register_next_step_handler(msg, pick_olymp)

        elif 'lesson' in call.data:
            name_user = receive_user_name(call.message)
            olympiad_name = main_dict[call.message.chat.id][1]
            lesson = lessons_dict[call.data]
            main_dict[call.message.chat.id].append(lesson)
            bot.delete_message(call.message.chat.id, call.message.id)
            pick_participation_stage(call.message)


        elif call.data in (
                'passed_registration', 'wrote_qualifying', 'passed_final', 'took_final', 'final_prize_winner',
                'winner_of_final'):
            name_user = main_dict[call.message.chat.id][0]
            olympiad_name = main_dict[call.message.chat.id][1]
            lesson = main_dict[call.message.chat.id][-1]
            all_olympiad = cursor_olymp.execute(f"SELECT * FROM olympiad WHERE user_name='{name_user}'").fetchall()
            flag = False

            for i in range(len(all_olympiad)):
                if all_olympiad[i][2] == olympiad_name and all_olympiad[i][3] == lesson and all_olympiad[i][4] == participation_stage_dict[call.data]:
                    flag = True
            if not flag:
                main_dict[call.message.chat.id].append(participation_stage_dict[call.data])
                bot.delete_message(call.message.chat.id, call.message.id)
                pick_mentor(call.message)
            else:
                bot.send_message(call.message.chat.id, f'Вы уже регистрировали {olympiad_name} на данной стадии участия\n\n')
                button_message(call.message)


        elif 'mentor' in call.data:
            main_dict[call.message.chat.id].append(mentors_dict[call.data])

            bot.delete_message(call.message.chat.id, call.message.id)
            correct_chak_olymp(call.message)

        elif call.data in ('correct', 'not_correct'):
            if call.data == 'correct':
                try:
                    new_olymp_reg(call.message)

                    bot.delete_message(call.message.chat.id, call.message.id)
                    bot.send_message(call.message.chat.id, 'Вы успешно зарегистрировали олимпиаду')
                    lessons = []
                    name_user = receive_user_name(call.message)
                    cursor_olymp.execute(
                        'UPDATE olympiad_rating SET olympiad_counter=olympiad_counter + ? WHERE user_name=?',
                        (1, name_user))
                    db_olympiad.commit()
                    del main_dict[call.message.chat.id]
                    button_message(call.message)
                except EOFError:
                    bot.send_message(call.message.chat.id, f'При регистрации олимпиады произошла ошибка {e}')
            else:
                bot.send_message(call.message.chat.id, 'Олимпиада не зарегистрирована')
                button_message(call.message)

        elif call.data in ('yes_rename', 'no_not_rename'):
            if call.data == 'yes_rename':
                end_rename_user(call.message)
            else:
                bot.send_message(call.message.chat.id, 'Имя пользователя не сменилось')
                button_message(call.message)

    @bot.message_handler(content_types=['text'])
    def button_answer(message):
        text = message.text

        cursor.execute(f"SELECT chat_id FROM user WHERE chat_id = '{message.chat.id}'")
        if cursor.fetchone() is None:
            if 'ФИО' in message.text.split(': '):
                name(message)
        elif text == '✏️Зарегистрироваться на олимпиаду':
            send_olympiad_list(message, 0)
        elif text == "🗑Удалить олимпиаду":
            user_olympiad_list(message)
            msg = bot.send_message(message.chat.id, 'Напишите ИНДЕКС олимпиады, которую хотите удалить')
            bot.register_next_step_handler(msg, del_olympiad)
        elif text == '📄Мои олимпиады':
            user_olympiad_list(message)
            button_message(message)
        elif text == '🏆Моё место в рейтинге':
            my_rating_place(message)
        elif text == '🔃Поменять имя':
            msg = bot.send_message(message.chat.id, 'Введите новое ФИО')
            bot.register_next_step_handler(msg, rename_user)
        elif text == '📊Статистика олимпиад':
            olympiad_rating(message)

    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as _ex:
            print(_ex)
            sleep(15)


if __name__ == '__main__':
    main()
