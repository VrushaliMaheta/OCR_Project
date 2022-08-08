# import packages
from keras.applications import VGG16
from keras.applications import imagenet_utils
from tensorflow.keras.utils import img_to_array
from tensorflow.keras.utils import load_img
from imutils import paths
import numpy as np
import argparse
import pickle
import imutils
import h5py
import cv2
from matplotlib import pyplot as plt
import math
from PIL import Image,ImageEnhance

# construct the argument parser
def check_angle(path):
    db = h5py.File("ad6.hdf5","r")
    labelNames = [int(angle) for angle in db["label_names"][:]]
    db.close()

    imagePath = path
    print("[INFO] loading network...")
    vgg = VGG16(weights="imagenet", include_top=False)

    print("[INFO] loading model...")
    model = pickle.loads(open("ad6.h5", "rb").read())

    orig = cv2.imread(imagePath)

    image = load_img(imagePath, target_size=(224, 224))
    image = img_to_array(image)

    image = np.expand_dims(image, axis=0)
    image = imagenet_utils.preprocess_input(image)

    features = vgg.predict(image)
    features = features.reshape((features.shape[0], 512 * 7 * 7))

    angle = model.predict(features)
    angle = -(labelNames[angle[0]])

    #increase brightness
    img2 = Image.fromarray(orig)
    enhancer = ImageEnhance.Brightness(img2)

    factor = 1.5  # gives original image
    im_output = enhancer.enhance(factor)
    eimage = np.asarray(im_output)
    r, g, b = cv2.split(eimage)
    eimage = cv2.merge([b, g, r])

    #sharp the image
    k = np.array([[0, -1, 0],
                  [-1, 5, -1],
                  [0, -1, 0]])
    image_sharp = cv2.filter2D(src=eimage, ddepth=-1, kernel=k)
    # correct the image based on the predictions
    rotated = imutils.rotate_bound(image_sharp, angle)

    cv2.imwrite("./static/images/rotate_img.jpg", rotated)
    print("angle : ", angle)

    return rotated

#check_angle("Images/monika_aadhar.jpg")