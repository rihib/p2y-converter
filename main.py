## Example >> python main.py -xml=filter_annotations -img=filter_images -yol=dataset/yolo -cls=dataset -err=dataset

import os
import re
import sys
from glob import glob

import cv2
from lxml import etree
from xml.etree import ElementTree
from tqdm import tqdm

IMAGE_EXTENSION = '.jpg'

class GetDataFromXMLfile:
    def __init__(self, xmlfile_path):
        self.xmlfile_path = xmlfile_path
        self.xmlfile_datalists_list = []

    def get_datalists_list(self):
        self.parse_xmlfile()
        return self.xmlfile_datalists_list

    def parse_xmlfile(self):
        lxml_parser = etree.XMLParser(encoding='utf-8')
        xmltree = ElementTree.parse(self.xmlfile_path, parser=lxml_parser).getroot()
        
        if xmltree.findall('object') == []: 
            # When there is no object present in any image or image is whole background
            # In this case, pascal voc ha not <object> feild
            self.xmlfile_datalists_list.append([])
            img_filename = xmltree.find('filename').text
            self.xmlfile_datalists_list.append(img_filename)
            self.xmlfile_datalists_list.append(self.xmlfile_path)
        else:
            # When objects are present in the scene       
            for object in xmltree.findall('object'):
                xmlfile_datalist = []
                class_name = object.find('name').text
                xmlfile_datalist.append(class_name)
                bndbox = object.find("bndbox")
                xmlfile_datalist.append(bndbox)
                self.xmlfile_datalists_list.append(xmlfile_datalist)

            img_filename = xmltree.find('filename').text
            self.add_data_to_datalist(img_filename)
    
    def add_data_to_datalist(self, img_filename):
        for xmlfile_datalist in self.xmlfile_datalists_list:
            xmin = float(xmlfile_datalist[1].find('xmin').text)
            ymin = float(xmlfile_datalist[1].find('ymin').text)
            xmax = float(xmlfile_datalist[1].find('xmax').text)
            ymax = float(xmlfile_datalist[1].find('ymax').text)
            bndbox_coordinates_list = [(xmin, ymin), (xmax, ymin), (xmax, ymax), (xmin, ymax)]
            xmlfile_datalist[1] = bndbox_coordinates_list
        self.xmlfile_datalists_list.append(img_filename)
        self.xmlfile_datalists_list.append(self.xmlfile_path)


class CreateYOLOfile:
    def __init__(self, xmlfile_datalists_list, classes_list, 
                        absolutepath_of_directory_with_imgfiles,
                        absolutepath_of_directory_with_yolofiles, 
                        absolutepath_of_directory_with_error_txt):

        self.xmlfile_datalists_list = xmlfile_datalists_list
        self.xmlfile_path = self.xmlfile_datalists_list.pop()
        self.img_filename = self.xmlfile_datalists_list.pop()
        self.yolofile_path = os.path.join( absolutepath_of_directory_with_yolofiles , os.path.basename(self.xmlfile_path).split('.', 1)[0] + '.txt')
        self.classes_list = classes_list
        self.abs_path_img = absolutepath_of_directory_with_imgfiles
        self.abs_path_err = absolutepath_of_directory_with_error_txt
        try:
            # Added .jpg extension type for copying .jpg file types from images folder
            (self.img_height, self.img_width, _) = cv2.imread(os.path.join(self.abs_path_img , self.img_filename+'IMAGE_EXTENSION')).shape
            self.create_yolofile()
        except:
            with open(os.path.join(self.abs_path_err,'xmlfiles_with_no_paired.txt'), 'a') as f:
                f.write(os.path.basename(self.xmlfile_path)+'\n')

    def create_yolofile(self):
        for xmlfile_datalist in self.xmlfile_datalists_list:
            if len(xmlfile_datalist) == 0:

                with open(self.yolofile_path, 'a') as f:
                    f.write("")
            else:
                yolo_datalist = self.convert_xml_to_yolo_format(xmlfile_datalist)

                with open(self.yolofile_path, 'a') as f:
                    f.write("%d %.06f %.06f %.06f %.06f\n" % (yolo_datalist[0], yolo_datalist[1], yolo_datalist[2], yolo_datalist[3], yolo_datalist[4]))

    def convert_xml_to_yolo_format(self, xmlfile_datalist):
        class_name = xmlfile_datalist[0]
        self.add_class_to_classeslist(class_name)
        bndbox_coordinates_list = xmlfile_datalist[1]
        coordinates_min = bndbox_coordinates_list[0]
        coordinates_max = bndbox_coordinates_list[2]

        class_id = self.classes_list.index(class_name)
        yolo_xcen = float((coordinates_min[0] + coordinates_max[0])) / 2 / self.img_width
        yolo_ycen = float((coordinates_min[1] + coordinates_max[1])) / 2 / self.img_height
        yolo_width = float((coordinates_max[0] - coordinates_min[0])) / self.img_width
        yolo_height = float((coordinates_max[1] - coordinates_min[1])) / self.img_height
        yolo_datalist = [class_id, yolo_xcen, yolo_ycen, yolo_width, yolo_height]

        return yolo_datalist
    
    def add_class_to_classeslist(self, class_name):
        if class_name not in self.classes_list:
            self.classes_list.append(class_name)


class CreateClasssesfile:
    def __init__(self, classes_list, absolutepath_of_directory_with_classes_txt):
        self.classes_list = classes_list
        self.abs_path_cls = absolutepath_of_directory_with_classes_txt
    def create_classestxt(self):
        with open(os.path.join(self.abs_path_cls , 'classes.txt'), 'w') as f:
            for class_name in self.classes_list:
                f.write(class_name+'\n')

def main(absolutepath_of_directory_with_xmlfiles, 
        absolutepath_of_directory_with_imgfiles,
        absolutepath_of_directory_with_yolofiles, 
        absolutepath_of_directory_with_classes_txt,
        absolutepath_of_directory_with_error_txt):
    
    xmlfiles_pathlist = [os.path.join(absolutepath_of_directory_with_xmlfiles,f) 
                        for f in os.listdir(absolutepath_of_directory_with_xmlfiles) 
                        if '.xml' in f]
    
    if len(xmlfiles_pathlist) == 0:
        print("No XML files could be located")
        sys.exit()
    
    classes_list = []

    for xmlfile_path in tqdm(xmlfiles_pathlist, desc = 'Creating Annotations'):
        process_xmlfile = GetDataFromXMLfile(xmlfile_path)
        xmlfile_datalists_list = process_xmlfile.get_datalists_list()
        CreateYOLOfile(xmlfile_datalists_list, classes_list, 
                        absolutepath_of_directory_with_imgfiles,
                        absolutepath_of_directory_with_yolofiles, 
                        absolutepath_of_directory_with_error_txt)

    process_classesfile = CreateClasssesfile(classes_list, absolutepath_of_directory_with_classes_txt)
    process_classesfile.create_classestxt()
    
    
if __name__ == '__main__':
    
    import argparse
    parser = argparse.ArgumentParser(description ='Create YOLO annotations from Pascal VOC')

    parser.add_argument('--absolutepath_of_directory_with_xmlfiles', '-xml', metavar='XML', type=str,  
    help = 'Path of xml files, It is okay to have a mix of xml files and images in the same directory.')
    
    parser.add_argument('--absolutepath_of_directory_with_imgfiles', '-img', metavar='IMG', type=str,  
    help = 'Path of image files')
    
    parser.add_argument('--absolutepath_of_directory_with_yolofiles', '-yol', metavar='YOLO', type=str,  
    help = 'Yolo annotation files will be created under this directory')
    
    parser.add_argument('--absolutepath_of_directory_with_classes_txt', '-cls', metavar='CLS', type=str,  
    help = 'You do not need to create classes.txt. classes.txt will be generated automatically in this path')
    
    parser.add_argument('--absolutepath_of_directory_with_error_txt', '-err', metavar='ERR', type=str,  
    help ='The names of files that do not have a paired xml or image file will be written to a text file under this directory')

    args = parser.parse_args()

    absolutepath_of_directory_with_xmlfiles = args.absolutepath_of_directory_with_xmlfiles
    absolutepath_of_directory_with_imgfiles = args.absolutepath_of_directory_with_imgfiles
    absolutepath_of_directory_with_yolofiles = args.absolutepath_of_directory_with_yolofiles  
    absolutepath_of_directory_with_classes_txt = args.absolutepath_of_directory_with_classes_txt  
    absolutepath_of_directory_with_error_txt = args.absolutepath_of_directory_with_error_txt

    main(absolutepath_of_directory_with_xmlfiles, 
            absolutepath_of_directory_with_imgfiles,
            absolutepath_of_directory_with_yolofiles, 
            absolutepath_of_directory_with_classes_txt,
            absolutepath_of_directory_with_error_txt)

