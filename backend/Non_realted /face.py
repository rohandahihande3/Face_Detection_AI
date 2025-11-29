import cv2 as cv 

def draw_boundary(img,classfier,scaleFactor,minNeighbour,color,text):
    gray_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    
    featuers = classfier.detectMultiScale(gray_img,scaleFactor,minNeighbour)
    coords = []
    for (x,y,w,h) in featuers:
        cv.rectangle(img,(x,y),(x+w,y+h),color,2)
        cv.putText(img,text,(x,y-4),cv.FONT_HERSHEY_SIMPLEX,0.8,color,1,cv.LINE_AA)
        coords = [x,y,w,h]
    return coords

def detect (img,facecascade,eyecascade,nosecascade,mouthcascade):
    color = {"blue":(255,0,0),"red":(0,0,255),"green":(0,255,0)}
    coords = draw_boundary(img,facecascade,1.1,10,color["blue"],"Face")
    
    if len(coords)==4:
       roi_img = img [coords[2]:coords[1]+coords[3],coords[0]:coords[0]+coords[1]]
       coords = draw_boundary(roi_img,eyecascade,1.1,14,color["green"],"Eyes")
       coords = draw_boundary(roi_img,nosecascade,1.1,5,color["red"],"Nose")
       coords = draw_boundary(roi_img,mouthcascade,1.1,20,(255,255,255),"Mouth")

    return img



face = cv.CascadeClassifier("frontal_facelt.xml")
nose = cv.CascadeClassifier("nose.xml")
eye = cv.CascadeClassifier("eye.xml")
mouth = cv .CascadeClassifier("mouth.xml")

capture = cv.VideoCapture(0)
# v = cv.imread("/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/IMG20221116125229.jpg")
# img = detect(v,face,nose,mouth,eye)
# cv.imshow("vins",v)
# cv.waitKey(0)



while True:
    isTrue, img = capture.read()

    img = detect(img,face,eye,nose,mouth)
  
    if not isTrue:
        break
    
    cv.imshow('Video', img)
    
    if cv.waitKey(20) & 0xFF == ord("d"):
        break


capture.release()

cv.destroyAllWindows()

