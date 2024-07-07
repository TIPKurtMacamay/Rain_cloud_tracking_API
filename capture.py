import cv2
import os
import numpy as np
import time

pattern_size = (8,6)
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
 
# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((8*6,3), np.float32)
objp[:,:2] = np.mgrid[0:6,0:8].T.reshape(-1,2)
 
# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.  
 
def capture_image_with_increment(resolution=(640, 480), camera_index=0, key_to_capture=32, output_directory='captured_images'):
    # Open the webcam
    cap = cv2.VideoCapture(camera_index)

    # Set the desired resolution
    cap.set(3, resolution[0])  # Width
    cap.set(4, resolution[1])  # Height

    # Check if the webcam is opened successfully
    if not cap.isOpened():
        print("Error: Unable to open the webcam.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    count = 1  # Initialize image count

    try:
        while True:
            # Capture a frame
            ret, frame = cap.read()

            if not ret:
                print("Error: Unable to capture frame.")
                break

            # Display the captured frame
            cv2.imshow('Captured Frame', frame)
            
            image_filename = os.path.join(output_directory, f"captured_image_{count}.jpg")
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            equ = cv2.equalizeHist(gray)
            # Apply adaptive thresholding
            _, thresh = cv2.threshold(equ, 127, 255, cv2.THRESH_BINARY)
            ret2, corners = cv2.findChessboardCorners(thresh, pattern_size, cv2.CALIB_CB_ADAPTIVE_THRESH)
         
            # If found, add object points, image points (after refining them)
            if ret2 == True:
                objpoints.append(objp)
         
                corners2 = cv2.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
                imgpoints.append(corners2)
         
                # Draw and display the corners
                cv2.drawChessboardCorners(gray, pattern_size, corners2, ret)
                cv2.imshow('Success', gray)
                cv2.imwrite(image_filename, frame)
            
                print(f"Image captured and saved to {image_filename}.")
                # Increment the count for the next image
                count += 1

            # Wait for 100 milliseconds (0.1 seconds)
            time.sleep(0.1)

            # Check for the 'q' key to exit the loop
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Release the VideoCapture object
        cap.release()
        cv2.destroyAllWindows()


# Specify the resolution, camera index, key to capture, and output directory
desired_resolution = (640, 480)
webcam_index = 1
capture_key = ord(' ')  # Capture when spacebar is pressed
output_folder = 'captured_images'

# Call the function to capture the image with incrementing filenames
capture_image_with_increment(resolution=desired_resolution, camera_index=webcam_index, key_to_capture=capture_key, output_directory=output_folder)
