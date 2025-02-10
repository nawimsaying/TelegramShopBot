import sqlite3
import time

def initialize_tables():
    """Проверка существования всех таблиц и создание недостающих."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute('CREATE TABLE IF NOT EXISTS users (userid int primary key, orders varchar, sum_of_orders int default 0, count_of_orders int default 0, state varchar default None)')
    db_cursor.execute('CREATE TABLE IF NOT EXISTS products (productid integer primary key autoincrement, type varchar, name varchar, price int, description varchar, photo varchar)')
    db_cursor.execute('CREATE TABLE IF NOT EXISTS orders (orderid integer primary key autoincrement, label varchar, username varchar, name varchar, price int, status varchar, userid int, duration int, type varchar, buyingdate varchar)')
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

def add_user_id(user_id):
    """Добавление нового пользователя в БД, если его там еще нет. Вернет: False - если пользователь уже существует в БД; True - если пользователь успешно добавлен в БД."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute('SELECT userid FROM users')
    users = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    if users is not None:
        for user in users:
            if user[0] == user_id:
                return False
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'INSERT INTO users (userid) VALUES ({user_id})')
    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    return True

def get_all_users():
    """Возвращает ID всех пользователей из БД."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute('SELECT userid FROM users')
    users = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return users

def change_state(user_id, new_state):
    """Изменяет состояние пользователя. Доступные состояния - stars_choose, stars_username, add_present, add_present_price, add_present_description, add_present_photo, add_premium, add_premium_price, add_premium_description, add_premium_photo, add_nftusername, add_nftusername_price, add_nftusername_description, add_nftusername_photo, add_nftpresent, add_nftpresent_price, add_nftpresent_description, add_nftpresent_photo, ads"""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'UPDATE users SET state = ? WHERE userid = {user_id}', (new_state, ))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

def get_state(user_id):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT userid, state FROM users WHERE userid = {user_id}')
    data = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return data[0][1]

def get_stats():
    """Возвращает всю таблицу с пользователями."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM users')
    data = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return data

def get_all_products():
    """Возвращает всю таблицу с товарами."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM products ORDER BY type')
    data = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return data

def get_product(productid):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM products WHERE productid = {productid}')
    data = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return data[0]

# Types of products - present, premium, nftusername, nftpresent, stars
def add_product(type: str, name, price, description, photo):
    """Добавляет новый товар в БД."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'INSERT INTO products (type, name, price, description, photo) VALUES (?, ?, ?, ?, ?)', (type, name, price, description, photo))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

def remove_product(productid):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'DELETE FROM products WHERE productid = {productid}')
    db_connection.commit()
    db_cursor.close()
    db_connection.close()

def get_all_orders():
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute('SELECT * FROM orders')
    orders = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return orders

def get_user_orders(user_id):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM orders WHERE userid = {user_id} AND status IN ("paid", "completed") ORDER BY status')
    orders = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    try:
        if len(orders) == 0:
            return 0
        else:
            return orders
    except:
        return 0

def get_order(label):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM orders WHERE label = {label}')
    order = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    return order[0]
    
def check_order_label(label):
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'SELECT * FROM orders WHERE label = {label}')
    order = db_cursor.fetchall()
    db_cursor.close()
    db_connection.close()
    if len(order) == 0:
        return True
    else:
        return False
    
def get_active_orders():
    result = []
    orders = get_all_orders()
    if orders is not None:
        for order in orders:
            if order[5] == 'paid':
                result.append(order)
        if len(result) == 0:
            return 1
        else:
            return result
    else:
        return 1

def get_completed_orders():
    result = []
    orders = get_all_orders()
    if orders is not None:
        for order in orders:
            if order[5] == 'completed':
                result.append(order)
        if len(result) == 0:
            return 1
        else:
            return result
    else:
        return 1
    
def get_earnings(interval):
    result = []
    orders = get_all_orders()
    if orders is not None:
        for order in orders:
            if order[5] == 'completed' or order[5] == 'paid':
                result.append(order)
        return result
    else:
        return 0

# Status of order - waiting, paid, completed
def create_new_order(label, username, name, price, user_id, type_of_product, duration = 0):
    timeNow = int(time.time())
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'INSERT INTO orders (label, username, name, price, status, userid, duration, type, buyingdate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (label, username, name, price, 'waiting', user_id, duration, type_of_product, timeNow))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()
    orders = get_all_orders()
    order = orders[-1]
    return order[1]

def change_order_status(label, new_status):
    """Изменяет статус у заказа. Доступные статусы - waiting, paid, completed."""
    db_connection = sqlite3.connect('data/MainDB.sql')
    db_cursor = db_connection.cursor()
    db_cursor.execute(f'UPDATE orders SET status = ? WHERE label = {label}', (new_status, ))
    db_connection.commit()
    db_cursor.close()
    db_connection.close()