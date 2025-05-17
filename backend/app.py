from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import shutil

# Import our custom modules
import file_processor
import prompt_builder
import llm_service

app = Flask(__name__)

# --- Configuration Change for UPLOAD_FOLDER ---
# Get the project root directory (which is one level up from 'backend')
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Define UPLOAD_FOLDER to be at the project root level, e.g., Test-Generator/temp_user_uploads/
UPLOAD_FOLDER = os.path.join(project_root, 'temp_user_uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure this new directory exists
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
        upload_type = request.form.get('uploadType')

        if uploaded_file.filename == '':
            return jsonify({"error": "No file selected for upload"}), 400

        if not upload_type:
            return jsonify({"error": "Missing 'uploadType' in form data"}), 400

        if not (uploaded_file and allowed_file(uploaded_file.filename)):
            return jsonify({"error": "File type not allowed"}), 400

        filename = secure_filename(uploaded_file.filename)
        # Extract module name (filename without extension)
        module_name, _ = os.path.splitext(filename)  # Gets 'name of file' from 'name of file.py'
        print(f"Processing file: {filename}, type: {upload_type}, module_name: {module_name}", flush=True)


        # file_processor will now use the updated app.config['UPLOAD_FOLDER']
        code_to_process, original_file_path_for_cleanup = file_processor.handle_and_extract_code(
            uploaded_file,
            upload_type,
            app.config['UPLOAD_FOLDER'],  # This is now the new path
            filename
        )

        language_preference = request.form.get("language", "python").strip().lower() # Get from form, default, sanitize
        framework_preference = request.form.get("framework", "unittest").strip().lower() # Get from form, default, sanitize
        user_specific_instructions = request.form.get("instructions", None) #Optional

        print(f"Language: {language_preference}, Framework: {framework_preference}", flush=True) # For debugging

        prompt = prompt_builder.construct_llm_prompt(
            code_snippet=code_to_process,
            module_name_to_test=module_name,  # Pass the extracted module name
            language=language_preference,
            test_framework=framework_preference,
            user_instructions=user_specific_instructions
        )

        if code_to_process is None:
            return jsonify({
                               "error": "Failed to process or extract code from file. Check file_processor.py logs or file content."}), 500

        if not code_to_process.strip() and upload_type == 'zip':
            print(f"No recognized code files found in zip: {filename}")
            if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup) and os.path.isdir(
                    original_file_path_for_cleanup):
                shutil.rmtree(original_file_path_for_cleanup)
            return jsonify({
                               "error": f"No recognized code files were found inside '{filename}'. Please ensure your zip contains supported file types."}), 400

        print(f"Code extracted successfully. Length: {len(code_to_process)} chars.", flush=True)

        language_preference = request.form.get("language", "python")
        framework_preference = request.form.get("framework", "unittest")
        user_specific_instructions = request.form.get("instructions", None)

        prompt = prompt_builder.construct_llm_prompt(
            code_snippet=code_to_process,
            module_name_to_test=module_name,  # Pass the extracted module name
            language=language_preference,
            test_framework=framework_preference,
            user_instructions=user_specific_instructions
        )

        print("Sending prompt to LLM service...", flush=True)
        generated_script = llm_service.get_tests_from_deepseek(prompt)

        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup):
            try:
                if os.path.isdir(original_file_path_for_cleanup):
                    shutil.rmtree(original_file_path_for_cleanup)
                    print(f"Cleaned up directory: {original_file_path_for_cleanup}", flush=True)
                else:
                    os.remove(original_file_path_for_cleanup)
                    print(f"Cleaned up file: {original_file_path_for_cleanup}", flush=True)
            except Exception as cleanup_err:
                app.logger.error(f"Error during cleanup of '{original_file_path_for_cleanup}': {cleanup_err}",
                                 exc_info=True)

        if not generated_script:
            return jsonify(
                {"error": "LLM failed to generate script or returned empty. Check llm_service.py logs."}), 500

        print("LLM script generation successful.", flush=True)
        return jsonify({
            "message": f"Successfully processed '{filename}' and generated tests.",
            "data": {
                "generated_script": generated_script,
                "original_filename": filename,
                "upload_type": upload_type
            }
        }), 200

    except ValueError as ve:
        app.logger.error(f"ValueError: {str(ve)}", exc_info=True)
        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup):
            try:
                if os.path.isdir(original_file_path_for_cleanup):
                    shutil.rmtree(original_file_path_for_cleanup)
                else:
                    os.remove(original_file_path_for_cleanup)
            except Exception as cleanup_err:
                app.logger.error(f"Error during cleanup after ValueError: {cleanup_err}", exc_info=True)
        return jsonify({"error": str(ve)}), 400

    except Exception as e:
        app.logger.error(f"An unexpected internal server error occurred: {e}", exc_info=True)
        if original_file_path_for_cleanup and os.path.exists(original_file_path_for_cleanup):
            try:
                if os.path.isdir(original_file_path_for_cleanup):
                    shutil.rmtree(original_file_path_for_cleanup)
                else:
                    os.remove(original_file_path_for_cleanup)
            except Exception as cleanup_err:
                app.logger.error(f"Error during cleanup after unhandled exception: {cleanup_err}", exc_info=True)
        return jsonify({"error": "An unexpected internal server error occurred. Please check backend logs."}), 500


if __name__ == '__main__':
    print("--- Starting Flask App on port 5001 (Reloader ENABLED) ---")
    # Re-enable the default reloader by simply using debug=True
    # Flask will use 'stat' or 'watchdog' if available.
    app.run(host='127.0.0.1', port=5001, debug=True)
