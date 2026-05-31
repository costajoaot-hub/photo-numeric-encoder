import os
import random
import shutil
from urllib.parse import unquote
import pandas as pd

# =================================================================
# ENVIRONMENT CONFIGURATION (Relative paths for portability)
# =================================================================
ORIGINAL_EXCEL_PATH = os.getenv("EXCEL_PATH", "photography_contest_base.xlsx")
PHOTOS_INPUT_DIR = os.getenv("PHOTOS_INPUT_DIR", "01_raw_photos")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "02_encoded_photos")
NEW_EXCEL_NAME = "encoded_contest_database.xlsx"
# =================================================================

def run_photo_anonymizer_audit():
    """
    Audits photography submission data from Excel and anonymizes image files
    by renaming them with unique, non-repeating 3-digit numeric codes.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # Load spreadsheet
    try:
        df_raw = pd.read_excel(ORIGINAL_EXCEL_PATH)
    except FileNotFoundError:
        print(f"[ERROR] Excel file not found at: {ORIGINAL_EXCEL_PATH}")
        print("Please check your configuration or file location.")
        return

    # Dynamically find the submission column containing photo links
    photo_column = next((c for c in df_raw.columns if "Submeta" in str(c) and "Fotografias" in str(c)), None)
    
    if not photo_column:
        print("[ERROR] Could not automatically detect the target photo submission column.")
        return

    # Generate unique, non-repeating 3-digit numeric codes (111 to 999)
    possible_codes = list(range(111, 1000))
    random.shuffle(possible_codes)
    
    processed_rows = []
    
    # Scan local directory for available image files
    if os.path.exists(PHOTOS_INPUT_DIR):
        photos_in_folder = set(f for f in os.listdir(PHOTOS_INPUT_DIR) if os.path.isfile(os.path.join(PHOTOS_INPUT_DIR, f)))
    else:
        print(f"[ERROR] Input folder not found at: {PHOTOS_INPUT_DIR}")
        return

    used_photos = set()
    excel_matching_errors = []

    for index, row in df_raw.iterrows():
        cell_content = str(row[photo_column])
        if cell_content.lower() == 'nan' or not cell_content.strip(): 
            continue

        # Extract individual links from the submission cell
        links = [l.strip() for l in cell_content.split(';') if l.strip()]
        for link in links:
            # Decode URL-encoded characters (e.g., spaces, special characters)
            original_name = unquote(link.split('/')[-1].split('?')[0])
            
            success = False
            target_name = original_name
            
            # ATTEMPT 1: Direct exact match
            if target_name in photos_in_folder:
                success = True
            else:
                # ATTEMPT 2: Fallback logic for truncated filenames (checks first 20 characters)
                for real_file in photos_in_folder:
                    if real_file.startswith(target_name[:20]):
                        target_name = real_file
                        success = True
                        break
            
            if success:
                # Assign a unique anonymous code
                anonymous_code = possible_codes.pop()
                file_extension = os.path.splitext(target_name)[1]
                
                # Securely copy file while preserving original metadata timestamps
                shutil.copy2(
                    os.path.join(PHOTOS_INPUT_DIR, target_name), 
                    os.path.join(OUTPUT_DIR, f"{anonymous_code}{file_extension}")
                )
                
                # Append data to the new structured output
                new_row = row.to_dict()
                new_row['Original_Photo_Name'] = target_name
                new_row['Anonymous_Photo_Code'] = anonymous_code
                processed_rows.append(new_row)
                used_photos.add(target_name)
            else:
                excel_matching_errors.append(original_name)

    # Save audited and anonymized results to a new Excel file
    if processed_rows:
        pd.DataFrame(processed_rows).to_excel(os.path.join(OUTPUT_DIR, NEW_EXCEL_NAME), index=False)
    
    # =================================================================
    # AUDIT REPORT TERMINAL OUTPUT
    # =================================================================
    print("-" * 50)
    print("FINAL AUDIT SUMMARY REPORT")
    print("-" * 50)
    print(f"-> Total files detected in raw folder: {len(photos_in_folder)}")
    print(f"-> Successfully processed photos:      {len(processed_rows)}")
    print(f"-> Orphan files (In folder but missing from Excel): {len(photos_in_folder - used_photos)}")
    
    orphan_files = photos_in_folder - used_photos
    if orphan_files:
        print("\n[?] ORPHAN FILES DETECTED (No matching Excel record):")
        for file in orphan_files: 
            print(f"  [?] {file}")

    if excel_matching_errors:
        print("\n[!] EXCEL ERRORS DETECTED (Links present without matching physical files):")
        for error in set(excel_matching_errors): 
            print(f"  [!] {error}")
    print("-" * 50)

if __name__ == "__main__":
    run_photo_anonymizer_audit()
