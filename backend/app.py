from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename # For securely saving filenames
import os
import shutil # For cleaning up directories if needed

# Import our custom modules
import file_processor
import prompt_builder
import llm_service

app = Flask(__name__)

# Configuration
# Assuming backend folder is at the root of Test-Generator project
# UPLOAD_FOLDER will be Test-Generator/backend/uploads/
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB upload limit
ALLOWED_EXTENSIONS = {'txt', 'py', 'js', 'java', 'cs', 'go', 'rb', 'ts', 'zip', 'jsx', 'tsx'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def index():
    print("--- Root / route HIT ---", flush=True)
    return "Flask backend is running (ready for API calls)!"

@app.route('/api/upload-and-generate', methods=['POST'])
def upload_and_generate_tests_route():
    print("--- Request received at /api/upload-and-generate endpoint ---", flush=True)
    original_file_path_for_cleanup = None

    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        uploaded_file = request.files['file']
        upload_type = request.form.get('uploadType') # 'single' or 'zip' as sent by frontend

        if uploaded_file.filename == '':
            return jsonify({"error": "No file selected for upload"}), 400

        if not upload_type:
            return jsonify({"error": "Missing 'uploadType' in form data"}), 400

        if not (uploaded_file and allowed_file(uploaded_file.filename)):
            return jsonify({"error": "File type not allowed"}), 400

        filename = secure_filename(uploaded_file.filename) # Sanitize filename
        print(f"Processing file: {filename}, type: {upload_type}", flush=True)

        # --- Step 1: Process the uploaded file using file_processor.py ---
        code_to_process, original_file_path_for_cleanup = file_processor.handle_and_extract_code(
            uploaded_file,
            upload_type,
            app.config['UPLOAD_FOLDER'],
            filename
        )

        if code_to_process is None:
            # file_processor should handle its own cleanup if it returns None due to its internal error
            return jsonify({"error": "Failed to process or extract code from file. Check file_processor.py logs or file content."}), 500

        if not code_to_process.strip() and upload_type == 'zip':
            print(f"No recognized code files found in zip: {filename}")
            if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup) and os.path.isdir(original_file_path_for_cleanup):
                shutil.rmtree(original_file_path_for_cleanup)
            return jsonify({"error": f"No recognized code files were found inside '{filename}'. Please ensure your zip contains supported file types."}), 400

        print(f"Code extracted successfully. Length: {len(code_to_process)} chars.", flush=True)
        # For debugging:
        # print(f"Extracted code snippet: {code_to_process[:200]}...", flush=True)

        # --- Step 2: Construct the prompt for DeepSeek Coder ---
        language_preference = request.form.get("language", "python") # Default or get from user
        framework_preference = request.form.get("framework", "unittest") # Default or from user
        user_specific_instructions = request.form.get("instructions", None) # Optional additional instructions

        prompt = prompt_builder.construct_llm_prompt(
            code_snippet=code_to_process,
            language=language_preference,
            test_framework=framework_preference,
            user_instructions=user_specific_instructions
        )

        # --- Step 3: Get test scripts from DeepSeek Coder ---
        print("Sending prompt to LLM service...", flush=True)
        generated_script = llm_service.get_tests_from_deepseek(prompt)

        # --- Cleanup after all processing is done (successful or not from LLM) ---
        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup):
            try:
                if os.path.isdir(original_file_path_for_cleanup): # If it was an extracted zip dir
                    shutil.rmtree(original_file_path_for_cleanup)
                    print(f"Cleaned up directory: {original_file_path_for_cleanup}", flush=True)
                else: # If it was a single file
                    os.remove(original_file_path_for_cleanup)
                    print(f"Cleaned up file: {original_file_path_for_cleanup}", flush=True)
            except Exception as cleanup_err:
                app.logger.error(f"Error during cleanup of '{original_file_path_for_cleanup}': {cleanup_err}", exc_info=True)

        if not generated_script:
            return jsonify({"error": "LLM failed to generate script or returned empty. Check llm_service.py logs."}), 500

        print("LLM script generation successful.", flush=True)
        return jsonify({
            "message": f"Successfully processed '{filename}' and generated tests.",
            "data": {
                "generated_script": generated_script,
                "original_filename": filename,
                "upload_type": upload_type
                # You could also return the extracted_code_snippet if useful for frontend
                # "extracted_code_snippet": code_to_process[:200] + "..." if len(code_to_process) > 200 else code_to_process,
            }
        }), 200

    except ValueError as ve:
        app.logger.error(f"ValueError: {str(ve)}", exc_info=True)
        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup): # Ensure cleanup
            try:
                if os.path.isdir(original_file_path_for_cleanup): shutil.rmtree(original_file_path_for_cleanup)
                else: os.remove(original_file_path_for_cleanup)
            except Exception as cleanup_err: app.logger.error(f"Error during cleanup after ValueError: {cleanup_err}", exc_info=True)
        return jsonify({"error": str(ve)}), 400 # Bad Request

    except Exception as e:
        app.logger.error(f"An unexpected internal server error occurred: {e}", exc_info=True)
        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup): # Ensure cleanup
            try:
                if os.path.isdir(original_file_path_for_cleanup): shutil.rmtree(original_file_path_for_cleanup)
                else: os.remove(original_file_path_for_cleanup)
            except Exception as cleanup_err: app.logger.error(f"Error during cleanup after unhandled exception: {cleanup_err}", exc_info=True)
        return jsonify({"error": "An unexpected internal server error occurred. Please check backend logs."}), 500

if __name__ == '__main__':
    print("--- Starting Flask App on port 5001 ---")
    # Use host='0.0.0.0' if you want to access it from other devices on your network
    # For local Vite proxy, '127.0.0.1' is fine.
    app.run(host='127.0.0.1', port=5001, debug=True)