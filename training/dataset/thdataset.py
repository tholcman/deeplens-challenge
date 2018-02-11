from __future__ import print_function, absolute_import
import numpy as np
import os
import numpy as np
from .imdb import Imdb
import xml.etree.ElementTree as ET
from evaluate.eval_voc import voc_eval
import cv2


class ThDB(object):
    """
    Base class for dataset loading

    Parameters:
    ----------
    setName : str
        setName train|validation
    """
    def __init__(self, setName, data_path, shuffle):
        self.setName = setName
        self.data_path = data_path
        self.classes = ["barbell","phone","dog","ship","car","horse","glasses","mug","guitar","tree","duck","chair","zavora","train","snake","rat","trumpet","bicycle","cone","dolphin"]
        self.num_classes = 20
        self.image_set_index = self._load_image_set_index(shuffle)
        self.num_images = len(self.image_set_index) * 2
        self.labels = self._load_image_labels()
        print(self.image_set_index)
        print(self.labels)

    def image_path_from_index(self, index):
        """
        given image index, find out full path

        Parameters:
        ----------
        index: int
            index of a specific image
        Returns:
        ----------
        full path of this image
        """
        index = self._index(index)

        assert self.image_set_index is not None, "Dataset not initialized"
        name = self.image_set_index[index]
        image_file = os.path.join(self.data_path, 'Images', name + '.jpg')
        assert os.path.exists(image_file), 'Path does not exist: {}'.format(image_file)
        return image_file

    def label_from_index(self, index):
        """
        given image index, return preprocessed ground-truth

        Parameters:
        ----------
        index: int
            index of a specific image
        Returns:
        ----------
        ground-truths of this image
        """
        index = self._index(index)

        assert self.labels is not None, "Labels not processed"
        return self.labels[index]

    def save_imglist(self, fname=None, root=None, shuffle=False):
        """
        save imglist to disk

        Parameters:
        ----------
        fname : str
            saved filename
        """
        def progress_bar(count, total, suffix=''):
            import sys
            bar_len = 24
            filled_len = int(round(bar_len * count / float(total)))

            percents = round(100.0 * count / float(total), 1)
            bar = '=' * filled_len + '-' * (bar_len - filled_len)
            sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', suffix))
            sys.stdout.flush()

        str_list = []
        for index in range(self.num_images):
            progress_bar(index, self.num_images)
            label = self.label_from_index(index)
            if label.size < 1:
                continue
            path = self.image_path_from_index(index)
            if root:
                path = os.path.relpath(path, root)
            str_list.append('\t'.join([str(index), str(2), str(label.shape[1])] \
              + ["{0:.4f}".format(x) for x in label.ravel()] + [path,]) + '\n')
        if str_list:
            if shuffle:
                import random
                random.shuffle(str_list)
            if not fname:
                fname = self.name + '.lst'
            with open(fname, 'w') as f:
                for line in str_list:
                    f.write(line)
        else:
            raise RuntimeError("No image in imdb")

    def _index(self, index):
        originalCount = len(self.image_set_index)
        base = int(index / originalCount) * originalCount
        print('index: {index} base: {base}'.format(index = index, base = base))
        return index - base


    def _load_image_set_index(self, shuffle):
        """
        find out which indexes correspond to given image set (train or val)

        Returns:
        ----------
        entire list of images specified in the setting
        """
        image_set_index_file = os.path.join(self.data_path, self.setName + '.txt')
        assert os.path.exists(image_set_index_file), 'Path does not exist: {}'.format(image_set_index_file)
        with open(image_set_index_file) as f:
            image_set_index = [x.strip() for x in f.readlines()]
        if shuffle:
            np.random.shuffle(image_set_index)
        return image_set_index


    def _load_image_labels(self):
        """
        preprocess all ground-truths

        Returns:
        ----------
        labels packed in [num_images x max_num_objects x 5] tensor
        """
        temp = []

        # load ground-truth from xml annotations
        for idx in self.image_set_index:
            label_file = self._label_path_from_index(idx)
            tree = ET.parse(label_file)
            root = tree.getroot()
            size = root.find('size')
            width = float(size.find('width').text)
            height = float(size.find('height').text)
            label = []

            for obj in root.iter('object'):
                difficult = int(obj.find('difficult').text)
                # if not self.config['use_difficult'] and difficult == 1:
                #     continue
                cls_name = obj.find('name').text
                if cls_name not in self.classes:
                    cls_id = len(self.classes)
                else:
                    cls_id = self.classes.index(cls_name)
                xml_box = obj.find('bndbox')
                xmin = float(xml_box.find('xmin').text) / width
                ymin = float(xml_box.find('ymin').text) / height
                xmax = float(xml_box.find('xmax').text) / width
                ymax = float(xml_box.find('ymax').text) / height
                label.append([cls_id, xmin, ymin, xmax, ymax, difficult])
            temp.append(np.array(label))
        return temp

    def _label_path_from_index(self, index):
        """
        given image index, find out annotation path

        Parameters:
        ----------
        index: int
            index of a specific image

        Returns:
        ----------
        full path of annotation file
        """
        label_file = os.path.join(self.data_path, 'Annotations', index + '.xml')
        assert os.path.exists(label_file), 'Path does not exist: {}'.format(label_file)
        return label_file
