import requests
from bs4 import BeautifulSoup
# words = ["again","also","ask","bad","boy","but","can","come","deaf","different","drink","drive","eat","email","excuse","family","feel","few","find","fine","fingerspelling","finish","food","for","forget","friend","get","girl","give","go","good","have","he","hearing","hello","help","home","how","internet","know","later","little","live","man","many","me","meet","more","my","name","need","new","no","not","now","ok","old","other","please","remember","same","say","school","see","she","should","sign","slow","some","sorry","store","take","tell","text","thank","their","they","think","time","tired","try","understand","use","wait","want","what","when","where","which","who","why","will","with","woman","work","write","yes","you",
# "your"]
for word in range(1554, 1555):
  print(f"Iterating through on iteration: {word}")
  website_content = requests.get(f'https://www.handspeak.com/word/{word}/')
  
  soup = BeautifulSoup(website_content.text, "html.parser")
  # if soup.find(string="Oops") != None:
  if len(soup.findAll('video')) > 0:
    title = soup.findAll('h1')[0].text
    words_in_title = title.split(" ")
    for word in words_in_title:
      for letter in word:
        if not letter.isupper():
          continue
        title = word
    
    video_source = soup.findAll('video')[0]['src']
    video_source_full_url = f'https://www.handspeak.com/{video_source}'
    print(f'{title}, {video_source_full_url}')