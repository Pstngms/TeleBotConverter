import requests
import json


class APIException(Exception):
    pass


class Converter:
    @staticmethod
    def get_key(d, value=None):
        for d_key, d_value in d.items():
            if value in d_value:
                return d_key
        if value not in d:
            raise APIException(f'Не удалось обработать валюту {value}')

    @staticmethod
    def get_price(quote, base, amount):
        keys = Converter.load_json()
        quote = Converter.get_key(keys, value=quote.lower())
        base = Converter.get_key(keys, value=base.lower())

        r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={quote}&tsyms={base}').content
        total_base = json.loads(r)[base] * float(amount)
        if total_base < 10:
            total_base = f'{total_base:.5f}'
        else:
            total_base = int(total_base)

        return total_base

    @staticmethod
    def log_data(message):
        with open('data.txt', 'a', encoding='utf8') as data:
            data.write(f'{message.chat.username}  {message.chat.first_name}:  {message.text}\n')

    @staticmethod
    def load_json():
        with open('keys_.json', encoding='utf8') as f:
            return json.load(f)
