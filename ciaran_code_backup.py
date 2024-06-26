import pymongo
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pytube import YouTube
from pubnub_publisher import publish_to_pubnub
import os
import time

MONGODB_URI = "mongodb+srv://jeremysoh222:kk6dGaMao5h7CoLW@cluster0.ke2biwp.mongodb.net/SmartParking"
client = pymongo.MongoClient(MONGODB_URI)
db = client.get_database()
collection = db["users"]

youtube_url = "https://youtu.be/6LQ8mvxLPMI?si=CdzfcgDRZmLE5ZqZ"

last_publish_time = time.time()

def main():
    try:
        yt = YouTube(youtube_url)
        stream = yt.streams.get_by_itag(18)  # You can adjust the itag based on your preference
        if stream is None:
            raise ValueError("Unable to retrieve the best stream.")
    except Exception as e:
        print("Error retrieving video information:", e)
        return

    # OpenCV video capture
    cap = cv2.VideoCapture(stream.url)
    
    if not cap.isOpened():
        print("Error: Could not open video stream")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Resize frame
        frame = cv2.resize(frame, (1280, 720))

        # Create a copy of the frame
        lane_image = np.copy(frame)

        # Call your processing function
        process(frame, lane_image)

        # Display the processed frame
        cv2.imshow("Combo image", frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

def process(frame, lane_image):
    global last_insert_time
    state = "free"
    idList = []
    parkList = []
    stateList = []

    gray = cv2.cvtColor(lane_image, cv2.COLOR_RGB2GRAY)
    blur = cv2.GaussianBlur(gray,(3,3), 1)
    lane_image = cv2.Canny(blur, 50, 100)

    x1_list = [360,500,770,920]
    x2_list = [475,615,885,1035]
    y1_list = [620,620,620,620]
    y2_list = [700,700,700,700]
    
    region_within_rect = []
    for i in range(len(x1_list)): #y1:y1, x1:x2
        region_within_rect.append(lane_image[round(y1_list[i]):round(y2_list[i]), round(x1_list[i]):round(x2_list[i])])

        # region_within_rect = (lane_image[600:800, 200:600])



    white_pixel_count = []
    for i in range(len(region_within_rect)):
        white_pixel_count.append(np.count_nonzero(region_within_rect[i]))
        if white_pixel_count[i] < 1149:
            cv2.rectangle(frame, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (0,255,0), thickness = 2)
            cv2.putText(frame, 'B'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
            state = "free"
            if state == "free":
                document = {
                    "A1": "free",
                }

                collection.insert_one(document)
                print("rectangle A", [i] , "is free" , "(", white_pixel_count[i], ")")
                result = collection.find_one({"A1": "free"})
            
            idList.append('B'+str(i+221))
            parkList.append(True)
            stateList.append("free")
        
        else:
            cv2.rectangle(frame, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (0,255,0), thickness = 2)
            cv2.putText(frame, 'A'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
            state = "taken"
            if state != "free":
                document = {
                    "A1": "taken",
                }
                collection.insert_one(document)
                print("rectangle A", [i] , "is taken" , "(", white_pixel_count[i], ")")
                result = collection.find_one({"A1": "taken"})
            
            idList.append('B'+str(i+221))
            parkList.append(False)
            stateList.append("taken")

    cv2.imshow("i", frame)
    cv2.waitKey(1) & 0xFF == ord('q')

    # for i in range(0, len(idList)):
    #     print(idList[i] + ' , ' + str(parkList[i]))

    channel_name = os.getenv('PN_CHANNEL')
    publish_to_pubnub(idList, parkList, channel_name, last_publish_time)


if __name__ == "__main__":
    main()