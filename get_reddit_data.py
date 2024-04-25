import pandas as pd
import praw
from praw.models import MoreComments
import re
from datetime import datetime
from get_ticker import ticker_data
import sys

def main():
    fin_data = ticker_data()
    reddit = praw.Reddit(
        user_agent="Post Extraction (by /u/jrbjrb1212)",
        client_id="eoU4CmxaLeFQhMrNGn5tjA",
        client_secret="xwzcJWlDdSAF-XVPoUj7lrnHqNtTLA",
    )

    # Specify the subreddit you want to gather posts from
    subreddit_name = "wallstreetbets"
    df = pd.DataFrame(
        columns=["Post_ID", "Text", "Ticker_Symbol", "Hist_Price", "Curr_Price", "Stock_Growth", "Post_Date", "Curr_Date", "Label"]
    )

    subreddit = reddit.subreddit(subreddit_name)
    curr_date = datetime.now().timestamp()
    submissions = subreddit.new(limit=1_000)

    for i, submission in enumerate(submissions):
        text = f"{submission.title} {submission.selftext}"
        text = clean_text(text)
        post_date = submission.created_utc

        ticker_symbol = fin_data.get_ticker(text)
        if ticker_symbol is None:
            continue

        curr_price = fin_data.get_current_price(ticker_symbol)
        if curr_price is None:
            continue

        hist_price = fin_data.get_historic_price(ticker_symbol, post_date)
        if hist_price is None:
            continue

        label, growth = fin_data.label_stock(curr_price, hist_price, post_date)

        post_id = submission.id
        df = df.append(
            {
                "Post_ID": post_id,
                "Text": text,
                "Ticker_Symbol": ticker_symbol,
                "Hist_Price": hist_price,
                "Curr_Price": curr_price,
                "Stock_Growth": growth,
                "Post_Date": post_date,
                "Curr_Date": curr_date,
                "Label": label,
            },
            ignore_index=True,
        )

    write_data(df)


def remove_urls(text):
    # Regular expression to match URLs
    url_pattern = r"http?://\S+|www\.\S+"
    # Replace URLs with an empty string
    return re.sub(url_pattern, "", text)


def clean_text(text):
    text = remove_urls(text)
    text = text.replace("\n", " ")
    text = text.replace(".", " ")
    text = text.replace(",", " ")
    text = text.replace("!", " ")
    text = text.replace("?", " ")
    text = text.replace("-", " ")
    text = text.strip()
    return text

def write_data(df):
    json_string = df.to_json(orient="records")

    file_path = "data/reddit_data.json"

    with open(file_path, "w") as json_file:
        json_file.write(json_string)

    print("Data saved to:", file_path)


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
    if len(sys.argv) != 2:
        print("Rerun: python3 get_reddit_data.py {version}")
        print("- Version 0: Scrape all data")
        print ("- Version 1: Load data from JSON string save")
    elif sys.argv[1] == "0":
        main()
    else:
        load_json()
