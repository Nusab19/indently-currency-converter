import httpx
import time
import os


def color_print(*args, color="green", **kwargs):
    """
    Function to print colorful text in the terminal.
    """
    colors = {
        "red": "\033[91m",
        "orange": "\033[38;5;214m",
        "yellow": "\033[93m",
        "green": "\033[92m",
        "blue": "\033[94m",
        "indigo": "\033[38;5;54m",
        "violet": "\033[95m",
    }

    reset = "\033[0m"

    if color in colors:
        print(colors[color], end="")
    print(*args, **kwargs)
    print(reset, end="")


class CachedClient:
    cache_db = {}

    def __init__(self, cache_timeout: int = 3600, **kwargs):
        base_url = "https://api.frankfurter.dev/v1/"
        self.ses = httpx.Client(base_url=base_url, timeout=10, **kwargs)
        self.cache_timeout = cache_timeout

    def __save_to_cache(self, path: str) -> dict:
        # color_print("Fetching data from API...", color="yellow")
        res = self.ses.get(path).json()
        cached = (res, time.time())
        self.cache_db[path] = cached

        return res

    def __get(self, path: str) -> dict:
        cached = self.cache_db.get(path)

        if not cached:
            return self.__save_to_cache(path)

        res, timestamp = cached

        if time.time() - timestamp > self.cache_timeout:
            return self.__save_to_cache(path)

        return res

    def get_currencies(self, show: bool = False, with_name: bool = False) -> dict:
        res = self.__get("currencies")
        if not show:  # just get the data
            return res

        color_print(f"Available Currencies:", color="orange" if with_name else "blue")

        if not with_name:
            color_print(*res.keys(), color="green")
            return res

        for symbol, name in res.items():
            color_print(symbol, name, sep=" -> ", color="violet")

        return res

    def convert(self, from_c: str, to_c: str, amount: float):
        curs = self.get_currencies()
        if from_c not in curs or to_c not in curs:
            return "INVALID_CURRENCY"

        res = self.__get(f"latest?from={from_c}&to={to_c}")
        rate = res["rates"][to_c]

        return amount * rate


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def show_menu():
    clear_screen()
    color_print("===== CURRENCY TERMINAL APP =====", color="blue")
    color_print("1. Show currencies (without names)")
    color_print("2. Show currencies (with names)")
    color_print("3. Convert currency")
    color_print("0. Exit", color="red")
    color_print("================================", color="blue")


def convert_currency_menu(client):
    clear_screen()
    color_print("===== CURRENCY CONVERSION =====", color="blue")

    from_currency = input("Enter the currency to convert FROM (e.g. USD): ").upper()
    to_currency = input("Enter the currency to convert TO (e.g. EUR): ").upper()

    try:
        amount = float(input("Enter the amount to convert: "))
    except ValueError:
        color_print("Invalid amount. Please enter a number.", color="red")
        input("Press Enter to continue...")
        return

    result = client.convert(from_currency, to_currency, amount)

    if result == "INVALID_CURRENCY":
        color_print(
            "Invalid currency code(s). Please check available currencies:", color="red"
        )
        client.get_currencies(show=True)
    else:
        color_print(
            f"{amount} {from_currency} = {result:.2f} {to_currency}", color="violet"
        )

    input("Press Enter to continue...")


def main():
    client = CachedClient()

    while True:
        show_menu()
        choice = input("Enter your choice (0-3): ")

        if choice == "0":
            cat = r"""
 /\_/\  
( o.o ) 
 > ^ <
"""
            color_print(cat, color='blue')
            color_print("See ya!", color="blue")
            color_print("Code by @Nusab19", color="violet")
            break
        elif choice == "1":
            clear_screen()
            client.get_currencies(show=True, with_name=False)
            input("Press Enter to continue...")
        elif choice == "2":
            clear_screen()
            client.get_currencies(show=True, with_name=True)
            input("Press Enter to continue...")
        elif choice == "3":
            convert_currency_menu(client)
        else:
            color_print("Invalid choice. Please try again.", color="red")
            input("Press Enter to continue...")


if __name__ == "__main__":
    main()
