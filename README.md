# Overview

This repo does a few things. It is a website, a web crawler for test poses, and a gesture recognizer. 
You can view the website at jscray.art, the website mostly just a stub. The website is a cloudfare CDN and is listening to the master branch and pointing to the dist directory.

Web scraping for poses it scrapes american sign language gestures from handspeak.com. It stores these 
gestures in csv files making them accessible for tests, etc.

Currently in development is a gesture recognizer. We have tests in transcribe-asl/tests/ which compare our transcribed gestures to tests we are using to judge the accuracy of the gesture recognizer.

In a future state, we would like to recognize gestures in real time.

# How you can contribute
We need all types of feedback. Whether it's the ease of installation or how the website looks. 
We want you to make comments, contributions, and to have your code merged. Look at any of the files, make an edit: instructions here: 

# Installation and Testing:
In order to start the web application navigate to the dist directory and run "npx serve"
Then load a page localhost:3000/testHandGestures to start testing with gestures!

In order to start testing the gesture recognizer, 
  navigate to the transcribe-asl directory, 
  `cd transcribe-asl`
  install dependencies
  `poetry install`
  Scrape the web and get the poses
  `poetry run python data_in/mediapp.py`
  Run tests
  `poetry run pytest`
  Make some changes, build
  `poetry publish --build`


# Branching
This is an open source repo that is contributable to  by anyone, however there is an approval process in order to preserve the integrity of the code.

1: Open up a branch with your feature or addition
2: Call on members to approve your branch
3: Merge the branch into main

