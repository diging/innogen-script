"""
This script uses the algorithm described in the following post to extract images from 
scanned documents.
https://answers.opencv.org/question/75482/detect-images-in-an-image-of-a-text-document/
"""

import cv2 as cv
import os
from argparse import ArgumentParser
from pathlib import Path

def read_file(filename, folder):
    print("[INFO] Reading image " + filename)
    if not os.path.exists(folder):
        os.mkdir(folder)
    return cv.imread(filename)

# convert image to grey
def to_greyscale(img, folder):
    print("[INFO] Converting image to greyscale.")
    grey_image = cv.cvtColor(img, cv.COLOR_BGR2GRAY )
    cv.imwrite(folder + "/01-greyscale.jpg", grey_image)
    return grey_image

# dilate and write into grey_image
def dilate_image(greyed_img, folder):
    print("[INFO] Dilating image.")
    kernel = cv.getStructuringElement(cv.MORPH_RECT,(15,15))
    cv.dilate(greyed_img, kernel, greyed_img)
    cv.imwrite(folder + "/02-dilated.jpg", greyed_img)
    return greyed_img

# change white to black and invert
def to_black_white(dilated_img, folder):
    print("[INFO] Converting image to black and white.")
    ret1,dst = cv.threshold(dilated_img, 240, 255, cv.THRESH_TOZERO)
    ret1,dst = cv.threshold(dst, 240, 255, cv.THRESH_BINARY_INV)
    cv.imwrite(folder + "/03-inverted.jpg", dst)
    return dst

#try to fill images rectangles and remove noise
def morph_image(bw_img, folder):
    print("[INFO] Morphing image.")
    kernel = cv.getStructuringElement(cv.MORPH_RECT,(20,20))
    gradient = cv.morphologyEx(bw_img, cv.MORPH_CLOSE, kernel)
    grad_img = cv.morphologyEx(gradient, cv.MORPH_OPEN, kernel)
    cv.imwrite(folder + "/04-morphed.jpg", grad_img)
    return grad_img

# find contours and extract images
def find_and_draw_contours(img_with_cont, original_img, filename, result_folder):
    print("[INFO] Extracting image regions.")
    contours, hierachy = cv.findContours(img_with_cont, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    Path(result_folder).mkdir(parents=True, exist_ok=True)
    # draw contours with rectangle
    img_counter = 0
    for j in range(len(contours)):
        area = cv.contourArea(contours[j])
        if area > 5000:
            print("[INFO] Extracting image with size: " + str(area))
            x,y,w,h = cv.boundingRect(contours[j])
            cropped = original_img[y:y+h, x:x+w]
            cv.imwrite(result_folder + "/" + filename + "-" + "{:03d}".format(img_counter) + ".jpg", cropped)
            img_counter += 1
            cv.rectangle(img_with_cont, (x, y), (x + w, y + h), (161,155,86), 5)
        else:
            print("[INFO] Image region too small, skipping (" + str(area) + ")")
    cv.imwrite(folder + "/05-img_with_cont.jpg", img_with_cont)

# find contours and extract images with approxPolyDP
def find_and_draw_contours_poly(img_with_cont, original_img, filename, result_folder):
    contours, hierachy = cv.findContours(img_with_cont, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    Path(result_folder).mkdir(parents=True, exist_ok=True)
    # draw contours with poly
    for j in range(len(contours)):
        cnt = contours[j]
        area = cv.contourArea(cnt)
        if area > 5000:
            epsilon = 0.15*cv.arcLength(cnt,True)
            approx = cv.approxPolyDP(cnt,epsilon,True)
            x,y,w,h = cv.boundingRect(approx)
            cropped = original_img[y:y+h, x:x+w]
            cv.imwrite(result_folder + "/" + filename + "-" + "{:03d}".format(j) + ".jpg", cropped)
            
            img_with_cont = cv.drawContours(img_with_cont, [approx],0, [161,155,86], thickness=5)
    cv.imwrite(folder + "/06-img_with_approx.jpg", img_with_cont)


parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="Image file to process.")
parser.add_argument("-o", "--output", dest="output_folder",
                    help="Folder to store created files in")
args = parser.parse_args()
folder = args.output_folder
filename = args.filename

image = read_file(filename, folder)
greyed = to_greyscale(image, folder)
dilated = dilate_image(greyed, folder)
black_white = to_black_white(dilated, folder)
morphed_image = morph_image(black_white, folder)

path_parts = filename.split("/")
no_extension = os.path.splitext(path_parts[len(path_parts)-1])

find_and_draw_contours(morphed_image, image, no_extension[0], folder + "/extracted")