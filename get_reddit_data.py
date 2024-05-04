import pandas as pd
from datetime import datetime
from get_ticker import ticker_data
import sys
import json

def main(file_path):
    fin_data = ticker_data()

    # Specify the subreddit you want to gather posts from
    df = pd.DataFrame(
        columns=["Post_ID", "Text", "Ticker_Symbol", "Hist_Price", "Curr_Price", "Stock_Growth", "Post_Date", "Curr_Date", "Label"]
    )

    curr_date = datetime.now().timestamp()
    seen_map = {}
    not_stock_set = set()

    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if i % 1000 == 0:
                print(f'Parsed {i}th post')
                print(f'- Found {len(df)} good posts')
                print(f'- Seen {len(seen_map)} stocks')
                print(f"- Seen {len(not_stock_set)} bad words that aren't stocks")

            data = json.loads(line)
            # Print the JSON data (or process it as needed)
            if "[removed]" in data["selftext"]:
                continue
            
            if "[deleted]" in data["selftext"]:
                continue

            text = f"{data['title']} {data['selftext']}"
            text = fin_data.clean_text(text)
            post_date = data['created_utc']

            ticker_symbol, curr_price = fin_data.get_ticker(text, seen_map, not_stock_set)
            if ticker_symbol is None:
                continue
            
            if ticker_symbol in seen_map:
                curr_price = seen_map[ticker_symbol]
            else:
                seen_map[ticker_symbol] = curr_price

            hist_price = fin_data.get_historic_price(ticker_symbol, post_date)
            if hist_price is None:
                del seen_map[ticker_symbol]
                continue

            label, growth = fin_data.label_stock(curr_price, hist_price, post_date)

            post_id = data['id']
            new_data = {
                "Post_ID": [post_id],
                "Text": [text],
                "Ticker_Symbol": [ticker_symbol],
                "Hist_Price": [hist_price],
                "Curr_Price": [curr_price],
                "Stock_Growth": [growth],
                "Post_Date": [post_date],
                "Curr_Date": [curr_date],
                "Label": [label],
            }

            new_row_df = pd.DataFrame(new_data)
            df = pd.concat([df, new_row_df], ignore_index=True)

        fin_data.write_data(df, year)



def load_json():
    # Specify the file path from which you want to load the JSON file
    file_path = "data/reddit_data.json"

    # Load JSON file into a DataFrame
    df = pd.read_json(file_path)
    memory = df.memory_usage(deep=True).sum()
    print(df)
    print(f"Posts that included stock that had desired growth: {(df['Label'] == 1).sum()}")
    print(f"Posts that included stock that did not have desired growth: {(df['Label'] == 0).sum()}")
    print(f"Current json file requires {memory} bytes")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        file_path = sys.argv[1]
        year = sys.argv[2]
        print(file_path, year)
        main(file_path)
    else:
        load_json()

    # if len(sys.argv) != 2:
    #     print("Rerun: python3 get_reddit_data.py {version}")
    #     print("- Version 0: Scrape all data")
    #     print ("- Version 1: Load data from JSON string save")
    # elif sys.argv[1] == "0":
    #     file_path = sys.argv[2]
    #     main(file_path)
    # else:
    #     load_json()
