from flask import Flask, request, jsonify
import os

# We'll import functions from other modules as we create them
# from file_processor import process_file_upload
# from prompt_builder import construct_llm_prompt
# from llm_service import get_tests_from_deepseek

app = Flask(__name__)

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads') # Creates an 'uploads' folder in the backend directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Example: 16MB upload limit

@app.route('/api/upload-and-generate', methods=['POST'])
def handle_upload_and_generate():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_file = request.files['file']
    upload_type = request.form.get('uploadType') # 'single' or 'zip' as sent by frontend

    if uploaded_file.filename == '':
        return jsonify({"error": "No file selected for upload"}), 400

    if not upload_type:
        return jsonify({"error": "Missing 'uploadType' in form data"}), 400

    if uploaded_file:
        try:
            # --- Step 1: Process the uploaded file ---
            # This function (which we'll define in file_processor.py)
            # will save the file, extract code if it's a zip, and return
            # the code content as a string (or list of strings/contents).
            # code_content_or_paths = process_file_upload(uploaded_file, upload_type, app.config['UPLOAD_FOLDER'])

            # Placeholder for file processing logic:
            # For now, let's save the file and read its content directly if it's not a zip.
            # More robust logic will go into file_processor.py
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            uploaded_file.save(file_path)

            extracted_code = ""
            if upload_type == 'single':
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_code = f.read()
            elif upload_type == 'zip':
                # TODO: Implement zip processing in file_processor.py
                # For now, we'll just indicate it's a zip.
                # In a real scenario, you'd extract, find relevant files, and get their content.
                extracted_code = f"Placeholder for code from zip: {uploaded_file.filename}"

            # Clean up the saved file after processing
            # os.remove(file_path) # Move this to after LLM call or handle temp files better

            if not extracted_code:
                return jsonify({"error": "Could not extract code from the uploaded file."}), 500

            # --- Step 2: Construct the prompt for DeepSeek Coder ---
            # (Logic will be in prompt_builder.py)
            # For now, a simple prompt:
            # user_preferences = {"language": "python", "framework": "unittest"} # Example
            # prompt = construct_llm_prompt(extracted_code, user_preferences)
            prompt = f"Generate unit tests for the following code:\n\n```\n{extracted_code}\n```\n\nPlease provide only the test code."


            # --- Step 3: Get test scripts from DeepSeek Coder ---
            # (Logic will be in llm_service.py)
            # generated_script = get_tests_from_deepseek(prompt)

            # Mocking LLM response for now:
            generated_script = f"# This is a mock test script for the provided code:\n# {extracted_code[:100]}...\n\nimport unittest\n\nclass TestMyCode(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()"

            # Clean up the saved file now that we are done with it for this request
            if os.path.exists(file_path):
                os.remove(file_path)

            if not generated_script:
                return jsonify({"error": "LLM failed to generate script."}), 500

            # Respond to the frontend as expected by CreateTestScriptPage.jsx
            return jsonify({
                "message": "Tests generated successfully (mocked)",
                "data": {
                    "generated_script": generated_script,
                    "original_filename": uploaded_file.filename
                }
            }), 200

        except Exception as e:
            # Log the full error e to the console or a log file for debugging
            print(f"Error processing file: {e}")
            if 'file_path' in locals() and os.path.exists(file_path): # Ensure cleanup on error
                os.remove(file_path)
            return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

    return jsonify({"error": "File processing failed."}), 500

if __name__ == '__main__':
    # Note: The frontend (Vite) usually runs on a different port (e.g., 5173).
    # You might need to configure a proxy in vite.config.js for /api calls
    # or enable CORS in Flask if running on different origins.
    app.run(debug=True, port=5001) # Example port for the backend
