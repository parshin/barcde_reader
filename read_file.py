# -*- coding: utf-8 -*-

import qrtools
import glob
import os
from pyzbar import pyzbar
import cv2
import logging
import requests


def read_files():

    os.chdir("./")
    orders = glob.glob("*.jpg")
    logging.info('total files: ' + str(len(orders)))

    total_recognized = 0
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
            total_recognized += 1
            logging.info("barcode data: " + barcode_data)


    logging.info('recognized files: ' + str(total_recognized))
    logging.info("qrtools recognized: " + str(qrtools_recognized))
    logging.info("pyzbar recognized: " + str(pyzbar_recognized))


if __name__ == "__main__":
    logging.basicConfig(filename='barcodes.log', level=logging.INFO, format='%(levelname)-8s [%(asctime)s] %(message)s')
    logging.info('start reading.')
    read_files()
    logging.info('done reading.')

