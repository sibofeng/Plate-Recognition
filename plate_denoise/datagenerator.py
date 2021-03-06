# encoding=utf-8
import numpy as np
import cv2
import os
import data_process.read_xml as rx
import tensorflow as tf


class ImageDataGenerator:
    def __init__(self, class_list, replace, scale_size, horizontal_flip=False, shuffle=False,
                 mean=np.array([127.5, 127.5, 127.5]), num_digit=8,
                 num_classes=2):  # mean=np.array([127.5]),np.array(,,)

        # Init params
        self.horizontal_flip = horizontal_flip
        self.n_digit = num_digit
        self.n_classes = num_classes
        self.shuffle = shuffle
        self.mean = mean
        self.scale_size = scale_size
        self.pointer = 0
        self.replace = replace
        self.read_class_list(class_list)

        if self.shuffle:
            self.shuffle_data()

    def read_class_list(self, class_list):
        """
        Scan the image file and get the image paths and labels
        """
        with open(class_list) as f:
            lines = f.readlines()
            self.images = []
            self.labels = []
            for l in lines:
                items = l.split()
                self.images.append(items[0])
                self.labels.append(items[0].replace(self.replace[0], self.replace[1]))

            # store total number of data
            self.data_size = len(self.labels)

    def shuffle_data(self):

        images = self.images
        labels = self.labels
        self.images = []
        self.labels = []

        # create list of permutated index and shuffle data accoding to list
        idx = np.random.permutation(len(labels))
        for i in idx:
            self.images.append(images[i])
            self.labels.append(labels[i])

    def reset_pointer(self):
        """
        reset pointer to begin of the list
        """
        self.pointer = 0

        if self.shuffle:
            self.shuffle_data()

    def next_batch(self, batch_size):
        """
        This function gets the next n ( = batch_size) images from the path list
        and labels and loads the images into them into memory
        """
        # Get next batch of image (path) and labels
        paths = self.images[self.pointer:self.pointer + batch_size]
        labels = self.labels[self.pointer:self.pointer + batch_size]

        # update pointer
        self.pointer += batch_size

        # Read images
        images = np.ndarray([batch_size, self.scale_size[0], self.scale_size[1], 3])
        source_images = np.ndarray([batch_size, self.scale_size[0], self.scale_size[1], 3])
        for i in range(len(paths)):
            img = cv2.imread(paths[i])
            img_resource = cv2.imread(labels[i])

            # rescale image
            try:
                img = cv2.resize(img, (self.scale_size[1], self.scale_size[0]))
                img_resource = cv2.resize(img_resource, (self.scale_size[1], self.scale_size[0]))
            except:
                print(paths[i])
            img = img.astype(np.float32)
            img_resource = img_resource.astype(np.float32)

            # subtract mean
            img -= self.mean
            img_resource -= self.mean

            images[i] = img
            source_images[i] = img_resource

        # return array of images and labels
        return images, source_images

# read_x = rx.read_xml(batch_size=32, num_digit=8, num_classes=82)
# label_dict, _ = read_x.read_file('./data_process/label_name.xml')
# print(label_dict)
# train = ImageDataGenerator('./path/train.txt', scale_size=(30, 100), num_digit=8, num_classes=82)
# x, y = train.next_batch(32)
# print(x.shape)
# str = 'E:\workspace\github\plate_dataset\plate'
# str2 = str.replace('plate', 'new')
# print(str, str2)
