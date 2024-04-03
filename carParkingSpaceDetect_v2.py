import os
import csv
import cv2
import numpy as np
import matplotlib.pyplot as plt
from pubnub_publisher import publish_to_pubnub

x1_list, x2_list, y1_list, y2_list = [], [], [], []
csv_file_path = 'allXY.csv'

with open(csv_file_path, 'r') as file:
    csv_reader = csv.DictReader(file)
    for row in csv_reader:
        x1_list.append(float(row['x1']))  # assuming x1 is a numeric column
        x2_list.append(float(row['x2']))
        y1_list.append(float(row['y1']))
        y2_list.append(float(row['y2']))

print("x1_list:", x1_list)
print("x2_list:", x2_list)
print("y1_list:", y1_list)
print("y2_list:", y2_list)



image = cv2.imread("test.jpg")
lane_image = np.copy(image)
#cv2.imshow("h",image)
# plt.figure(figsize=(18,18))
# plt.imshow(image)
# plt.axis('off')
# plt.show()
idList = []
parkList = []

# gray = cv2.cvtColor(lane_image, cv2.COLOR_RGB2GRAY)
gray = cv2.cvtColor(lane_image, cv2.COLOR_BGR2GRAY)
blur = cv2.GaussianBlur(gray,(3,3), 1)
# blur = cv2.GaussianBlur(gray,(5,5), 0)
lane_image = cv2.Canny(blur, 50, 150)

region_within_rect_top_row = []
for i in range(len(x1_list)): #y1:y1, x1:x2
  region_within_rect_top_row.append(lane_image[round(y1_list[i]):round(y2_list[i]), round(x1_list[i]):round(x2_list[i])])

# region_within_rect_bottom_row = []
# for i in range(len(coordinates_top_row_width)):
#   region_within_rect_bottom_row.append(lane_image[coordinates_bottom_row[0]:coordinates_bottom_row[1], coordinates_top_row_width[i]:coordinates_top_row_height[i]])
A = 'A'
B = 'B'

white_pixel_count = []
for i in range(len(region_within_rect_top_row)):
  white_pixel_count.append(np.count_nonzero(region_within_rect_top_row[i]))
  # print("rectangle A", [i] , white_pixel_count[i])
  if white_pixel_count[i] < 50: #let test with 10, 50, 150 default is 50
    if i >=104:
      cv2.rectangle(image, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (0,255,0), thickness = 2)
      cv2.putText(image, 'B'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
      print("rectangle B", [i] , "is free" , "(", white_pixel_count[i], ")")
      idList.append('B'+str(i))
      parkList.append(True)
    else:
      cv2.rectangle(image, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (0,255,0), thickness = 2)
      cv2.putText(image, 'A'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
      print("rectangle A", [i] , "is free" , "(", white_pixel_count[i], ")")
      idList.append('A'+str(i))
      parkList.append(True)
  else:
    if i >=104:
      cv2.rectangle(image, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (255,0,0), thickness = 2)
      cv2.putText(image, 'B'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
      print("rectangle B", [i] , "is taken" , "(", white_pixel_count[i], ")")
      idList.append('B'+str(i))
      parkList.append(False)
    else:
      cv2.rectangle(image, (round(x1_list[i]), round(y1_list[i])), (round(x2_list[i]), round(y2_list[i])), (255,0,0), thickness = 2)
      cv2.putText(image, 'A'+str(i), (round(x1_list[i]), round(y1_list[i]-5)), cv2.FONT_HERSHEY_COMPLEX,0.3, (0,0,255), 1)
      print("rectangle A", [i] , "is taken" , "(", white_pixel_count[i], ")")
      idList.append('A'+str(i))
      parkList.append(False)

plt.figure(figsize=(18,18))
plt.imshow(image)
plt.axis('off')
plt.show()
#cv2.imshow("test",image)
#cv2_imshow(region_within_rect[2])

for i in range(0, len(idList)):
     print(idList[i] + ' , ' + str(parkList[i]))

channel_name = os.getenv('PN_CHANNEL')
publish_to_pubnub(idList, parkList, channel_name)
