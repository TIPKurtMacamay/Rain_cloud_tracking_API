import cv2
import numpy as np
import glob

# Checkboard dimensions
CHECKERBOARD = (8,6)

subpix_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
calibration_flags = cv2.fisheye.CALIB_RECOMPUTE_EXTRINSIC + cv2.fisheye.CALIB_CHECK_COND + cv2.fisheye.CALIB_FIX_SKEW

objp = np.zeros((1, CHECKERBOARD[0]*CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

images = glob.glob('Rain Cloud True Cam 2/*.jpg')
count = 0
for fname in images:
    img = cv2.imread(fname)
    img_shape = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    equ = cv2.equalizeHist(gray)
    # Apply adaptive thresholding
    _, thresh = cv2.threshold(equ, 127, 255, cv2.THRESH_BINARY)
    
    # Find the chess board corners
    ret, corners = cv2.findChessboardCorners(thresh, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
    # If found, add object points, image points (after refining them)
    print(fname,ret)
    if ret == True:
        count+=1
        objpoints.append(objp)
        cv2.cornerSubPix(gray,corners,(3,3),(-1,-1),subpix_criteria)
        imgpoints.append(corners)

###
# Calibrate the camera
ret, K, D, rvecs, tvecs = cv2.fisheye.calibrate(objpoints, imgpoints, gray.shape[::-1], None, None)

# Undistort an example image
example_image = cv2.imread('Rain Cloud True Cam 2/captured_image_22.jpg')
undistorted_image = cv2.fisheye.undistortImage(example_image, K, D, Knew=K)

# Display the original and undistorted images
cv2.imshow('Original Image', example_image)
cv2.imshow('Undistorted Image', undistorted_image)

# Compute mean reprojection error
mean_error = 0
for i in range(len(objpoints)):
    imgpoints2, _ = cv2.fisheye.projectPoints(objpoints[i].reshape(-1, 1, 3), rvecs[i], tvecs[i], K, D)
    error = cv2.norm(imgpoints[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
    mean_error += error

mean_error /= len(objpoints)

print(f'Mean Reprojection Error: {mean_error}')



