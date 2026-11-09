"""画面写真が PDF の中で元々どれだけ細かいか(1ポイントあたりの画素数)を調べる"""
import fitz, sys, statistics
doc = fitz.open(sys.argv[1])
ratios = []
for pno in [48, 196, 300, 640, 660]:
    page = doc[pno]
    for info in page.get_image_info():
        r = fitz.Rect(info['bbox'])
        if r.width < 40:
            continue
        ratio = info['width'] / r.width
        ratios.append(ratio)
        print(pno + 1, 'native', info['width'], 'x', info['height'], 'shown', round(r.width), 'pt', 'ratio', round(ratio, 2))
print('median ratio', round(statistics.median(ratios), 2))
