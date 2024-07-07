import cv2
from patchify import patchify
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm

from tqdm import tqdm

import numpy as np
from keras.applications import InceptionV3
from keras.models import Model
from keras.layers import Dense, GlobalAveragePooling2D
from keras.optimizers import SGD

import cloud_segmentation



def create_model(weights_path):
    # Load pre-trained InceptionV3 model
    base_model = InceptionV3(weights='imagenet', include_top=False, input_shape=(125, 125, 3))

    # Add custom classification layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(1024, activation='relu')(x)
    predictions = Dense(5, activation='softmax')(x)

    model = Model(inputs=base_model.input, outputs=predictions)

    # Compile model
    model.compile(optimizer=SGD(learning_rate=0.0001, momentum=0.9), loss='categorical_crossentropy', metrics=['accuracy'])
    model.load_weights('model_weights.hdf5')

    model.summary()
    return model


def predict_image(model,image,mask):
    pred = []
    unique_colors = {
        '0':(153,204,51, 255),   # Low
        '1':(255,204,0, 255),   # Moderate
        '2':(204,51,0, 255),   # High
        '3':(255,204,0, 255), # Moderate
        '4':(153,204,51, 255)  # Low
    }

    patches = patchify(image, (125, 125, 3), step=25)
    width, height = patches.shape[1], patches.shape[0]
    img = Image.new("RGB", (width,height), color="white")

    # Prepare all patches for batch prediction
    all_patches = []
    for i in range(height):
        for j in range(width):
            single_image = np.array(patches[i, j, 0]) / 255.0
            all_patches.append(single_image)
    all_patches = np.array(all_patches)
    
    # Predict in batches
    batch_size = 32
    predictions = []
    for i in tqdm(range(0, len(all_patches), batch_size), desc="Inferencing Image"):
        batch = all_patches[i:i+batch_size]
        batch_predictions = model.predict(batch, verbose=0)
        predictions.extend(batch_predictions)
    
    predictions = np.array(predictions)
    predictions = np.argmax(predictions, axis=1)

    # Reshape predictions to match the image shape
    pred = predictions.reshape(height, width)

    for y in range(height):
      for x in range(width):
        img.putpixel((x,y),unique_colors[str(pred[y][x])])
    
    resized_np = np.array(img.resize((640, 480), resample=Image.LANCZOS))

    masked_image_np = np.zeros_like(resized_np)
    for i in range(3): 
        masked_image_np[:, :, i] = resized_np[:, :, i] * mask

    return cv2.cvtColor(masked_image_np, cv2.COLOR_RGB2BGR)
            

model = create_model("model_weights.hdf5")

if __name__ == "__main__":
    cap = cv2.VideoCapture('timelapse/4899355-uhd_3840_2160_30fps.mp4')

    count=0
    while True:
        ret, frame = cap.read()
        resized = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(cv2.resize(frame, (1280, 760)), cv2.COLOR_BGR2RGB)
        cv2.imshow('raw',resized)

        mask = cloud_segmentation.hyta_segmentation(resized)
        cv2.imshow('segmented',mask)

        segmented_cloud_type = predict_image(model, frame_rgb, mask)
        cv2.imshow('pred',segmented_cloud_type)
        # count += 1
        # print(f"output_clouds\cloud_{count}.png")
        # cv2.imwrite(f"output_clouds\cloud_{count}.png", segmented_cloud_type)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # count = 372
    # count2 = 0
    # while True:
    #     count2 += 1 
    #     img = cv2.imread(f"output_clouds\cloud_{count2}.png")
    #     cv2.imshow('Clouds',img)

    #     if count2 == count:
    #         count2 = 0
    #     if cv2.waitKey(25) & 0xFF == ord('q'):
    #         break
