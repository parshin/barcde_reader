# -*- coding: utf-8 -*-

import qrtools
import glob
from pyzbar import pyzbar
import cv2
import os
import zxing
from pdf2image import convert_from_path

recognized_files = 0

qrtools_recognized = 0
pyzbar_recognized = 0
zxing_recognized = 0


def read_qrtools(jpgfile):
    global qrtools_recognized
    result = "NULL"
    qr = qrtools.QR()
    qr.decode(jpgfile)
    result = qr.data
    if result != "NULL":
        qrtools_recognized += 1
    return result


def read_pyzbar(jpgfile):
    global pyzbar_recognized
    result = "NULL"
    im = cv2.imread(jpgfile)
    barcodes = pyzbar.decode(im)
    for barcode in barcodes:
        result = barcode.data
        pyzbar_recognized += 1

    return result

def read_zxing(jpgfile):
    global zxing_recognized
    result = "NULL"
    reader = zxing.BarCodeReader("/home/parshin/PycharmProjects/barcode_reader/zxing")
    result = reader.decode(jpgfile)
    if result is not None:
        zxing_recognized += 1
        return result.data
    else:
        return "NULL"


if __name__ == "__main__":

    pdf_files = glob.glob("./pdf/*.pdf")
    for pdf_file in pdf_files:
        convert_from_path(pdf_file, 100, output_folder="./jpg", fmt='jpg')

    os.chdir("./jpg")
    orders = glob.glob("*.jpg")
    total_files = len(orders)

    for jpgfile in orders:

        barcode_data = read_qrtools(jpgfile)

        if barcode_data == "NULL":
            barcode_data = read_pyzbar(jpgfile)

        if barcode_data == "NULL":
            barcode_data = read_zxing(jpgfile)

        if barcode_data == "NULL":
            print(jpgfile, "barcode wasn't recognized!")
        else:
            recognized_files += 1
            print(jpgfile, barcode_data)
            os.remove(jpgfile)

    print('total files: ' + str(total_files))
    print('recognized files: ' + str(recognized_files))
    print("qrtools recognized: " + str(qrtools_recognized))
    print("pyzbar recognized: " + str(pyzbar_recognized))
    print("zxing recognized: " + str(zxing_recognized))
    if total_files > 0:
        print("percent : " + str(round(recognized_files*100/total_files, 2)))

