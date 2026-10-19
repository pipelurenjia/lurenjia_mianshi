import cv2
import numpy as np

detector = cv2.QRCodeDetector()

def imread_cn(p):
    return cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)

cases = [
    ("xhs-orig", r"D:\Coding\lurenjia_mianshi\小红书公众号二维码及商品图片\微信图片_20261019132626_4_7.jpg", (690, 1050, 908, 1249)),
    ("wechat-orig", r"D:\Coding\lurenjia_mianshi\小红书公众号二维码及商品图片\微信图片_20261019143549_86_4.jpg", (155, 387, 686, 906)),
]

for name, path, (x1, y1, x2, y2) in cases:
    img = imread_cn(path)
    crop = img[max(0, y1-10):y2+10, max(0, x1-10):x2+10]
    h, w = crop.shape[:2]
    print(f"{name} native crop {w}x{h}")
    # try decoder with various scales
    best = ""
    for scale in (1, 2, 3, 4):
        c = cv2.resize(crop, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        gray = cv2.cvtColor(c, cv2.COLOR_BGR2GRAY)
        d, pts, _ = detector.detectAndDecode(gray)
        print(f"  scale{scale}: detected={pts is not None} data={d!r}")
        if d:
            best = d
            break
        if scale == 4 and not d:
            # also try inverted / sharpened
            blur = cv2.GaussianBlur(gray, (0, 0), 3)
            sharp = cv2.addWeighted(gray, 1.5, blur, -0.5, 0)
            d2, _, _ = detector.detectAndDecode(sharp)
            print(f"  scale4-sharp: data={d2!r}")
            if d2:
                best = d2
    print(f"  RESULT: {best or 'NO DECODE (possible center logo)'}\n")
