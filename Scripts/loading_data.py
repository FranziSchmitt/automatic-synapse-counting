import numpy as np
import os

import cv2

def load_data(filepath):
    
    images = []
      
    for (dirpath, dirnames, filenames) in os.walk(filepath):
        for filename in filenames:
            if filename.endswith('tif'):
                imagepath = os.path.join(dirpath, filename)
                img = cv2.imread(imagepath)
                images.append(img)
            else:
                continue
    
    
    fileparts = filepath.split('/')
    textpath = os.path.join(filepath, '{}.txt'.format(fileparts[-2]))
    
    with open(textpath, 'r', encoding='UTF-8') as f:
        info = f.readlines()
    
    return images, info

def extract_voxel(info):
    voxel_size = 0
    voxel_depth = 0
    
    for line in info:
        if 'Voxel-Height' in line.split():
            voxel_size = float(line.split()[-1][:-1])

        if 'Voxel-Depth' in line.split():
            voxel_depth = float(line.split()[-1][:-1])
    
    return voxel_size, voxel_depth  

def crop_images(images, voxel_size, y_start=400, x_start=200):

    cropped_images = []
    pixel_number = 10/voxel_size
    print(pixel_number)
    y_stop = int(y_start + pixel_number)
    x_stop = int(x_start + pixel_number)

    for image in images:
        cropped_image = image[y_start:y_stop, x_start:x_stop]
        cropped_images.append(cropped_image)
    
    return cropped_images

if __name__ == '__main__':
    print(f'blub')

