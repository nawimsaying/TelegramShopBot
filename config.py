import telebot

# Токен для бота
file = open('./mytoken.txt')
mytoken = file.read()
try: bot = telebot.TeleBot(mytoken)
except Exception: 
    print('Токен бота введен неверно! Введите токен бота в файл mytoken.txt в виде: 7851823102:AAHP67oWiosFNY4fDJNbc3uh_3H5MMvyGlM\nПеред началом работы удостоверьтесь, что ввели свои токены в файлы:\n- mytoken.txt (токен для бота, обязательный);\n- tokencrypto.txt (токен для работы с CryptoPayAPI, необязательный);\nА также настроили оплату с помощью YooMoney (необязательно) по гайду - https://yoomoney.ru/docs/wallet')
    raise SystemExit

# Токен для CryptoBot API
file = open('./tokencrypto.txt')
crypto_token = file.read()
headers = {
    'Host': 'pay.crypt.bot',
    'Crypto-Pay-API-Token': f'{crypto_token}'
}

# Геттеры
def get_bot():
    """Геттер с переменной бота."""
    return bot

def get_crypto():
    """Геттер с переменной токена для CryptoPayAPI."""
    return crypto_token

def get_headers():
    """Геттер с переменной headers для отправки запроса к CryptoPayAPI."""
    return headers