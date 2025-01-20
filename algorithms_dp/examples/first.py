import ccxt
import time

def get_bitcoin_price():
    try:
        exchange = ccxt.binance()  # Используем Binance
        ticker = exchange.fetch_ticker('BTC/USDT')  # Получаем данные по паре BTC/USDT
        return round(ticker['last'], 4)  # Последняя цена
    except Exception as e:
        print(f"Error fetching price: {e}")
        return None
def main():
    start_cap = 100
    cap = start_cap
    limit_hand = 100
    cells = 0.0004
    mini = 0.00008
    a = time.time()
    b = 99597.4600
    times = 0
    flag = 1
    hand = 1
    while True:
        flag *= -1
        price = get_bitcoin_price()
        if price is not None:
            times += time.time() - a
            print(f"Current Bitcoin price: ${price:.4f}, {time.time() - a}")
            alpha1 = b / price
            if times >= 10:
                print(alpha1, hand)
                if flag == -1:
                    k = cap
                    cap = cap + cap * hand - cap * hand * (2 - alpha1) - cap * cells
                    hand = min([max([(k - cap) / mini, 1]), limit_hand])
                    print()

                else:
                    k = cap
                    cap = cap + cap * hand - cap * hand * alpha1 - cap * cells
                    hand = min([max([(k - cap)/mini, 1]), limit_hand])

                print(b / price - 1)
                print(cap)
                times = 0
                b = price
            a = time.time()
        time.sleep(0.1)  # Обновляем каждую секунду

if __name__ == "__main__":
    main()
