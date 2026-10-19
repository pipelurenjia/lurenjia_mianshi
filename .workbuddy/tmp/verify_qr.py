import cv2
import numpy as np

detector = cv2.QRCodeDetector()
paths = {
    "xhs-qr": r"D:\Coding\lurenjia_mianshi\assets\img\xhs-qr.png",
    "wechat-qr": r"D:\Coding\lurenjia_mianshi\assets\img\wechat-qr.png",
}

def try_decode(img):
    variants = []
    variants.append(("raw", img))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variants.append(("gray", gray))
    _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(("otsu", th))
    up = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    _, th2 = cv2.threshold(up, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    variants.append(("2x-otsu", th2))
    for name, v in variants:
        data, pts, _ = detector.detectAndDecode(v)
        if pts is not None:
            print(f"   [{name}] detected, decoded={data!r}")
            if data:
                return data
        else:
            print(f"   [{name}] no detection")
    # multi
    ok, decoded, pts, _ = detector.detectAndDecodeMulti(gray)
    if ok and pts is not None:
        print(f"   [multi] {decoded!r}")
        return ",".join([d for d in decoded if d])
    return ""

for k, p in paths.items():
    img = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)
    h, w = img.shape[:2]
    print(f"{k} ({w}x{h}):")
    d = try_decode(img)
    print(f"   => result: {d or 'DECODE FAILED'}")
