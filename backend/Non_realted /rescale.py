import cv2 as cv

img = cv.imread("/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/opencv-course/Resources/Photos/cat_large.jpg")

cv.imshow("large",img)

def rescaleframe(frame,scale = 0.75):
    width = int(frame.shape[1]*scale)

    height = int(frame.shape[0]*scale)

    dimensions =(width,height)

    return cv.resize(frame,dimensions,interpolation=cv.INTER_AREA)

resized_img = rescaleframe(img,scale=.2)
cv.imshow("img",resized_img)
# cv.imshow("cat",resized_img)
# def change_res(width,height):
#     capture.set(3,width)
#     capture.set(4,height)

# capture = cv.VideoCapture("/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/opencv-course/Resources/Videos/dog.mp4")

# while True:
#     isTrue,frame = capture.read()

#     frame_resized =rescaleframe(frame,scale=.2)

#     cv.imshow("video",frame)

#     cv.imshow('video_resized',frame_resized)

#     if cv.waitKey(20) & 0xFF == ('d'):
#         break

# capture.release()
cv.waitKey(0)
cv.destroyAllWindows()


