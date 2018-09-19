import glob
from pdf2image import convert_from_path


pdf_files = glob.glob("./pdf/*.pdf")
for pdf_file in pdf_files:
    convert_from_path(pdf_file, 100, output_folder="./jpg", fmt='jpg')
