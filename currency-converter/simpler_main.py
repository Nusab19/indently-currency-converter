import httpx, time


def colorPrint(*args, color="green", **kwargs):
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
    cacheDB = {}

    def __init__(self, cacheTimeout: int = 3600, **kwargs):
        base_url = "https://api.frankfurter.dev/v1/"
        self.ses = httpx.Client(base_url=base_url, timeout=10, **kwargs)
        self.cacheTimeout = cacheTimeout

    def __saveToCache(self, path: str) -> dict:
        res = self.ses.get(path).json()
        cached = (res, time.time())
        self.cacheDB[path] = cached

        return res

    def __get(self, path: str) -> dict:
        cached = self.cacheDB.get(path)

        if not cached:
            return self.__saveToCache(path)

        res, timestamp = cached

        if time.time() - timestamp > self.cacheTimeout:
            return self.__saveToCache(path)

        return res

    def getCurrencies(self, show: bool = False, withName: bool = False) -> None:
        res = self.__get("currencies")
        if not show:  # just get the data
            return res

        colorPrint(f"Available Currencies:", color="orange" if withName else "blue")

        if not withName:
            colorPrint(*res.keys(), color="green")
            return None

        for symbol, name in res.items():
            colorPrint(symbol, name, sep=" -> ", color="violet")

    def convert(self, fromC: str, toC: str, amount: float):
        curs = self.getCurrencies()
        if fromC not in curs or toC not in curs:
            return "INVALID CURRENCY"

        res = self.__get(f"latest?base={fromC}&symbols={toC}")
        rate = res["rates"][toC]

        return round(amount * rate, 2)


client = CachedClient()


def convert_currency(from_currency: str, to_currency: str, amount: int) -> None:
    res = client.convert(from_currency, to_currency, amount)
    if res == "INVALID CURRENCY":
        colorPrint("Your currency is invalid", color="red")
        client.getCurrencies(show=True)
        return None

    print(f"{amount} {from_currency} is {res} {to_currency}")


if __name__ == "__main__":
    client.getCurrencies(show=True)
    print()
    fromC = input("Enter the currency to convert FROM (e.g. USD): ").upper()
    toC = input("Enter the currency to convert TO (e.g. EUR): ").upper()
    try:
        amount = float(input("Enter the amount to convert: "))
    except ValueError:
        colorPrint("Invalid amount. Please enter a number.", color="red")
        exit(0)

    convert_currency(fromC, toC, amount)
