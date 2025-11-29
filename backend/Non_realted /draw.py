import cv2 as cv
import numpy as np
blank =np.zeros((500,500,3),dtype='uint8')

cv.imshow("Blank",blank)

#1.paint the image 

blank[:]=0,0,0

# cv.imshow('Green',blank)
#2.rectangle

# cv.rectangle(blank,(0,0),(blank.shape[1]//2,blank.shape[0]//2),(0,0,0),thickness=-1)

# cv.imshow("rectangle",blank)

# cv.circle(blank,(blank.shape[1]//2,blank.shape[0]//2),40,(0,0,255),thickness=-1)
# cv.imshow("circle",blank)

# cv.line(blank,(0,0),(blank.shape[1]//2,blank.shape[0]//2),(0,45,0),thickness=3)
# cv.imshow('line',blank)

cv.putText(blank,"Hello, my name is Rohan",(5,255),cv.FONT_HERSHEY_TRIPLEX,1.0,(0,255,0),2)

cv.imshow("text",blank)

cv.waitKey(0)