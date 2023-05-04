#-----------------------IMPORT Python PACKAGES--------------------------------#
import pandas as pd
import os
import urllib.request as urllib
import shutil
from tqdm import tqdm
import csv
import numpy as np
from barcode import Code128
from barcode.writer import ImageWriter
import cv2
from PIL import Image
#------------------------Class IMAGE_SCRAPER----------------------------------#
class IMAGE_SCRAPER:
    # constructor dunction
    def __init__(self, pth):
        # takes csv file as input from user
        self.PTH = pth
        # path to output images files folder
        self.Opth = 'Images/'
        # check if the path to images is not exist 
        if not os.path.exists(self.Opth):
            # make folder is not made
            os.mkdir(self.Opth)
        # tegger main function
        self.main()
    #--------------------- READING DATA FROM INPUT CSV FILE-------------------#
    def Read_Data(self, pth):
        # empty data list for latter use
        DATA = []
        # read data from csv and save as pandas dataframe
        df = pd.read_csv(pth)
        
        # iterate over dataframe rows
        for index, row in df.iterrows():
            # save first column data to variable
            ColFilter= row[0]
            SaleChan = row[1]
            # alocate third column data to variable
            SKU      = row[2]
            # alocated sixth column data + QTY string to variable
            QTY      = 'QTY'+str(row[3])
            # alocated second column data to variable
            ORDER_ID = row[4]
            STR_COLOR = row[5]
            try:
                if np.isnan(STR_COLOR):
                    STR_COLOR = 'blank'
            except:
                STR_COLOR = STR_COLOR
            # building image names from multiple variables
            
            ImageName = str(SaleChan)+'-'+str(SKU)+'-'+str(QTY)+'-'+ str(ORDER_ID)
            ImageNewName = str(ColFilter)+'-'+str(SaleChan)+'-'+str(SKU)+'-'+str(QTY)+'-'+ str(ORDER_ID)+'-'+STR_COLOR
            # making dictionay of all existing columns with additional two columns data
            # one for image name and second for image url
            DIC = {'Color Filter':row[0], 'Sales Channal':row[1], 'Item Code/SKU':row[2], 'Quantity':row[3],
                   'Order ID':row[4], 'Print Url':row[6], 'Image Name':ImageName, 'Image New Name': ImageNewName}
            
            # appending DIC to DATA list
            DATA.append(DIC)
        # returning DATA list as function output
        return DATA
    #-------------------------FUNCTION DOWNLOADING FILES----------------------#
    def Barcodes(self, order_id, name):
        try:
            # creating barcode using code128 in format jpeg
            barcode = Code128(order_id, writer=ImageWriter('jpeg'))
            # path to save code
            outpth = 'Barcodes'
            # create path if not exists
            if not os.path.exists(outpth):
                os.mkdir(outpth)
            # path to save barcode image with its name in created path
            filePth = outpth+'/'+name
            # save barcode image 
            barcode.save(filePth)
            print('Barcode Created')
        except:
            outpth = 'Barcodes'
            # create path if not exists
            if not os.path.exists(outpth):
                os.mkdir(outpth)
            # path to save barcode image with its name in created path
            filePth = outpth+'/'+name+'.jpeg'
            array = np.full((280, 376, 3), 255, dtype = np.uint8)
            cv2.putText(array, 'Barcode Failed', (80, 144), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0, 255), 3)
            # display the image
            cv2.imwrite(filePth, array)
            print('Barcode Failed')

    #-------------------------FUNCTION Barcodes Creation----------------------#
    def Download_Files(self, pth, ImageName, ImageURL):
        # split image name into two parts
        _, ImgName = os.path.split(str(ImageURL))
        # split last part of image name by . to get image extension
        ImageEXT   = ImgName.split('.')
        
        # make complete path where image will be downloaded
        ImagePth   = pth+'/'+ImageName+'.'+ImageEXT[-1]
        # check if image is not already exists in folder
        if not os.path.exists(ImagePth):
        # download image file to images folder
          try:
              request = urllib.Request(ImageURL, headers={'User-Agent': 'Mozilla/5.0'})
              content = urllib.urlopen(request)
              c = 0
              while content.status != 200:
                  request = urllib.Request(ImageURL, headers={'User-Agent': 'Mozilla/5.0'})
                  c+=1
                  if c == 3:
                      break
              with urllib.urlopen(request) as response, open(ImagePth, 'wb') as out_file:
                  shutil.copyfileobj(response, out_file)
                  
                  return str('Yes')
          except:
              return str('No')
        elif os.path.exists(ImagePth):
            return str('No')
    #-----------------------------------Main function-------------------------#
    def main(self):
        # save path to the pth variable
        pth = self.PTH
        if not os.path.exists(pth):
            print('file not exists')
        Opth = self.Opth
        # trigger Read_data function and save output as data variable
        data = self.Read_Data(pth)
        header = ['Color Filter','Sales Channal', 'Item Code/SKU', 'Quantity', 'Order ID', 
                  'Print Url', 'Image Name', 'Image New Name', 'Image_Status']
        # open Output.csv file with new data points
        with open('Ouptput_With_Image_Status.csv', 'w', newline = '') as output_csv:
            # initialize rows writer
            csv_writer = csv.writer(output_csv)
            # write headers to the file
            csv_writer.writerow(header)
            # iterate over data
            for e, d in enumerate(tqdm(data)):
                # time.sleep(10)
                # save image name to the variable
                ImageName  = d['Image New Name']
                # save image url to variable
                ImageURL   = d['Print Url']
                OrderID    = d['Order ID']
                # call Download files
                status = self.Download_Files(Opth, ImageName, ImageURL)
                if status == 'Yes':
                    d['Image_Status'] = 'Yes'
                #   # # write rows to csv file
                    csv_writer.writerow(d.values())
                    self.Barcodes(OrderID, ImageName)
                elif status == 'No':
                    d['Image_Status'] = 'No'
                    # write rows to csv file
                    csv_writer.writerow(d.values())
                
                
            # Display process completed message
            print('\n\n', '[INFO] PROCESS COMPLETED')
        
        return        


