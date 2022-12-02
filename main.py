import json

from telebot import types

from config import TOKEN
from extensions import APIException, Converter
import telebot

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Помощь", callback_data="help")
        btn2 = types.InlineKeyboardButton("Узнать валюты", callback_data="value")
        btn3 = types.InlineKeyboardButton("Добавить вариант названия валюты", callback_data="change")

        markup.add(btn1, btn2, btn3)

        username = message.chat.first_name
        text = f'<b>Привет, {username}!</b>\n\nЯ БОТ для конвертации валют.\nЕсли ты впервые пользуешься мной напиши команду ' \
               f'<b>/help</b> или нажми на кнопку "Помощь"\n\nУвидеть список всех доступных валют: ' \
               f'\n<b>/values</b>\nДобавить вариант ' \
               f'названия валюты: \n<b>/change</b>'

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)


@bot.message_handler(commands=['help'])
def handle_help(message):
    try:
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Узнать валюты", callback_data="value")
        btn2 = types.InlineKeyboardButton("Добавить вариант названия валюты", callback_data="change")
        markup.add(btn1, btn2)

        text = f'Чтобы начать работу введите команду боту в следующем формате:\n[имя валюты цену ' \
               f'которой он хочет узнать]  [имя валюты в которой надо узнать цену первой валюты]  [количество первой ' \
               f'валюты]\n\nНапример: <b>рубль доллар 120</b>\n\nУвидеть список всех доступных валют: \n<b>/values</b>\nДобавить вариант ' \
               f'названия валюты: \n<b>/change</b> '

        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode='HTML')

    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    try:
        if call.data == 'value':
            handle_values(call.message)

        elif call.data == 'change':
            change_info(call.message)

        elif call.data == 'help':
            handle_help(call.message)

    except Exception as e:
        bot.send_message(call.message.chat.id, 'Непредвиденная ошибка')
        print(e)


@bot.message_handler(commands=['values'])
def handle_values(message):
    try:
        keys = Converter.load_json()
        text = 'Доступные валюты:\n'

        for key in keys.values():
            text = '\n'.join((text, f'<b>{key[0]}</b> - {tuple(key)}'))
        bot.send_message(message.chat.id, text, parse_mode='HTML')

    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)


@bot.message_handler(commands=['change'])
def change_info(message):
    try:
        text = 'Для добавления варианта названия валюты введите команду боту в следующем формате:\n"change [название ' \
               'валюты] ' \
               '[дополнительное название валюты]"\nНапример: <b>change рубли руб</b>'
        bot.send_message(message.chat.id, text, parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)


@bot.message_handler(content_types=['text', ])
def change(message):
    try:
        values = message.text.split(' ')
        keys = Converter.load_json()
        list_ = []
        for v in keys.values():
            for i in v:
                list_.append(i)
        if values[0] == 'change':
            if values[1] not in list_:
                raise IndexError
            val = Converter.get_key(keys, value=values[1].lower())

            if values[2] in list_:
                bot.send_message(message.chat.id, 'Данное название уже существует')
            else:
                keys[val].append(values[2].lower())
                with open('keys_.json', 'w', encoding='utf8') as f:
                    json.dump(keys, f, ensure_ascii=False, indent=4)
                bot.reply_to(message, 'Запись добавлена')
        else:
            convert(message)
    except IndexError:
        bot.send_message(message.chat.id, 'Ошибка в добавлении названия')
    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)


def convert(message):
    try:
        values = message.text.split(' ')

        Converter.log_data(message)

        if len(values) > 3:
            raise APIException('Слишком много параметров.\nВведите <b>/help</b> чтобы посмотреть инструкцию')
        if len(values) < 3:
            raise APIException('Недостаточно параметров.\nВведите <b>/help</b> чтобы посмотреть инструкцию')

        quote, base, amount = values
        total_base = Converter.get_price(quote, base, amount)
        text = f'Цена {amount} {quote} - {total_base} {base}'

    except APIException as e:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("Помощь", callback_data="help")
        markup.add(btn)
        bot.send_message(message.chat.id, str(e), reply_markup=markup, parse_mode='HTML')
    except Exception as e:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')
        print(e)
    else:
        bot.reply_to(message, text)


bot.polling(none_stop=True)
