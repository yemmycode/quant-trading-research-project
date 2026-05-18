
"""
IBKR package import test.

This script only confirms that ib_insync is installed.
It does not connect to IBKR.
It does not place trades.
"""

def main():
    try:
        import ib_insync
        from ib_insync import IB, Stock, MarketOrder, LimitOrder

        print("ib_insync import successful.")
        print("IB class:", IB)
        print("Stock contract class:", Stock)
        print("MarketOrder class:", MarketOrder)
        print("LimitOrder class:", LimitOrder)
        print("No broker connection was attempted.")

    except ImportError as e:
        print("ib_insync import failed.")
        print(e)


if __name__ == "__main__":
    main()
