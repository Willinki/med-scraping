import pdfplumber
import json
from tqdm import tqdm

#OPTION 1
def pdf_to_text(pdf_path, txt_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in tqdm(pdf.pages):
            # Extract text from each page
            page_text = page.extract_text(layout=False)
            if page_text:
                text += page_text + "\n"

    # Write the extracted text to a text file
    with open(txt_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

#OPTION 2
import fitz  # PyMuPDF

def pdf_to_text_2(pdf_path, txt_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    # Initialize an empty string to store the text
    text = ""

    # Iterate over each page in the PDF
    for page_num in tqdm(range(len(pdf_document))):
        page = pdf_document.load_page(page_num)
        text += page.get_text()

    # Write the extracted text to a text file
    with open(txt_path, "w", encoding="utf-8") as text_file:
        text_file.write(text)

if __name__ == "__main__":
    # Replace 'your_pdf_file.pdf' with your PDF file path
    # Replace 'output_text_file.txt' with the desired output text file path
    pdf_path = '/Users/detsutut/testi/pdf/Terapia delle malattie neurologiche (Angelo Sghirlanzoni (auth.)) (Z-Library).pdf'
    txt_path = '../output_text_file.txt'
    pdf_to_text(pdf_path, txt_path)