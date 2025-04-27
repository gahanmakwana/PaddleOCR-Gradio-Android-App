import os
from flask import Flask, request, jsonify
from paddleocr import PaddleOCR

app = Flask(__name__)

# Global variable to hold the OCR instance
ocr = None

# Function to initialize the OCR model
def get_ocr():
    global ocr
    if ocr is None:
        # Ensure the /tmp/ocr_models directory exists
        os.makedirs('/tmp/ocr_models', exist_ok=True)

        # Initialize the OCR model
        ocr = PaddleOCR(
            use_angle_cls=False,
            use_gpu=False,
            lang='en',
            det_model_dir='/tmp/ocr_models/det',
            rec_model_dir='/tmp/ocr_models/rec',
            cls_model_dir='/tmp/ocr_models/cls'
        )
    return ocr

@app.route('/')
def home():
    return "OCR App is running!"

@app.route('/extract-text', methods=['POST'])
def extract_text():
    # Get OCR model
    ocr_model = get_ocr()

    # Get the image file from the request
    image_file = request.files.get('image')
    if image_file:
        # Perform OCR on the uploaded image
        result = ocr_model.ocr(image_file, cls=False)

        # Extract text from OCR result
        text = '\n'.join([line[1][0] for line in result[0]])

        return jsonify({"extracted_text": text})

    return jsonify({"error": "No image uploaded!"}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=False)
