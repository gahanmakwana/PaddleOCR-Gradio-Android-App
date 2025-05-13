# download_ocr_models.py (Corrected v3)
from paddleocr import PaddleOCR
import os
import shutil # For copying files/folders later if you want to automate it

# --- CONFIGURATION ---
# 1. CHOOSE THE LANGUAGE YOU WANT TO DOWNLOAD MODELS FOR:
LANGUAGE_TO_DOWNLOAD = 'en'  # <<< ***** CHANGE THIS TO YOUR TARGET LANGUAGE *****
# --- END CONFIGURATION ---

print(f"Attempting to download/locate models for language: '{LANGUAGE_TO_DOWNLOAD}'...")

try:
    # Initialize PaddleOCR. This action will trigger the download of models
    # for the specified language if they are not already in the local cache.
    ocr_temp_engine = PaddleOCR(use_angle_cls=True, lang=LANGUAGE_TO_DOWNLOAD, show_log=True)
    print(f"\nModels for '{LANGUAGE_TO_DOWNLOAD}' should now be in the PaddleOCR cache.")

    # --- Accessing the model paths from the initialized engine ---
    # The args object is an argparse.Namespace, access attributes directly.
    
    args = ocr_temp_engine.args # This is an argparse.Namespace object

    # Use hasattr to check if attributes exist before accessing them
    det_model_dir_cache = args.det_model_dir if hasattr(args, 'det_model_dir') else None
    rec_model_dir_cache = args.rec_model_dir if hasattr(args, 'rec_model_dir') else None
    cls_model_dir_cache = args.cls_model_dir if hasattr(args, 'use_angle_cls') and args.use_angle_cls and hasattr(args, 'cls_model_dir') else None
    rec_char_dict_path_from_args = args.rec_char_dict_path if hasattr(args, 'rec_char_dict_path') else None


    print("\n--- CACHE PATHS FOR THE DOWNLOADED MODELS (from PaddleOCR config) ---")
    if det_model_dir_cache:
        print(f"Detection ({LANGUAGE_TO_DOWNLOAD}) model cache path: {det_model_dir_cache}")
    else:
        print(f"Detection ({LANGUAGE_TO_DOWNLOAD}) model cache path: Not found in args (Attribute 'det_model_dir' missing).")
    
    if rec_model_dir_cache:
        print(f"Recognition ({LANGUAGE_TO_DOWNLOAD}) model cache path: {rec_model_dir_cache}")
    else:
        print(f"Recognition ({LANGUAGE_TO_DOWNLOAD}) model cache path: Not found in args (Attribute 'rec_model_dir' missing).")

    if cls_model_dir_cache:
        print(f"Classification model cache path: {cls_model_dir_cache}")
    elif hasattr(args, 'use_angle_cls') and args.use_angle_cls:
        print("Classification model enabled but path not found in args (Attribute 'cls_model_dir' missing or invalid).")
    else:
        print("Classification model not used or path not found in args.")


    # --- Instructions for copying ---
    print("\n--- ACTION REQUIRED ---")
    print("1. Create a folder named 'paddleocr_models' in your project's root directory (if it doesn't exist).")
    
    project_root = os.getcwd() 
    project_model_dir_target = os.path.join(project_root, 'paddleocr_models')
    if not os.path.exists(project_model_dir_target):
        try:
            os.makedirs(project_model_dir_target)
            print(f"   Created directory: {project_model_dir_target}")
        except OSError as e:
            print(f"   ERROR creating directory {project_model_dir_target}: {e}")
            print("   Please create it manually.")
    else:
        print(f"   Your project's 'paddleocr_models' folder is at: {project_model_dir_target}")


    print(f"\n2. Manually copy the following folders from the cache paths printed above (or from PaddleOCR's initial debug log) into '{project_model_dir_target}':")

    # Detection model
    if det_model_dir_cache and os.path.exists(det_model_dir_cache):
        det_target_name = os.path.basename(os.path.normpath(det_model_dir_cache))
        print(f"   - Detection Model Folder to Copy: '{det_target_name}'")
        print(f"     (Full path of source: {det_model_dir_cache})")
        print(f"     (Target location: {os.path.join(project_model_dir_target, det_target_name)})")
    else:
        print(f"   - Detection model directory NOT FOUND or path is invalid based on script access: {det_model_dir_cache}")
        print(f"     IMPORTANT: Please check the initial PaddleOCR debug logs (the long block of text when PaddleOCR starts).")
        print(f"     Look for the line starting with 'det_model_dir=' and use THAT PATH to find the folder to copy manually.")


    # Recognition model
    if rec_model_dir_cache and os.path.exists(rec_model_dir_cache):
        rec_target_name = os.path.basename(os.path.normpath(rec_model_dir_cache))
        print(f"   - Recognition Model Folder to Copy: '{rec_target_name}'")
        print(f"     (Full path of source: {rec_model_dir_cache})")
        print(f"     (Target location: {os.path.join(project_model_dir_target, rec_target_name)})")
        
        if rec_char_dict_path_from_args and os.path.exists(rec_char_dict_path_from_args):
             print(f"     (Dictionary file used by PaddleOCR: '{os.path.basename(rec_char_dict_path_from_args)}' found at {rec_char_dict_path_from_args})")
             print(f"     (Ensure a similar .txt dictionary file, like '{os.path.basename(rec_char_dict_path_from_args)}', is inside the '{rec_target_name}' folder you copy)")
        else: 
            found_dicts = [f for f in os.listdir(rec_model_dir_cache) if f.endswith('.txt')]
            if found_dicts:
                print(f"     (Ensure dictionary file like '{found_dicts[0]}' is inside the '{rec_target_name}' folder you copy)")
            else:
                print(f"     WARNING: Dictionary file (e.g., '{LANGUAGE_TO_DOWNLOAD}_dict.txt') NOT FOUND in {rec_model_dir_cache}")
    else:
        print(f"   - Recognition model directory NOT FOUND or path is invalid based on script access: {rec_model_dir_cache}")
        print(f"     IMPORTANT: Please check the initial PaddleOCR debug logs.")
        print(f"     Look for the line starting with 'rec_model_dir=' and use THAT PATH to find the folder to copy manually.")


    # Classification model (optional)
    if cls_model_dir_cache and os.path.exists(cls_model_dir_cache):
        cls_target_name = os.path.basename(os.path.normpath(cls_model_dir_cache))
        print(f"   - Classification Model Folder to Copy (Optional): '{cls_target_name}'")
        print(f"     (Full path of source: {cls_model_dir_cache})")
        print(f"     (Target location: {os.path.join(project_model_dir_target, cls_target_name)})")

    elif hasattr(args, 'use_angle_cls') and args.use_angle_cls:
        print(f"   - Classification model directory NOT FOUND or path is invalid based on script access: {cls_model_dir_cache}")
        print(f"     IMPORTANT: Please check the initial PaddleOCR debug logs.")
        print(f"     Look for the line starting with 'cls_model_dir=' and use THAT PATH to find the folder to copy manually if needed.")


    print("\n3. After copying, your 'paddleocr_models' directory in your project should contain these model subfolders.")
    print("4. Verify paths in your main `app.py` match these folder names.")
    print("   For example, if your log showed 'en_PP-OCRv3_det_infer' for detection, app.py should use that name.")

except AttributeError as ae:
    print(f"An AttributeError occurred during script execution (not PaddleOCR init): {ae}")
    print("This might indicate an unexpected structure in the PaddleOCR object or its arguments when accessed by the script.")
    print("Please carefully review the FULL initial debug output from PaddleOCR when it initializes.")
    print("The lines starting with 'det_model_dir=', 'rec_model_dir=', 'cls_model_dir=' are key.")
    print("You can use those paths directly to find and copy the model folders manually.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    print("Please ensure PaddleOCR and PaddlePaddle are installed correctly.")

