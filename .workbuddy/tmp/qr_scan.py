import cv2
import numpy as np
import os
import glob

SRC_DIR = r"D:\Coding\lurenjia_mianshi\小红书公众号二维码及商品图片"
OUT_DIR = r"D:\Coding\lurenjia_mianshi\assets\img"
os.makedirs(OUT_DIR, exist_ok=True)

detector = cv2.QRCodeDetector()

for path in sorted(glob.glob(os.path.join(SRC_DIR, "*.jpg"))):
    name = os.path.basename(path)
    img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print(f"[SKIP] {name}: cannot read")
        continue
    h, w = img.shape[:2]
    data, points, _ = detector.detectAndDecode(img)
    if points is not None:
        pts = points[0].astype(int)
        x1, y1 = pts.min(axis=0)
        x2, y2 = pts.max(axis=0)
        print(f"[QR] {name} ({w}x{h}) -> bbox=({x1},{y1})-({x2},{y2}) data={data[:80]!r}")
    else:
        # try multi detection
        retval, decoded, pts2, _ = detector.detectAndDecodeMulti(img)
        if retval and pts2 is not None:
            for d, p in zip(decoded, pts2):
                p = p.astype(int)
                x1, y1 = p.min(axis=0)
                x2, y2 = p.max(axis=0)
                print(f"[QR-MULTI] {name} ({w}x{h}) -> bbox=({x1},{y1})-({x2},{y2}) data={str(d)[:80]!r}")
        else:
            print(f"[NO-QR] {name} ({w}x{h})")
