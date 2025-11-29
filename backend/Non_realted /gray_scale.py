import cv2 as cv
import numpy as np




img = cv.imread("/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/opencv-course/Resources/Photos/cat.jpg")

height , width, channels = img.shape

print(width ,"x",height )



if img is None:
    print("Error: Unable to load image")
else:
    if len(img.shape) == 3: 
        img_gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    elif len(img.shape) == 2:  
        img_gray = img

    else:
        print("Error: Unsupported image format")

cv.imshow("windo",img_gray)
img [:,:,1]
cv.imshow("windo2",img_gray)
cv.imshow("wind",img)

cv.waitKey(0)
