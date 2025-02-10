import telebot
import time
from telebot import types
import requests
import re

import config
from admin import info_admin, inline_admin, photo_admin
import controller_db as db
import payments_quickpay as pq
import payments_history as ph
import urls as URLs

bot = config.get_bot()
headers = config.get_headers()
crypto_token = config.get_crypto

db.initialize_tables()

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def welcome(message):
    db.add_user_id(message.chat.id)

    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="💫 Товары", callback_data='AllProducts')
    button2 = types.InlineKeyboardButton(text="⌛️ Заказы", callback_data='MyOrders')
    button3 = types.InlineKeyboardButton(text="📨 Отзывы", url=URLs.reviews_channel)
    button4 = types.InlineKeyboardButton(text="🛠 Поддержка", url=URLs.support_channel)
    button5 = types.InlineKeyboardButton(text="🌐 Наш канал", url=URLs.main_channel)
    markup.add(button1, button2)
    markup.add(button3)
    markup.add(button4, button5)

    bot.send_message(message.chat.id, f'💫 Добро пожаловать в главное меню магазина, <b>{message.chat.username}</b>!\n🔍 Здесь ты найдешь различные предложения для Telegram: покупка звезд, премиум-подписок, NFT-юзернеймов и уникальных подарков.', parse_mode='HTML', reply_markup=markup)

# Обработчик текстовых сообщений от пользователя
@bot.message_handler()
def info(message):
    try:
        state = db.get_state(message.chat.id)
    except:
        unknown_situation()

    try:
        # Обработка состояния для выбора количества звезд для покупки
        if state == 'stars_choose':
            try:
                count_of_stars = int(message.text)
                if count_of_stars < 50:
                    markup = types.InlineKeyboardMarkup()
                    button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                    markup.add(button2)

                    bot.send_message(message.chat.id, f'⚠️ Минимальное количество звезд для покупки - <b>50 шт.</b>\n🔍 Пожалуйста, введи корректное количество звезд...', parse_mode='HTML', reply_markup=markup)

                    delete_last_messages(message)
                else:
                    markup = types.InlineKeyboardMarkup()
                    button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                    markup.add(button2)

                    bot.send_message(message.chat.id, f'🔍 Введи имя пользователя Telegram, на которое хотел бы купить звезды.\n💡 Пример: <b>@username</b>', parse_mode='HTML', reply_markup=markup)

                    db.change_state(message.chat.id, f'stars_username={count_of_stars}')

                    delete_last_messages(message)
            except:
                markup = types.InlineKeyboardMarkup()
                button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                markup.add(button2)

                delete_last_messages(message)
                bot.send_message(message.chat.id, f'🔍 Введи целое количество звезд, которое хочешь купить...\n💡 Пример: <b>50</b>', parse_mode='HTML', reply_markup=markup)
        elif state.split('=')[0] == 'stars_username':
            count_of_stars = int(state.split('=')[1])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💳 Картой", callback_data=f"{count_of_stars * 2}_BuyStars")
            button2 = types.InlineKeyboardButton(text="💎 Криптой", callback_data=f"{count_of_stars * 2}_BuyStarsCrypto")
            button3 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToStars")
            markup.add(button1, button2)
            markup.add(button3)

            delete_last_messages(message)

            if message.text[0] == '@':
                bot.send_message(message.chat.id, f'💫 Товар: <b>{count_of_stars}</b> звезд Telegram>\n💎 Стоимость: <b>{count_of_stars * 2} руб.</b>\n🥋 Получатель: <b>{message.text}</b>\n🔖 Описание: «Звезды» — внутренняя валюта Telegram.', parse_mode='HTML', reply_markup=markup)
            else:
                bot.send_message(message.chat.id, f'💫 Товар: <b>{count_of_stars}</b> звезд Telegram\n💎 Стоимость: <b>{count_of_stars * 2} руб.</b>\n🥋 Получатель: <b>@{message.text}</b>\n🔖 Описание: «Звезды» — внутренняя валюта Telegram.', parse_mode='HTML', reply_markup=markup)
                
                db.change_state(message.chat.id, 'None')
        elif state.split('=')[0] == 'order':
            product_id = state.split('=')[1]
            product = db.get_product(product_id)

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💳 Картой", callback_data=f"{product_id}_Buy")
            button2 = types.InlineKeyboardButton(text="💎 Криптой", callback_data=f"{product_id}_BuyCrypto")
            button3 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToPresent")
            markup.add(button1, button2)
            markup.add(button3)

            delete_last_messages(message)

            text = ''
            if product[1] == 'present':
                text = 'Подарок '

            if product[5] == '-':
                if product[4] == '-':
                    if message.text[0] == '@':
                        bot.send_message(message.chat.id, f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>{message.text}</b>', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{message.text}</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    if message.text[0] == '@':
                        bot.send_message(message.chat.id, f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>{message.text}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{message.text}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            else:
                if product[4] == '-':
                    if message.text[0] == '@':
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>{message.text}</b>', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{message.text}</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    if message.text[0] == '@':
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>{message.text}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{text}{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{message.text}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
        elif state.split('=')[0] == 'nftusername':
            product_id = state.split('=')[1]

            markup = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
            markup.add(button2)
            delete_last_messages(message)
            try:
                phone_number = int(message.text)
                bot.send_message(message.chat.id, f'🔍 Введи количество дней <b>(от 7)</b>, на которое хочешь арендовать юзернейм.\n💡 Пример: <b>7</b>', parse_mode='HTML', reply_markup=markup)
                db.change_state(message.chat.id, f'nftusername_duration={product_id}={phone_number}')
            except:
                bot.send_message(message.chat.id, f'⚠️ Номер телефона введен неверно! В номере должны быть только цифры, знак "+" ставить не нужно.\n💡 Пример: <b>89652223333</b>', parse_mode='HTML', reply_markup=markup)
                db.change_state(message.chat.id, f'nftusername={product_id}')
        elif state.split('=')[0] == 'nftusername_duration':
            product_id = state.split('=')[1]
            product = db.get_product(product_id)
            phone_number = state.split('=')[2]
            try:
                duration = int(message.text)
                if duration < 7:
                    raise ValueError('Not enough days specified.')
                product = db.get_product(product_id)
                price = duration * int(product[3])
                db.change_state(message.chat.id, f'nftusername_buy={product_id}={phone_number}={duration}')

                markup = types.InlineKeyboardMarkup()
                button1 = types.InlineKeyboardButton(text="💳 Картой", callback_data=f"{product_id}_Buy")
                button2 = types.InlineKeyboardButton(text="💎 Криптой", callback_data=f"{product_id}_BuyCrypto")
                button3 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToNFTUsername")
                markup.add(button1, button2)
                markup.add(button3)

                delete_last_messages(message)

                if product[5] == '-':
                    if product[4] == '-':
                        bot.send_message(message.chat.id, f'💫 Товар: <b>NFT Юзернейм ({product[2]})</b>\n💎 Стоимость: <b>{price} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_message(message.chat.id, f'💫 Товар: <b>NFT Юзернейм ({product[2]})</b>\n💎 Стоимость: <b>{price} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
                else:
                    if product[4] == '-':
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>NFT Юзернейм ({product[2]})</b>\n💎 Стоимость: <b>{price} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>', parse_mode='HTML', reply_markup=markup)
                    else:
                        bot.send_photo(message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>NFT Юзернейм ({product[2]})</b>\n💎 Стоимость: <b>{price} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            except:
                markup = types.InlineKeyboardMarkup()
                button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                markup.add(button2)
                delete_last_messages(message)
                bot.send_message(message.chat.id, f'⚠️ Количество дней введено неверно. Укажи количество дней для аренды юзернейма числом, не меньше 7.\n💡 Пример: <b>7</b>', parse_mode='HTML', reply_markup=markup)
                db.change_state(message.chat.id, f'nftusername_duration={product_id}={phone_number}')
        else:
            info_admin(message, state)
    except: pass

@bot.callback_query_handler(func=lambda c:True)
def inline(c):
    try:
        # Обработка оплаты картой
        if c.data.split('_')[1] == 'Buy':
            buy_card(c)
        elif c.data.split('_')[1] == 'CheckPayment':
            check_payment_card(c)

        # Обработка оплаты через CryptoBot
        elif c.data.split('_')[1] == 'BuyCrypto':
            buy_crypto(c)
        elif c.data.split('_')[1] == 'CheckPaymentCrypto':
            check_payment_crypto(c)

        # Обработка кнопки покупки звезд с помощью YooMoney (функционал отличается от покупки других товаров)
        elif c.data.split('_')[1] == 'BuyStars':
            loading_animation(c.message)
            username = ''
            words = re.split(r'[ \n]+', c.message.text)
            for word in words:
                if word[0] == '@':
                    username = word[1:]

            price = int(c.data.split('_')[0])
            transaction = pq.create_transaction(price, c.message.chat.id)
            orderid = db.create_new_order(transaction[1], username, f'Звезды ({int(price / 2)} шт.)', price, c.message.chat.id, type_of_product='stars')

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=transaction[0])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPayment")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)

            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>Звезды ({int(price / 2)} шт.)</b>\n💎 Стоимость: <b>{int(price)} руб.</b>\n🥋 Получатель: <b>@{username}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        
        # Обработка кнопки покупки звезд с помощью CryptoBot (функционал отличается от покупки других товаров)
        elif c.data.split('_')[1] == 'BuyStarsCrypto':
            loading_animation(c.message)
            username = ''
            words = re.split(r'[ \n]+', c.message.text)
            for word in words:
                if word[0] == '@':
                    username = word[1:]

            price_rub = int(c.data.split('_')[0])
            price = round(float(price_rub / 90), 1)

            response = requests.get('https://pay.crypt.bot/api/createInvoice', headers=headers, params={'asset': 'USDT', 'amount': price})
            response = response.json()
            orderid = response['result']['invoice_id']
            orderid = db.create_new_order(f'{response['result']['invoice_id']}', username, f'Звезды ({int(price_rub / 2)} шт.)', price_rub, c.message.chat.id, type_of_product='stars')

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=response['result']['pay_url'])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPaymentCrypto")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)

            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>Звезды ({int(price_rub / 2)} шт.)</b>\n💎 Стоимость: <b>{int(price_rub)} руб.</b>\n🥋 Получатель: <b>@{username}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        
        # Обработка кнопок для переключения между страницами
        elif c.data.split('_')[1] == 'NextPage':
            try:
                page = int(c.data.split('_')[0])
                orders = db.get_active_orders()
                skip = 0
                count = 10 * page - 10
                count_end = count + 10

                if len(orders) < count or page == 0:
                    return

                markup = types.InlineKeyboardMarkup()
                try:
                    for order in orders:
                        skip += 1
                        if skip > count and skip <= count_end:
                            markup.add(types.InlineKeyboardButton(text=f"#{order[1]} (ID - {order[0]})", callback_data=f"{order[1]}_Order"))
                except:
                    pass
                button2 = types.InlineKeyboardButton(text="<--", callback_data=f"{page - 1}_NextPage")
                button3 = types.InlineKeyboardButton(text=f"Страница {page}", callback_data="None")
                button4 = types.InlineKeyboardButton(text="-->", callback_data=f"{page + 1}_NextPage")
                button5 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                markup.add(button2, button3, button4)
                markup.add(button5)

                try: bot.delete_message(c.message.chat.id, c.message.id)
                except: pass
                bot.send_message(c.message.chat.id, f'📜 <b>История заказов</b>\n🔍 Здесь ты можешь увидеть свои предыдущие покупки и их статусы.', parse_mode='HTML', reply_markup=markup)
            except:
                pass
        elif c.data.split('_')[1] == 'UserNextPage':
            try:
                page = int(c.data.split('_')[0])
                orders = db.get_user_orders(c.message.chat.id)
                skip = 0
                count = 5 * page - 5
                count_end = count + 5

                if len(orders) < count or page == 0:
                    return

                markup = types.InlineKeyboardMarkup()
                try:
                    for order in orders:
                        skip += 1
                        if skip > count and skip <= count_end:
                            if order[5] == 'paid':
                                markup.add(types.InlineKeyboardButton(text=f"⌛️ Заказ #{order[1]} - Оплачен", callback_data=f"{order[1]}_UserCheckOrder"))
                            elif order[5] == 'completed':
                                markup.add(types.InlineKeyboardButton(text=f"✅ Заказ #{order[1]} - Выполнен", callback_data=f"{order[1]}_UserCheckOrder"))
                except:
                    pass
                button2 = types.InlineKeyboardButton(text="<--", callback_data=f"{page - 1}_UserNextPage")
                button3 = types.InlineKeyboardButton(text=f"Страница {page}", callback_data="None")
                button4 = types.InlineKeyboardButton(text="-->", callback_data=f"{page + 1}_UserNextPage")
                button5 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
                markup.add(button2, button3, button4)
                markup.add(button5)

                try: bot.delete_message(c.message.chat.id, c.message.id)
                except: pass
                bot.send_message(c.message.chat.id, f'📜 <b>История заказов</b>\n🔍 Здесь ты можешь увидеть свои предыдущие покупки и их статусы.', parse_mode='HTML', reply_markup=markup)
            except: pass

        # Первый шаг в покупке товара - процесс введения юзернейма
        elif c.data.split('_')[1] == 'UsernameStep':
            markup = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
            markup.add(button2)

            bot.send_message(c.message.chat.id, f'🔍 Введи имя пользователя Telegram, на которое хочешь купить товар...\n💡 Пример: <b>@username</b>', parse_mode='HTML', reply_markup=markup)
            db.change_state(c.message.chat.id, f'order={c.data.split('_')[0]}')

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
        elif c.data.split('_')[1] == 'NFTUsernameStep':
            markup = types.InlineKeyboardMarkup()
            button2 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
            markup.add(button2)

            bot.send_message(c.message.chat.id, f'🔍 Введи номер телефона от аккаунта Telegram, на который хочешь купить юзернейм...\n💡 Пример: <b>89652223333</b>', parse_mode='HTML', reply_markup=markup)
            db.change_state(c.message.chat.id, f'nftusername={c.data.split('_')[0]}')

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
    except: pass

    # Обработка кнопки для вывода всех заказов пользователя
    if c.data == 'MyOrders':
        show_user_orders(c)

    # Обработка кнопки для вывода главного каталога товаров
    elif c.data == 'AllProducts':
        product_list(c.message)

    # Обработка кнопок для вывода товаров в наличии
    elif c.data == 'StarsCatalog':
        stars_catalog(c.message)
    elif c.data == 'PresentCatalog':
        loading_animation(c.message)
        catalog(c.message, 'present')
    elif c.data == 'PremiumCatalog':
        loading_animation(c.message)
        catalog(c.message, 'premium')
    elif c.data == 'NFTUsernameCatalog':
        loading_animation(c.message)
        catalog(c.message, 'nftusername')
    elif c.data == 'NFTPresentCatalog':
        loading_animation(c.message)
        catalog(c.message, 'nftpresent')

    # Обработка кнопок для возвращения обратно
    elif c.data == 'BackToMenu':
        db.change_state(c.message.chat.id, 'None')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        welcome(c.message)
    elif c.data == 'Welcome':
        welcome(c.message)
    elif c.data == 'BackToStars':
        db.change_state(c.message.chat.id, 'None')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        stars_catalog(c.message)
    elif c.data == 'BackToPresent':
        db.change_state(c.message.chat.id, 'None')
        loading_animation(c.message)
        catalog(c.message, 'present')
    elif c.data == 'BackToPremium':
        db.change_state(c.message.chat.id, 'None')
        loading_animation(c.message)
        catalog(c.message, 'premium')
    elif c.data == 'BackToNFTUsername':
        db.change_state(c.message.chat.id, 'None')
        loading_animation(c.message)
        catalog(c.message, 'nftusername')
    elif c.data == 'BackToNFTPresent':
        db.change_state(c.message.chat.id, 'None')
        loading_animation(c.message)
        catalog(c.message, 'nftpresent')
    
    # Проверка на вызов админ-панели
    else:
        inline_admin(c)
        
    try:
        # Вывод информации о выбранном пользователем товаре
        if c.data.split('_')[1] == 'PresentProduct':
            product = db.get_product(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Купить", callback_data=f"{c.data.split('_')[0]}_UsernameStep")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToPresent")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            if product[5] == '-':
                if product[4] == '-':
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>Подарок {product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>Подарок {product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            else:
                if product[4] == '-':
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>Подарок {product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>Подарок {product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
        elif c.data.split('_')[1] == 'PremiumProduct':
            product = db.get_product(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Купить", callback_data=f"{c.data.split('_')[0]}_UsernameStep")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToPremium")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            if product[5] == '-':
                if product[4] == '-':
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            else:
                if product[4] == '-':
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
        elif c.data.split('_')[1] == 'NFTUsernameProduct':
            product = db.get_product(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Купить", callback_data=f"{c.data.split('_')[0]}_NFTUsernameStep")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToNFTUsername")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            if product[5] == '-':
                if product[4] == '-':
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            else:
                if product[4] == '-':
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
        elif c.data.split('_')[1] == 'NFTPresentProduct':
            product = db.get_product(c.data.split('_')[0])

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Купить", callback_data=f"{c.data.split('_')[0]}_UsernameStep")
            button2 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="BackToNFTPresent")
            markup.add(button1)
            markup.add(button2)

            try: bot.delete_message(c.message.chat.id, c.message.id)
            except: pass
            if product[5] == '-':
                if product[4] == '-':
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_message(c.message.chat.id, f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
            else:
                if product[4] == '-':
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>', parse_mode='HTML', reply_markup=markup)
                else:
                    bot.send_photo(c.message.chat.id, open(product[5], 'rb'), f'💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🔖 Описание: {product[4]}', parse_mode='HTML', reply_markup=markup)
    except:
        pass

# Обработка фото (только для администраторов)
@bot.message_handler(content_types='photo')
def get_photo(message):
    photo_admin(message)

def product_list(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text=f"✨ Звезды", callback_data="StarsCatalog")
    button2 = types.InlineKeyboardButton(text=f"👑 TG Premium", callback_data="PremiumCatalog")
    button3 = types.InlineKeyboardButton(text=f"🎁 Подарки из магазина", callback_data="PresentCatalog")
    button4 = types.InlineKeyboardButton(text=f"🌐 NFT Юзернеймы", callback_data="NFTUsernameCatalog")
    button5 = types.InlineKeyboardButton(text=f"🚀 NFT Подарки", callback_data="NFTPresentCatalog")
    button6 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
    markup.add(button1, button2)
    markup.add(button3)
    markup.add(button4, button5)
    markup.add(button6)

    try: bot.delete_message(message.chat.id, message.id)
    except: pass
    bot.send_message(message.chat.id, f'📦 <b>Каталог товаров</b>\n🔍 Выбери, что тебя интересует, чтобы узнать подробнее...', parse_mode='HTML', reply_markup=markup)

def stars_catalog(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="AllProducts")
    markup.add(button1)

    try: bot.delete_message(message.chat.id, message.id)
    except: pass
    bot.send_message(message.chat.id, f'🔍 Введи количество звезд, которое хочешь купить...', reply_markup=markup)
    db.change_state(message.chat.id, 'stars_choose')

def catalog(message, product_type: str):
    """Вывод каталога товаров. Доступные типы товаров (product_type) - present, premium, nftusername, nftpresent"""
    products = db.get_all_products()

    label = ''
    text = ''
    if product_type == 'present': 
        label = 'Present'
        text = f'🎁 Поделитесь радостью с друзьями через <b>подарки в Telegram.</b>\n🔍 Выбери нужный подарок, чтобы узнать о нем подробнее...'
    elif product_type == 'premium': 
        label = 'Premium'
        text = f'👑 Получи максимум возможностей с <b>Telegram Premium</b>: улучшенное качество медиа, эксклюзивные стикеры и многое другое!'
    elif product_type == 'nftusername': 
        label = 'NFTUsername'
        text = f'🌐 Обладайте уникальным юзернеймом в Telegram. <b>NFT-юзернеймы</b> гарантируют ваш эксклюзивный цифровой идентификатор.\n🔍 Выбери свой будущий юзернейм, чтобы узнать о нем подробнее...'
    elif product_type == 'nftpresent': 
        label = 'NFTPresent'
        text = f'🚀 Дарите по-настоящему <b>эксклюзивные цифровые подарки!</b>\n🔍 Выбери нужный NFT-подарок, чтобы узнать о нем подробнее...'

    markup = types.InlineKeyboardMarkup()
    try:
        for product in products:
            if product[1] == product_type:
                markup.add(types.InlineKeyboardButton(text=f"{product[2]}", callback_data=f"{product[0]}_{label}Product"))
    except:
        pass
    button1 = types.InlineKeyboardButton(text="↩️ Назад", callback_data="AllProducts")
    markup.add(button1)

    try: bot.delete_message(message.chat.id, message.id)
    except: bot.delete_message(message.chat.id, message.id + 1)
    finally: pass
    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=markup)

def show_user_orders(c):
    orders = db.get_user_orders(c.message.chat.id)
    count = 0

    if orders == 0:
        bot.answer_callback_query(c.id, "⚠️ У тебя нет оплаченных или выполненных заказов.", show_alert=False)
        return
    
    loading_animation(c.message)

    markup = types.InlineKeyboardMarkup()
    try:
        for order in orders:
            count += 1
            if count <= 5:
                if order[5] == 'paid':
                    markup.add(types.InlineKeyboardButton(text=f"⌛️ Заказ #{order[1]} - Оплачен", callback_data=f"{order[1]}_UserCheckOrder"))
                elif order[5] == 'completed':
                    markup.add(types.InlineKeyboardButton(text=f"✅ Заказ #{order[1]} - Выполнен", callback_data=f"{order[1]}_UserCheckOrder"))
    except:
        pass
    button2 = types.InlineKeyboardButton(text="<--", callback_data="Empty")
    button3 = types.InlineKeyboardButton(text=f"Страница {1}", callback_data="Empty")
    button4 = types.InlineKeyboardButton(text="-->", callback_data="2_UserNextPage")
    button5 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
    markup.add(button2, button3, button4)
    markup.add(button5)

    try: bot.delete_message(c.message.chat.id, c.message.id + 1)
    except: pass
    bot.send_message(c.message.chat.id, f'📜 <b>История заказов</b>\n🔍 Здесь ты можешь увидеть свои предыдущие покупки и их статусы.', parse_mode='HTML', reply_markup=markup)

def buy_card(c):
    loading_animation(c.message)
    try: state = db.get_state(c.message.chat.id)
    except: pass

    if state.split('=')[0] == 'nftusername_buy':
        try:
            product_id = state.split('=')[1]
            product = db.get_product(product_id)
            phone_number = state.split('=')[2]
            duration = int(state.split('=')[3])
            price = duration * int(product[3])

            transaction = pq.create_transaction(int(price), c.message.chat.id)
            orderid = db.create_new_order(transaction[1], phone_number, product[2], price, c.message.chat.id, type_of_product='nftusername', duration=int(duration))

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=transaction[0])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPayment")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)
            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{price} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        except:
            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'⚠️ Возникла проблема при создании счета. Попробуйте связаться с администратором.')
    else:
        try:
            product = db.get_product(c.data.split('_')[0])

            try:
                username = ''
                words = re.split(r'[ \n]+', c.message.text)
                for word in words:
                    if word[0] == '@':
                        username = word[1:]
            except:
                username = ''
                words = re.split(r'[ \n]+', c.message.caption)
                for word in words:
                    if word[0] == '@':
                        username = word[1:]

            transaction = pq.create_transaction(int(product[3]), c.message.chat.id)
            orderid = db.create_new_order(transaction[1], username, product[2], product[3], c.message.chat.id, type_of_product=f'{product[1]}')

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=transaction[0])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPayment")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)

            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{username}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        except:
            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'⚠️ Возникла проблема при создании счета. Попробуйте связаться с администратором.')

def check_payment_card(c):
    status = ph.get_operation_status(c.data.split('_')[0])
    if status == 1:
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="🛠 Связаться с поддержкой", url=URLs.support_channel)
        markup.add(button1)
        bot.send_message(c.message.chat.id, f'⚠️ Заказ #{c.data.split('_')[0]} еще не оплачен. Если у вас возникли проблемы с заказом - обратитесь в поддержку.', reply_markup=markup)
    else:
        db.change_order_status(c.data.split('_')[0], 'paid')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'💸 Заказ #{c.data.split('_')[0]} оплачен! Наш администратор скоро свяжется с вами для выполнения заказа.')

def buy_crypto(c):
    loading_animation(c.message)
    try: state = db.get_state(c.message.chat.id)
    except: pass

    if state.split('=')[0] == 'nftusername_buy':
        try:
            product_id = state.split('=')[1]
            product = db.get_product(product_id)
            phone_number = state.split('=')[2]
            duration = int(state.split('=')[3])
            price_usd = round(float(product[3] * duration / 90), 1)
            price_rub = product[3] * duration

            response = requests.get('https://pay.crypt.bot/api/createInvoice', headers=headers, params={'asset': 'USDT', 'amount': price_usd})
            response = response.json()
            orderid = response['result']['invoice_id']
            orderid = db.create_new_order(f'{response['result']['invoice_id']}', phone_number, product[2], price_rub, c.message.chat.id, type_of_product='nftusername', duration=int(duration))

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=response['result']['pay_url'])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPaymentCrypto")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)

            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{price_rub} руб.</b>\n⌛️ Длительность: <b>{duration} дней.</b>\n🥋 Получатель: <b>{phone_number}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        except:
            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'⚠️ Возникла проблема при создании счета. Попробуйте связаться с администратором.')
    else:
        try:
            try:
                username = ''
                words = re.split(r'[ \n]+', c.message.text)
                for word in words:
                    if word[0] == '@':
                        username = word[1:]
            except:
                username = ''
                words = re.split(r'[ \n]+', c.message.caption)
                for word in words:
                    if word[0] == '@':
                        username = word[1:]

            product = db.get_product(c.data.split('_')[0])
            price = round(float(product[3] / 90), 1)

            response = requests.get('https://pay.crypt.bot/api/createInvoice', headers=headers, params={'asset': 'USDT', 'amount': price})
            response = response.json()
            orderid = response['result']['invoice_id']
            orderid = db.create_new_order(f'{response['result']['invoice_id']}', username, product[2], product[3], c.message.chat.id, type_of_product=f'{product[1]}')

            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton(text="💸 Оплатить", url=response['result']['pay_url'])
            button2 = types.InlineKeyboardButton(text="🔍 Проверить", callback_data=f"{orderid}_CheckPaymentCrypto")
            button3 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="Welcome")
            markup.add(button1, button2)
            markup.add(button3)

            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'🔖 Номер заказа <b>#{orderid}</b>\n💫 Товар: <b>{product[2]}</b>\n💎 Стоимость: <b>{product[3]} руб.</b>\n🥋 Получатель: <b>@{username}</b>\n⚠️ После оплаты нажмите кнопку "Проверить".', parse_mode='HTML', reply_markup=markup)
        except:
            try: bot.delete_message(c.message.chat.id, c.message.id + 1)
            except: pass
            bot.send_message(c.message.chat.id, f'⚠️ Возникла проблема при создании счета. Попробуйте связаться с администратором.')

def check_payment_crypto(c):
    response = requests.get('https://pay.crypt.bot/api/getInvoices', headers=headers, params={'invoice_ids': f'{c.data.split('_')[0]}'})
    response = response.json()
    status = response['result']['items'][0]['status']
    if status == 'active' or status == 'expired':
        markup = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="🛠 Связаться с поддержкой", url=URLs.support_channel)
        markup.add(button1)
        bot.send_message(c.message.chat.id, f'⚠️ Заказ #{c.data.split('_')[0]} еще не оплачен. Если у вас возникли проблемы с заказом - обратитесь в поддержку.', reply_markup=markup)
    elif status == 'paid':
        db.change_order_status(c.data.split('_')[0], 'paid')
        try: bot.delete_message(c.message.chat.id, c.message.id)
        except: pass
        bot.send_message(c.message.chat.id, f'💸 Заказ #{c.data.split('_')[0]} оплачен! Наш администратор скоро свяжется с вами для выполнения заказа.')

def delete_last_messages(message):
    """Удаляет последние два сообщения в диалоге."""
    print(message.text)
    try:
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message.id - 1)
    except: pass

def loading_animation(message):
    try: bot.delete_message(message.chat.id, message.id)
    except: pass
    bot.send_message(message.chat.id, f'📁')
    time.sleep(1)

def unknown_situation(message):
    """Выводит сообщение пользователю, что возникла ошибка с просьбой вернуться в главное меню."""
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="🏠 Назад в меню", callback_data="BackToMenu")
    markup.add(button1)

    bot.send_message(message.chat.id, f'⚠️ Возникла ошибка. Попробуйте вернуться в главное меню и начать заново.', reply_markup=markup)

# Строчка, чтобы программа не останавливалась
bot.polling(none_stop=True)