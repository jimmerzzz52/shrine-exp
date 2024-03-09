import cv2
import mediapipe as mp
import datetime
from pathlib import Path
from multiprocessing import Pool
from cap_from_youtube import cap_from_youtube

from math import atan2, degrees, sqrt
from itertools import zip_longest
import os

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

# Excute in parallel?
execute_parallel = False


def transcribe_word(word):
    pose_name = f"{word.get('id')}_Transcription_Pose"
    left_name = f"{word.get('id')}_Transcription_Left_Hand"
    rigth_name = f"{word.get('id')}_Transcription_Right_Hand"

    if (
        not os.path.isfile(f"./gesture_data/{pose_name}.csv")
        or not os.path.isfile(f"./gesture_data/{left_name}.csv")
        or not os.path.isfile(f"./gesture_data/{rigth_name}.csv")
    ):
        if word.get("video_url").startswith("https://www.youtube.com"):
            cap = cap_from_youtube(word.get("video_url"))
        else:
            cap = cv2.VideoCapture(f'{word.get("video_url")}')

        # TODO 04: clean this.
        # pose_csv = "time,index,x_angle,y_angle,z_angle,x,y,z,pose_id\n"
        # left_hand_csv = "time,index,x_angle,y_angle,z_angle,x,y,z\n"
        # right_hand_csv = "time,index,x_angle,y_angle,z_angle,x,y,z\n"

        pose_csv = "time,index,x,y,z,pose_id\n"
        left_hand_csv = "time,index,x,y,z\n"
        right_hand_csv = "time,index,x,y,z\n"

        print("Capturing feed and registering pose points")
        with mp_holistic.Holistic(
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            enable_segmentation=True,
            refine_face_landmarks=True,
        ) as holistic:
            start_time = datetime.datetime.now()
            while cap.isOpened():
                success, image = cap.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    cap.release()
                    continue

                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)
                timeOfEvent = datetime.datetime.now()

                """
                TODO: 01: Issue here. We need to find the nearest limb to recrod the angle against instead of sequentially.
                e.g. for right and left hands. The limbs attached are as follows:
                0-1-2-3-4, 0-5-6-7-8, 0-9-10-11-12, 0-13-14-15-16, 0-17-18-19-20 etc.
                See here for a full registrar of poses, and what limb is closest.\
                    Hands: https://developers.google.com/mediapipe/solutions/vision/hand_landmarker
                    Poses: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker/

                There are 21 points for each hand, and 33 poses.
                """
                """
                First we need to create a dict of limb conections
                points 5, 9, 13 and 17 are also conected, but they
                tend to be close in angle and differential position for different poses.
                Seems best to use the tip points distance and angles for measuring whatever
                those conections would measure.
                """
                # limb_connections = {
                #     "thumb": [0, 1, 2, 3, 4],
                #     "index": [0, 5, 6, 7, 8],
                #     "middle": [0, 9, 10, 11, 12],
                #     "ring": [0, 13, 14, 15, 16],
                #     "pinky": [0, 17, 18, 19, 20],
                #     "palm": [2, 5, 9, 13, 17],
                # }

                # The angles are organized in the csv as being one set of angles for each node.
                # But node 0, for instance, appears in all limbs. So it will appear
                # 5 times in the csv. So it doesn't seem adequate to record one set of angles for each node.
                # It seems better to record the angles for each limb, and then the position of the nodes.


                # TODO: Move this into a module of some type.
                if results.pose_landmarks:
                    for index, data_point in enumerate(results.pose_landmarks.landmark):
                        
                        pose_csv = (
                            pose_csv
                            + f"{timeOfEvent - start_time},"
                            + f"{index},"
                            + f"{data_point.x},"
                            + f"{data_point.y},"
                            + f"{data_point.z},"
                            + f'{word.get("id")} \n'
                        )

                if results.right_hand_landmarks:
                    
                    data = list(results.right_hand_landmarks.landmark)
                    for index, value in enumerate(data):

                        right_hand_csv = (
                            right_hand_csv
                            + f"{timeOfEvent - start_time},"
                            + f"{index},"
                            + f"{value.x},"
                            + f"{value.y},"
                            + f"{value.z} \n"
                        )
                        
                if results.left_hand_landmarks:
                    
                    data = list(results.left_hand_landmarks.landmark)
                    for index, value in enumerate(data):

                        left_hand_csv = (
                            left_hand_csv
                            + f"{timeOfEvent - start_time},"
                            + f"{index},"
                            + f"{value.x},"
                            + f"{value.y},"
                            + f"{value.z} \n"
                        )
                        
                image.flags.writeable = True
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                
                # For testing, if you want to see this....
                # mp_drawing.draw_landmarks(
                #     image,
                #     results.pose_landmarks,
                #     mp_holistic.POSE_CONNECTIONS,
                #     landmark_drawing_spec=mp_drawing_styles
                #     .get_default_pose_landmarks_style())

                # mp_drawing.draw_landmarks(
                #     image,
                #     results.left_hand_landmarks,
                #     mp_holistic.HAND_CONNECTIONS,
                #     landmark_drawing_spec=mp_drawing_styles
                #     .get_default_pose_landmarks_style())

                # mp_drawing.draw_landmarks(
                #     image,
                #     results.right_hand_landmarks,
                #     mp_holistic.HAND_CONNECTIONS,
                #     landmark_drawing_spec=mp_drawing_styles
                #     .get_default_pose_landmarks_style())

                # cv2.imshow('MediaPipe Holistic', image)
                # if cv2.waitKey(5) & 0xFF == 27:
                #     break
        cap.release()

        file = open(f"./gesture_data/{pose_name}.csv", "w")
        file.write(pose_csv)
        file.close()

        file = open(f"./gesture_data/{left_name}.csv", "w")
        file.write(left_hand_csv)
        file.close()

        file = open(f"./gesture_data/{rigth_name}.csv", "w")
        file.write(right_hand_csv)
        file.close()

        file = open(f"./gesture_data/all_pose.csv", "w")
        file.write(pose_csv)
        file.close()


words = [
    {
        "id": "ONE_YT",
        "video_url": "https://www.youtube.com/watch?v=DZK886Tz1aQ",
    },
    {
        "id": "ONE",
        "video_url": "https://www.handspeak.com//word/o/one/one-cardinal.mp4",
    },
    {
        "id": "HANDSPEAK",
        "video_url": "https://www.handspeak.com//word/h/han/handspeak.mp4",
    },
    {
        "id": "INTROSPECT",
        "video_url": "https://www.handspeak.com//word/i/int/introspect.mp4",
    },
    {"id": "ABANDON", "video_url": "https://www.handspeak.com//word/a/aba/abandon.mp4"},
    {
        "id": "ABBREVIATE",
        "video_url": "https://www.handspeak.com//word/a/abb/abbreviate.mp4",
    },
    {
        "id": "STILLBORN",
        "video_url": "https://www.handspeak.com//word/s/sti/stillborn.mp4",
    },
    {"id": "ABOUT", "video_url": "https://www.handspeak.com//word/a/abo/about.mp4"},
    {
        "id": "REGARDING",
        "video_url": "https://www.handspeak.com//word/r/reg/regarding.mp4",
    },
    {"id": "ABOVE", "video_url": "https://www.handspeak.com//word/a/abo/above.mp4"},
    {"id": "ARTWORK", "video_url": "https://www.handspeak.com//word/a/art/artwork.mp4"},
    {"id": "ACCEPT", "video_url": "https://www.handspeak.com//word/a/acc/accept.mp4"},
    {"id": "BABY", "video_url": "https://www.handspeak.com//word/b/bab/baby.mp4"},
    {"id": "BACON", "video_url": "https://www.handspeak.com//word/b/bac/bacon.mp4"},
    {
        "id": "REAR-FACING",
        "video_url": "https://www.handspeak.com//word/r/rea/rear-facing-carseat.mp4",
    },
    {"id": "SPINE", "video_url": "https://www.handspeak.com//word/b/bac/backbone.mp4"},
    {
        "id": "BACKSTROKE",
        "video_url": "https://www.handspeak.com//word/b/bac/backstroke.mp4",
    },
    {
        "id": "FORTH",
        "video_url": "https://www.handspeak.com//word/b/bac/back-forth.mp4",
    },
    {"id": "CAKE", "video_url": "https://www.handspeak.com//word/c/cak/cake-fs.mp4"},
    {
        "id": "CALCULATOR",
        "video_url": "https://www.handspeak.com//word/c/cal/calculator.mp4",
    },
    {"id": "CALGARY", "video_url": "https://www.handspeak.com//word/c/cal/calgary.mp4"},
    {
        "id": "FLAMES",
        "video_url": "https://www.handspeak.com//word/c/cal/calgary-flames.mp4",
    },
    {
        "id": "ACCIDENT",
        "video_url": "https://www.handspeak.com//word/a/acc/accident.mp4",
    },
    {
        "id": "ACCIDENTAL",
        "video_url": "https://www.handspeak.com//word/a/acc/accidental.mp4",
    },
    {
        "id": "ACCOUNTING",
        "video_url": "https://www.handspeak.com//word/a/acc/accounting.mp4",
    },
    {"id": "ACROSS", "video_url": "https://www.handspeak.com//word/a/across.mp4"},
    {"id": "ACTIVE", "video_url": "https://www.handspeak.com//word/a/act/active.mp4"},
    {
        "id": "ACTIVITY",
        "video_url": "https://www.handspeak.com//word/a/act/activity.mp4",
    },
    {"id": "PLUS", "video_url": "https://www.handspeak.com//word/p/plu/plus.mp4"},
    {"id": "ADD", "video_url": "https://www.handspeak.com//word/a/add/add.mp4"},
    {
        "id": "ADDICTION",
        "video_url": "https://www.handspeak.com//word/a/add/addictive.mp4",
    },
    {"id": "ADDRESS", "video_url": "https://www.handspeak.com//word/a/add/address.mp4"},
    {"id": "ADMIRE", "video_url": "https://www.handspeak.com//word/a/adm/admire.mp4"},
    {"id": "ADMIT", "video_url": "https://www.handspeak.com//word/a/adm/admit.mp4"},
    {
        "id": "EDUCATION",
        "video_url": "https://www.handspeak.com//word/a/adult-education.mp4",
    },
    {
        "id": "PRIVILEGE",
        "video_url": "https://www.handspeak.com//word/p/pri/privilege-benefit.mp4",
    },
    {
        "id": "ARBITRATE",
        "video_url": "https://www.handspeak.com//word/a/arb/arbitrate.mp4",
    },
    {
        "id": "ADVENTURE",
        "video_url": "https://www.handspeak.com//word/a/adv/adventure-fs.mp4",
    },
    {
        "id": "ADVERTISE",
        "video_url": "https://www.handspeak.com//word/a/adv/advertisement.mp4",
    },
    {
        "id": "CATALOGUE",
        "video_url": "https://www.handspeak.com//word/c/cat/catalog-fs.mp4",
    },
    {"id": "ADVISE", "video_url": "https://www.handspeak.com//word/a/adv/advice2.mp4"},
    {
        "id": "ADVOCACY",
        "video_url": "https://www.handspeak.com//word/a/adv/advocacy-support.mp4",
    },
    {
        "id": "AESTHETICS",
        "video_url": "https://www.handspeak.com//word/a/aesthetics.mp4",
    },
    {"id": "HARVEST", "video_url": "https://www.handspeak.com//word/h/har/harvest.mp4"},
    {
        "id": "AFFILIATE",
        "video_url": "https://www.handspeak.com//word/a/aff/affiliate.mp4",
    },
    {"id": "DATE", "video_url": "https://www.handspeak.com//word/u/upd/update.mp4"},
    {
        "id": "AFGHANISTAN",
        "video_url": "https://www.handspeak.com//word/a/afghanistan-rohullah.mp4",
    },
    {"id": "CITIES", "video_url": "https://www.handspeak.com//word/a/afghanista.mp4"},
    {"id": "AFRAID", "video_url": "https://www.handspeak.com//word/a/afr/afraid.mp4"},
    {"id": "AFRICA", "video_url": "https://www.handspeak.com//word/a/afr/africa.mp4"},
    {"id": "AFTER", "video_url": "https://www.handspeak.com//word/a/aft/after.mp4"},
    {
        "id": "AFTERNOON",
        "video_url": "https://www.handspeak.com//word/a/aft/afternoon.mp4",
    },
    {"id": "AGAIN", "video_url": "https://www.handspeak.com//word/a/aga/again.mp4"},
    {"id": "AGAINST", "video_url": "https://www.handspeak.com//word/a/aga/against.mp4"},
    {
        "id": "AGGRESSIVE",
        "video_url": "https://www.handspeak.com//word/a/agg/aggressive.mp4",
    },
    {"id": "AGREE", "video_url": "https://www.handspeak.com//word/a/agree.mp4"},
    {"id": "AHEAD", "video_url": "https://www.handspeak.com//word/a/ahe/ahead.mp4"},
    {
        "id": "AIRPLANE",
        "video_url": "https://www.handspeak.com//word/a/air/airplane.mp4",
    },
    {"id": "AIRPORT", "video_url": "https://www.handspeak.com//word/a/air/airport.mp4"},
    {"id": "ALARM", "video_url": "https://www.handspeak.com//word/a/ala/alarm.mp4"},
    {
        "id": "ANONYMOUS",
        "video_url": "https://www.handspeak.com//word/a/ano/anonymous.mp4",
    },
    {"id": "ALL", "video_url": "https://www.handspeak.com//word/a/all/all.mp4"},
    {
        "id": "EVERYBODY",
        "video_url": "https://www.handspeak.com//word/e/eve/everybody.mp4",
    },
    {"id": "RIGHT", "video_url": "https://www.handspeak.com//word/a/all/all-right.mp4"},
    {"id": "ALLERGY", "video_url": "https://www.handspeak.com//word/a/all/allergy.mp4"},
    {
        "id": "ATTACK",
        "video_url": "https://www.handspeak.com//word/a/all/allergy-attack.mp4",
    },
    {"id": "ALLOW", "video_url": "https://www.handspeak.com//word/a/all/allow.mp4"},
    {"id": "ALMOST", "video_url": "https://www.handspeak.com//word/a/alm/almost.mp4"},
    {"id": "BREADTH", "video_url": "https://www.handspeak.com//word/b/by/by-hair.mp4"},
    {"id": "ALONE", "video_url": "https://www.handspeak.com//word/a/alo/alone.mp4"},
    {"id": "ALSO", "video_url": "https://www.handspeak.com//word/a/also.mp4"},
    {
        "id": "ALTOGETHER",
        "video_url": "https://www.handspeak.com//word/a/alt/altogether.mp4",
    },
    {"id": "ALWAYS", "video_url": "https://www.handspeak.com//word/a/alw/always.mp4"},
    {
        "id": "AMBULANCE",
        "video_url": "https://www.handspeak.com//word/a/amb/ambulance.mp4",
    },
    {"id": "AMERICA", "video_url": "https://www.handspeak.com//word/a/ame/america.mp4"},
    {
        "id": "AMERICA",
        "video_url": "https://www.handspeak.com//word/n/nor/north-america2.mp4",
    },
    {
        "id": "AMERICA",
        "video_url": "https://www.handspeak.com//word/s/sou/south-america2.mp4",
    },
    {"id": "FLU", "video_url": "https://www.handspeak.com//word/f/flu/flu-fs.mp4"},
    {"id": "AID", "video_url": "https://www.handspeak.com//word/f/fir/first-aid.mp4"},
    {
        "id": "FRACTURE",
        "video_url": "https://www.handspeak.com//word/f/fra/fracture.mp4",
    },
    {"id": "AND", "video_url": "https://www.handspeak.com//word/a/and/and.mp4"},
    {"id": "Language", "video_url": "https://www.handspeak.com//word/a/ang/angel.mp4"},
    {"id": "ANGRY", "video_url": "https://www.handspeak.com//word/a/ang/angry.mp4"},
    {"id": "ANIMAL", "video_url": "https://www.handspeak.com//word/a/ani/animal.mp4"},
    {
        "id": "ANIMATION",
        "video_url": "https://www.handspeak.com//word/a/ani/animation.mp4",
    },
    {
        "id": "APOLOGIZE",
        "video_url": "https://www.handspeak.com//word/a/apo/apology.mp4",
    },
    {
        "id": "ANNOUNCEMENT",
        "video_url": "https://www.handspeak.com//word/a/ann/announce.mp4",
    },
    {"id": "ANNOYED", "video_url": "https://www.handspeak.com//word/a/ann/annoy.mp4"},
    {"id": "ANNUAL", "video_url": "https://www.handspeak.com//word/a/ann/annual.mp4"},
    {"id": "ANOINT", "video_url": "https://www.handspeak.com//word/a/anoint.mp4"},
    {"id": "ANOTHER", "video_url": "https://www.handspeak.com//word/a/another.mp4"},
    {"id": "ANSWER", "video_url": "https://www.handspeak.com//word/a/answer.mp4"},
    {"id": "ANY", "video_url": "https://www.handspeak.com//word/a/any/any.mp4"},
    {
        "id": "ANYTHING",
        "video_url": "https://www.handspeak.com//word/a/any/anything2.mp4",
    },
    {
        "id": "ANYTIME",
        "video_url": "https://www.handspeak.com//word/a/any/any-time.mp4",
    },
    {"id": "APART", "video_url": "https://www.handspeak.com//word/a/apa/apart.mp4"},
    {
        "id": "APPEAR",
        "video_url": "https://www.handspeak.com//word/a/app/appear-showup.mp4",
    },
    {
        "id": "APPEARANCE",
        "video_url": "https://www.handspeak.com//word/a/app/appearance.mp4",
    },
    {"id": "APPLE", "video_url": "https://www.handspeak.com//word/a/app/apple.mp4"},
    {
        "id": "APPOINTMENT",
        "video_url": "https://www.handspeak.com//word/a/app/appoint.mp4",
    },
    {
        "id": "APPROACH",
        "video_url": "https://www.handspeak.com//word/a/app/approach.mp4",
    },
    {
        "id": "TACTIC",
        "video_url": "https://www.handspeak.com//word/t/tac/tactic-plan.mp4",
    },
    {
        "id": "APPROPRIATION",
        "video_url": "https://www.handspeak.com//word/a/app/appropriation.mp4",
    },
    {
        "id": "APPROVAL",
        "video_url": "https://www.handspeak.com//word/a/app/approve.mp4",
    },
    {"id": "NOW", "video_url": "https://www.handspeak.com//word/u/up-to-now.mp4"},
    {"id": "ARGUMENT", "video_url": "https://www.handspeak.com//word/a/arg/argue.mp4"},
    {"id": "ARM", "video_url": "https://www.handspeak.com//word/a/arm/arm.mp4"},
    {
        "id": "ARMADILLO",
        "video_url": "https://www.handspeak.com//word/a/arm/armadillo.mp4",
    },
    {"id": "ARMY", "video_url": "https://www.handspeak.com//word/a/arm/army.mp4"},
    {
        "id": "AROUND",
        "video_url": "https://www.handspeak.com//word/a/aro/around-env.mp4",
    },
    {
        "id": "SURROUND",
        "video_url": "https://www.handspeak.com//word/s/sur/surrounding.mp4",
    },
    {"id": "ARREST", "video_url": "https://www.handspeak.com//word/a/arr/arrest.mp4"},
    {"id": "DETAIN", "video_url": "https://www.handspeak.com//word/d/det/detain.mp4"},
    {"id": "SEIZE", "video_url": "https://www.handspeak.com//word/s/sei/seize.mp4"},
    {"id": "ARRIVE", "video_url": "https://www.handspeak.com//word/a/arr/arrive.mp4"},
    {"id": "ART", "video_url": "https://www.handspeak.com//word/a/art/art-fs.mp4"},
    {"id": "FLICKER", "video_url": "https://www.handspeak.com//word/f/fli/flicker.mp4"},
    {"id": "ARTICLE", "video_url": "https://www.handspeak.com//word/a/art/article.mp4"},
    {"id": "ASK", "video_url": "https://www.handspeak.com//word/a/ask/ask.mp4"},
    {"id": "AWAY", "video_url": "https://www.handspeak.com//word/a/ask/ask-away.mp4"},
    {"id": "OUT", "video_url": "https://www.handspeak.com//word/a/ask/ask-out.mp4"},
    {"id": "Language", "video_url": "https://www.handspeak.com//word/a/asl/asl-fs.mp4"},
    {
        "id": "ROTE",
        "video_url": "https://www.handspeak.com//word/r/rot/rote-learning.mp4",
    },
    {
        "id": "ASSOCIATION",
        "video_url": "https://www.handspeak.com//word/a/ass/association.mp4",
    },
    {"id": "ASTHMA", "video_url": "https://www.handspeak.com//word/a/ast/asthma.mp4"},
    {"id": "ATHLETE", "video_url": "https://www.handspeak.com//word/a/ath/athlete.mp4"},
    {
        "id": "ATTENTION",
        "video_url": "https://www.handspeak.com//word/a/att/attention.mp4",
    },
    {"id": "HEAR", "video_url": "https://www.handspeak.com//word/h/hea/hear-sound.mp4"},
    {
        "id": "EYE-CATCHING",
        "video_url": "https://www.handspeak.com//word/e/eye/eyecatching-attract.mp4",
    },
    {
        "id": "ATTITUDE",
        "video_url": "https://www.handspeak.com//word/a/att/attitude.mp4",
    },
    {
        "id": "ATTRACTIVE",
        "video_url": "https://www.handspeak.com//word/a/att/attract.mp4",
    },
    {"id": "AUCTION", "video_url": "https://www.handspeak.com//word/a/auction.mp4"},
    {
        "id": "AUDIOLOGY",
        "video_url": "https://www.handspeak.com//word/a/aud/audiology.mp4",
    },
    {"id": "AUNT", "video_url": "https://www.handspeak.com//word/a/aunt.mp4"},
    {
        "id": "AUSTRALIA",
        "video_url": "https://www.handspeak.com//word/a/aus/australia.mp4",
    },
    {
        "id": "AUSSIE",
        "video_url": "https://www.handspeak.com//word/a/aus/australia2.mp4",
    },
    {"id": "AUSTRIA", "video_url": "https://www.handspeak.com//word/a/aus/austria.mp4"},
    {
        "id": "AUSTRIAN",
        "video_url": "https://www.handspeak.com//word/a/aus/austria2.mp4",
    },
    {"id": "AUTHOR", "video_url": "https://www.handspeak.com//word/a/aut/author.mp4"},
    {
        "id": "AUTOMATIC",
        "video_url": "https://www.handspeak.com//word/a/aut/automatic.mp4",
    },
    {"id": "MEDIAN", "video_url": "https://www.handspeak.com//word/m/med/median.mp4"},
    {"id": "AVERAGE", "video_url": "https://www.handspeak.com//word/a/ave/average.mp4"},
    {"id": "AVOID", "video_url": "https://www.handspeak.com//word/a/avo/avoid.mp4"},
    {
        "id": "AWARD",
        "video_url": "https://www.handspeak.com//word/a/awa/award-verb.mp4",
    },
    {"id": "PRIZE", "video_url": "https://www.handspeak.com//word/p/pri/prize-fs.mp4"},
    {"id": "AWAY", "video_url": "https://www.handspeak.com//word/a/awa/away.mp4"},
    {"id": "AWE", "video_url": "https://www.handspeak.com//word/a/awe/awe.mp4"},
    {
        "id": "AWESTRUCK",
        "video_url": "https://www.handspeak.com//word/a/awe/awestruck.mp4",
    },
    {"id": "AWFUL", "video_url": "https://www.handspeak.com//word/a/awful.mp4"},
    {"id": "AWKWARD", "video_url": "https://www.handspeak.com//word/a/awk/awkward.mp4"},
    {
        "id": "BACKWARD",
        "video_url": "https://www.handspeak.com//word/b/bac/backward.mp4",
    },
    {"id": "BAD", "video_url": "https://www.handspeak.com//word/b/bad/bad.mp4"},
    {"id": "BAGEL", "video_url": "https://www.handspeak.com//word/b/bag/bagel-fs.mp4"},
    {"id": "BAHRAIN", "video_url": "https://www.handspeak.com//word/b/bahrain.mp4"},
    {"id": "BALD", "video_url": "https://www.handspeak.com//word/b/bal/bald.mp4"},
    {"id": "BALL", "video_url": "https://www.handspeak.com//word/b/bal/ball.mp4"},
    {"id": "BALLOON", "video_url": "https://www.handspeak.com//word/b/bal/balloon.mp4"},
    {"id": "BANANA", "video_url": "https://www.handspeak.com//word/b/ban/banana.mp4"},
    {
        "id": "BASEMENT",
        "video_url": "https://www.handspeak.com//word/b/bas/basement.mp4",
    },
    {"id": "BASIC", "video_url": "https://www.handspeak.com//word/b/bas/basic.mp4"},
    {
        "id": "BASKETBALL",
        "video_url": "https://www.handspeak.com//word/b/bas/basketball.mp4",
    },
    {"id": "BASKING", "video_url": "https://www.handspeak.com//word/b/bas/basking.mp4"},
    {
        "id": "BATTERY",
        "video_url": "https://www.handspeak.com//word/b/bat/battery-power.mp4",
    },
    {"id": "BARK", "video_url": "https://www.handspeak.com//word/b/bar/bark.mp4"},
    {
        "id": "BASEBALL",
        "video_url": "https://www.handspeak.com//word/b/bas/baseball.mp4",
    },
    {"id": "BATH", "video_url": "https://www.handspeak.com//word/b/bat/bath.mp4"},
    {"id": "OUT", "video_url": "https://www.handspeak.com//word/b/bawl-out.mp4"},
    {"id": "THERE", "video_url": "https://www.handspeak.com//word/b/bee/been-to.mp4"},
    {"id": "BEACH", "video_url": "https://www.handspeak.com//word/b/bea/beach.mp4"},
    {"id": "BEAR", "video_url": "https://www.handspeak.com//word/b/bea/bear.mp4"},
    {
        "id": "VANQUISH",
        "video_url": "https://www.handspeak.com//word/b/bea/beat-it.mp4",
    },
    {"id": "BEAT", "video_url": "https://www.handspeak.com//word/b/bea/beat-hit.mp4"},
    {
        "id": "BEAUTIFUL",
        "video_url": "https://www.handspeak.com//word/b/bea/beautiful.mp4",
    },
    {"id": "BECAUSE", "video_url": "https://www.handspeak.com//word/b/bec/because.mp4"},
    {"id": "AS", "video_url": "https://www.handspeak.com//word/a/as-since.mp4"},
    {"id": "BECOME", "video_url": "https://www.handspeak.com//word/b/bec/become.mp4"},
    {"id": "BED", "video_url": "https://www.handspeak.com//word/b/bed/bed.mp4"},
    {"id": "BEDROOM", "video_url": "https://www.handspeak.com//word/b/bed/bedroom.mp4"},
    {"id": "BEFORE", "video_url": "https://www.handspeak.com//word/b/bef/before.mp4"},
    {
        "id": "HITHERTO",
        "video_url": "https://www.handspeak.com//word/h/hit/hitherto.mp4",
    },
    {
        "id": "FORERUNNER",
        "video_url": "https://www.handspeak.com//word/p/pre/predecessor.mp4",
    },
    {"id": "BEG", "video_url": "https://www.handspeak.com//word/b/beg/beg.mp4"},
    {
        "id": "PETITION",
        "video_url": "https://www.handspeak.com//word/p/pet/petition.mp4",
    },
    {"id": "BEHIND", "video_url": "https://www.handspeak.com//word/b/beh/behind.mp4"},
    {"id": "BELIEF", "video_url": "https://www.handspeak.com//word/b/bel/believe.mp4"},
    {"id": "BELOW", "video_url": "https://www.handspeak.com//word/b/bel/below.mp4"},
    {"id": "BELT", "video_url": "https://www.handspeak.com//word/b/bel/belt-waist.mp4"},
    {"id": "BENEFIT", "video_url": "https://www.handspeak.com//word/b/ben/benefit.mp4"},
    {
        "id": "SWITZERLAND",
        "video_url": "https://www.handspeak.com//word/b/ber/bern-ch.mp4",
    },
    {"id": "BEST", "video_url": "https://www.handspeak.com//word/b/bes/best.mp4"},
    {"id": "BETTER", "video_url": "https://www.handspeak.com//word/b/bet/better.mp4"},
    {"id": "BETWEEN", "video_url": "https://www.handspeak.com//word/b/bet/between.mp4"},
    {"id": "NEPAL", "video_url": "https://www.handspeak.com//word/b/bhaktapur.mp4"},
    {"id": "BIBLE", "video_url": "https://www.handspeak.com//word/b/bib/bible.mp4"},
    {"id": "BICYCLE", "video_url": "https://www.handspeak.com//word/b/bic/bicycle.mp4"},
    {"id": "BID", "video_url": "https://www.handspeak.com//word/b/bid/bid.mp4"},
    {"id": "BIG", "video_url": "https://www.handspeak.com//word/b/big/big.mp4"},
    {"id": "OSAMA", "video_url": "https://www.handspeak.com//word/b/bin/bin-laden.mp4"},
    {
        "id": "BINOCULAR",
        "video_url": "https://www.handspeak.com//word/b/bin/binocular.mp4",
    },
    {"id": "Language", "video_url": "https://www.handspeak.com//word/b/bir/bird.mp4"},
    {
        "id": "BIRTHDAY",
        "video_url": "https://www.handspeak.com//word/b/bir/birthday.mp4",
    },
    {
        "id": "BIRTHDATE",
        "video_url": "https://www.handspeak.com//word/b/bir/birthdate.mp4",
    },
    {"id": "ELSE", "video_url": "https://www.handspeak.com//word/w/wha/what-else.mp4"},
    {
        "id": "BITE",
        "video_url": "https://www.handspeak.com//word/b/bit/bite-something.mp4",
    },
    {"id": "GNAW", "video_url": "https://www.handspeak.com//word/g/gnaw-bite.mp4"},
    {
        "id": "IMPAIRED",
        "video_url": "https://www.handspeak.com//word/h/hea/hearing-impaired.mp4",
    },
    {"id": "BITTER", "video_url": "https://www.handspeak.com//word/b/bit/bitter.mp4"},
    {"id": "ACID", "video_url": "https://www.handspeak.com//word/a/aci/acid-fs.mp4"},
    {
        "id": "DIRECTORS",
        "video_url": "https://www.handspeak.com//word/b/boa/board-org.mp4",
    },
    {"id": "BOAT", "video_url": "https://www.handspeak.com//word/b/boa/boat.mp4"},
    {"id": "BODY", "video_url": "https://www.handspeak.com//word/b/bod/body.mp4"},
    {"id": "BOOK", "video_url": "https://www.handspeak.com//word/b/boo/book.mp4"},
    {"id": "ART", "video_url": "https://www.handspeak.com//word/b/boo/book-art.mp4"},
    {
        "id": "BOOKCASE",
        "video_url": "https://www.handspeak.com//word/b/boo/bookcase.mp4",
    },
    {"id": "BORING", "video_url": "https://www.handspeak.com//word/b/bor/boring.mp4"},
    {
        "id": "BLAND",
        "video_url": "https://www.handspeak.com//word/b/bla/bland-taste.mp4",
    },
    {"id": "BORN", "video_url": "https://www.handspeak.com//word/b/bor/born.mp4"},
    {"id": "BORROW", "video_url": "https://www.handspeak.com//word/b/bor/borrow.mp4"},
    {"id": "BOTHER", "video_url": "https://www.handspeak.com//word/b/bot/bother.mp4"},
    {"id": "BOTTLE", "video_url": "https://www.handspeak.com//word/b/bot/bottle.mp4"},
    {"id": "BOTTOM", "video_url": "https://www.handspeak.com//word/b/bot/bottom.mp4"},
    {
        "id": "BOUNCE",
        "video_url": "https://www.handspeak.com//word/b/bou/bounce-ball.mp4",
    },
    {"id": "REBOUND", "video_url": "https://www.handspeak.com//word/b/bou/bounce.mp4"},
    {"id": "BOWL", "video_url": "https://www.handspeak.com//word/b/bow/bowl.mp4"},
    {"id": "BOY", "video_url": "https://www.handspeak.com//word/b/boy/boy.mp4"},
    {
        "id": "BOYFRIEND",
        "video_url": "https://www.handspeak.com//word/b/boy/boyfriend.mp4",
    },
    {"id": "BLACK", "video_url": "https://www.handspeak.com//word/b/bla/black.mp4"},
    {"id": "BLAME", "video_url": "https://www.handspeak.com//word/b/bla/blame.mp4"},
    {"id": "BLESS", "video_url": "https://www.handspeak.com//word/b/ble/bless.mp4"},
    {"id": "BLIND", "video_url": "https://www.handspeak.com//word/b/bli/blind.mp4"},
    {
        "id": "GENTLEMAN",
        "video_url": "https://www.handspeak.com//word/g/gen/gentleman.mp4",
    },
    {"id": "BLONDE", "video_url": "https://www.handspeak.com//word/b/blo/blonde.mp4"},
    {"id": "BLOOD", "video_url": "https://www.handspeak.com//word/b/blo/blood.mp4"},
    {"id": "BLUE", "video_url": "https://www.handspeak.com//word/b/blu/blue.mp4"},
    {"id": "BLUR", "video_url": "https://www.handspeak.com//word/b/blu/blur.mp4"},
    {
        "id": "BOLIVIA",
        "video_url": "https://www.handspeak.com//word/b/bol/bolivia-bo.mp4",
    },
    {"id": "BOMB", "video_url": "https://www.handspeak.com//word/b/bom/bomb.mp4"},
    {"id": "BOSS", "video_url": "https://www.handspeak.com//word/b/bos/boss.mp4"},
    {
        "id": "BOSSY",
        "video_url": "https://www.handspeak.com//word/b/bos/bossy-command.mp4",
    },
    {"id": "BOTH", "video_url": "https://www.handspeak.com//word/b/bot/both.mp4"},
    {"id": "BOXING", "video_url": "https://www.handspeak.com//word/b/box/boxing.mp4"},
    {"id": "BRAG", "video_url": "https://www.handspeak.com//word/b/bra/brag.mp4"},
    {"id": "BRAID", "video_url": "https://www.handspeak.com//word/b/bra/braid.mp4"},
    {
        "id": "BRAINSTORM",
        "video_url": "https://www.handspeak.com//word/b/bra/brainstorm.mp4",
    },
    {
        "id": "BRAINWASH",
        "video_url": "https://www.handspeak.com//word/b/bra/brainwash.mp4",
    },
    {"id": "BRAILLE", "video_url": "https://www.handspeak.com//word/b/bra/braille.mp4"},
    {"id": "BRAVE", "video_url": "https://www.handspeak.com//word/b/bra/brave.mp4"},
    {"id": "BREAD", "video_url": "https://www.handspeak.com//word/b/bre/bread.mp4"},
    {"id": "BREAK", "video_url": "https://www.handspeak.com//word/b/bre/break.mp4"},
    {"id": "INSERT", "video_url": "https://www.handspeak.com//word/i/ins/insert.mp4"},
    {"id": "DOWN", "video_url": "https://www.handspeak.com//word/b/bre/break-down.mp4"},
    {"id": "UP", "video_url": "https://www.handspeak.com//word/b/bre/break-up.mp4"},
    {
        "id": "BREAKFAST",
        "video_url": "https://www.handspeak.com//word/b/bre/breakfast.mp4",
    },
    {
        "id": "BREASTFEEDING",
        "video_url": "https://www.handspeak.com//word/b/bre/breastfeed.mp4",
    },
    {
        "id": "BREASTSTROKE",
        "video_url": "https://www.handspeak.com//word/b/bre/breaststroke.mp4",
    },
    {"id": "BREATHE", "video_url": "https://www.handspeak.com//word/b/bre/breathe.mp4"},
    {"id": "GULP", "video_url": "https://www.handspeak.com//word/g/gul/gulp.mp4"},
    {"id": "GERMANY", "video_url": "https://www.handspeak.com//word/b/bre/bremen.mp4"},
    {
        "id": "BRIEF",
        "video_url": "https://www.handspeak.com//word/b/bri/brief-short.mp4",
    },
    {"id": "BRIGHT", "video_url": "https://www.handspeak.com//word/b/bri/bright.mp4"},
    {
        "id": "BRILLIANT",
        "video_url": "https://www.handspeak.com//word/b/bri/brilliant.mp4",
    },
    {"id": "BRING", "video_url": "https://www.handspeak.com//word/b/bri/bring.mp4"},
    {
        "id": "AUSTRALIA",
        "video_url": "https://www.handspeak.com//word/b/bri/brisbane-au.mp4",
    },
    {
        "id": "BROADCAST",
        "video_url": "https://www.handspeak.com//word/b/bro/broadcast.mp4",
    },
    {
        "id": "BROKE",
        "video_url": "https://www.handspeak.com//word/b/bro/broke-empty.mp4",
    },
    {"id": "BROTHER", "video_url": "https://www.handspeak.com//word/b/bro/brother.mp4"},
    {"id": "BROWN", "video_url": "https://www.handspeak.com//word/b/bro/brown-usa.mp4"},
    {
        "id": "BROWNNOSE",
        "video_url": "https://www.handspeak.com//word/b/bro/brownnose.mp4",
    },
    {
        "id": "MOLLYCODDLE",
        "video_url": "https://www.handspeak.com//word/m/mol/mollycoddle.mp4",
    },
    {
        "id": "BRUISE",
        "video_url": "https://www.handspeak.com//word/b/bru/bruise-arm.mp4",
    },
    {
        "id": "DISCOLOR",
        "video_url": "https://www.handspeak.com//word/d/dis/discolor.mp4",
    },
    {"id": "BLEMISH", "video_url": "https://www.handspeak.com//word/b/ble/blemish.mp4"},
    {
        "id": "BIRTHMARK",
        "video_url": "https://www.handspeak.com//word/b/bir/birthmark.mp4",
    },
    {
        "id": "BRUSH",
        "video_url": "https://www.handspeak.com//word/b/bru/brush-comb.mp4",
    },
    {
        "id": "BLOWER",
        "video_url": "https://www.handspeak.com//word/b/bub/bubble-blower.mp4",
    },
    {
        "id": "FIZZ",
        "video_url": "https://www.handspeak.com//word/b/bub/bubble-container.mp4",
    },
    {"id": "FROTH", "video_url": "https://www.handspeak.com//word/f/fro/froth.mp4"},
    {
        "id": "BUDDHISM",
        "video_url": "https://www.handspeak.com//word/b/bud/buddhism-ojennings.mp4",
    },
    {
        "id": "BUDDHISM",
        "video_url": "https://www.handspeak.com//word/b/bud/buddhism-ojennings.mp4",
    },
    {
        "id": "BUDDHISM",
        "video_url": "https://www.handspeak.com//word/b/bud/buddhism-ojennings.mp4",
    },
    {"id": "BUDGET", "video_url": "https://www.handspeak.com//word/b/bud/budget.mp4"},
    {"id": "BUG", "video_url": "https://www.handspeak.com//word/b/bug/bug-insect.mp4"},
    {"id": "BUILD", "video_url": "https://www.handspeak.com//word/b/bui/build.mp4"},
    {"id": "BULL", "video_url": "https://www.handspeak.com//word/b/bul/bull.mp4"},
    {"id": "YONDER", "video_url": "https://www.handspeak.com//word/y/yonder.mp4"},
    {
        "id": "BURQA",
        "video_url": "https://www.handspeak.com//word/b/bur/burkha-mesh.mp4",
    },
    {
        "id": "HEADWEAR",
        "video_url": "https://www.handspeak.com//word/h/hea/headwear.mp4",
    },
    {"id": "CLOAK", "video_url": "https://www.handspeak.com//word/c/clo/cloak.mp4"},
    {"id": "PAUSE", "video_url": "https://www.handspeak.com//word/p/pause.mp4"},
    {
        "id": "BUSINESS",
        "video_url": "https://www.handspeak.com//word/b/bus/business.mp4",
    },
    {"id": "BUSY", "video_url": "https://www.handspeak.com//word/b/bus/busy.mp4"},
    {"id": "BUT", "video_url": "https://www.handspeak.com//word/b/but/but.mp4"},
    {"id": "BUTTER", "video_url": "https://www.handspeak.com//word/b/but/butter.mp4"},
    {
        "id": "BUTTERFLY",
        "video_url": "https://www.handspeak.com//word/b/but/butterfly.mp4",
    },
    {"id": "BUTTON", "video_url": "https://www.handspeak.com//word/b/but/button.mp4"},
    {"id": "BUY", "video_url": "https://www.handspeak.com//word/b/buy/buy.mp4"},
    {
        "id": "PURCHASE",
        "video_url": "https://www.handspeak.com//word/p/pur/purchase.mp4",
    },
    {"id": "BYE", "video_url": "https://www.handspeak.com//word/b/bye/bye-wave.mp4"},
    {"id": "SO-LONG", "video_url": "https://www.handspeak.com//word/b/bye/bye-bye.mp4"},
    {"id": "DUB", "video_url": "https://www.handspeak.com//word/c/cal/call-name.mp4"},
    {"id": "CALL", "video_url": "https://www.handspeak.com//word/c/cal/call-phone.mp4"},
    {
        "id": "EXCLAIM",
        "video_url": "https://www.handspeak.com//word/c/cal/call-summon.mp4",
    },
    {"id": "CALM", "video_url": "https://www.handspeak.com//word/c/cal/calm.mp4"},
    {"id": "SERENE", "video_url": "https://www.handspeak.com//word/s/ser/serene2.mp4"},
    {"id": "CAMERA", "video_url": "https://www.handspeak.com//word/c/cam/camera.mp4"},
    {"id": "JULIENNE", "video_url": "https://www.handspeak.com//word/j/julienne.mp4"},
    {"id": "CAMP", "video_url": "https://www.handspeak.com//word/c/cam/camping2.mp4"},
    {"id": "RADAR", "video_url": "https://www.handspeak.com//word/r/rad/radar.mp4"},
    {"id": "CAN", "video_url": "https://www.handspeak.com//word/c/can/can.mp4"},
    {"id": "CANNOT", "video_url": "https://www.handspeak.com//word/c/can/cannot.mp4"},
    {"id": "CANADA", "video_url": "https://www.handspeak.com//word/c/can/canada.mp4"},
    {"id": "PHONEME", "video_url": "https://www.handspeak.com//word/p/pho/phoneme.mp4"},
    {
        "id": "SYLLABLE",
        "video_url": "https://www.handspeak.com//word/s/syl/syllable2.mp4",
    },
    {"id": "CANCEL", "video_url": "https://www.handspeak.com//word/c/can/cancel.mp4"},
    {
        "id": "CANCER",
        "video_url": "https://www.handspeak.com//word/c/can/cancer-fs.mp4",
    },
    {"id": "CANDLE", "video_url": "https://www.handspeak.com//word/c/can/candle.mp4"},
    {"id": "CANDY", "video_url": "https://www.handspeak.com//word/c/can/candy-usa.mp4"},
    {
        "id": "CAPITALISM",
        "video_url": "https://www.handspeak.com//word/c/cap/capitalism.mp4",
    },
    {"id": "CAPTURE", "video_url": "https://www.handspeak.com//word/c/cap/capture.mp4"},
    {
        "id": "CARJACKING",
        "video_url": "https://www.handspeak.com//word/c/car/carjacking.mp4",
    },
    {"id": "CAR", "video_url": "https://www.handspeak.com//word/c/car/car2.mp4"},
    {
        "id": "ON",
        "video_url": "https://www.handspeak.com//word/g/get/get-in-vehicle.mp4",
    },
    {
        "id": "RACING",
        "video_url": "https://www.handspeak.com//word/h/hor/horse-racing.mp4",
    },
    {"id": "CAR", "video_url": "https://www.handspeak.com//word/b/bum/bumper-car.mp4"},
    {"id": "LIFE", "video_url": "https://www.handspeak.com//word/l/lif/life.mp4"},
    {"id": "UPROOT", "video_url": "https://www.handspeak.com//word/u/upr/uproot.mp4"},
    {"id": "IN", "video_url": "https://www.handspeak.com//word/p/pul/pull-over.mp4"},
    {
        "id": "LEAN",
        "video_url": "https://www.handspeak.com//word/l/lea/lean-on-car.mp4",
    },
    {
        "id": "INSURANCE",
        "video_url": "https://www.handspeak.com//word/c/car/car-insurance.mp4",
    },
    {"id": "CAREFUL", "video_url": "https://www.handspeak.com//word/c/car/careful.mp4"},
    {
        "id": "LESS",
        "video_url": "https://www.handspeak.com//word/c/cou/couldnt-careless.mp4",
    },
    {"id": "CARE", "video_url": "https://www.handspeak.com//word/c/car/care-for.mp4"},
    {"id": "CARRY", "video_url": "https://www.handspeak.com//word/c/car/carry.mp4"},
    {"id": "CASTE", "video_url": "https://www.handspeak.com//word/c/cas/caste.mp4"},
    {"id": "CAT", "video_url": "https://www.handspeak.com//word/c/cat/cat.mp4"},
    {"id": "CATCALL", "video_url": "https://www.handspeak.com//word/c/cat/catcall.mp4"},
    {"id": "CATCH", "video_url": "https://www.handspeak.com//word/c/cat/catch.mp4"},
    {"id": "CATCH", "video_url": "https://www.handspeak.com//word/c/cat/catch-22.mp4"},
    {
        "id": "CATHOLIC",
        "video_url": "https://www.handspeak.com//word/c/cat/catholic.mp4",
    },
    {"id": "WHITE", "video_url": "https://www.handspeak.com//word/c/cau/causacian.mp4"},
    {"id": "CAUSE", "video_url": "https://www.handspeak.com//word/c/cau/cause.mp4"},
    {
        "id": "CELEBRATE",
        "video_url": "https://www.handspeak.com//word/c/cel/celebrate.mp4",
    },
    {
        "id": "TRIWEEKLY",
        "video_url": "https://www.handspeak.com//word/t/tri/triweekly.mp4",
    },
    {"id": "STUFF", "video_url": "https://www.handspeak.com//word/s/stu/stuff-fs.mp4"},
    {
        "id": "DISABILITIES",
        "video_url": "https://www.handspeak.com//word/p/people-disabilities.mp4",
    },
    {"id": "TOPPLE", "video_url": "https://www.handspeak.com//word/t/top/topple.mp4"},
    {"id": "CENTER", "video_url": "https://www.handspeak.com//word/c/cen/center.mp4"},
    {
        "id": "AMERICA",
        "video_url": "https://www.handspeak.com//word/c/cen/central-america.mp4",
    },
    {"id": "OCEANIA", "video_url": "https://www.handspeak.com//word/o/oce/oceania.mp4"},
    {
        "id": "CERTIFICATE",
        "video_url": "https://www.handspeak.com//word/c/cer/certificate.mp4",
    },
    {"id": "CHAIR", "video_url": "https://www.handspeak.com//word/c/cha/chair.mp4"},
    {
        "id": "CHAIRPERSON",
        "video_url": "https://www.handspeak.com//word/c/cha/chair-meeting.mp4",
    },
    {"id": "CHAIN", "video_url": "https://www.handspeak.com//word/c/cha/chain.mp4"},
    {
        "id": "CHALLENGE",
        "video_url": "https://www.handspeak.com//word/c/cha/challenge.mp4",
    },
    {
        "id": "CHAMPAGNE",
        "video_url": "https://www.handspeak.com//word/c/cha/champagne.mp4",
    },
    {
        "id": "CHAMPION",
        "video_url": "https://www.handspeak.com//word/c/cha/champion.mp4",
    },
    {"id": "CHANCE", "video_url": "https://www.handspeak.com//word/c/cha/chance.mp4"},
    {"id": "CHANGE", "video_url": "https://www.handspeak.com//word/c/cha/change.mp4"},
    {"id": "TWEAK", "video_url": "https://www.handspeak.com//word/t/twe/tweak.mp4"},
    {"id": "CHAOS", "video_url": "https://www.handspeak.com//word/c/cha/chaos.mp4"},
    {
        "id": "CHARACTERISTIC",
        "video_url": "https://www.handspeak.com//word/c/cha/characteristic.mp4",
    },
    {
        "id": "CHARACTER",
        "video_url": "https://www.handspeak.com//word/c/cha/character-role.mp4",
    },
    {"id": "CHARGE", "video_url": "https://www.handspeak.com//word/c/cha/charge.mp4"},
    {"id": "CHASE", "video_url": "https://www.handspeak.com//word/c/cha/chase.mp4"},
    {
        "id": "CHAT",
        "video_url": "https://www.handspeak.com//word/c/cha/chat-conversation.mp4",
    },
    {"id": "CHATTY", "video_url": "https://www.handspeak.com//word/c/cha/chat2.mp4"},
    {"id": "CHEAP", "video_url": "https://www.handspeak.com//word/c/che/cheap.mp4"},
    {
        "id": "CHEAT",
        "video_url": "https://www.handspeak.com//word/c/che/cheat-eyben.mp4",
    },
    {"id": "BOGUS", "video_url": "https://www.handspeak.com//word/b/bog/bogus.mp4"},
    {"id": "TUMOR", "video_url": "https://www.handspeak.com//word/t/tum/tumor-fs.mp4"},
    {"id": "ON", "video_url": "https://www.handspeak.com//word/c/che/cheat-on.mp4"},
    {
        "id": "MARK",
        "video_url": "https://www.handspeak.com//word/c/che/check-mark2.mp4",
    },
    {
        "id": "CHECKOUT",
        "video_url": "https://www.handspeak.com//word/c/che/checkout.mp4",
    },
    {"id": "CHECK", "video_url": "https://www.handspeak.com//word/c/che/check.mp4"},
    {
        "id": "CHEERLEADING",
        "video_url": "https://www.handspeak.com//word/c/che/cheerlead.mp4",
    },
    {"id": "CHEESE", "video_url": "https://www.handspeak.com//word/c/che/cheese.mp4"},
    {"id": "CHEETAH", "video_url": "https://www.handspeak.com//word/c/che/cheetah.mp4"},
    {"id": "REVERE", "video_url": "https://www.handspeak.com//word/r/rev/revere.mp4"},
    {
        "id": "CHERRY",
        "video_url": "https://www.handspeak.com//word/c/che/cherry-heathermika.mp4",
    },
    {"id": "CHECK", "video_url": "https://www.handspeak.com//word/c/che/cheque.mp4"},
    {
        "id": "INVOICE",
        "video_url": "https://www.handspeak.com//word/i/inv/invoice-fs.mp4",
    },
    {"id": "CHEW", "video_url": "https://www.handspeak.com//word/c/che/chew.mp4"},
    {"id": "CHICKEN", "video_url": "https://www.handspeak.com//word/c/chi/chicken.mp4"},
    {"id": "CHILDREN", "video_url": "https://www.handspeak.com//word/c/chi/child.mp4"},
    {
        "id": "OFFSPRING",
        "video_url": "https://www.handspeak.com//word/o/off/offspring-child.mp4",
    },
    {"id": "CHINA", "video_url": "https://www.handspeak.com//word/c/chi/china.mp4"},
    {
        "id": "CHOCOLATE",
        "video_url": "https://www.handspeak.com//word/c/cho/chocolate.mp4",
    },
    {"id": "BOMB", "video_url": "https://www.handspeak.com//word/t/tim/timebomb.mp4"},
    {"id": "CHOICE", "video_url": "https://www.handspeak.com//word/c/cho/choice.mp4"},
    {"id": "CHRIST", "video_url": "https://www.handspeak.com//word/c/chr/christ.mp4"},
    {
        "id": "CHRISTMAS",
        "video_url": "https://www.handspeak.com//word/c/chr/christmas.mp4",
    },
    {
        "id": "LIGHTS",
        "video_url": "https://www.handspeak.com//word/c/chr/christmas-lights.mp4",
    },
    {"id": "CHUBBY", "video_url": "https://www.handspeak.com//word/c/chu/chubby.mp4"},
    {"id": "CHURCH", "video_url": "https://www.handspeak.com//word/c/chu/church.mp4"},
    {"id": "CIGAR", "video_url": "https://www.handspeak.com//word/c/cig/cigar.mp4"},
    {
        "id": "CIGARETTE",
        "video_url": "https://www.handspeak.com//word/c/cig/cigarette.mp4",
    },
    {"id": "CIRCLE", "video_url": "https://www.handspeak.com//word/c/cir/circle.mp4"},
    {"id": "CLAM", "video_url": "https://www.handspeak.com//word/c/cla/clam.mp4"},
    {"id": "CLASS", "video_url": "https://www.handspeak.com//word/c/cla/class.mp4"},
    {
        "id": "EMERGENCY",
        "video_url": "https://www.handspeak.com//word/e/eme/emergency.mp4",
    },
    {"id": "CLEANSE", "video_url": "https://www.handspeak.com//word/c/cle/cleanse.mp4"},
    {"id": "CLEAR", "video_url": "https://www.handspeak.com//word/c/cle/clear.mp4"},
    {
        "id": "LAURENT",
        "video_url": "https://www.handspeak.com//word/c/cle/clerc-laurent.mp4",
    },
    {
        "id": "CLICKBAIT",
        "video_url": "https://www.handspeak.com//word/c/cli/clickbait-tempt.mp4",
    },
    {"id": "CLICK", "video_url": "https://www.handspeak.com//word/c/cli/click-fs.mp4"},
    {"id": "CLIMB", "video_url": "https://www.handspeak.com//word/c/cli/climb.mp4"},
    {"id": "COVET", "video_url": "https://www.handspeak.com//word/c/cov/covet.mp4"},
    {
        "id": "CLOSE",
        "video_url": "https://www.handspeak.com//word/c/clo/close-hour.mp4",
    },
    {
        "id": "ADJACENT",
        "video_url": "https://www.handspeak.com//word/a/adj/adjacent.mp4",
    },
    {"id": "CLOTHE", "video_url": "https://www.handspeak.com//word/c/clo/clothe.mp4"},
    {"id": "CLOUD", "video_url": "https://www.handspeak.com//word/c/clo/cloud2.mp4"},
    {"id": "CLOWN", "video_url": "https://www.handspeak.com//word/c/clo/clown.mp4"},
    {"id": "COAT", "video_url": "https://www.handspeak.com//word/c/coa/coat.mp4"},
    {"id": "COCAINE", "video_url": "https://www.handspeak.com//word/c/coc/cocaine.mp4"},
    {"id": "COFFEE", "video_url": "https://www.handspeak.com//word/c/cof/coffee.mp4"},
    {"id": "COLD", "video_url": "https://www.handspeak.com//word/c/col/cold-brr.mp4"},
    {"id": "COLD", "video_url": "https://www.handspeak.com//word/c/col/cold-flu.mp4"},
    {"id": "COLLEGE", "video_url": "https://www.handspeak.com//word/c/col/college.mp4"},
    {
        "id": "PREPERATORY",
        "video_url": "https://www.handspeak.com//word/c/col/college-preparatory.mp4",
    },
    {"id": "COLOR", "video_url": "https://www.handspeak.com//word/c/col/color.mp4"},
    {
        "id": "COLORFUL",
        "video_url": "https://www.handspeak.com//word/c/col/colorful.mp4",
    },
    {"id": "COMB", "video_url": "https://www.handspeak.com//word/c/com/comb.mp4"},
    {"id": "COMBINE", "video_url": "https://www.handspeak.com//word/c/com/combine.mp4"},
    {"id": "COME", "video_url": "https://www.handspeak.com//word/c/com/come.mp4"},
    {"id": "HERE", "video_url": "https://www.handspeak.com//word/c/com/come-here.mp4"},
    {
        "id": "COMFORTABLE",
        "video_url": "https://www.handspeak.com//word/c/com/comfortable.mp4",
    },
    {
        "id": "COMMITMENT",
        "video_url": "https://www.handspeak.com//word/c/com/commit.mp4",
    },
    {"id": "COMMAND", "video_url": "https://www.handspeak.com//word/c/com/command.mp4"},
    {
        "id": "COMMANDO",
        "video_url": "https://www.handspeak.com//word/c/com/commando.mp4",
    },
    {"id": "COMMENT", "video_url": "https://www.handspeak.com//word/c/com/comment.mp4"},
    {
        "id": "COMMITTEE",
        "video_url": "https://www.handspeak.com//word/c/com/committee.mp4",
    },
    {"id": "COMMON", "video_url": "https://www.handspeak.com//word/c/com/common.mp4"},
    {
        "id": "UNCOMMON",
        "video_url": "https://www.handspeak.com//word/u/unc/uncommon.mp4",
    },
    {
        "id": "SENSE",
        "video_url": "https://www.handspeak.com//word/c/com/common-sense.mp4",
    },
    {
        "id": "COMMUNICATION",
        "video_url": "https://www.handspeak.com//word/c/com/communication.mp4",
    },
    {
        "id": "COMMUNISM",
        "video_url": "https://www.handspeak.com//word/c/com/communist.mp4",
    },
    {
        "id": "TOTALITARIAN",
        "video_url": "https://www.handspeak.com//word/t/tot/totalitarian.mp4",
    },
    {
        "id": "TWITTER",
        "video_url": "https://www.handspeak.com//word/t/twi/twitter-bird.mp4",
    },
    {
        "id": "COMMUNITY",
        "video_url": "https://www.handspeak.com//word/c/com/community.mp4",
    },
    {
        "id": "COMPANY",
        "video_url": "https://www.handspeak.com//word/c/com/company-co.mp4",
    },
    {
        "id": "THROMBUS",
        "video_url": "https://www.handspeak.com//word/t/thr/thrombus.mp4",
    },
    {"id": "COMPETE", "video_url": "https://www.handspeak.com//word/c/com/compete.mp4"},
    {
        "id": "COMPLAIN",
        "video_url": "https://www.handspeak.com//word/c/com/complain.mp4",
    },
    {
        "id": "VERITABLE",
        "video_url": "https://www.handspeak.com//word/v/ver/veritable.mp4",
    },
    {
        "id": "COMPLETE",
        "video_url": "https://www.handspeak.com//word/c/com/complete-done.mp4",
    },
    {"id": "COMPLEX", "video_url": "https://www.handspeak.com//word/c/com/complex.mp4"},
    {
        "id": "COMPLICATED",
        "video_url": "https://www.handspeak.com//word/c/com/complicate-isl.mp4",
    },
    {
        "id": "DESIGN",
        "video_url": " https://www.handspeak.com//word/c/com/composition-art.mp4",
    },
    {
        "id": "COMPUTER",
        "video_url": "https://www.handspeak.com//word/c/com/computer-arm.mp4",
    },
    {
        "id": "SCIENCE",
        "video_url": "https://www.handspeak.com//word/c/com/computer-science.mp4",
    },
    {
        "id": "SYSTEMS",
        "video_url": "https://www.handspeak.com//word/c/com/computer-info-systems.mp4",
    },
    {
        "id": "ENGINEERING",
        "video_url": "https://www.handspeak.com//word/e/eng/engineering.mp4",
    },
    {
        "id": "CONCEITED",
        "video_url": "https://www.handspeak.com//word/c/conc/conceited.mp4",
    },
    {
        "id": "ARROGANT",
        "video_url": "https://www.handspeak.com//word/a/arr/arrogant.mp4",
    },
    {
        "id": "CONCEPT",
        "video_url": "https://www.handspeak.com//word/c/conc/concept.mp4",
    },
    {
        "id": "CONCERN",
        "video_url": "https://www.handspeak.com//word/c/conc/concern.mp4",
    },
    {
        "id": "CONDITION",
        "video_url": "https://www.handspeak.com//word/c/cond/conditions.mp4",
    },
    {"id": "CONDOM", "video_url": "https://www.handspeak.com//word/c/cond/condom2.mp4"},
    {
        "id": "CONFESS",
        "video_url": "https://www.handspeak.com//word/c/conf/confess.mp4",
    },
    {
        "id": "CONFIDENCE",
        "video_url": "https://www.handspeak.com//word/c/conf/confident.mp4",
    },
    {
        "id": "CONFIDENTIAL",
        "video_url": "https://www.handspeak.com//word/c/conf/confidential.mp4",
    },
    {
        "id": "CONFLICT",
        "video_url": "https://www.handspeak.com//word/c/conf/conflict.mp4",
    },
    {
        "id": "CONFUSED",
        "video_url": "https://www.handspeak.com//word/c/conf/confused.mp4",
    },
    {
        "id": "CONGRATULATION",
        "video_url": "https://www.handspeak.com//word/c/cong/congratulation.mp4",
    },
    {
        "id": "CONGRESS",
        "video_url": "https://www.handspeak.com//word/c/cong/congress-wfd.mp4",
    },
    {"id": "CONNECT", "video_url": "https://www.handspeak.com//word/c/connect.mp4"},
    {
        "id": "CONSCIOUS",
        "video_url": "https://www.handspeak.com//word/c/cons/conscious.mp4",
    },
    {
        "id": "CONSIDER",
        "video_url": "https://www.handspeak.com//word/c/cons/consider.mp4",
    },
    {
        "id": "CONSTITUTION",
        "video_url": "https://www.handspeak.com//word/c/cons/constitution.mp4",
    },
    {
        "id": "CONSTRUCTION",
        "video_url": "https://www.handspeak.com//word/c/cons/construct.mp4",
    },
    {
        "id": "CONTINENT",
        "video_url": "https://www.handspeak.com//word/c/cont/continents.mp4",
    },
    {
        "id": "CONTINUE",
        "video_url": "https://www.handspeak.com//word/c/cont/continue.mp4",
    },
    {
        "id": "CONTRACT",
        "video_url": "https://www.handspeak.com//word/c/cont/contract-paper.mp4",
    },
    {
        "id": "CONTROL",
        "video_url": "https://www.handspeak.com//word/c/cont/control.mp4",
    },
    {"id": "COOK", "video_url": "https://www.handspeak.com//word/c/coo/cook.mp4"},
    {"id": "COOKIE", "video_url": "https://www.handspeak.com//word/c/coo/cookie.mp4"},
    {"id": "OUT", "video_url": "https://www.handspeak.com//word/c/coo/cool-off.mp4"},
    {"id": "COOL", "video_url": "https://www.handspeak.com//word/c/coo/cool-neat.mp4"},
    {
        "id": "COOPERATE",
        "video_url": "https://www.handspeak.com//word/c/coo/cooperate-cir.mp4",
    },
    {
        "id": "COOPERATIVE",
        "video_url": "https://www.handspeak.com//word/c/coo/cooperative.mp4",
    },
    {
        "id": "COORDINATE",
        "video_url": "https://www.handspeak.com//word/c/coo/coordinate.mp4",
    },
    {
        "id": "COPYEDITING",
        "video_url": "https://www.handspeak.com//word/c/cop/copyediting.mp4",
    },
    {
        "id": "COPYCAT",
        "video_url": "https://www.handspeak.com//word/c/cop/copy-imitate.mp4",
    },
    {
        "id": "PHOTOCOPY",
        "video_url": "https://www.handspeak.com//word/p/pho/photocopy.mp4",
    },
    {
        "id": "COPYWRITING",
        "video_url": "https://www.handspeak.com//word/c/cop/copywriting.mp4",
    },
    {
        "id": "COPYRIGHT",
        "video_url": "https://www.handspeak.com//word/c/cop/copyright.mp4",
    },
    {
        "id": "COMPOSE",
        "video_url": "https://www.handspeak.com//word/c/com/compose-write.mp4",
    },
    {"id": "COUGH", "video_url": "https://www.handspeak.com//word/c/cou/cough.mp4"},
    {
        "id": "SYRUP",
        "video_url": "https://www.handspeak.com//word/c/cou/cough-syrup.mp4",
    },
    {"id": "COUNT", "video_url": "https://www.handspeak.com//word/c/cou/count.mp4"},
    {"id": "COUNTRY", "video_url": "https://www.handspeak.com//word/c/cou/country.mp4"},
    {"id": "WITH", "video_url": "https://www.handspeak.com//word/p/put/putup-with.mp4"},
    {"id": "COURAGE", "video_url": "https://www.handspeak.com//word/c/cou/courage.mp4"},
    {
        "id": "COURSE",
        "video_url": "https://www.handspeak.com//word/c/cou/course-class.mp4",
    },
    {"id": "COURT", "video_url": "https://www.handspeak.com//word/c/cou/court-law.mp4"},
    {"id": "COUSIN", "video_url": "https://www.handspeak.com//word/c/cou/cousin.mp4"},
    {
        "id": "RACISM",
        "video_url": "https://www.handspeak.com//word/r/rac/racism-fs.mp4",
    },
    {"id": "COVER", "video_url": "https://www.handspeak.com//word/c/cov/cover.mp4"},
    {
        "id": "BOOKCOVER",
        "video_url": "https://www.handspeak.com//word/b/boo/bookcover.mp4",
    },
    {"id": "CATTLE", "video_url": "https://www.handspeak.com//word/c/cat/cattle.mp4"},
]

if __name__ == "__main__":
    if execute_parallel:
        with Pool() as p:
            p.map(transcribe_word, words)
            # This seems to introduce a memory leak, still not a problem on my
            # machine but can be a problem for others. I recommend using parallel
            # execution only if your system has 32GB of RAM or more.
    else:
        for word in words:
            print(word)
            transcribe_word(word)
