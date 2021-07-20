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

# -*- coding: utf-8 -*-

# Configure environment for google cloud vision
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"

# Create a ImageAnnotatorClient
VisionAPIClient = vision.ImageAnnotatorClient()

path = 'images'

for filename in glob.glob(os.path.join(path, '*.*')):

    with io.open(filename, 'rb') as image_file:
        content = image_file.read()

    img = cv2.imread(filename)
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
    try:
        combined.sort(key = lambda x: x[1][0]['x'])
    except Exception as e:
        print("sorting not done")

    final_text = ''.join([x[0] for x in combined if x[0].isalnum()])
    print(final_text.upper())


