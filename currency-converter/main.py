"""
Name: CURRENCY CONVERTER
Author: Nusab Taha
"""

import httpx
import time
import os


def color_print(*args, color="green", **kwargs):
    colors = {
        "red": "\033[91m",
        "orange": "\033[38;5;214m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "violet": "\033[95m",
    }
    reset = "\033[0m"

    if color in colors:
        print(colors[color], end="")
    print(*args, **kwargs)
    print(reset, end="")


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


class CachedClient:
    cache_db = {}

    def __init__(self, cache_timeout=3600):
        self.ses = httpx.Client(base_url="https://api.frankfurter.dev/v1/", timeout=10)
        self.cache_timeout = cache_timeout

    def __save_to_cache(self, path):
        # color_print("Fetching data...", color="orange")
        res = self.ses.get(path).json()
        self.cache_db[path] = (res, time.time())
        return res

    def __get(self, path):
        cached = self.cache_db.get(path)
        if not cached:
            return self.__save_to_cache(path)

        res, timestamp = cached
        if time.time() - timestamp > self.cache_timeout:
            return self.__save_to_cache(path)

        return res

    def get_currencies(self, show=False, with_name=False):
        res = self.__get("currencies")
        if not show:
            return res

        color_print("Available Currencies:", color="blue")

        if not with_name:
            color_print(*res.keys(), color="green")
            return res

        for symbol, name in res.items():
            color_print(symbol, name, sep=" -> ", color="violet")

        return res

    def convert(self, from_c, to_c, amount):
        curs = self.get_currencies()
        if from_c not in curs or to_c not in curs:
            return "INVALID_CURRENCY"

        res = self.__get(f"latest?from={from_c}&to={to_c}")
        return amount * res["rates"][to_c]


def handle_show_currencies(client, with_name=False):
    clear_screen()
    client.get_currencies(show=True, with_name=with_name)
    input("Press Enter to continue...")


def handle_convert_currency(client):
    clear_screen()
    from_currency = input("Convert FROM (e.g. USD): ").upper()
    to_currency = input("Convert TO (e.g. EUR): ").upper()

    try:
        amount = float(input("Amount: "))
    except ValueError:
        color_print("Invalid amount!", color="red")
        input("Press Enter to continue...")
        return

    result = client.convert(from_currency, to_currency, amount)

    if result == "INVALID_CURRENCY":
        color_print("Invalid currency code(s)!", color="red")
        client.get_currencies(show=True)
    else:
        color_print(
            f"{amount} {from_currency} = {result:.2f} {to_currency}", color="violet"
        )

    input("Press Enter to continue...")


def display_menu():
    clear_screen()
    color_print("===== CURRENCY CONVERTER =====", color="blue")
    color_print("1. Show currencies (without names)", color="green")
    color_print("2. Show currencies (with names)", color="green")
    color_print("3. Convert currency", color="green")
    color_print("0. Exit", color="red")
    return input("Enter choice (0-3): ")


def main():
    client = CachedClient()

    while True:
        choice = display_menu()

        if choice == "0":
            cat = r"""
 /\_/\  
( o.o ) 
 > ^ <
"""
            color_print(cat, color="blue")
            color_print("See ya!", color="blue")
            color_print("Code by @Nusab19", color="violet")
            break

        elif choice == "1":
            handle_show_currencies(client, with_name=False)
        elif choice == "2":
            handle_show_currencies(client, with_name=True)
        elif choice == "3":
            handle_convert_currency(client)
        else:
            color_print("Invalid choice!", color="red")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
