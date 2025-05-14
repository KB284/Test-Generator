import os
import zipfile

def process_file_upload(uploaded_file_obj, upload_type, temp_dir):
    """
    Handles saving the uploaded file, extracting contents if it's a zip,
    and returning the code content(s) to be processed.
    """
    # Ensure the temp_dir exists
    os.makedirs(temp_dir, exist_ok=True)

    file_path = os.path.join(temp_dir, uploaded_file_obj.filename)
    uploaded_file_obj.save(file_path)

    all_code_content = [] # To store content of one or more files

    if upload_type == 'zip':
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                for member_name in zip_ref.namelist():
                    # Add more sophisticated logic to identify relevant code files
                    # For example, by extension or a manifest file if provided.
                    if member_name.endswith(('.py', '.js', '.java', '.ts', '.cs', '.go', '.rb')): # Example extensions
                        try:
                            with zip_ref.open(member_name) as code_file:
                                all_code_content.append(code_file.read().decode('utf-8', errors='ignore'))
                        except Exception as e:
                            print(f"Error reading {member_name} from zip: {e}")
            # For now, join all found code contents.
            # Consider how to handle multiple files for the LLM (e.g., send one by one, or a combined context)
            code_to_process = "\n\n--- Next File: {} ---\n\n".format(member_name).join(all_code_content) if all_code_content else ""
        else:
            os.remove(file_path) # Clean up invalid zip
            raise ValueError("Uploaded file was marked as zip but is not a valid zip archive.")
    elif upload_type == 'single':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code_to_process = f.read()
    else:
        os.remove(file_path) # Clean up if type is unknown
        raise ValueError(f"Unknown upload type: {upload_type}")

    # Clean up the originally saved file/zip after extraction
    # The caller (app.py) should handle this once the content is used or processing is done.
    # For now, returning path along with content for explicit cleanup by caller.
    return code_to_process, file_path

# Future considerations:
# - Max file size for individual files within a zip.
# - Max number of files to process from a zip.
# - Smarter identification of "main" project files.