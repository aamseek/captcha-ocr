        def get_captcha():
            th1 = 90
            th2 = 30
            sig = 1.5
            orignal = Image.open("captcha.png")
            orignal.save("orignal.png")
            black_and_white = orignal.convert("L")
            black_and_white.save("black_and_white.png")
            first_threshold = black_and_white.point(lambda p:p>th1 and 255)
            first_threshold.save("first_threshold.png")
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
            
            # #path = r'captcha'
            # #for filename in glob.glob(os.path.join(path, '*.png')):

            with io.open("first_threshold.png", 'rb') as image_file:
                content = image_file.read()
                image = vision.types.Image(content=content)
                response = VisionAPIClient.document_text_detection(image=image)
                document = response.full_text_annotation
                # to identify and compare the break object (e.g. SPACE and LINE_BREAK) obtained in API response
                breaks = vision.enums.TextAnnotation.DetectedBreak.BreakType

                # generic counter
                c = 0

                # List of lines extracted
                lines = []

                # List of corresponding confidence scores of lines
                confidence = []

                # Initialising list of lines
                lines.append('')

                # Initialising list of confidence scores
                confidence.append(2)

                # Loop through all symbols returned and store them in lines list alongwith
                # corresponding confidence scores in confidence list
                for page in document.pages:
                    for block in page.blocks:
                        for paragraph in block.paragraphs:
                            for word in paragraph.words:
                                for symbol in word.symbols:
                                    lines[c] = lines[c] + symbol.text
                                    if re.match(r'^[a-zA-Z]+\Z', symbol.text) or symbol.text.isdigit():
                                        confidence[c] = min(confidence[c], symbol.confidence)
                                    if symbol.property.detected_break.type == breaks.LINE_BREAK or \
                                            symbol.property.detected_break.type == breaks.EOL_SURE_SPACE:
                                        c += 1
                                        lines.append('')
                                        confidence.append(2)
                                    elif symbol.property.detected_break.type == breaks.SPACE or \
                                            symbol.property.detected_break.type == breaks.SURE_SPACE:
                                        lines[c] = lines[c] + ' '
                result = ""
                for i in lines:
                    result = result+i
                res =result.replace(' ', '')
                #result.replace(' ', '')
                print("the result is:" ,res)
                return res