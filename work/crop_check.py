"""画像の左上を切り出して確認用に保存"""
import sys
from PIL import Image
im = Image.open(sys.argv[1])
im.crop((0, 0, int(sys.argv[3]), int(sys.argv[4]))).save(sys.argv[2])
