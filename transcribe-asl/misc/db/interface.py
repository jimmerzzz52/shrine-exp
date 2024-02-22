print("""Hello you are interacting with a gesture recognition library (beta).
We have crawled through many of the gestures online at handspeak.com and have metadata attached to them. 

Here are some of the options you may have:

1: Show all gestures from user classification
2: Show data on a gesture
3: Show gestures of a certain speed
4: Show the average speed of a gesture
5: Show the count of gestures a user has created
6: Show me how many times a user has recorded a certain gesture
7: Show me all related gestures to a certain gesture
8: Show me how many times a certain user has recorded a certain gesture and all related gestures""")

num = input ("Enter a choice here:")
from mysql import connector
conn = connector.connect(
  host = "localhost",
  user = "root",
  password = "hellsway52",
  database='gestures'
)
cursor = conn.cursor()

if num == "1":
  print(f"Ok, you have selected option number {num}")
  user_classification = input ("What is the user classification?: ")
  print(f"Ok, you want to show all gestures belonging to {user_classification}s")
  
  query = f"""SELECT name, gesture_name FROM users 
  JOIN gestures ON name = creating_user
    WHERE classification = '{user_classification}'
  """
  cursor.execute(query)
  for (name, gesture_name) in cursor:
    print("{} is a User who has recorded {}".format(name, gesture_name))
  
elif num == "2":
  print(f"Ok, you have selected option number {num}")
  gesture = input ("What gesture called?: ")
  print(f"Ok, you want to show all users who have recorded the gesture {gesture}s")
  
  query = f"""SELECT name, email FROM users 
  JOIN gestures ON name = creating_user
    WHERE gesture_name = '{gesture}'
  """
  cursor.execute(query)
  for (name, email) in cursor:
    print("{} is a User who has recorded {} and has the email {}".format(name, gesture, email))
  
  
elif num == "3":
  print(f"Ok, you have selected option number {num}")
  speed = input ("What is min speed of the gestures?: ")
  print(f"Ok, you want to show all gestures faster than {speed}s")
  
  query = f"""SELECT DISTINCT name, gesture_name FROM users 
  JOIN gestures ON name = creating_user
  JOIN direction 
    WHERE speed > '{int(speed)}'
  """
  cursor.execute(query)
  for (name, gesture_name) in cursor:
    print("{} is a User who has recorded {}".format(name, gesture_name))
elif num == "4":
  print(f"Ok, you have selected option number {num}")
  print(f"You want to know the average speed of a gesture we have recorded")
  
  query = f"""SELECT AVG(speed) AS average_speed FROM direction """
  # TODO: Fix issue where some gestures have more coordinates.
  cursor.execute(query)
  for average_speed in cursor:
    print("{} is the average speed".format(average_speed))
elif num == "5":
  print(f"Ok, you have selected option number {num}")
  gesture = input ("What gesture do you want to show counts of?: ")
  print(f"Ok, you want to show how many times a user has recorded the gesture {gesture}")
  
  query = f"""SELECT DISTINCT gesture_name, COUNT(gesture_name) AS count FROM users 
  JOIN gestures ON name = gestures.creating_user
    WHERE gesture_name = '{gesture}'
    GROUP BY gesture_name
  """
  cursor.execute(query)
  for (gesture_name, count) in cursor:
    print("{} has been recorded {} times".format(gesture_name, count))
elif num == "6":
  print(f"Ok, you have selected option number {num}")
  gesture = input ("What do you want to show related gestures to?: ")
  print(f"Ok, you want to show gestures related to {gesture}")
  
  query = f"""SELECT gesture_to FROM related_gestures
    WHERE gesture_base = '{gesture}'
  """
  cursor.execute(query)
  for (gesture_to) in cursor:
    print("{} is related to {}".format(gesture_to, gesture))
elif num == "7":
  print(f"Ok, you have selected optoion number {num}")
  gesture = input ("What gesture do you want to show counts of and any related gestures?: ")
  print(f"Ok, you want to show how many times a user has recorded the gesture {gesture} and any other related gestures")
  
  query = f"""SELECT DISTINCT gesture_name, gesture_to, COUNT(gesture_name) AS count FROM users 
  JOIN gestures ON name = gestures.creating_user
  JOIN related_gestures ON related_gestures.gesture_base = gestures.gesture_name
    WHERE gesture_name = '{gesture}'
    GROUP BY gesture_name, gesture_to
  """
  print(query)
  cursor.execute(query)
  for (gesture_name, gesture_to, count) in cursor:
    print("{} is related to {} and has been recorded {} times".format(gesture_name, gesture_to, count))
else: 
  print(f"The option you have selected is not available. Bye!")