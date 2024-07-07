#https://medium.com/@itberrios6/introduction-to-motion-detection-part-1-e031b0bb9bb2

import cv2
import numpy as np
from patchify import patchify, unpatchify
import matplotlib.pyplot as plt

def plot_histogram(image, title):
    hist, bins = np.histogram(image, bins=256, range=[-1, 1])
    
    # Plot histogram using Matplotlib
    plt.figure()
    plt.title(title)
    plt.xlabel('Intensity Value')
    plt.ylabel('Pixel Count')
    plt.plot(bins[:-1], hist)  # bins[:-1] to match the number of hist values
    plt.xlim([-1, 1])
    plt.show()


def mce_thresholding(x):
    mce_tresh = 0.25
    binary_mask = np.where(x < mce_tresh, 1.0, 0.0)
    return binary_mask


def fixed_thresholding(x):
  unimodal_tresh = 0.250
  binary_mask = np.where(x < unimodal_tresh, 1.0, 0.0)
  return binary_mask


def hyta_segmentation(image):
    STD_THRESHOLD = 0.03

    b, g, r = cv2.split(image)
    r[r==0] = 1
    x = b/r
    n = (x-1)/(x+1)

    std = np.std(x)
    if std>STD_THRESHOLD:
        print("Bimodal",std)
        return(mce_thresholding(n))
    else:
        print("Unimodal",std)
        return(fixed_thresholding(n))



if __name__ == "__main__":
    # # Path to the video file
    video_path = 'timelapse/4899355-uhd_3840_2160_30fps.mp4'

    # Define the new dimensions for resizing
    new_width = 640
    new_height = 480

    # Create a VideoCapture object
    cap = cv2.VideoCapture(video_path)

    # Check if the video file was opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        exit()

    # Read the first frame
    ret, prev_frame = cap.read()

    
    if not ret:
        print("Error reading first frame")
        exit()

    # Read until video is completed
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        if ret:
            # Display the current frame
            resized = cv2.resize(frame, (new_width, new_height))
            cloud = hyta_segmentation(resized)

            cv2.imshow("Raw",resized)
            cv2.imshow('HYTA',cloud)

            # Press Q on keyboard to exit
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break
        else:
            break

    # Release the video capture object
    cap.release()

    # Close all OpenCV windows
    cv2.destroyAllWindows()