from google.cloud import vision
import io
import os
import re
import glob
import string
import json
import requests
import cv2
from google.protobuf.json_format import MessageToDict
import numpy as np

# -*- coding: utf-8 -*-

# Configure environment for google cloud vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"

# Create a ImageAnnotatorClient
VisionAPIClient = vision.ImageAnnotatorClient()

path = 'images'

for filename in glob.glob(os.path.join(path, '*.*')):
    print(filename)
    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    img = cv2.imread(filename)
    # print(img.shape)
    # Send the image content to vision and stores text-related response in text
    image = vision.types.Image(content=content)
    response = VisionAPIClient.document_text_detection(image=image)

    # Converts google vision response to dictionary
    response = MessageToDict(response, preserving_proto_field_name=True)

    document = response.get('full_text_annotation')

    # to identify and compare the break object (e.g. SPACE and LINE_BREAK) obtained in API response
    breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType

    # Initialising line and bounding_box
    lines = ''
    bounding_box = []

    for page in document.get('pages'):
        for block in page.get('blocks'):
            for paragraph in block.get('paragraphs'):
                for word in paragraph.get('words'):
                    for symbol in word.get('symbols'):
                        lines = lines + symbol.get('text')
                        bounding_box.append(symbol.get(
                            'bounding_box', {}).get('vertices'))

    combined = list(zip(lines, bounding_box))

    ww = 95
    hh = 95
    color = (255,255,255)

    for index, box in enumerate(bounding_box):
        # print(box)
        try:
            x1 = min(abs(box[0]['x']), abs(box[2]['x']))
            y1 = min(abs(box[0]['y']), abs(box[2]['y']))
            x2 = max(abs(box[0]['x']), abs(box[2]['x']))
            y2 = max(abs(box[0]['y']), abs(box[2]['y']))
        except Exception as e:
            x1, y1, x2, y2 = 0,0,0,0
        x1, y1, x2, y2 = max(x1-5,0), max(y1-5,0), min(x2+5,300), min(y2+5,300)
        v = img[y1:y2, x1:x2]
        ht, wd, cc = v.shape
        result = np.full((hh,wd,cc), color, dtype=np.uint8)
        # compute center offset
        xx = (wd - wd) // 2
        yy = (hh - ht) // 2

        # copy img image into center of result image
        result[yy:yy+ht, xx:xx+wd] = v

        if index == 0:
            image = result
        else:
            image = np.concatenate((image, result), axis=1)

    cv2.imwrite(filename,image)
    # cv2.imshow("image", image)
    # cv2.waitKey(0)

    try:
        combined.sort(key = lambda x: x[1][0]['x'])
    except Exception as e:
        print("sorting not done")

    final_text = ''.join([x[0] for x in combined])
    print(final_text)

