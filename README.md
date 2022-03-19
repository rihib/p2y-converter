# Convert Pascal VOC XML Annotation files to YOLO format text files
This script converts a Pascal voc file to a text file in YOLO format.
For Japanese → https://qiita.com/Rihib/items/e163d90c009f4fe12782

### Code Usage Instructions
```
Example 1:
>>python main.py --help
usage: main.py [-h] [--absolutepath_of_directory_with_xmlfiles XML]
               [--absolutepath_of_directory_with_imgfiles IMG]
               [--absolutepath_of_directory_with_yolofiles YOLO]
               [--absolutepath_of_directory_with_classes_txt CLS]
               [--absolutepath_of_directory_with_error_txt ERR]

Create YOLO annotations from Pascal VOC

optional arguments:
  -h, --help            show this help message and exit
  --absolutepath_of_directory_with_xmlfiles XML, -xml XML
                        Path of xml files, It is okay to have a mix of xml
                        files and images in the same directory.
  --absolutepath_of_directory_with_imgfiles IMG, -img IMG
                        Path of image files
  --absolutepath_of_directory_with_yolofiles YOLO, -yol YOLO
                        Yolo annotation files will be created under this
                        directory
  --absolutepath_of_directory_with_classes_txt CLS, -cls CLS
                        You do not need to create classes.txt. classes.txt
                        will be generated automatically in this path
  --absolutepath_of_directory_with_error_txt ERR, -err ERR
                        The names of files that do not have a paired xml or
                        image file will be written to a text file under this
                        directory
Example 2:
>>python main.py -xml=filter_annotations -img=filter_images -yol=dataset/yolo -cls=dataset -err=dataset
```
