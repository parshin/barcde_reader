import zxing
import os
import glob
import sys

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/home/parshin/PycharmProjects/barcode_reader'])
os.chdir("./jpg")
reader = zxing.BarCodeReader("/home/parshin/PycharmProjects/barcode_reader/zxing")
files = glob.glob("*.jpg")
total_files = len(files)
recognized_files = 0

for img_file in files:
    result = reader.decode(img_file)
    if result is not None:
        recognized_files += 1
        print(img_file, result.data)
    else:
        print(img_file)


print(total_files, recognized_files)
