import os
import zipfile
from werkzeug.utils import secure_filename # Already in Flask dependencies

def handle_and_extract_code(uploaded_file_obj, upload_type: str, temp_dir: str, secured_base_filename: str):
    """
    Saves the uploaded file, extracts code content.
    If it's a zip, it concatenates content of recognized code files.

    Args:
        uploaded_file_obj: The file object from Flask request.files.
        upload_type: 'single' or 'zip'.
        temp_dir: The directory to temporarily save uploads.
        secured_base_filename: The sanitized filename.

    Returns:
        A tuple (str_code_content, path_to_cleanup) or (None, None) on error.
        str_code_content: String containing the code content(s).
        path_to_cleanup: The path of the initially saved file (or extracted dir) that app.py should clean.
    """

    saved_file_path = os.path.join(temp_dir, secured_base_filename)
    uploaded_file_obj.save(saved_file_path)

    all_code_extracted = []
    path_to_cleanup_after_use = saved_file_path # This will be the default path to cleanup

    try:
        if upload_type == 'zip':
            if zipfile.is_zipfile(saved_file_path):
                # Create a temporary directory for extracting zip contents
                extracted_zip_dir = os.path.join(temp_dir, f"extracted_{secured_base_filename.rsplit('.', 1)[0]}")
                os.makedirs(extracted_zip_dir, exist_ok=True)
                path_to_cleanup_after_use = extracted_zip_dir # Now we clean up this whole dir

                with zipfile.ZipFile(saved_file_path, 'r') as zip_ref:
                    zip_ref.extractall(extracted_zip_dir)

                # Walk through extracted files
                for root, _, files in os.walk(extracted_zip_dir):
                    for file in files:
                        if file.endswith(('.py', '.js', '.java', '.ts', '.cs', '.go', '.rb', '.jsx', '.tsx')): # Add more code extensions
                            try:
                                with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as code_f:
                                    all_code_extracted.append(f"# File: {os.path.join(os.path.relpath(root, extracted_zip_dir), file)}\n\n{code_f.read()}")
                            except Exception as e_read:
                                print(f"Warning: Could not read file {file} from zip: {e_read}")

                os.remove(saved_file_path) # Remove the original zip file now

                if not all_code_extracted:
                    # If no code files found, but it was a zip.
                    # We might still want to return None or an error for the caller.
                    # For now, returning empty string, caller (app.py) should check.
                    print(f"Warning: No recognized code files found in zip {secured_base_filename}")
                    return "", path_to_cleanup_after_use

            else: # Not a valid zip file
                os.remove(saved_file_path)
                raise ValueError("Uploaded file was marked as 'zip' but is not a valid zip archive.")

        elif upload_type == 'single':
            with open(saved_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                all_code_extracted.append(f.read())
            # For single files, app.py will remove 'saved_file_path' after use.

        else: # Unknown upload type
            os.remove(saved_file_path)
            raise ValueError(f"Unknown upload type: '{upload_type}'")

        # Join all extracted code pieces. Add separators for clarity if multiple files.
        # This simple join might be too naive for large projects from a zip.
        # Consider if you want to send one file at a time, or a summary, or let user choose.
        final_code_content = "\n\n\n\n".join(all_code_extracted)
        return final_code_content, path_to_cleanup_after_use

    except Exception as e:
        # Clean up if an error occurred during processing
        if os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        if 'extracted_zip_dir' in locals() and os.path.exists(extracted_zip_dir):
            import shutil
            shutil.rmtree(extracted_zip_dir)
        print(f"Error in handle_and_extract_code: {e}")
        raise # Re-raise the exception to be caught by app.py for a proper HTTP response