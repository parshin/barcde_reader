import qrtools
import glob
import logging
import requests
from conf import ws_address
from conf import nu_address
from conf import files_dir
import json
from base64 import b64encode
import os
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance

recognized_files = 0


def read_qr(jpg_file):
    qr = qrtools.QR()
    qr.decode(jpg_file)
    return qr.data


def send_barcode(jpg_file, barcode_data):
    with open(jpg_file, 'rb') as f:
        base64_bytes = b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
        response = requests.post(ws_address["ws_address"],
                                 data=json.dumps({"barcode": barcode_data, "file": base64_string}))
        try:
            response = response.json()
            if response["result"]:
                os.remove(jpg_file)
            else:
                logging.info('file not_recognized: ' + jpg_file)
        except IOError:
            logging.error('response is not json: ' + str(response))


def enhance_img(jpg_file):
    image = Image.open(jpg_file)

    w, h = image.size
    left, top, right, bottom = 0, 0, w, 150
    image = image.crop((left, top, right, bottom))

    image = ImageEnhance.Contrast(image)
    image = image.enhance(3)

    image.save(files_dir["files_dir"] + "_cropped_" + jpg_file)

    barcode_data = read_qr(files_dir["files_dir"] + "_cropped_" + jpg_file)

    if barcode_data == "NULL":
        image = ImageEnhance.Sharpness(image)
        image = image.enhance(0)
        image.save(files_dir["files_dir"] + "_cropped_" + jpg_file)

    barcode_data = read_qr(files_dir["files_dir"] + "_cropped_" + jpg_file)

    os.remove(files_dir["files_dir"] + "_cropped_"+jpg_file)
    return barcode_data


def pdf_to_jpg(dpi=100):
    os.chdir(files_dir["files_dir"])
    pdf_files = glob.glob("*.pdf")

    count_pdf_files = len(pdf_files)

    for pdf_file in pdf_files:
        convert_from_path(pdf_file, dpi, output_folder=files_dir["files_dir"], fmt='jpg')
        os.remove(pdf_file)

    return count_pdf_files


def read_files():
    global total_files
    global recognized_files

    os.chdir(files_dir["files_dir"])
    orders = glob.glob("*.jpg")
    total_files = len(orders)

    for jpg_file in orders:
        logging.info(jpg_file)

        barcode_data = read_qr(jpg_file)

        if barcode_data == "NULL":
            barcode_data = enhance_img(jpg_file)

        if barcode_data == "NULL":
            logging.info(jpg_file + "barcode wasn't recognized!")
        else:
            recognized_files += 1
            send_barcode(jpg_file, barcode_data)

    return total_files


if __name__ == "__main__":
    logging.basicConfig(filename='barcodes.log', level=logging.INFO, format='%(levelname)-8s [%(asctime)s] %(message)s')
    logging.info('start reading.')

    total_files = 0

    count_pdf_files = pdf_to_jpg()
    if count_pdf_files > 0:
        total_files = read_files()

    logging.info('total files: ' + str(total_files))
    logging.info('recognized files: ' + str(recognized_files))

    if total_files > 0:
        logging.info("percent : " + str(round(recognized_files * 100 / total_files, 2)))
        payload = {'role': 'Ответственный за загрузку заказов КиС',
                   'user': '',
                   'total_files': total_files,
                   'recognized_files': recognized_files}
        r = requests.get(nu_address["nu_address"], params=payload)
    logging.info('done reading.')
