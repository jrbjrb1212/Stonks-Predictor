import yfinance as yf

def get_tickers(category):
    """
    Get all ticker symbols for a specific category of instruments.

    Parameters:
    category (str): Category of instruments (e.g., 'stocks', 'etfs', 'currencies', 'cryptocurrencies', 'indices').

    Returns:
    list: List of ticker symbols.
    """
    tickers = []

    # Fetch tickers based on the specified category
    if category == 'stocks':
        tickers = yf.Tickers('^GSPC')  # Use any symbol; we're just interested in the list of stocks.
        tickers = tickers.tickers
    elif category == 'etfs':
        tickers = yf.Tickers('SPY')  # Use any ETF symbol; we're just interested in the list of ETFs.
        tickers = tickers.tickers
    elif category == 'currencies':
        tickers = yf.Tickers('USD=X')  # Use any currency symbol; we're just interested in the list of currencies.
        tickers = tickers.tickers
    elif category == 'cryptocurrencies':
        tickers = yf.Tickers('BTC-USD')  # Use any cryptocurrency symbol; we're just interested in the list of cryptocurrencies.
        tickers = tickers.tickers
    elif category == 'indices':
        tickers = yf.Tickers('^GSPC')  # Use any index symbol; we're just interested in the list of indices.
        tickers = tickers.tickers

    return tickers

if __name__ == "__main__":
    category = 'stocks'  # Specify the category of instruments ('stocks', 'etfs', 'currencies', 'cryptocurrencies', 'indices')
    ticker_symbols = get_tickers(category)
    print(ticker_symbols)