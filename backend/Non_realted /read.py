import cv2
import numpy as np

# Initialize a video capture object
cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# Initialize a keypoint detector (e.g., ORB, SIFT, SURF)
detector = cv2.ORB_create()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
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
        cv2.rectangle(frame, (int(min_x), int(min_y)), (int(max_x), int(max_y)), (0, 255, 0), 2)

    # Display the frame with the single rectangle
    cv2.imshow('Frame with Single Rectangle', frame)
    
    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
