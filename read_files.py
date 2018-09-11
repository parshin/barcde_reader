# -*- coding: utf-8 -*-

import qrtools
import glob
from pyzbar import pyzbar
import cv2
import logging
import requests
from conf import ws_addr
from conf import nu_addr
import json
from base64 import b64encode
import os
from pdf2image import convert_from_path

total_files = 0
recognized_files = 0


def send_barcode(jpg_file, barcode_data):
    logging.info('sending file to service.')
    with open(jpg_file, 'rb') as f:
        base64_bytes = b64encode(f.read())
        base64_string = base64_bytes.decode('utf-8')
        r = requests.post(ws_addr["ws_address"], data=json.dumps({'barcode': barcode_data, 'file': base64_string}))
        logging.info('service response: ' + str(r))
        response = r.json()
        if response['result']:
            os.remove(jpg_file)
            logging.info('deleted recognized file')
        else:
            logging.info('file not_recognized: ' + jpg_file)


def pdf_to_jpg():
    os.chdir("./")
    pdf_files = glob.glob("*.pdf")

    for pdf_file in pdf_files:
        convert_from_path(pdf_file, 200, output_folder="./", fmt='jpg')


def read_files():
    global total_files
    global recognized_files

    os.chdir("./")
    orders = glob.glob("*.jpg")
    total_files = len(orders)
    logging.info('total files: ' + str(total_files))

    qrtools_recognized = 0
    pyzbar_recognized = 0

    for jpgfile in orders:
        logging.info(jpgfile)
        barcode_data = "NULL"

        qr = qrtools.QR()
        qr.decode(jpgfile)
        barcode_data = qr.data

        if barcode_data == "NULL":
            im = cv2.imread(jpgfile)
            barcodes = pyzbar.decode(im)
            for barcode in barcodes:
                barcode_data = barcode.data
                pyzbar_recognized += 1
        else:
            qrtools_recognized += 1

        if barcode_data == "NULL":
            logging.info("barcode wasn't recognized!")
        else:
            recognized_files += 1
            logging.info("barcode data: " + barcode_data)
            send_barcode(jpgfile, barcode_data)

    logging.info('recognized files: ' + str(recognized_files))
    logging.info("qrtools recognized: " + str(qrtools_recognized))
    logging.info("pyzbar recognized: " + str(pyzbar_recognized))


if __name__ == "__main__":
    logging.basicConfig(filename='barcodes.log', level=logging.INFO, format='%(levelname)-8s [%(asctime)s] %(message)s')
    logging.info('start reading.')
    pdf_to_jpg()
    read_files()
    if total_files > 0:
        payload = {'role': 'Ответственный за загрузку заказов КиС',
                   'user': '',
                   'total_files': total_files,
                   'recognized_files': recognized_files}
        r = requests.get(nu_addr["nu_address"], params=payload)
    logging.info('done reading.')
