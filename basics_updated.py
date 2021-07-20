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

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/chandrimasabharwal/scrapy_projects/EPFscraper/EPFscraper/spiders/client_secrets.json"
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
topLeft_x= 1150
topLeft_y =580
bottomRight_x =1550
bottomRight_y=675
cropped_image = im.crop((topLeft_x, topLeft_y, bottomRight_x, bottomRight_y))
cropped_image.save("captcha.png")

search_input = driver.find_element_by_xpath("//input[@id='estName']")

search_input.send_keys("shbsj")
# code_input= driver.find_element_by_xpath("//*[@id='estCode']")
# code_input.send_keys("0056162")
def get_captcha():
    # th1 = 90
    # th2 = 30
    # sig = 1.5
    # orignal = Image.open("captcha.png")
    # orignal.save("orignal.png")
    # black_and_white = orignal.convert("L")
    # black_and_white.save("black_and_white.png")
    # first_threshold = black_and_white.point(lambda p:p>th1 and 255)
    # first_threshold.save("first_threshold.png")
    #blur = numpy.array(first_threshold)
    #blurred = gaussian_filter(blur,sigma=sig)
    #blurred = Image.fromarray(blurred)
    #blurred.save('blurred.png')
    #final = blurred.point(lambda p:p>th2 and 255)
    #final = final.filter(ImageFilter.EDGE_ENHANCE_MORE)
    #final = final.filter(ImageFilter.SHARPEN)
    #final.save("final.png")
    #number = pytesseract.image_to_string(Image.open(os.path.abspath('first_threshold.png')))
    
    # image = r'/Users/chandrimasabharwal/scrapy_projects/EPFscraper/captcha.png'
    VisionAPIClient = vision.ImageAnnotatorClient()

# path = 'images'

# for filename in glob.glob(os.path.join(path, '*.*')):

    with io.open("captcha.png", 'rb') as image_file:
        content = image_file.read()

#img = cv2.imread(filename)
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




            # VisionAPIClient = vision.ImageAnnotatorClient()
            
            # # #path = r'captcha'
            # # #for filename in glob.glob(os.path.join(path, '*.png')):

            # with io.open("first_threshold.png", 'rb') as image_file:
            #     content = image_file.read()
            #     image = vision.types.Image(content=content)
            #     response = VisionAPIClient.document_text_detection(image=image)
            #     document = response.full_text_annotation
            #     # to identify and compare the break object (e.g. SPACE and LINE_BREAK) obtained in API response
            #     breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType

            #     # generic counter
            #     c = 0

            #     # List of lines extracted
            #     lines = []

            #     # List of corresponding confidence scores of lines
            #     confidence = []

            #     # Initialising list of lines
            #     lines.append('')

            #     # Initialising list of confidence scores
            #     confidence.append(2)

            #     # Loop through all symbols returned and store them in lines list alongwith
            #     # corresponding confidence scores in confidence list
            #     for page in document.pages:
            #         for block in page.blocks:
            #             for paragraph in block.paragraphs:
            #                 for word in paragraph.words:
            #                     for symbol in word.symbols:
            #                         lines[c] = lines[c] + symbol.text
            #                         if re.match(r'^[a-zA-Z]+\Z', symbol.text) or symbol.text.isdigit():
            #                             confidence[c] = min(confidence[c], symbol.confidence)
            #                         if symbol.property.detected_break.type == breaks.LINE_BREAK or \
            #                                 symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
            #                             c += 1
            #                             lines.append('')
            #                             confidence.append(2)
            #                         elif symbol.property.detected_break.type == breaks.SPACE or \
            #                                 symbol.property.detected_break.type == breaks.SURE_SPACE:
            #                             lines[c] = lines[c] + ' '
            #     result = ""
            #     for i in lines:
            #         result = result+i
            #     res =result.replace(' ', '')
    
            #     #result.replace(' ', '')
            #     print("the result is:" ,res)
    return final_text.upper()
        # # html = driver.page_source 
        # # print("THIS IS THE HTML :" ,html)
        

captcha_input = driver.find_element_by_id('captcha')
        
captcha_input.send_keys(get_captcha())

search_btn =  driver.find_element_by_id("searchEmployer")
search_btn.send_keys(Keys.ENTER)
sleep(5)
if driver.find_element_by_xpath("//html/body/div/div/div[2]/div[4]/div/div[2]/div/div").text == "No details found for this criteria. Please enter valid Establishment name or code number .":
    print("INVALID INPUT")
if driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div").text == "Please enter valid captcha.":
    print("CAPTCHA WRONG")
    driver.refresh()

# with open('test.json') as f:
#     data = json.load(f)
records =driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[1]/div").text
if records == "Total Records Found : 1":
    establishment_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[2]").text
    office_name = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[4]").text
    view_details = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr/td[5]/a").click()
    sleep(8)
    view_payment = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[5]/div/div[2]/div/div/a")
    sleep(5)
    view_payment.click()
    sleep(3)
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
    


    #view_payment.send_keys(Keys.CONTROL+Keys.TAB)
    # driver.save_screenshot("after_captcha1.png")
    # print("__________________________NO ERROR______________")
else:
#     establishments = driver.find_element_by_xpath("/html/body/div/div/div[2]/div[4]/div/div[2]/div/div/div[2]/table/tbody/tr")
#     for establishment in establishments:
#         establishment_code = establishment.xpath(".//td[1]/text()").get()
#         establishment_name = establishment.xpath(".//td[2]/text()").get()
#         establishment_address = establishment.xpath(".//td[3]/text()").get()
#         office_name = establishment.xpath(".//td[4]/text()").get()
#         print(establishment_name)
        #  {
        #         "establishment_code":establishment_code,
        #         "establishment_name":establishment_name,
        #         "establishment_address":establishment_address,
        #         "office_name":office_name
        #     }
            
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
        except:
            try:
                new_next= driver.find_element_by_xpath("//*[@class='paginate_button next']")
                new_next.click()
                i=1
            except Exception as e:
                print("ERROR",e)
                break
         
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
# sleep(2)







#search_btn = driver.find_element_by_id("search_button_homepage")
#search_btn.click()