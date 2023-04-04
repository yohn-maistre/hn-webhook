import requests
import datetime as dt
import pytz
import re
import html
import os

# Constants
WEBHOOK_URL = os.environ["WEBHOOK_URL"]
MAX_POSTS = 10
BEST_POSTS_URL = 'https://hacker-news.firebaseio.com/v0/beststories.json'
TOP_POSTS_URL = 'https://hacker-news.firebaseio.com/v0/topstories.json'
GET_ITEM_URL = 'https://hacker-news.firebaseio.com/v0/item/{}.json'
REQUEST_HEADER = {"User-Agent": "Hacker News Best 10 Bot"}

def clean_text(text):
  # Hapus tag HTML & kurangi jumlah karakter ke 280.
  cleaned_text = html.unescape(re.sub(re.compile('<.*?>'), '', text))

  if len(cleaned_text) > 280:
    cleaned_text = f"{cleaned_text[:277]}..."
  
  return cleaned_text

def fetch_top_posts(max_posts):
  # tarik 10 ID post dari 'topstories'
  with requests.get(TOP_POSTS_URL, headers=REQUEST_HEADER) as response:
    item_ids = response.json()
    item_ids = item_ids[:max_posts]
    top_posts = [get_item(item_id) for item_id in item_ids]

    return top_posts

def fetch_best_posts(max_posts):
  # tarik 10 ID post dari 'beststories'
  with requests.get(BEST_POSTS_URL, headers=REQUEST_HEADER) as response:
    item_ids = response.json()
    item_ids = item_ids[:max_posts]
    best_posts = [get_item(item_id) for item_id in item_ids]

    return best_posts

def get_item(item_id):
  # tarik metadata post
  with requests.get(GET_ITEM_URL.format(item_id), headers=REQUEST_HEADER) as response:
    data = response.json()

    item = {}
    item['id'] = data.get('id')
    item['timestamp'] = f"{dt.datetime.fromtimestamp(data.get('time')).strftime('%Y-%m-%dT%H:%M:%S')}.000Z"
    item['by'] = data.get('by')
    item['title'] = data.get('title')
    item['comments'] = data.get('descendants')
    item['score'] = data.get('score')
    item['permalink'] = f'https://news.ycombinator.com/item?id={item["id"]}'
    item['url'] = data.get('url')
    item['text'] = data.get('text')

    if item['url'] == None:
      item['url'] = item['permalink']
    
    if item['text'] == None:
      item['text'] = ""
    else:
      item['text'] = clean_text(item['text'])

    return item


def sendtop_to_webhook(posts):
  # Kirim payload TOP POSTS dalam JSON ke URL Discord Webhook
  timezone = pytz.timezone('Asia/Jayapura')
  current_datetime = dt.datetime.now(timezone)
  current_date = current_datetime.strftime('%B %d, %Y')

  payload = {
    'username': "Y Combinator's Hacker News",
    'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Y_Combinator_logo.svg/240px-Y_Combinator_logo.svg.png',
    'content': f"__**{MAX_POSTS} Postingan *Trending* 🔥 Hari Ini ({current_date})**__",
    'embeds': [
      {
        'color': '16737792',
        'author': {
          'name': post['by']
        },
        'title': f"{post['title']}",
        'url': f"{post['url']}",
        'description': "" if post['text'] == None else f"{post['text']}",
        'timestamp': post['timestamp'],
        'fields': [
          {
            'name': 'Post ID',
            'value': f"[{post['id']}]({post['permalink']})",
            'inline': True
          },
          {
            'name': 'Score',
            'value': f"{post['score']} points",
            'inline': True
          },
          {
            'name': 'Comments',
            'value': f"{post['comments']}",
            'inline': True
          }
        ],
        'footer': {
          'text': 'HN Bot by YG',
          'icon_url': 'https://news.ycombinator.com/y18.gif'
        }
      } for post in posts
    ]
  }

  with requests.post(WEBHOOK_URL, json=payload) as response:
    print(response.status_code)
    print(response.text)

def sendbest_to_webhook(posts):
  # Kirim payload BEST POSTS dalam JSON ke URL Discord Webhook
  timezone = pytz.timezone('Asia/Jayapura')
  current_datetime = dt.datetime.now(timezone)
  current_date = current_datetime.strftime('%B %d, %Y')

  payload = {
    'username': "Y Combinator's Hacker News",
    'avatar_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b2/Y_Combinator_logo.svg/240px-Y_Combinator_logo.svg.png',
    'content': f"__**{MAX_POSTS} Postingan Terbaik 🚀 Belakangan Ini ({current_date})**__",
    'embeds': [
      {
        'color': '16737792',
        'author': {
          'name': post['by']
        },
        'title': f"{post['title']}",
        'url': f"{post['url']}",
        'description': "" if post['text'] == None else f"{post['text']}",
        'timestamp': post['timestamp'],
        'fields': [
          {
            'name': 'Post ID',
            'value': f"[{post['id']}]({post['permalink']})",
            'inline': True
          },
          {
            'name': 'Score',
            'value': f"{post['score']} points",
            'inline': True
          },
          {
            'name': 'Comments',
            'value': f"{post['comments']}",
            'inline': True
          }
        ],
        'footer': {
          'text': 'HN Bot by YG',
          'icon_url': 'https://news.ycombinator.com/y18.gif'
        }
      } for post in posts
    ]
  }

  with requests.post(WEBHOOK_URL, json=payload) as response:
    print(response.status_code)
    print(response.text)

def main():
  print("Menghubungi Hacker News...")
  top_posts = fetch_top_posts(MAX_POSTS)
  best_posts = fetch_best_posts(MAX_POSTS)
  print("Data diterima. Mengirim ke webhook...")
  sendtop_to_webhook(top_posts)
  sendbest_to_webhook(best_posts)

if __name__ == "__main__":
  main()