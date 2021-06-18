# -*- coding: utf-8 -*-
"""
Created on Thu Jun 10 21:47:27 2021

@author: WATARU
"""

import streamlit as st
from google.cloud import vision
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import cv2
import os
import csv
import re
import pandas as pd
from googletrans import Translator
translator = Translator()

# selectbox
option = st.selectbox(
    'SELECT BOX:',
    ["TAA-CAA", "ARAI(comingsoon)"]
)

#st.write('You selected: ', option)
print(option)

uploaded_file = st.file_uploader('just for TAA CAA Choose a sheet file',type=["png", "jpg", "jpeg"], accept_multiple_files=False)
if uploaded_file is not None:
    # service accountのjsonからclientの生成
    client = vision.ImageAnnotatorClient.from_service_account_json(secrets.ACCESS_KEY)
    
    # 対象画像の読み込み
    content = uploaded_file.read()
    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=['ja-t-i0-handwrit',"en"])
    
    # APIに投げる
    response = client.text_detection(image=image)
    document = response.full_text_annotation
    
    import xml.etree.ElementTree as ET
    annotation = 'sample-' + option +'.xml'
    tree = ET.parse(annotation) # input_xmlはxmlのパス
    root = tree.getroot()
    
    image = Image.open(uploaded_file)
    st.image(image, caption='Input', use_column_width=True)
    img_array = np.array(image)
    cv2.imwrite('out.jpg', cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY))
    img = cv2.imread('out.jpg')
    img_labeled = img.copy()
    for obj in root.findall("./object"):
      name = obj.find('name').text
      xmin = obj.find('bndbox').find('xmin').text
      ymin = obj.find('bndbox').find('ymin').text
      xmax = obj.find('bndbox').find('xmax').text
      ymax = obj.find('bndbox').find('ymax').text
      xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
      cv2.rectangle(img_labeled, (xmin, ymin), (xmax, ymax), (0, 255, 0), thickness=1, lineType=cv2.LINE_AA)
      cv2.putText(img_labeled, name, (xmin, ymin), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), thickness=1)
    plt.figure(figsize=[10,10])
    plt.imshow(img_labeled[:,:,::-1]);plt.title("img_labeled")
    
    text_infos = []
    document = response.full_text_annotation
    for page in document.pages:
      for block in page.blocks:
        for paragraph in block.paragraphs:
          for word in paragraph.words:
            for symbol in word.symbols:
              bounding_box = symbol.bounding_box
              xmin = bounding_box.vertices[0].x
              ymin = bounding_box.vertices[0].y
              xmax = bounding_box.vertices[2].x
              ymax = bounding_box.vertices[2].y
              xcenter = (xmin+xmax)/2
              ycenter = (ymin+ymax)/2
              text = symbol.text
              text_infos.append([text, xcenter, ycenter])
    
    result_dict = {}
    for obj in root.findall("./object"):
      name = obj.find('name').text
      xmin = obj.find('bndbox').find('xmin').text
      ymin = obj.find('bndbox').find('ymin').text
      xmax = obj.find('bndbox').find('xmax').text
      ymax = obj.find('bndbox').find('ymax').text
      xmin, ymin, xmax, ymax = int(xmin), int(ymin), int(xmax), int(ymax)
      texts = ''
      for text_info in text_infos:
        text = text_info[0]
        xcenter = text_info[1]
        ycenter = text_info[2]
        if xmin <= xcenter <= xmax and ymin <= ycenter <= ymax:
          texts += text
      result_dict[name] = texts
    
    #for k, v in result_dict.items():
      #print('{} : {}'.format(k, v))
    
    # テキストの取得
    #print(response.text_annotations[0].description)
    f = open('temp.txt', 'w',encoding="SHIFT-JIS",errors="ignore")
    for k, v in result_dict.items():
        #text = st.text_area(label='Multi-line message', value='{} : {}'.format(k, v))
        #st.write(': ','{} : {}'.format(k, v))
        f.write('{} : {}'.format(k, v))
    f.close()
    
    read_text_file = pd.read_csv ("temp.txt",encoding="SHIFT-JIS",delimiter='KAIGYO',engine='python')
    read_text_file.to_csv ("temp.csv", index=None,encoding="SHIFT-JIS")
    df = pd.read_csv("temp.csv",encoding="SHIFT-JIS")
    df.T.to_csv("temp.csv",encoding="SHIFT-JIS")
    with open ('temp.csv','r',encoding="SHIFT-JIS",errors="ignore") as f :
        reader = csv.reader(f)
        for line in reader:
            st.write(str(line).replace("['","" ).replace("']","").replace("Unnamed: 0",""))
    
    st.write('To make sure manufacture year, type chassis number here: ','http://oliac.com/autos/')
    #st.write('',df2.loc[11].str)     
