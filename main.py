############    Please edit this section only. ###############################################################################################################################################################################################################################

#  The paths must end with '/'.      
absolutepath_of_directory_with_xmlfiles = 'Enter the absolute path of directory here.'  #　It is okay to have a mix of xml files and images in the same directory.
absolutepath_of_directory_with_imgfiles = 'Enter the absolute path of directory here.'
absolutepath_of_directory_with_yolofiles = 'Enter the absolute path of directory here.'  # Yolo files will be created under this directory.
absolutepath_of_directory_with_classes_txt = 'Enter the absolute path of directory here.'  # You do not need to create classes.txt. classes.txt will be generated automatically.
absolutepath_of_directory_with_error_txt = 'Enter the absolute path of directory here.'  # The names of files that do not have a paired xml or image file will be written to a text file under this directory.

##############################################################################################################################################################################################################################################################################


import os
import cv2
from lxml import etree
from xml.etree import ElementTree
from glob import glob


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
    def __init__(self, xmlfile_datalists_list, classes_list):
        self.xmlfile_datalists_list = xmlfile_datalists_list
        self.xmlfile_path = self.xmlfile_datalists_list.pop()
        self.img_filename = self.xmlfile_datalists_list.pop()
        self.yolofile_path = absolutepath_of_directory_with_yolofiles + os.path.basename(self.xmlfile_path).split('.', 1)[0] + '.txt'
        self.classes_list = classes_list
        try:
            (self.img_height, self.img_width, _) = cv2.imread(absolutepath_of_directory_with_imgfiles + self.img_filename).shape
            self.create_yolofile()
        except:
            with open(absolutepath_of_directory_with_error_txt+'xmlfiles_with_no_paired.txt', 'a') as f:
                f.write(os.path.basename(self.xmlfile_path)+'\n')

    def create_yolofile(self):
        for xmlfile_datalist in self.xmlfile_datalists_list:
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
    def __init__(self, classes_list):
        self.classes_list = classes_list

    def create_classestxt(self):
        with open(absolutepath_of_directory_with_classes_txt + 'classes.txt', 'w') as f:
            for class_name in self.classes_list:
                f.write(class_name+'\n')


def main():
    xmlfiles_pathlist = glob(absolutepath_of_directory_with_xmlfiles + "/*.xml")
    classes_list = []

    for xmlfile_path in xmlfiles_pathlist:
        process_xmlfile = GetDataFromXMLfile(xmlfile_path)
        xmlfile_datalists_list = process_xmlfile.get_datalists_list()
        CreateYOLOfile(xmlfile_datalists_list, classes_list)

    process_classesfile = CreateClasssesfile(classes_list)
    process_classesfile.create_classestxt()
    
    
if __name__ == '__main__':
    main()
