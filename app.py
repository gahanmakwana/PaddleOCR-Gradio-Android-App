import gradio as gr
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image
import numpy as np
import os
from gtts import gTTS # Import gTTS

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
REC_CHAR_DICT_FILENAME = 'en_dict.txt' # Or whatever your .txt file is named
REC_CHAR_DICT_PATH_DEFAULT = os.path.join(REC_MODEL_DIR_DEFAULT, REC_CHAR_DICT_FILENAME)

# --- Font for drawing OCR results ---
FONT_PATH = 'latin.ttf' # Ensure 'latin.ttf' (e.g., DejaVuSans.ttf renamed) is in your project root.
if not os.path.exists(FONT_PATH):
    print(f"WARNING: Font file '{FONT_PATH}' not found. Text rendering on images might fail or look incorrect.")

# --- Directory for TTS output ---
TTS_OUTPUT_DIR = "tts_outputs"
if not os.path.exists(TTS_OUTPUT_DIR):
    os.makedirs(TTS_OUTPUT_DIR)

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
    Processes the uploaded image with PaddleOCR using the pre-loaded models,
    and generates TTS for the extracted text.
    """
    if ocr_engine is None:
        return None, "PaddleOCR engine is not available. Please check the application logs for errors.", None
    if image_pil is None:
        return None, "No image provided. Please upload an image.", None

    print(f"Processing with pre-loaded language: {SELECTED_LANGUAGE}")
    
    # Default audio path for errors or no text
    audio_output_path = None

    try:
        img_np = np.array(image_pil.convert('RGB')) # Ensure image is RGB

        print("Performing OCR...")
        result = ocr_engine.ocr(img_np, cls=ocr_engine.use_angle_cls) 
        print("OCR processing complete.")

        if result is None or not result[0]: 
            print("No text detected.")
            return image_pil, "No text detected.", None

        lines = result[0]
        boxes = [line[0] for line in lines]
        txts = [line[1][0] for line in lines]
        scores = [line[1][1] for line in lines]

        print("Drawing OCR results...")
        if not os.path.exists(FONT_PATH):
            print(f"Font file '{FONT_PATH}' still not found. Cannot draw results on image.")
            extracted_text_raw = "\n".join(txts)
            # Generate TTS even if font is missing for drawing
            if extracted_text_raw.strip():
                try:
                    tts = gTTS(text=extracted_text_raw, lang=SELECTED_LANGUAGE)
                    # Use a unique filename to avoid conflicts if multiple users access
                    audio_filename = f"output_{hash(extracted_text_raw)}.mp3"
                    audio_output_path = os.path.join(TTS_OUTPUT_DIR, audio_filename)
                    tts.save(audio_output_path)
                    print(f"TTS generated: {audio_output_path}")
                except Exception as tts_e:
                    print(f"Error during TTS generation: {tts_e}")
                    audio_output_path = None # Reset on error
            return image_pil, f"Font file missing. Extracted text (raw):\n{extracted_text_raw}", audio_output_path

        im_show = draw_ocr(image_pil, boxes, txts, scores, font_path=FONT_PATH)
        im_show_pil = Image.fromarray(im_show) 
        print("OCR results drawn.")

        extracted_text = "\n".join(txts)

        # --- Text-to-Speech Generation ---
        if extracted_text.strip(): # Only generate TTS if there's text
            print("Generating TTS...")
            try:
                tts = gTTS(text=extracted_text, lang=SELECTED_LANGUAGE)
                # Using a simple naming, consider more robust naming for production/concurrent users
                audio_filename = f"output_{hash(extracted_text)}.mp3" # simple unique name
                audio_output_path = os.path.join(TTS_OUTPUT_DIR, audio_filename)
                tts.save(audio_output_path)
                print(f"TTS generated and saved to: {audio_output_path}")
            except AssertionError as ae: # Handles empty string for gTTS if strip() fails
                 print(f"TTS generation skipped: Text was empty or whitespace. Error: {ae}")
                 extracted_text += "\n(TTS skipped: No valid text to speak)"
                 audio_output_path = None
            except Exception as tts_e:
                print(f"Error during TTS generation: {tts_e}")
                extracted_text += f"\n(TTS generation failed: {tts_e})" # Append error to text output
                audio_output_path = None # Ensure no audio path if TTS fails
        else:
            print("No text extracted for TTS.")
            extracted_text = "No text detected for TTS." # Update message if needed
            audio_output_path = None

        return im_show_pil, extracted_text, audio_output_path

    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return image_pil, f"An error occurred during OCR: {str(e)}", None

# --- Gradio Interface Definition ---
title = "PaddleOCR Web App with TTS (Bundled Models)"
description = f"""
Upload an image to perform OCR and listen to the extracted text.
This app uses PaddleOCR with pre-bundled models for the **{SELECTED_LANGUAGE.upper()}** language.
Detection: `{DET_MODEL_FOLDER_NAME}`
Recognition: `{REC_MODEL_FOLDER_NAME}` (using `{REC_CHAR_DICT_FILENAME}`)
TTS is generated using gTTS.
Make sure the model files are correctly placed in the `paddleocr_models` directory
and the font file `{FONT_PATH}` is in the project root.
A `{TTS_OUTPUT_DIR}` folder will be created for audio files.
"""
article = "<p style='text-align: center'>Powered by PaddleOCR, gTTS, and Gradio. Deployed on Hugging Face Spaces.</p>"

supported_langs_display_for_dropdown = {
    "English (Loaded)": "en",
}

iface = gr.Interface(
    fn=ocr_process,
    inputs=[
        gr.Image(type="pil", label="Upload Image"),
        gr.Dropdown(
            choices=list(supported_langs_display_for_dropdown.keys()),
            label="Language (Using Pre-loaded Model)",
            value=[k for k, v in supported_langs_display_for_dropdown.items() if v == SELECTED_LANGUAGE][0]
        )
    ],
    outputs=[
        gr.Image(type="pil", label="Processed Image with OCR"),
        gr.Textbox(label="Extracted Text", lines=10, show_copy_button=True),
        gr.Audio(label="Listen to Extracted Text", type="filepath") # Added Audio output
    ],
    title=title,
    description=description,
    article=article,
    allow_flagging='never',
)

if __name__ == '__main__':
    if ocr_engine is None:
        print("OCR Engine could not be initialized. The Gradio app will not function correctly.")
    print("Launching Gradio interface...")
    iface.launch() 
    print("Gradio interface launched.")