import requests
from bs4 import BeautifulSoup

for i in range(2460, 2461):
  print(f"Iterating through on iteration: {i}")
  website_content = requests.get(f'https://www.handspeak.com/word/{i}')
  
  soup = BeautifulSoup(website_content.text, "html.parser")
  title = soup.findAll('h1')[0].text
  words_in_title = title.split(" ")
  for word in words_in_title:
    for letter in word:
      if not letter.isupper():
        continue
      title = word
  
  print(title)
  
  video_source = soup.findAll('video')[0]['src']
  video_source_full_url = f'https://www.handspeak.com/{video_source}'
  print(video_source_full_url)