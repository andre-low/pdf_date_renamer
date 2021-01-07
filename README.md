# PDF Date Renamer
Extract dates from a scanned and OCRed PDF (typically letters), detect and parse dates, and renames the file based on the first detected date in the document. Renamed to big-endian (i.e. YYYYMMDD) format.

## Required dependencies
- Python 3
- Python packages:
  - pdfminer.six
  - dateparser
Install python dependencies with pip:
```console
$ pip install pdfminer.six dateparser
```

## Usage
To rename a single file `document.pdf`
```console
$ python pdf_date_renamer.py document.pdf
```

To rename all PDFs in the current directory (resursive)
```console
$ python pdf_date_renamer.py .
```

To rename all PDFs in a specified directory
```console
$ python pdf_date_renamer.py path_to_directory
```
