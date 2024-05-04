import yfinance as yf
import re
from datetime import datetime
import re


class ticker_data:

    def __init__(self):
        # Growth needed annualized to garner the ranking of good stock pick
        self.growth_needed = 0.06 

    # function to retrieve ticker from a body of text
    def get_ticker(self, body, seen_map, not_stock_set):
        # frequent words that look like tickers but aren't
        blacklist_words = [
            "YOLO",
            "TOS",
            "CEO",
            "CFO",
            "CTO",
            "DD",
            "BTFD",
            "WSB",
            "OK",
            "RH",
            "KYS",
            "FD",
            "TYS",
            "US",
            "USA",
            "IT",
            "ATH",
            "RIP",
            "BMW",
            "GDP",
            "OTM",
            "ATM",
            "ITM",
            "IMO",
            "LOL",
            "DOJ",
            "BE",
            "PR",
            "PC",
            "ICE",
            "TYS",
            "ISIS",
            "PRAY",
            "PT",
            "FBI",
            "SEC",
            "GOD",
            "NOT",
            "POS",
            "COD",
            "AYYMD",
            "FOMO",
            "TL;DR",
            "EDIT",
            "STILL",
            "LGMA",
            "WTF",
            "RAW",
            "PM",
            "LMAO",
            "LMFAO",
            "ROFL",
            "EZ",
            "RED",
            "BEZOS",
            "TICK",
            "IS",
            "DOW" "AM",
            "PM",
            "LPT",
            "GOAT",
            "FL",
            "CA",
            "IL",
            "PDFUA",
            "MACD",
            "HQ",
            "OP",
            "DJIA",
            "PS",
            "AH",
            "TL",
            "DR",
            "JAN",
            "FEB",
            "JUL",
            "AUG",
            "SEP",
            "SEPT",
            "OCT",
            "NOV",
            "DEC",
            "FDA",
            "IV",
            "ER",
            "IPO",
            "RISE" "IPA",
            "URL",
            "MILF",
            "BUT",
            "SSN",
            "FIFA",
            "USD",
            "CPU",
            "AT",
            "GG",
            "ELON",
            "I",
            "WE",
            "A",
            "AND",
            "THE",
            "THIS",
            "TO",
            "BUY",
            "MY",
            "MOST",
            "ARK",
            "IN",
            "S",
            "BABY",
            "APES",
            "NONE",
        ]

        # FIRST CHECK IF THERE'S A $TICKER WITH DOLLAR SIGN
        if "$" in body:
            index = body.find("$") + 1
            word = self.check_after_dollarsign(body, index)

            if word and word not in blacklist_words:
                try:
                    if word in not_stock_set:
                        pass

                    elif word in seen_map:
                        return word, seen_map[word]
                    
                    # special case for $ROPE
                    curr_price = self.get_current_price(word)
                    if curr_price == None:
                        not_stock_set.add(word)
                        pass
                    else:
                        return word, curr_price
                except Exception as e:
                    pass

        # IF NO TICKER WITH DOLLAR SIGN, CHECK FOR TICKER WITHOUT IT: splits every body into list of words
        word_list = re.sub("[^\w]", " ", body).split()
        for count, word in enumerate(word_list):
            # initial screening of words
            if (
                word.isupper()
                and len(word) >= 1
                and (word.upper() not in blacklist_words)
                and len(word) <= 5
                and word.isalpha()
            ):
                try:
                    if word in not_stock_set:
                        continue

                    elif word in seen_map:
                        return word, seen_map[word]
                    # special case for $ROPE
                    curr_price = self.get_current_price(word)
                    if curr_price == None:
                        not_stock_set.add(word)
                        pass
                    else:
                        return word, curr_price
                except Exception as e:
                    continue

        # if no ticker was found
        return None, None

    def check_after_dollarsign(self, body, start_index):
        """
        Given a starting index and text, this will extract the ticker, return None if it is incorrectly formatted.
        """
        count = 0
        ticker = ""

        for char in body[start_index:]:
            # if it should return
            if not char.isalpha():
                # if there aren't any letters following the $
                if count == 0:
                    return None

                return ticker.upper()
            else:
                ticker += char
                count += 1

        return ticker.upper()

    def get_current_price(self, stock_symbol):
        if stock_symbol.lower() == "none":
            return None
        stock = yf.Ticker(stock_symbol)
        periods = ["1d", "5d"]
        for i, period in enumerate(periods):
            try:
                current_price = stock.history(period=period)["Close"].iloc[-1]
            except:
                continue

            return current_price

        return None

    def get_historic_price(self, stock_symbol, start_date):
        # 86,400 seconds in a day
        sec_in_day = 86_400
        end_date = start_date + sec_in_day
        ticker = yf.Ticker(stock_symbol)

        try:
            while datetime.fromtimestamp(end_date).weekday() >= 5:
                end_date += sec_in_day

            while datetime.fromtimestamp(start_date).weekday() >= 5:
                start_date -= sec_in_day 

            start_date = datetime.fromtimestamp(start_date).strftime(
                "%Y-%m-%d"
            )
            end_date = datetime.fromtimestamp(end_date).strftime("%Y-%m-%d")
            historical_data = ticker.history(start=start_date, end=end_date)
            closing_price = historical_data["Close"][0]
            return closing_price
        except Exception as e:
            print("Error: ", e)
            return None

    def label_stock(self, curr_price, hist_price, post_date):
        now_date = datetime.now().timestamp()
        year_in_sec = 31_536_000
        time_diff = post_date - float(now_date)

        raw_val_diff = (curr_price/hist_price) - 1

        adjusted_diff = raw_val_diff

        # Growth needed is proportional to time but min capped at 2%
        adjusted_growth_need = max(0.02, self.growth_needed * (time_diff / year_in_sec))

        if adjusted_diff > adjusted_growth_need:
            return 1, adjusted_diff
        else:
            return 0, adjusted_diff
    
    def remove_urls(self, text):
        # Regular expression to match URLs
        url_pattern = r"http?://\S+|www\.\S+"
        # Replace URLs with an empty string
        return re.sub(url_pattern, "", text)


    def clean_text(self, text):
        text = self.remove_urls(text)
        text = text.replace("\n", " ")
        text = text.replace(".", " ")
        text = text.replace(",", " ")
        text = text.replace("!", " ")
        text = text.replace("?", " ")
        text = text.replace("-", " ")
        text = text.strip()
        return text

    def write_data(self, df, year):
        json_string = df.to_json(orient="records")

        file_path = f"data/{year}_data.json"

        with open(file_path, "w") as json_file:
            json_file.write(json_string)

        print("Data saved to:", file_path)
