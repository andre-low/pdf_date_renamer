# Misc libraries
import re  # regex
import os  # os
from secrets import token_hex
from io import StringIO  # string IO streaming
from sys import argv  # accept command line arguments

# PDF libraries
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# Date-parsing libraries
from dateparser.search import search_dates  # Identify dates from a string
from datetime import datetime

# Functions
def preclean_text(text):  # removes colons which seem to throw the date parser
    cleaned_text = re.sub(r':\s', ' ', text, flags=re.IGNORECASE)
    return cleaned_text


def find_dates(text):
    dates = search_dates(text, languages=['en'], settings={
                         'DATE_ORDER': 'DMY',
                         'PREFER_LOCALE_DATE_ORDER': False,
                         'TIMEZONE': 'Asia/Singapore',
                         'STRICT_PARSING': True,
                         'PREFER_DATES_FROM': 'past',
                         'PARSERS': ['absolute-time']})
    return dates

def find_resident_name(text):
    # make sure to exclude matching Louis' name
    nameRegex = "(?:MR|MS|MDM|Mr|Ms|Mdm)(?!Kheng Wee|KHENG WEE) (.*)"
    output = re.search(nameRegex, text)
    if not output:
        print("No name found for this case")
        return
    name = output.group(1)
    name = name.upper()
    # replace spaces with underscores, and replace / in the name (ie. Muthu S/O Kumar) as it messes with filepath conversion
    name = name.replace(" ", "_")
    name = name.replace("/", "")
    # print(name)
    return(name)

def find_agency_and_case_number(text):
    # find our reference number, if it is provided in the return email 
    referenceRegex = "(RV[0-9]{4})-[0-9]{6}-([^\s]+)"
    output = re.search(referenceRegex, text)
    if not output:
        print("No agency found for this case, returning first line")
        return text.split('\n', 1)[0].strip()
    case = re.search(referenceRegex, text).group(1).strip()
    agency = re.search(referenceRegex, text).group(2).strip()
    # print(agency + '_' + case)
    return(agency + '_' + case)


def pdf_parser(path):  # Open and parses PDF, returns string with cleaned text
    output_string = StringIO()
    with open(path, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        for page in PDFPage.create_pages(doc):
            interpreter.process_page(page)
    raw_text = (output_string.getvalue())
    cleaned_text = preclean_text(raw_text)
    # print(cleaned_text)
    return cleaned_text


def pdf_date_renamer(path):
    if path.endswith('.pdf'): # only acts on PDF files
        print("Trying to rename: " + path)
        newFileName = ""
        pdfText = pdf_parser(path)
        name = find_resident_name(pdfText)
        agencyCase = find_agency_and_case_number(pdfText)
        # check if a date is detected
        if find_dates(pdfText): 
            detected_date = find_dates(pdfText)[0][1]
            formatted_date = detected_date.strftime('%Y%m%d')
            newFileName += formatted_date + "_"
        # check if an agency and case were generated
        if agencyCase:
            newFileName += agencyCase + "_"
        # check if a name was generated
        if name:
            newFileName += name
        if newFileName != "":
            newFileName += ".pdf"
            os.rename(path, newFileName)
            print("File renamed to: " + newFileName)
        else: 
            print("Skipping " + path + " as no date was found.")
    return


# Walks through the entire directory, and touches all files with a specified function.
def traverse_and_touch(directory, touch):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            touch(os.path.join(root, filename))
    return

# Command line argument assignment to variables
arg1 = argv[1]
if arg1.endswith('.pdf'):
    print("Renaming file: " + arg1)
    pdf_date_renamer(arg1)
else:
    print("Renaming PDF files at path: " + arg1)
    traverse_and_touch(arg1, pdf_date_renamer)
