from selenium import webdriver
from google.cloud import vision
import io
import os
import re
import glob
import string
import json
import scrapy
import pytesseract
from scrapy_selenium import SeleniumRequest
from PIL import Image
import numpy
from scrapy.selector import Selector
from selenium.webdriver.common.keys import Keys
from PIL import ImageFilter
from scipy.ndimage.filters import gaussian_filter
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from time import sleep
from google.protobuf.json_format import MessageToDict

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "client_secrets.json"
print('Credendtials from environ: {}'.format(
    os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')))

driver = webdriver.Chrome(executable_path="./chromedriver.exe")
driver.get("http://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome")
#captcha_url= driver.find_element_by_xpath("//div[@id='captchaImg']/img").get_attribute('src')
#print(captcha_url)
#if captcha_url:
#           driver.get(captcha_url)
 #           driver.save_screenshot('captcha.png')
#driver.get("http://unifiedportal-epfo.epfindia.gov.in/publicPortal/no-auth/misReport/home/loadEstSearchHome")
driver.save_screenshot("screen.png")

im = Image.open("screen.png")
width, height = im.size
print(width,height)
topLeft_x= 550
topLeft_y = 275
bottomRight_x = 700
bottomRight_y= 375
cropped_image = im.crop((topLeft_x, topLeft_y, bottomRight_x, bottomRight_y))
cropped_image.save("captcha.png")

search_input = driver.find_element_by_xpath("//input[@id='estName']")
search_input.send_keys("Reliance")
# code_input= driver.find_element_by_xpath("//*[@id='estCode']")
# code_input.send_keys("0032560")
def get_captcha():

    VisionAPIClient = vision.ImageAnnotatorClient()

    with io.open("captcha.png", 'rb') as image_file:
        content = image_file.read()

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

    return final_text.upper()
        # # html = driver.page_source
        # # print("THIS IS THE HTML :" ,html)

captcha_input = driver.find_element_by_id('captcha')
captcha_input.send_keys(get_captcha())

search_btn =  driver.find_element_by_id("searchEmployer")
search_btn.send_keys(Keys.ENTER)
sleep(5)

# with open('test.json') as f:
#     data = json.load(f)
records =driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[1]/div").text
if records == "Total Records Found : 1":
    establishment_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[2]").text
    office_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[4]").text
    view_details = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[5]/a").click()
    sleep(8)
    print("-------------------")
    print(establishment_name,office_name,view_details)
    view_payment = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[5]/div/div[2]/div/div/a")
    view_payment.click()
    sleep(5)
    new_window = driver.window_handles[1]
    driver.switch_to_window(new_window)
    if driver.find_element_by_xpath("/html/body/div/div/div[2]/div").text == "No Payment details found for this Establishment.":
        print("NO DETAILS FOUND")
    next_btn = driver.find_element_by_xpath("//*[@class='paginate_button next']")
    count = 0
    while next_btn:
        try:
            next_btn.click()
            next_btn = driver.find_element_by_xpath("//*[@class='paginate_button next']")
            count = count+1
            print(count)
        except:
            break
    detail_row = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[1]/div/div[2]/div/table/tbody/tr[1]/td[5]/a")
    j=1
    while j:
        try:
            detail_row = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[1]/div/div[2]/div/table/tbody/tr[j]/td[5]/a")
            j=j+1
        except:
            break

    detail_row.click()
    sleep(5)
    name_search = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[2]/div/div[2]/div/div/div/div[2]/div/div[2]/label/input")
    name_search.send_keys("Amit")

else:

    i = 1
    while i:
        try:
            establishment_code = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr["+str(i)+"]/td[1]").text
            establishment_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr["+str(i)+"]/td[2]").text
            establishment_address = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr["+str(i)+"]/td[3]").text
            office_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr["+str(i)+"]/td[4]").text

            a_dict=  {
                "establishment_code":establishment_code,
                "establishment_name":establishment_name,
                "establishment_address":establishment_address,
                "office_name":office_name
            }
            print(a_dict)
            i = i+1
            # data.update(a_dict)
            # with open('test.json', 'w') as f:
            #     json.dump(data, f)
        except Exception as e:
            print("ERROR",e)
            break

# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# sleep(2)

#search_btn = driver.find_element_by_id("search_button_homepage")
#search_btn.click()
