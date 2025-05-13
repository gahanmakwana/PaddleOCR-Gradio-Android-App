import gradio as gr
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import numpy as np
import os

# --- Configuration: Model and Font Paths ---
# IMPORTANT: Ensure these paths and folder names match exactly what you have
# in your 'paddleocr_models' directory.

# Define the language
SELECTED_LANGUAGE = 'en' # This informs which dictionary to look for primarily

# Base directory for your bundled models
MODEL_BASE_DIR = 'paddleocr_models'

# --- Model paths based on your logs ---
# Detection model: en_PP-OCRv3_det_infer
DET_MODEL_FOLDER_NAME = 'en_PP-OCRv3_det_infer'
DET_MODEL_DIR_DEFAULT = os.path.join(MODEL_BASE_DIR, DET_MODEL_FOLDER_NAME)

# Recognition model: en_PP-OCRv4_rec_infer
REC_MODEL_FOLDER_NAME = 'en_PP-OCRv4_rec_infer'
REC_MODEL_DIR_DEFAULT = os.path.join(MODEL_BASE_DIR, REC_MODEL_FOLDER_NAME)

# Classification model: ch_ppocr_mobile_v2.0_cls_infer (often shared)
CLS_MODEL_FOLDER_NAME = 'ch_ppocr_mobile_v2.0_cls_infer'
CLS_MODEL_DIR_DEFAULT = os.path.join(MODEL_BASE_DIR, CLS_MODEL_FOLDER_NAME)

# --- Character Dictionary Path ---
# Since en_dict.txt might not be directly in the rec_model_dir after copying from cache,
# we assume you've copied the default en_dict.txt into your REC_MODEL_FOLDER_NAME.
# If you copied it from the PaddleOCR package utils, this path should be correct.
# Ensure 'en_dict.txt' is inside 'paddleocr_models/en_PP-OCRv4_rec_infer/'
REC_CHAR_DICT_FILENAME = 'en_dict.txt' # Or whatever your .txt file is named
REC_CHAR_DICT_PATH_DEFAULT = os.path.join(REC_MODEL_DIR_DEFAULT, REC_CHAR_DICT_FILENAME)

# --- Font for drawing OCR results ---
FONT_PATH = 'latin.ttf' # Ensure 'latin.ttf' (e.g., DejaVuSans.ttf renamed) is in your project root.
if not os.path.exists(FONT_PATH):
    print(f"WARNING: Font file '{FONT_PATH}' not found. Text rendering on images might fail or look incorrect.")

# --- Initialize PaddleOCR Engine ---
ocr_engine = None
try:
    # Check if essential model directories exist
    if not os.path.exists(DET_MODEL_DIR_DEFAULT):
        raise FileNotFoundError(f"Detection model directory not found: '{DET_MODEL_DIR_DEFAULT}'. Please ensure it exists and contains model files.")
    if not os.path.exists(REC_MODEL_DIR_DEFAULT):
        raise FileNotFoundError(f"Recognition model directory not found: '{REC_MODEL_DIR_DEFAULT}'. Please ensure it exists and contains model files.")
    
    # Check if the character dictionary file exists
    if not os.path.exists(REC_CHAR_DICT_PATH_DEFAULT):
        raise FileNotFoundError(f"Recognition character dictionary not found: '{REC_CHAR_DICT_PATH_DEFAULT}'. Please ensure it's in the recognition model folder.")

    print(f"Initializing PaddleOCR with language: {SELECTED_LANGUAGE}")
    print(f"  Detection Model Dir: {DET_MODEL_DIR_DEFAULT}")
    print(f"  Recognition Model Dir: {REC_MODEL_DIR_DEFAULT}")
    print(f"  Recognition Char Dict Path: {REC_CHAR_DICT_PATH_DEFAULT}")
    
    use_cls = os.path.exists(CLS_MODEL_DIR_DEFAULT)
    if use_cls:
        print(f"  Classification Model Dir: {CLS_MODEL_DIR_DEFAULT}")
    else:
        print(f"  Classification Model: Not found at '{CLS_MODEL_DIR_DEFAULT}' or not used.")

    ocr_engine = PaddleOCR(
        use_angle_cls=use_cls,
        lang=SELECTED_LANGUAGE, # Still useful for some internal logic, but dict path is key
        det_model_dir=DET_MODEL_DIR_DEFAULT,
        rec_model_dir=REC_MODEL_DIR_DEFAULT,
        rec_char_dict_path=REC_CHAR_DICT_PATH_DEFAULT, # Explicitly providing the dictionary path
        cls_model_dir=CLS_MODEL_DIR_DEFAULT if use_cls else None,
        show_log=True, # Set to False for less verbose logs in production if desired
        use_gpu=False # Set to True if you have GPU hardware on Spaces and paddlepaddle-gpu
    )
    print("PaddleOCR engine initialized successfully from local models.")

except FileNotFoundError as fnf_error:
    print(f"FATAL ERROR (FileNotFound): {fnf_error}")
    print("Please check your 'paddleocr_models' directory and model/dict file paths in app.py.")
    ocr_engine = None
except Exception as e:
    print(f"FATAL ERROR: Could not initialize PaddleOCR engine: {e}")
    ocr_engine = None # Ensure it's None if initialization fails

def ocr_process(image_pil, language_key_display_name):
    """
    Processes the uploaded image with PaddleOCR using the pre-loaded models.
    """
    if ocr_engine is None:
        # This message will be displayed to the user in the Gradio interface
        return None, "PaddleOCR engine is not available. Please check the application logs for errors."
    if image_pil is None:
        return None, "No image provided. Please upload an image."

    print(f"Processing with pre-loaded language: {SELECTED_LANGUAGE}")

    try:
        img_np = np.array(image_pil.convert('RGB')) # Ensure image is RGB

        print("Performing OCR...")
        # The `ocr` method automatically uses the det, cls (if enabled), and rec models.
        result = ocr_engine.ocr(img_np, cls=ocr_engine.use_angle_cls) 
        print("OCR processing complete.")

        # PaddleOCR v2.6+ returns results in a different structure: result = [[box, (text, score)], ...]
        # Check if result is not None and the first element (lines) is not empty
        if result is None or not result[0]: 
            print("No text detected.")
            return image_pil, "No text detected." 

        # Correctly extract boxes, texts, and scores from the result structure
        # result[0] contains the list of lines, where each line is [box, (text, score)]
        lines = result[0]
        boxes = [line[0] for line in lines]
        txts = [line[1][0] for line in lines]
        scores = [line[1][1] for line in lines]

        print("Drawing OCR results...")
        if not os.path.exists(FONT_PATH):
            print(f"Font file '{FONT_PATH}' still not found. Cannot draw results on image.")
            # Return original image and extracted text without drawn boxes
            extracted_text_raw = "\n".join(txts)
            return image_pil, f"Font file missing. Extracted text (raw):\n{extracted_text_raw}"

        # draw_ocr expects the image in a format it can handle (PIL Image is fine)
        im_show = draw_ocr(image_pil, boxes, txts, scores, font_path=FONT_PATH)
        im_show_pil = Image.fromarray(im_show) # Convert numpy array from draw_ocr back to PIL Image
        print("OCR results drawn.")

        extracted_text = "\n".join(txts)
        return im_show_pil, extracted_text

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        # Return original image and error message
        return image_pil, f"An error occurred during OCR: {str(e)}"

# --- Gradio Interface Definition ---
title = "PaddleOCR Web App (Bundled Models)"
description = f"""
Upload an image to perform OCR. This app uses PaddleOCR with pre-bundled models
for the **{SELECTED_LANGUAGE.upper()}** language to avoid re-downloads on Hugging Face Spaces.
Detection: `{DET_MODEL_FOLDER_NAME}`
Recognition: `{REC_MODEL_FOLDER_NAME}` (using `{REC_CHAR_DICT_FILENAME}`)
Make sure the model files are correctly placed in the `paddleocr_models` directory
and the font file `{FONT_PATH}` is in the project root.
"""
article = "<p style='text-align: center'>Powered by PaddleOCR and Gradio. Deployed on Hugging Face Spaces.</p>"

# For this setup, the language dropdown is mainly informational as models are pre-loaded.
# To truly switch languages, ocr_engine would need re-initialization with different model/dict paths.
supported_langs_display_for_dropdown = {
    "English (Loaded)": "en",
    # "Chinese (Not Loaded)": "ch", # Example if you were to add more
}

iface = gr.Interface(
    fn=ocr_process,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Dropdown(
            choices=list(supported_langs_display_for_dropdown.keys()),
            label="Language (Using Pre-loaded Model)",
            # Default to the key corresponding to SELECTED_LANGUAGE
            value=[k for k, v in supported_langs_display_for_dropdown.items() if v == SELECTED_LANGUAGE][0]
        )
    ],
    outputs=[
        gr.Image(type="pil", label="Processed Image with OCR"),
        gr.Textbox(label="Extracted Text", lines=10, show_copy_button=True)
    ],
    title=title,
    description=description,
    article=article,
    allow_flagging='never', # Disables the "Flag" button
    # You can add example images to your repository and list them here
    # examples=[
    #     ["path_to_your_example_image_in_repo.png", "English (Loaded)"] 
    # ]
)

if __name__ == '__main__':
    if ocr_engine is None:
        print("OCR Engine could not be initialized. The Gradio app will not function correctly.")
        # In a real scenario, you might want to display an error in the Gradio UI itself
        # by modifying the interface or raising an error that Gradio can catch.
    print("Launching Gradio interface...")
    iface.launch() 
    print("Gradio interface launched.")
