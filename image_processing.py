import easyocr as eo
import re
import numpy as np
import imutils
import cv2
from PIL import Image,ImageEnhance
import angle

def img_pro(path,doc_type):
    # Find angle and rotate (use 4 angle)
    rotated = angle.check_angle(path)

    img2 = Image.fromarray(rotated)
    enhancer = ImageEnhance.Brightness(img2)

    factor = 1.5  # gives original image
    im_output = enhancer.enhance(factor)
    eimage = np.asarray(im_output)
    r, g, b = cv2.split(eimage)
    eimage = cv2.merge([b, g, r])

    # apply Easy ocr for find test
    reader = eo.Reader(['en'])
    result = reader.readtext(eimage)
    print(result)
    # list to String (easy ocr return list)
    text = ""
    for res in result:
        text += res[1] + ' '
    print(text)

    #find keyword
    resource = find_keyword(text,doc_type)
    print("Document Response",resource)
    return resource

def find_keyword(string2,doc_type):
    response={}
    aadharKeyWord = string2;
    if((re.search("GOV",string2,re.IGNORECASE) and re.search("india",string2,re.IGNORECASE) or re.search("IIDIA",string2,re.IGNORECASE) or re.search("IMDIA",string2,re.IGNORECASE))):
        print("Adhar card")
        if(doc_type=="Adhar Card"):
            response=aadhar_card(string2)
        else:
            #print("uploaded is not",doc_type)
            response["Doc Type Error"] = "uploaded Document is not " + doc_type
    elif ((re.search("ELECTION", string2, re.IGNORECASE) and re.search("india", string2, re.IGNORECASE)) or (re.search("COMMISION", string2, re.IGNORECASE) and re.search("INDIA", string2, re.IGNORECASE))):
        print("Voter ID Front")
        if(doc_type=="Voter ID Front"):
            response=voter_card_front(string2)
        else:
            response["Doc Type Error"] = "uploaded Document is not "+doc_type
    elif(re.search("Registration Officer",string2,re.IGNORECASE)):
        print("Voter ID Back")
        if(doc_type=="Voter ID Back"):
            response=voter_card_back(string2)
        else:
            response["Doc Type Error"] = "uploaded Document is not "+doc_type
    elif ((re.search("DRIVING", string2, re.IGNORECASE) and re.search("LICENCE", string2, re.IGNORECASE)) or (re.search("DRIVING", string2, re.IGNORECASE))):
        print("Driving licence ")
        if(doc_type=="Driving License"):
            response=driving_license(string2)
        else:
            response["Doc Type Error"] = "uploaded Document is not "+doc_type
    elif (re.search("UNION", string2, re.IGNORECASE) or (re.search("REPUBLIC",string2,re.IGNORECASE)) and re.search("INDIA", string2, re.IGNORECASE)):
        print("Driving licence ")
        if(doc_type=="Driving License"):
            response=driving_license(string2)
        else:
            response["Doc Type Error"] = "uploaded Document is not "+doc_type
    else:
        #print("other doc")
        response["Doc Type Error"] = "Document not valid for OCR Please upload valid " + doc_type
    return response

def camel_case_split(str):
    return re.findall(r'[A-Z](?:[a-z]+|[A-Z]*(?=[A-Z]|$))', str)

def is_camel_case(s):
    return s != s.lower() and s != s.upper() and "_" not in s

#extract text from aadhar card
def aadhar_card(text):
    Name = ""
    gender= ""
    dob = ""
    a_number =""
    aadhar_rep ={}
    rx = r"\b[A-Z]\w*(?:\s+[A-Z]\w*)+"
    result = [" ".join(x.split()) for x in re.findall(rx, text)]
    nameArr = []
    for j in result:
        arrInner = camel_case_split(j)
        for k in arrInner:
            if len(k) >= 4:
                if is_camel_case(k):
                    if k != 'Government' and k != 'India' and k != 'Male' and k != 'Mobile' and k != 'Female' and k != 'Father' and k != 'Year' and k != 'Birth':
                        nameArr.append(k)
                    # print(k)
    #print("Name: ",str(nameArr).replace("]", "").replace("[","").replace("'", "").replace(",", ""))
    name = str(nameArr).replace("]", "").replace("[","").replace("'", "").replace(",", "")
    nm1 = name.replace("Profile Added ","")
    nm = nm1.replace("Mera Aadhaar Meri Pehchaan","")
    aadhar_rep["Name"] = nm

    if (re.search("female", text, re.IGNORECASE)):
        gender = "Female"
    elif (re.search("male", text, re.IGNORECASE)):
        gender = "Male"
    else:
        gender=""
    #print("Gender: ",gender)
    aadhar_rep["Gender"] = gender

    if (re.search("Year of Birth", text, re.IGNORECASE) or (re.search("Year", text, re.IGNORECASE) and re.search("Birth", text, re.IGNORECASE))):
        res = re.search(r'\d{4}', text)
        if res:
            #print("year of birth: ",res.group())
            dob = res.group()
        else:
            print("Year of birth not fetch")
            dob = "Not Fetch"
    else:
        dob = str(re.findall(r"[\d]{1,4}[/-][\d]{1,4}[/-][\d]{1,4}", text)).replace("]", "").replace("[","").replace("'", "")

    aadhar_rep["Date/Year of Birth"] = dob

    testStr = text.replace(" ", "")
    number = re.search(r'\d{12}', testStr)
    if number:
        #print("Aadhar number: ",number.group())
        a_number=number.group()
    else:
        print("Aadhar number not fetch")
        a_number = "Not Fetch"
    aadhar_rep["Aadhar Number"] = a_number
    return  aadhar_rep

#extract texr from driving license
def driving_license(text):
   dri_rep = {}
   if (re.search(r"([\d]{1,4}-[\d]{1,4}-[\d]{1,4})", text)):
      x = re.findall(r"([\d]{1,4}-[\d]{1,4}-[\d]{1,4})", text)
      first_issue = x[0]
      expire_date = x[1]
      birth_date = x[2]
   elif (re.search(r"([\d]{1,4}/[\d]{1,4}/[\d]{1,4})", text)):
      x = re.findall(r"([\d]{1,4}/[\d]{1,4}/[\d]{1,4})", text)
      y = re.findall(r"([\d]{1,4}\|[\d]{1,4}/[\d]{1,4})", text)
      first_issue = x[0]
      expire_date = x[3]
      birth_date = y[0]
   else:
      first_issue = "Date of issue not fetch"
      expire_date = "Expire date not fetch"
      birth_date = "Birth date not fetch"

   dri_rep["Date of First Issue"] = first_issue
   dri_rep["Expire Date"] = expire_date
   dri_rep["Birth Date"] = birth_date

   s = text.split(" ")
   strings_with_states = []
   count = 0

   list_of_states = {'JK', 'HP', 'PN', 'CH', 'UK', 'UA', 'HR', 'DL', 'RJ', 'UP', 'BR', 'SK', 'AR', 'AS', 'NL', 'MN',
                     'ML', 'TR', 'MZ', 'WB', 'JH', 'OR', 'OD', 'CG', 'MP', 'GJ', 'MH', 'DD', 'DN', 'TS', 'AP', 'KA',
                     'KL', 'TN', 'PY', 'GA', 'AN', 'LD'}

   for word in s:
      for state in list_of_states:
         if state in word:
            strings_with_states.append(word)

   for string in strings_with_states:
      for i in string:
         if (i.isdigit()):
            count = count + 1

      if count < 13:
         index = s.index(string)
         s1 = s[index] + s[index + 1]
         if len(s) >= 15:
            for i in s1:
               if (i.isdigit()):
                  count = count + 1
            if count > 13:
               s1 = s1[-16:]
               dri_rep["Driving License Number"] = s1
               break
               break
      else:
         dri_rep["Driving License Number"] = string
         break
         break

   name=''
   if 'Name' in s:
      index = s.index('Name')
      name =  s[index + 1] + ' ' + s[index + 2]
   elif 'NAME' in s:
      index = s.index('NAME')
      name = s[index+1]+' ' +s[index+2]
   elif 'MAME' in s:
      index = s.index('MAME')
      name = s[index+1]+' '+s[index+2]
   else:
      name = "Name of the card holder not fetch"
   dri_rep["Name of license holder"] = name
   return dri_rep

def voter_card_back(text):
    gender = ""
    dob = ""
    address = ""
    voter_rep = {}

    # exract gender from image
    if (re.search("female", text, re.IGNORECASE)):
        gender = "Female"
    elif (re.search("male", text, re.IGNORECASE)):
        gender = "Male"
    else:
        gender=""
    #print("Gender: ",gender)
    voter_rep["Gender"] = gender

    #extract date of birth or age from image
    if(str(re.search(r"[\d]{1,4}[/-][\d]{1,4}[/-][\d]{1,4}", text).group()).replace("]", "").replace("[", "").replace("'", "")):
        dob = str(re.search(r"[\d]{1,4}[/-][\d]{1,4}[/-][\d]{1,4}", text).group()).replace("]", "").replace("[", "").replace("'", "")
    elif(str(re.search(r"[\d]{1,2}", text).group()).replace("]", "").replace("[", "").replace("'", "")):
        dob = str(re.search(r"[\d]{1,2}", text).group()).replace("]", "").replace("[", "'", "")
    else:
        dob = "Not fetch Date of Birth/Age"

    voter_rep["Date of Birth/Age"] = dob

    #extract address from image
    if(re.search(r"\bAddress(.+?)Dist.(?:\s+[A-Z]\w*)",text)):
        x = re.search(r"\bAddress(.+?)Dist.(?:\s+[A-Z]\w*)",text).group()
        add = x.replace("Address ","")
    else:
        add = "Address not fetch"

    voter_rep["Address"] = add

    return voter_rep

def voter_card_front(text):
    Name = ""
    voter_rep ={}

    if(re.search(r"\bName\w*(?:\s+[A-z ]\w*(?:\s+[A-z ]\w*))",text)):
        x = re.search(r"\bName\w*(?:\s+[A-z ]\w*(?:\s+[A-z ]\w*))",text)
        xx = x.group()
        xxx = xx.replace("Name ","")
        voter_rep["Name"] = xxx

    if(re.search(r"\bFather\'s Name\w*(?:\s+[A-z ]\w*)", text)):
        y = re.search(r"\bFather\'s Name\w*(?:\s+[A-z ]\w*)", text)
        yy = y.group()
        yyy = yy.replace("Father\'s Name ","")
        voter_rep["Father Name"] = yyy
    elif(re.search(r"\bHusband\'s Name\w*(?:\s+[A-z ]\w*)", text)):
        z = re.search(r"\bHusband\'s Name\w*(?:\s+[A-z ]\w*)", text)
        zz = z.group()
        zzz = zz.replace("Husband\'s Name ", "")
        voter_rep["Husband Name"] = zzz
    else:
        a = "Not Fatch Father Name/Husband Name"
        voter_rep["Father Name"] = a

    return  voter_rep
