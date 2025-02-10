import telebot
from telebot import types
import random
import time

import controller_db as db
import config

bot = config.get_bot()
admin_ids = []

class admin_state:
    name: str
    price: int
    description: str

def info_admin(message, state):
    if message.chat.id in admin_ids:
        if message.text == '!admin':
            try: delete_last_messages(message)
            except: bot.delete_message(message.chat.id, message.id)
            finally: pass
            show_admin(message)
        elif state == 'ads':
            users = db.get_all_users()
            count = 0
            if users is not None:
                for user in users:
                    try:
                        bot.send_message(int(user[0]), message.text)
                        count += 1
                    except:
                        pass
            delete_last_messages(message)
            bot.send_message(message.chat.id, f'✅ Рассылка отправлена <b>{count} из {len(users)} пользователям</b>!', parse_mode='HTML')

        # Функционал добавления товаров
        try: 
            if state.split('_')[0] == 'add':
                add_product(message, state)
        except: pass

def inline_admin(c):
    try:
        # Обработка кнопок для работы с заказами из админ-панели
        if c.data.split('_')[1] == 'Order':
            order = db.get_order(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="✅ Отметить выполненным", callback_data=f"{c.data.split('_')[0]}_Complete")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            bot.send_message(c.message.chat.id, f'Заказ #{order[1]} (ID - {order[0]})\nПокупатель - @{order[2]}\nТовар - {order[3]}\nСтоимость - {order[4]} руб.', reply_markup=markup)
        elif c.data.split('_')[1] == 'Complete':
            db.change_order_status(c.data.split('_')[0], 'completed')

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            bot.send_message(c.message.chat.id, f'✅ Заказ #{c.data.split('_')[0]} отмечен как выполненный!')
        elif c.data.split('_')[1] == 'OrderCompleted':
            order = db.get_order(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="⚠️ Вернуть в активные заказы", callback_data=f"{c.data.split('_')[0]}_CompleteUndo")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            bot.send_message(c.message.chat.id, f'Заказ #{order[1]} (ID - {order[0]})\nПокупатель - @{order[2]}\nТовар - {order[3]}\nСтоимость - {order[4]} руб.', reply_markup=markup)
        elif c.data.split('_')[1] == 'CompleteUndo':
            db.change_order_status(c.data.split('_')[0], 'paid')

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            bot.send_message(c.message.chat.id, f'✅ Заказ #{c.data.split('_')[0]} отмечен как активный!')

        # Обработка кнопок для выбора интервала статистики
        elif c.data.split('_')[0] == 'Stats':
            get_stats(c, c.data.split('_')[1])
    except: pass

    # Обработка кнопок для вывода каталога товаров
    if c.data == 'AddProduct':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="🎁 Подарки из магазина", callback_data="AddProductPresent")
        button2 = types.InlineKeyboardButton(text="👑 Telegram Premium", callback_data="AddProductPremium")
        button3 = types.InlineKeyboardButton(text="🌐 NFT Юзернеймы", callback_data="AddProductNTFUsername")
        button4 = types.InlineKeyboardButton(text="🚀 NFT Подарки", callback_data="AddProductNFTPresent")
        button5 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button1)
        markup.add(button2)
        markup.add(button3, button4)
        markup.add(button5)
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Выбери категорию товара...', reply_markup=markup)

    # Обработка кнопок для добавления и удаления товаров
    elif c.data == 'AddProductPresent':
        db.change_state(c.message.chat.id, 'add_present')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Напиши название подарка для продажи...\nПример: Мишка')
    elif c.data == 'AddProductPremium':
        db.change_state(c.message.chat.id, 'add_premium')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Напиши название товара с длительностью премиума...\nПример: Telegram Premium (1 мес)')
    elif c.data == 'AddProductNTFUsername':
        db.change_state(c.message.chat.id, 'add_nftusername')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Введи NFT Юзернейм в формате @username...\nПример: @username')
    elif c.data == 'AddProductNFTPresent':
        db.change_state(c.message.chat.id, 'add_nftpresent')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Введи название NFT Подарка для продажи...\nПример: Мишка')
    elif c.data == 'RemoveProduct':
        products = db.get_all_products()
        markup = types.InlineKeyboardMarkup()
        try:
            for product in products:
                if product[1] == 'nftusername':
                    markup.add(types.InlineKeyboardButton(text=f"{product[1]} / {product[2]} / {product[3]} за день.", callback_data=f"{product[0]}"))
                else:
                    markup.add(types.InlineKeyboardButton(text=f"{product[1]} / {product[2]} / {product[3]} за шт.", callback_data=f"{product[0]}"))
        except:
            pass
        button4 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button4)
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Выбери товар, который хочешь удалить...', reply_markup=markup)

    # Обработка кнопок для отслеживания оплаченных и выполненных заказов из админ-панели
    elif c.data == 'ActiveOrders':
        orders = db.get_active_orders()
        count = 0

        if orders == 1:
            bot.answer_callback_query(c.id, "⚠️ Активных заказов сейчас нет.", show_alert=False)
            return

        markup = types.InlineKeyboardMarkup()
        try:
            for order in orders:
                count += 1
                if count <= 10:
                    markup.add(types.InlineKeyboardButton(text=f"#{order[1]} (ID - {order[0]})", callback_data=f"{order[1]}_Order"))
        except:
            pass
        button2 = types.InlineKeyboardButton(text="<--", callback_data="Empty")
        button3 = types.InlineKeyboardButton(text=f"Страница {1}", callback_data="Empty")
        button4 = types.InlineKeyboardButton(text="-->", callback_data="2_NextPage")
        button4 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button2, button3, button4)
        markup.add(button4)

        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Все активные заказы...', reply_markup=markup)
    elif c.data == 'CompletedOrders':
        orders = db.get_completed_orders()
        count = 0

        if orders == 1:
            bot.answer_callback_query(c.id, "⚠️ Выполненных заказов еще нет.", show_alert=False)
            return

        markup = types.InlineKeyboardMarkup()
        try:
            for order in orders:
                count += 1
                if count <= 10:
                    markup.add(types.InlineKeyboardButton(text=f"#{order[1]} (ID - {order[0]})", callback_data=f"{order[1]}_OrderCompleted"))
        except:
            pass
        button2 = types.InlineKeyboardButton(text="<--", callback_data="Empty")
        button3 = types.InlineKeyboardButton(text=f"Страница {1}", callback_data="Empty")
        button4 = types.InlineKeyboardButton(text="-->", callback_data="2_NextPage")
        button4 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button2, button3, button4)
        markup.add(button4)

        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Все выполненные заказы...', reply_markup=markup)

    # Обработка кнопки статистики
    elif c.data == 'GetStats':
        count_of_users = len(db.get_stats())

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="1 дн.", callback_data="Stats_1d")
        button2 = types.InlineKeyboardButton(text="3 дн.", callback_data="Stats_3d")
        button3 = types.InlineKeyboardButton(text="7 дн.", callback_data="Stats_7d")
        button4 = types.InlineKeyboardButton(text="10 дн.", callback_data="Stats_10d")
        button5 = types.InlineKeyboardButton(text="2 нед.", callback_data="Stats_14d")
        button6 = types.InlineKeyboardButton(text="1 мес.", callback_data="Stats_30d")
        button7 = types.InlineKeyboardButton(text="3 мес.", callback_data="Stats_90d")
        button8 = types.InlineKeyboardButton(text="Все время", callback_data="Stats_All")
        button9 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button1, button2)
        markup.add(button3, button4)
        markup.add(button5, button6)
        markup.add(button7, button8)
        markup.add(button9)

        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🥋 Всего пользователей в боте: <b>{count_of_users} чел.</b>\n🔍 Выбери временной промежуток, чтобы ознакомиться с подробной статистикой.', parse_mode='HTML', reply_markup=markup)

    # Обработка кнопки рассылки
    elif c.data == 'Ads':
        db.change_state(c.message.chat.id, 'ads')

        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToAdmin")
        markup.add(button1)

        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'🔍 Отправь текст рассылки и по желанию прикрепи картинку (одним сообщением)...', reply_markup=markup)

    elif c.data == 'BackToAdmin':
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        show_admin(c.message)
    else:
        try:
            products = db.get_all_products()
            for product in products:
                if product[0] == int(c.data):
                    db.remove_product(product[0])
                    bot.send_message(c.message.chat.id, f'✅ Товар успешно удален!')
                    try: bot.delete_message(c.message.chat.id, c.message.id)
                    except: pass
                    show_admin(c.message)
        except:
            pass

def photo_admin(message):
    try:
        state = db.get_state(message.chat.id)
    except:
        pass
    try:
        if state == 'add_present_photo':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            number = random.randint(9, 99999)
            save_path = f'{number}.jpg'
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            db.add_product('present', admin_state.name, admin_state.price, admin_state.description, save_path)
            try: bot.delete_message(message.chat.id, message.id)
            except: pass
            bot.send_message(message.chat.id, f'✅ Товар успешно добавлен!')
            show_admin(message)
        elif state == 'add_premium_photo':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            number = random.randint(9, 99999)
            save_path = f'{number}.jpg'
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            db.add_product('premium', admin_state.name, admin_state.price, admin_state.description, save_path)
            try: bot.delete_message(message.chat.id, message.id)
            except: pass
            bot.send_message(message.chat.id, f'✅ Товар успешно добавлен!')
            show_admin(message)
        elif state == 'add_nftusername_photo':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            number = random.randint(9, 99999)
            save_path = f'{number}.jpg'
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            db.add_product('nftusername', admin_state.name, admin_state.price, admin_state.description, save_path)
            try: bot.delete_message(message.chat.id, message.id)
            except: pass
            bot.send_message(message.chat.id, f'✅ Товар успешно добавлен!')
            show_admin(message)
        elif state == 'add_nftpresent_photo':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            number = random.randint(9, 99999)
            save_path = f'{number}.jpg'
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)
            db.add_product('nftpresent', admin_state.name, admin_state.price, admin_state.description, save_path)
            try: bot.delete_message(message.chat.id, message.id)
            except: pass
            bot.send_message(message.chat.id, f'✅ Товар успешно добавлен!')
            show_admin(message)
        elif state == 'ads':
            photo = message.photo[-1]
            file_info = bot.get_file(photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            number = random.randint(9, 99999)
            save_path = f'{number}.jpg'
            with open(save_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            users = db.get_all_users()
            count = 0
            if users is not None:
                for user in users:
                    try:
                        bot.send_photo(int(user[0]), open(save_path, 'rb'), message.caption)
                        count += 1
                    except:
                        pass
            try: bot.delete_message(message.chat.id, message.id)
            except: pass
            bot.send_message(message.chat.id, f'✅ Рассылка отправлена <b>{count} из {len(users)} пользователям!</b>', parse_mode='HTML')
            show_admin(message)
    except:
        try: bot.delete_message(message.chat.id, message.id)
        except: pass
        bot.send_message(message.chat.id, f'⚠️ Возникла ошибка при добавлении фото. Возможно, фото с таким названием уже существует в файлах сервера. Попробуй переименовать изображение.')
        show_admin(message)

def show_admin(message):
    db.change_state(message.chat.id, 'None')

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="1️⃣ Добавить товар", callback_data="AddProduct")
    button2 = types.InlineKeyboardButton(text="2️⃣ Удалить товар", callback_data="RemoveProduct")
    button3 = types.InlineKeyboardButton(text="3️⃣ Активные заказы", callback_data="ActiveOrders")
    button4 = types.InlineKeyboardButton(text="4️⃣ Завершенные заказы", callback_data="CompletedOrders")
    button5 = types.InlineKeyboardButton(text="5️⃣ Рассылка", callback_data="Ads")
    button6 = types.InlineKeyboardButton(text="6️⃣ Статистика", callback_data="GetStats")
    button7 = types.InlineKeyboardButton(text="🏠 Выйти из админ-панели", callback_data="BackToMenu")
    markup.add(button1, button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5, button6)
    markup.add(button7)

    bot.send_message(message.chat.id, f'🚀 Добро пожаловать в админ панель!', reply_markup=markup)

def delete_last_messages(message):
    """Удаляет последние два сообщения в диалоге."""
    print(message.text)
    try:
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message.id - 1)
    except: pass

def add_product(message, state):    
    try:
        if state.split('_')[2] == 'price': 
            # Состояния - add_present_price, add_premium_price, add_nftusername_price, add_nftpresent_price
            try: 
                admin_state.price = int(message.text)
            except:
                bot.send_message(message.chat.id, f'⚠️ Стоимость введена неверно. Введи ее <b>целым числом</b>!\n💡 Пример: <b>59</b>', parse_mode='HTML')
                return
            db.change_state(message.chat.id, f'add_{state.split('_')[1]}_description')
            delete_last_messages(message)
            bot.send_message(message.chat.id, f'🔍 Напиши описание для товара... Если описание отсутствует отправь знак "-".\n💡 Пример: <b>Подробное описание товара.</b>', parse_mode='HTML')
        elif state.split('_')[2] == 'description': 
            # Состояния - add_present_description, add_premium_description, add_nftusername_description, add_nftpresent_description
            admin_state.description = message.text
            db.change_state(message.chat.id, f'add_{state.split('_')[1]}_photo')
            delete_last_messages(message)
            bot.send_message(message.chat.id, f'🔍 Отправь фото для товара... Если картинка отсутствует, отправь знак "-".')
        elif state.split('_')[2] == 'photo': 
            # Состояния - add_present_photo, add_premium_photo, add_nftusername_photo, add_nftpresent_photo
            if message.text == '-':
                db.add_product(f'{state.split('_')[1]}', admin_state.name, admin_state.price, admin_state.description, message.text)
                delete_last_messages(message)
                bot.send_message(message.chat.id, f'✅ Товар успешно добавлен!')
                show_admin(message)
    except: 
        # Состояния - add_present, add_premium, add_nftusername, add_nftpresent
        if state.split('_')[1] == 'nftusername':
            if message.text[0] == '@': 
                admin_state.name = message.text
            else: 
                admin_state.name = f'@{message.text}'
        else: 
            admin_state.name = message.text
        db.change_state(message.chat.id, f'{state}_price')
        delete_last_messages(message)
        bot.send_message(message.chat.id, f'🔍 Напиши стоимость товара в рублях...\n💡 Пример: <b>59</b>', parse_mode='HTML')

def get_stats(c, interval):
    result = db.get_earnings(interval)
    time_now = int(time.time())
    time_end = 0

    earnings_general = 0
    earnings_stars = 0
    count_of_stars = 0
    earnings_present = 0
    present_text = ''
    earnings_premium = 0
    premium_text = ''
    earnings_nftusername = 0
    nftusername_text = ''
    earnings_nftpresent = 0
    nftpresent_text = ''

    text = ''
    if interval == '1d': 
        text = '1 день'
        time_end = time_now - 86400
    elif interval == '3d': 
        text = '3 дня'
        time_end = time_now - 259200
    elif interval == '7d': 
        text = '7 дней'
        time_end = time_now - 604800
    elif interval == '10d': 
        text = '10 дней'
        time_end = time_now - 864000
    elif interval == '14d': 
        text = '2 недели'
        time_end = time_now - 1209600
    elif interval == '30d': 
        text = '1 месяц'
        time_end = time_now - 2592000
    elif interval == '90d': 
        text = '3 месяца'
        time_end = time_now - 7776000
    elif interval == 'All': 
        text = 'все время'

    for res in result:
        if int(res[9]) > time_end or time_end == 0:
            earnings_general += int(res[4])
            if res[8] == 'stars':
                earnings_stars += int(res[4])
                count_of_stars = int(res[4] / 2)
            elif res[8] == 'present':
                earnings_present += int(res[4])
                present_text += f' {res[3]} - {int(res[4])} руб. /'
            elif res[8] == 'premium':
                earnings_premium += int(res[4])
                premium_text += f' {res[3]} - {int(res[4])} руб. /'
            elif res[8] == 'nftusername':
                earnings_nftusername += int(res[4])
                nftusername_text += f' {res[3]} - {int(res[4])} руб. ({int(res[7])} дн.) /'
            elif res[8] == 'nftpresent':
                earnings_nftpresent += int(res[4])
                nftpresent_text += f' {res[3]} - {int(res[4])} руб. /'

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="GetStats")
    markup.add(button1)

    try: bot.delete_message(c.message.chat.id, c.message.id)
    except: pass
    bot.send_message(c.message.chat.id, 
        f'🔍 Статистика за <b>{text}.</b>\n'
        f'💸 Заработок за {text}: <b>{earnings_general} руб.</b>\n'
        f'1️⃣ Проданы звезды в количестве <b>{count_of_stars} шт.</b> на сумму <b>{earnings_stars} руб.</b>\n'
        f'2️⃣ Проданы подарки на сумму <b>{earnings_present} руб.</b>:{present_text[:-1]}\n'
        f'3️⃣ Продан Premium на сумму <b>{earnings_premium} руб.</b>:{premium_text[:-1]}\n'
        f'4️⃣ Проданы NFT Юзернеймы на сумму <b>{earnings_nftusername} руб.</b>:{nftusername_text[:-1]}\n'
        f'5️⃣ Проданы NFT Подарки на сумму <b>{earnings_nftpresent} руб.</b>:{nftpresent_text[:-1]}\n',
        parse_mode='HTML', reply_markup=markup)