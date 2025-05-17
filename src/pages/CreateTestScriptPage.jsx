import React, {useState, useRef} from 'react'; // Import useState and useRef

function CreateTestScriptPage() {
    // State for the single file input
    const [selectedSingleFile, setSelectedSingleFile] = useState(null);
    // State for the zip file input
    const [selectedZipFile, setSelectedZipFile] = useState(null);
    // Unified message state
    const [message, setMessage] = useState('');
    // Loading state for API call
    const [isLoading, setIsLoading] = useState(false);
    // **** ADD NEW STATE FOR THE GENERATED SCRIPT ****
    const [generatedScript, setGeneratedScript] = useState(''); // Initialize as empty string

    // **** ADD NEW STATE FOR LANGUAGE AND FRAMEWORK ****
    const [language, setLanguage] = useState('python'); // Default to python
    const [testFramework, setTestFramework] = useState('unittest'); // Default to unittest

    // Refs to clear file input values if needed
    const singleFileInpuRef = useRef(null);
    const zipFileInpuRef = useRef(null);

    const handleFileChangeReset = () => {
        setIsLoading(false); // Reset loading state
        setGeneratedScript(''); // **** CLEAR PREVIOUS SCRIPT ****
    };

    const handleSingleFileChange = (event) => {
        handleFileChangeReset(); // Call common reset logic
        const file = event.target.files[0];
        if (file) {
            setSelectedSingleFile(file);
            setSelectedZipFile(null);
            if (zipFileInpuRef.current) {
                zipFileInpuRef.current.value = '';
            }
            setMessage(`Single file selected: ${file.name}`);
        } else {
            setSelectedSingleFile(null);
            if (!selectedZipFile) setMessage('');
        }
    };

    const handleZipFileChange = (event) => {
        handleFileChangeReset(); // Call common reset logic
        const file = event.target.files[0];
        if (file) {
            if (file.name.endsWith('.zip')) {
                setSelectedZipFile(file);
                setSelectedSingleFile(null);
                if (singleFileInpuRef.current) {
                    singleFileInpuRef.current.value = '';
                }
                setMessage(`ZIP file selected: ${file.name}`);
            } else {
                setSelectedZipFile(null);
                event.target.value = null;
                setMessage('Invalid file type. Please select a .zip file for project uploads.');
            }
        } else {
            setSelectedZipFile(null);
            if (!selectedSingleFile) setMessage('');
        }
    };

    const handleGenerateTests = async () => {
        let fileToUpload = null;
        let uploadType = '';

        if (selectedSingleFile) {
            fileToUpload = selectedSingleFile;
            uploadType = 'single';
        } else if (selectedZipFile) {
            fileToUpload = selectedZipFile;
            uploadType = 'zip';
        } else {
            setMessage('Please select a file or a .zip archive using one of the options.');
            setGeneratedScript(''); // Clear any old script
            return;
        }

        setIsLoading(true);
        setMessage(`Uploading and processing ${fileToUpload.name}...`);
        setGeneratedScript(''); // **** CLEAR PREVIOUS SCRIPT ON NEW GENERATION ****

        const formData = new FormData();
        formData.append('file', fileToUpload);
        formData.append('uploadType', uploadType);
        // **** APPEND LANGUAGE AND FRAMEWORK TO FORMDATA ****
        formData.append('language', language);
        formData.append('framework', testFramework);

        // You could also add a field for 'user_instructions' from another input
        // const userInstructions = document.getElementById('userInstructionsInput')?.value;
        // if (userInstructions) formData.append('instructions', userInstructions);

        const API_ENDPOINT = '/api/upload-and-generate';

        try {
            const response = await fetch(API_ENDPOINT, {
                method: 'POST',
                body: formData,
            });

            setIsLoading(false);

            if (response.ok) {
                const result = await response.json();
                setMessage(`Success: ${result.message || 'File processed.'} (Backend response)`);
                // **** SET THE GENERATED SCRIPT STATE ****
                if (result.data && result.data.generated_script) {
                    setGeneratedScript(result.data.generated_script);
                } else {
                    setGeneratedScript('No script was returned by the backend.');
                }
                console.log('Backend result:', result);
            } else {
                const errorResult = await response.json().catch(() => ({message: 'Could not parse error response.'}));
                setMessage(`Error: ${response.status} - ${errorResult.message || response.statusText}`);
                setGeneratedScript(''); // Clear script on error
            }
        } catch (error) {
            setIsLoading(false);
            console.error('Network or fetch error:', error);
            setMessage(`Network Error: Failed to send file. ${error.message}`);
            setGeneratedScript(''); // Clear script on error
        }
    };

    const handleCopyToClipboard = () => {
        if (generatedScript) {
            navigator.clipboard.writeText(generatedScript)
                .then(() => {
                    setMessage('Script copied to clipboard!');
                    // Optionally, reset message after a few seconds
                    setTimeout(() => {
                        if (message === 'Script copied to clipboard!') { // Avoid overwriting other messages
                            setMessage(''); // Or reset to the success message related to generation
                        }
                    }, 3000);
                })
                .catch(err => {
                    console.error('Failed to copy script: ', err);
                    setMessage('Failed to copy script. Please copy manually.');
                });
        }
    };


    return (
        <main className="App-content">
            {/* File Upload Sections (Single and Zip) - Keep as they are */}
            <div style={{marginBottom: '40px', paddingBottom: '20px', borderBottom: '1px solid #eee'}}>
                <h3>Option 1: Upload Single Code File</h3>
                <p>Select an individual code file (e.g., .js, .py, .java) for analysis.</p>
                <input
                    type="file"
                    ref={singleFileInpuRef}
                    onChange={handleSingleFileChange}
                    style={{marginTop: '10px'}}
                    disabled={isLoading}
                />
            </div>

            <div style={{marginBottom: '40px', paddingBottom: '20px', borderBottom: '1px solid #eee'}}>
                <h3>Option 2: Upload Project Folder (as .zip)</h3>
                <p>Compress your entire project folder into a <strong>.zip</strong> file and upload it.</p>
                <input
                    type="file"
                    ref={zipFileInpuRef}
                    onChange={handleZipFileChange}
                    accept=".zip,application/zip,application/x-zip-compressed,application/octet-stream"
                    style={{marginTop: '10px'}}
                    disabled={isLoading}
                />
            </div>

            {/* **** ADD INPUTS FOR LANGUAGE AND FRAMEWORK **** */}
            <div style={{
                marginTop: '20px',
                marginBottom: '20px',
                paddingBottom: '20px',
                borderBottom: '1px solid #eee',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '15px'
            }}>
                <h3>Test Generation Preferences:</h3>
                <div>
                    <label htmlFor="language" style={{marginRight: '10px'}}>
                        Code Language:
                    </label>
                    <input
                        type="text"
                        id="language"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value.toLowerCase())}
                        placeholder="e.g., python, javascript, java"
                        style={{padding: '8px', minWidth: '200px'}}
                        disabled={isLoading}
                    />
                </div>
                <div>
                    <label htmlFor="testFramework" style={{marginRight: '10px'}}>
                        Test Framework:
                    </label>
                    <input
                        type="text"
                        id="testFramework"
                        value={testFramework}
                        onChange={(e) => setTestFramework(e.target.value.toLowerCase())}
                        placeholder="e.g., unittest, jest, junit"
                        style={{padding: '8px', minWidth: '200px'}}
                        disabled={isLoading}
                    />
                </div>
                {/* You could also add a textarea for specific user instructions to pass to the prompt */}
                {/* <div>
          <label htmlFor="userInstructionsInput" style={{display: 'block', marginBottom: '5px'}}>Specific Instructions (Optional):</label>
          <textarea
            id="userInstructionsInput"
            rows="3"
            style={{width: '100%', maxWidth: '400px', padding: '8px'}}
            placeholder="e.g., focus on testing the login function, ensure all error codes are checked"
            disabled={isLoading}
          ></textarea>
        </div>
        */}
            </div>


            {message && (
                <p
                    style={{
                        marginTop: '30px',
                        padding: '10px',
                        backgroundColor: message.startsWith('Invalid file type') || message.startsWith('Error') || message.startsWith('Network Error') ? '#ffcccb' : message.startsWith('Success') || message.startsWith('Script copied') ? '#d4edda' : '#f0f0f0',
                        border: `1px solid ${message.startsWith('Invalid file type') || message.startsWith('Error') || message.startsWith('Network Error') ? 'red' : message.startsWith('Success') || message.startsWith('Script copied') ? 'green' : '#ccc'}`,
                        borderRadius: '5px',
                        fontStyle: 'italic',
                        color: message.startsWith('Invalid file type') || message.startsWith('Error') || message.startsWith('Network Error') ? 'darkred' : message.startsWith('Success') || message.startsWith('Script copied') ? 'darkgreen' : 'inherit',
                    }}
                >
                    {message}
                </p>
            )}

            <button
                onClick={handleGenerateTests}
                style={{marginTop: '30px', padding: '10px 20px', cursor: 'pointer', fontSize: '1em'}}
                disabled={(!selectedSingleFile && !selectedZipFile) || isLoading}
            >
                {isLoading ? 'Processing...' : 'Process and Generate Tests'}
            </button>

            {generatedScript && (
                <div style={{marginTop: '30px', textAlign: 'left', width: '100%', maxWidth: '800px'}}>
                    <h3>Generated Test Script:</h3>
                    <button onClick={handleCopyToClipboard} style={{marginBottom: '10px', padding: '5px 10px'}}>
                        Copy to Clipboard
                    </button>
                    <pre style={{
                        backgroundColor: '#f5f5f5',
                        border: '1px solid #ccc',
                        padding: '15px',
                        borderRadius: '5px',
                        whiteSpace: 'pre-wrap',
                        wordWrap: 'break-word',
                        maxHeight: '500px',
                        overflowY: 'auto'
                    }}>
            <code>
              {generatedScript}
            </code>
          </pre>
                </div>
            )}
        </main>
    );
}

export default CreateTestScriptPage;