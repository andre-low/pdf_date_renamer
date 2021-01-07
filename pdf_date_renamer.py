# Misc libraries
import re  # regex
import os  # os
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
                         'STRICT_PARSING': True,
                         'PREFER_DATES_FROM': 'past',
                         'PARSERS': ['absolute-time']})
    return dates


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
    return cleaned_text


def pdf_date_renamer(path):
    global count
    if path.endswith('.pdf'): # only acts on PDF files
        if find_dates(pdf_parser(path)) is not None: # only proceeds if a date is detected
            count += 1
            detected_date = find_dates(pdf_parser(path))[0][1]
            formated_date = detected_date.strftime('%Y%m%d')
            os.rename(path, formated_date + '_' + str(count).zfill(3) + '.pdf')
    return


# Walks through the entire directory, and touches all files with a specified function.
def traverse_and_touch(directory, touch):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            touch(os.path.join(root, filename))
    return

count = 0

# Command line argument assignment to variables
arg1 = argv[1]

if arg1.endswith('.pdf'):
    pdf_date_renamer(arg1)
else:
    traverse_and_touch(arg1, pdf_date_renamer)
