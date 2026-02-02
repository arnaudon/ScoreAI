from PIL import Image
import numpy as np
from pdf2image import convert_from_path

pdf_path = "test.pdf"
images = convert_from_path(pdf_path, dpi=200)
image = images[1]
# reader = easyocr.Reader(["de"])
# res = reader.readtext(image, detail=0)
# print(res)

from surya.foundation import FoundationPredictor
from surya.recognition import RecognitionPredictor
from surya.detection import DetectionPredictor

# image = Image.open(IMAGE_PATH)
foundation_predictor = FoundationPredictor()
recognition_predictor = RecognitionPredictor(foundation_predictor)
detection_predictor = DetectionPredictor()

predictions = recognition_predictor([image], det_predictor=detection_predictor)
print(predictions)
