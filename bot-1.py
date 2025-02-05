import tweepy
import tkinter as tk
from tkinter import ttk
import time
from config import TWITTER_CONFIG

# Configure main window
root = tk.Tk()
root.title("TilinBot - Twitter Automation")
root.geometry("400x600")
root.configure(bg="#f0f0f0")

# Style configuration
style = ttk.Style()
style.configure("TFrame", background="#f0f0f0")
style.configure("TLabel", 
    background="#f0f0f0",
    font=("Helvetica", 10)
)
style.configure("TEntry", 
    padding=5
)
style.configure("TButton",
    padding=10,
    font=("Helvetica", 10, "bold")
)

# Create main frame
main_frame = ttk.Frame(root, padding="20")
main_frame.pack(fill=tk.BOTH, expand=True)

# Title
title_label = tk.Label(
    main_frame,
    text="TilinBot",
    font=("Helvetica", 24, "bold"),
    bg="#f0f0f0",
    fg="#1DA1F2"  # Twitter blue
)
title_label.pack(pady=(0, 20))

# Input frame
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill=tk.BOTH, expand=True)

# Create and pack widgets with better spacing and organization
entries = {
    "Search Term:": None,
    "Number of Tweets:": None,
    "Response Message:": None,
    "Reply? (yes/no):": None,
    "Retweet? (yes/no):": None,
    "Favorite? (yes/no):": None,
    "Follow? (yes/no):": None
}

for idx, (label_text, _) in enumerate(entries.items()):
    label = ttk.Label(input_frame, text=label_text)
    label.grid(row=idx, column=0, pady=5, padx=5, sticky="w")
    entry = ttk.Entry(input_frame, width=30)
    entry.grid(row=idx, column=1, pady=5, padx=5, sticky="ew")
    entries[label_text] = entry

# Status frame
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill=tk.BOTH, pady=20)

status_label = ttk.Label(
    status_frame,
    text="Ready to start",
    font=("Helvetica", 9, "italic")
)
status_label.pack()

def update_status(message):
    status_label.config(text=message)
    root.update()

# Modified main function to use the new entry references
def main():
    update_status("Bot is running...")
    api, client = init_twitter_api()
    
    # Get user inputs
    search = entries["Search Term:"].get()
    try:
        numberOfTweets = int(entries["Number of Tweets:"].get())
    except ValueError:
        update_status("Error: Number of tweets must be a number")
        return
        
    phrase = entries["Response Message:"].get()
    reply = entries["Reply? (yes/no):"].get().lower()
    retweet = entries["Retweet? (yes/no):"].get().lower()
    favorite = entries["Favorite? (yes/no):"].get().lower()
    follow = entries["Follow? (yes/no):"].get().lower()

    # Handle Reply
    if reply == "yes":
        for tweet in tweepy.Cursor(api.search_tweets, q=search).items(numberOfTweets):
            try:
                username = tweet.user.screen_name
                api.update_status(
                    f"@{username} {phrase}",
                    in_reply_to_status_id=tweet.id
                )
                print(f"Replied with {phrase}")
            except tweepy.TweepError as e:
                print(e.reason)
            except StopIteration:
                break

    # Handle Retweet
    if retweet == "yes":
        for tweet in tweepy.Cursor(api.search_tweets, q=search).items(numberOfTweets):
            try:
                tweet.retweet()
                print("Retweeted tweet")
            except tweepy.TweepError as e:
                print(e.reason)
            except StopIteration:
                break

    # Handle Favorite
    if favorite == "yes":
        for tweet in tweepy.Cursor(api.search_tweets, q=search).items(numberOfTweets):
            try:
                tweet.favorite()
                print("Favorited tweet")
            except tweepy.TweepError as e:
                print(e.reason)
            except StopIteration:
                break

    # Handle Follow
    if follow == "yes":
        for tweet in tweepy.Cursor(api.search_tweets, q=search).items(numberOfTweets):
            try:
                tweet.user.follow()
                print(f"Followed {tweet.user.screen_name}")
            except tweepy.TweepError as e:
                print(e.reason)
            except StopIteration:
                break

    update_status("Task completed!")

# Create styled start button
start_button = ttk.Button(
    main_frame,
    text="Start Bot",
    command=main,
    style="TButton"
)
start_button.pack(pady=20)

# Keep existing API functions
def init_twitter_api():
    auth = tweepy.OAuthHandler(
        TWITTER_CONFIG['consumer_key'],
        TWITTER_CONFIG['consumer_secret']
    )
    auth.set_access_token(
        TWITTER_CONFIG['access_token'],
        TWITTER_CONFIG['access_token_secret']
    )
    api = tweepy.API(auth)
    client = tweepy.Client(
        bearer_token=TWITTER_CONFIG['bearer_token'],
        consumer_key=TWITTER_CONFIG['consumer_key'],
        consumer_secret=TWITTER_CONFIG['consumer_secret'],
        access_token=TWITTER_CONFIG['access_token'],
        access_token_secret=TWITTER_CONFIG['access_token_secret']
    )
    return api, client

def follow_followers(api):
    for follower in tweepy.Cursor(api.followers, count=100).items():
        try:
            follower.follow()
            print("Followed everyone that is following " + follower.name)
        except tweepy.RateLimitError:
            print("Rate limit reached. Sleeping for 15 minutes.")
            time.sleep(15 * 60)
        except tweepy.TweepError as e:
            print(e.reason)
        except StopIteration:
            break

def interact_with_tweets(api, client, search_query, num_tweets, reply_phrase):
    for tweet in tweepy.Cursor(api.search_tweets, q=search_query).items(num_tweets):
        try:
            client.create_favorite(tweet_id=tweet.id)
            username = tweet.user.screen_name
            api.update_status(
                f"@{username} {reply_phrase}",
                in_reply_to_status_id=tweet.id
            )
            print(f"Replied with {reply_phrase}")
        except tweepy.TweepError as e:
            print(e.reason)
        except StopIteration:
            break

# Center the window on screen
root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

root.mainloop()