from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='en', use_gpu=False)
img_path = r"C:\Users\KRUNAL\OneDrive\Pictures\Camera imports\2024-08-22 (2)\1000015730.jpg"
result = ocr.ocr(img_path, cls=True)

print(result)

