import React, { useState, useRef } from 'react'; // Import useState and useRef

function CreateTestScriptPage() {
  // State for the single file input
  const [selectedSingleFile, setSelectedSingleFile] = useState(null);
  // State for the zip file input
  const [selectedZipFile, setSelectedZipFile] = useState(null);
  // Unified message state
  const [message, setMessage] = useState('');
  // Loading state for API call
  const [isLoading, setIsLoading] = useState(false);

  // Refs to clear file input values if needed
  const singleFileInpuRef = useRef(null);
  const zipFileInpuRef = useRef(null);

  const handleSingleFileChange = (event) => {
    const file = event.target.files[0];
    setIsLoading(false); // Reset loading state on new selection
    if (file) {
      setSelectedSingleFile(file);
      setSelectedZipFile(null); // Clear the other selection's state
      if (zipFileInpuRef.current) {
        zipFileInpuRef.current.value = ''; // Clear the other input's displayed file
      }
      setMessage(`Single file selected: ${file.name}`);
    } else {
      setSelectedSingleFile(null);
      if (!selectedZipFile) setMessage('');
    }
  };

  const handleZipFileChange = (event) => {
    const file = event.target.files[0];
    setIsLoading(false); // Reset loading state on new selection
    if (file) {
      if (file.name.endsWith('.zip')) {
        setSelectedZipFile(file);
        setSelectedSingleFile(null); // Clear the other selection's state
        if (singleFileInpuRef.current) {
          singleFileInpuRef.current.value = ''; // Clear the other input's displayed file
        }
        setMessage(`ZIP file selected: ${file.name}`);
      } else {
        setSelectedZipFile(null);
        event.target.value = null; // Reset this input as it's invalid
        setMessage('Invalid file type. Please select a .zip file for project uploads.');
      }
    } else {
      setSelectedZipFile(null);
      if (!selectedSingleFile) setMessage('');
    }
  };

  // --- UPDATED FUNCTION ---
  const handleGenerateTests = async () => {
    let fileToUpload = null;
    let uploadType = '';

    if (selectedSingleFile) {
      fileToUpload = selectedSingleFile;
      uploadType = 'single'; // Type identifier for backend
    } else if (selectedZipFile) {
      fileToUpload = selectedZipFile;
      uploadType = 'zip'; // Type identifier for backend
    } else {
      setMessage('Please select a file or a .zip archive using one of the options.');
      return; // Stop if nothing is selected
    }

    setIsLoading(true); // Indicate processing started
    setMessage(`Uploading and processing ${fileToUpload.name}...`);

    // Create FormData to send the file
    const formData = new FormData();
    formData.append('file', fileToUpload); // Key 'file' holds the file data
    formData.append('uploadType', uploadType); // Send the type

    // Define your backend endpoint URL (replace later)
    const API_ENDPOINT = '/api/upload-and-generate';

    try {
      // Send the file to the backend
      const response = await fetch(API_ENDPOINT, {
        method: 'POST',
        body: formData,
        // No need to set Content-Type header for FormData
      });

      setIsLoading(false); // Processing finished

      // Handle the response from the backend
      if (response.ok) {
        const result = await response.json(); // Assuming backend sends JSON
        setMessage(`Success: ${result.message || 'File processed.'} (Backend response)`);
        // TODO: Display results or generated scripts based on 'result.data'
        console.log('Backend result:', result);
      } else {
        // Handle HTTP errors (e.g., 400, 500)
        const errorResult = await response.json().catch(() => ({ message: 'Could not parse error response.' }));
        setMessage(`Error: ${response.status} - ${errorResult.message || response.statusText}`);
      }
    } catch (error) {
      setIsLoading(false); // Processing finished due to error
      console.error('Network or fetch error:', error);
      setMessage(`Network Error: Failed to send file. ${error.message}`);
    }
  };
  // --- END OF UPDATED FUNCTION ---

  return (
    <main className="App-content">
      <div style={{ marginBottom: '40px', paddingBottom: '20px', borderBottom: '1px solid #eee' }}>
        <h3>Option 1: Upload Single Code File</h3>
        <p>Select an individual code file (e.g., .js, .py, .java) for analysis.</p>
        <input
          type="file"
          ref={singleFileInpuRef}
          onChange={handleSingleFileChange}
          style={{ marginTop: '10px' }}
          disabled={isLoading} // Disable input while loading
        />
      </div>

      <div>
        <h3>Option 2: Upload Project Folder (as .zip)</h3>
        <p>Compress your entire project folder into a <strong>.zip</strong> file and upload it.</p>
        <input
          type="file"
          ref={zipFileInpuRef}
          onChange={handleZipFileChange}
          accept=".zip,application/zip,application/x-zip-compressed,application/octet-stream"
          style={{ marginTop: '10px' }}
          disabled={isLoading} // Disable input while loading
        />
      </div>

      {message && (
        <p
          style={{
            marginTop: '30px',
            fontStyle: 'italic',
             color: message.startsWith('Invalid file type') || message.startsWith('Error') || message.startsWith('Network Error') ? 'red' : 'inherit',
          }}
        >
          {message}
        </p>
      )}

      <button
        onClick={handleGenerateTests}
        style={{ marginTop: '30px', padding: '10px 20px', cursor: 'pointer' }}
        disabled={(!selectedSingleFile && !selectedZipFile) || isLoading} // Disabled if nothing selected OR loading
      >
        {/* Change button text based on loading state */}
        {isLoading ? 'Processing...' : 'Process and Generate Tests'}
      </button>
    </main>
  );
}

export default CreateTestScriptPage;