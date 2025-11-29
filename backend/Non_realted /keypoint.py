import cv2
import numpy as np

# Load the image
image_path = '/home/rohan/Rohan_WorksSpace/OPENCV/opencv_git/opencv-course/Resources/Faces/train/Ben Afflek/2.jpg'
image = cv2.imread(image_path)

# Convert the image to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Initialize a keypoint detector (e.g., ORB, SIFT, SURF)
detector = cv2.ORB_create()

# Detect keypoints
keypoints = detector.detect(gray, None)

# Get the bounding box of all keypoints
if keypoints:
    # Get the coordinates of the keypoints
    kp_pts = np.float32([kp.pt for kp in keypoints]).reshape(-1, 1, 2)
    
    # Find the minimum and maximum x and y coordinates
    min_x, min_y = np.min(kp_pts, axis=0).squeeze()
    max_x, max_y = np.max(kp_pts, axis=0).squeeze()
    
    # Draw a single rectangle around the bounding box
    cv2.rectangle(image, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 255, 0), 2)

# Display the image with the single rectangle
cv2.imshow('Image with Single Rectangle', image)
cv2.waitKey(0)
cv2.destroyAllWindows()
