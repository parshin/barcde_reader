# -*- coding: utf-8 -*-

import qrtools
import glob
# from pyzbar import pyzbar
# import cv2
import logging
import requests
from conf import ws_addr
from conf import nu_addr
import json
from base64 import b64encode
import os
from pdf2image import convert_from_path
import shutil
from PIL import Image, ImageEnhance

total_files = 0
recognized_files = 0
# qrtools_recognized = 0
# pyzbar_recognized = 0


def read_qrtools(jpgfile):
    # global qrtools_recognized
    # result = "NULL"
    qr = qrtools.QR()
    qr.decode(jpgfile)
    return qr.data
    # if result != "NULL":
    #     qrtools_recognized += 1

    # return result


# def read_pyzbar(jpgfile):
#     global pyzbar_recognized
#     result = "NULL"
#     im = cv2.imread(jpgfile)
#     barcodes = pyzbar.decode(im)
#     for barcode in barcodes:
#         result = barcode.data
#         pyzbar_recognized += 1
#
#     return result


def send_barcode(jpg_file, barcode_data):
    logging.info('sending file to service.')
    with open(jpg_file, 'rb') as f:
        base64_bytes = b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
        r = requests.post(ws_addr["ws_address"], data=json.dumps({"barcode": barcode_data, "file": base64_string}))
        logging.info('service response: ' + str(r))
        # noinspection PyBroadException
        try:
            response = r.json()
            if response["result"]:
                os.remove(jpg_file)
                # shutil.move(jpg_file, "/home/parshin/PycharmProjects/barcode_reader/done/"+jpg_file)
                logging.info('deleted recognized file')
            else:
                logging.info('file not_recognized: ' + jpg_file)
        except Exception:
            logging.error('response is not json: ' + str(r))



def pdf_to_jpg(dpi=100):
    os.chdir("/home/parshin/PycharmProjects/barcode_reader/pdf")
    pdf_files = glob.glob("*.pdf")

    for pdf_file in pdf_files:
        convert_from_path(pdf_file, dpi, output_folder="/home/parshin/PycharmProjects/barcode_reader/jpg/", fmt='jpg')


def enhance_img(jpg_file):
    image = Image.open(jpg_file)

    w, h = image.size
    left, top, right, bottom = 0, 0, w, 150
    image = image.crop((left, top, right, bottom))

    image = ImageEnhance.Contrast(image)
    image = image.enhance(3)

    image.save("/home/parshin/PycharmProjects/barcode_reader/cropped/"+jpg_file)

    barcode_data = read_qrtools("/home/parshin/PycharmProjects/barcode_reader/cropped/"+jpg_file)

    if barcode_data == "NULL":
        image = ImageEnhance.Sharpness(image)
        image = image.enhance(0)
        image.save("/home/parshin/PycharmProjects/barcode_reader/cropped/" + jpg_file)

    barcode_data = read_qrtools("/home/parshin/PycharmProjects/barcode_reader/cropped/" + jpg_file)

    os.remove("/home/parshin/PycharmProjects/barcode_reader/cropped/"+jpg_file)
    return barcode_data


def read_files():
    global total_files
    global recognized_files

    os.chdir("/home/parshin/PycharmProjects/barcode_reader/jpg/")
    orders = glob.glob("*.jpg")
    total_files = len(orders)

    for jpg_file in orders:
        logging.info(jpg_file)
        barcode_data = "NULL"

        barcode_data = read_qrtools(jpg_file)

        # if barcode_data == "NULL":
        #     barcode_data = read_pyzbar(jpgfile)

        if barcode_data == "NULL":
            barcode_data = enhance_img(jpg_file)

        if barcode_data == "NULL":
            logging.info("barcode wasn't recognized!")
        else:
            recognized_files += 1
            logging.info("barcode data: " + barcode_data)
            send_barcode(jpg_file, barcode_data)


if __name__ == "__main__":
    logging.basicConfig(filename='barcodes.log', level=logging.INFO, format='%(levelname)-8s [%(asctime)s] %(message)s')
    logging.info('start reading.')

    pdf_to_jpg()
    read_files()

    logging.info('total files: ' + str(total_files))
    logging.info('recognized files: ' + str(recognized_files))

    if total_files > 0:
        logging.info("percent : " + str(round(recognized_files * 100 / total_files, 2)))
        payload = {'role': 'Ответственный за загрузку заказов КиС',
                   'user': '',
                   'total_files': total_files,
                   'recognized_files': recognized_files}
        r = requests.get(nu_addr["nu_address"], params=payload)
    logging.info('done reading.')
