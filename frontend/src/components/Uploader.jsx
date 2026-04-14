import React, { useState, useRef } from 'react';
import axios from 'axios';
import { UploadCloud, FileText, CheckCircle, XCircle, Loader2 } from 'lucide-react';

const Uploader = ({ onUploadSuccess }) => {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
  const inputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const onButtonClick = () => {
    inputRef.current.click();
  };

  const showToast = (message, type) => {
    setToast({ show: true, message, type });
    setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
  };

  const handleUpload = async () => {
    if (!file) return;

    // Validate type roughly
    if (!file.name.match(/\.(jpg|jpeg|png|pdf)$/i)) {
      showToast("Invalid file type. Please upload a receipt image or PDF.", "error");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/receipts/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showToast("Receipt uploaded successfully! Processing...", "success");
      setFile(null);
      if (onUploadSuccess) onUploadSuccess();
    } catch (error) {
      showToast("Upload or extraction failed. Please try again.", "error");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="card animate-fade-in" style={{ animationDelay: '0.5s' }}>
      <h2 className="card-title">Upload Receipt</h2>
      
      <div 
        onDragEnter={handleDrag} 
        onDragLeave={handleDrag} 
        onDragOver={handleDrag} 
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${dragActive ? 'var(--color-blue)' : 'var(--border-color)'}`,
          backgroundColor: dragActive ? '#eff6ff' : 'transparent',
          borderRadius: '8px',
          padding: '2rem',
          textAlign: 'center',
          transition: 'all 0.2s',
          cursor: 'pointer'
        }}
        onClick={onButtonClick}
      >
        <input 
          ref={inputRef} 
          type="file" 
          onChange={handleChange} 
          style={{ display: 'none' }} 
          accept=".jpg,.jpeg,.png,.pdf"
        />
        
        {file ? (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={48} color="var(--color-blue)" />
            <p style={{ fontWeight: 500 }}>{file.name}</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{(file.size / 1024).toFixed(1)} KB</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <UploadCloud size={48} color="var(--text-secondary)" />
            <p style={{ fontWeight: 500 }}>Drag & drop your receipt here</p>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Supports JPG, PNG, PDF</p>
          </div>
        )}
      </div>

      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
        {file && (
          <button 
            onClick={(e) => { e.stopPropagation(); setFile(null); }}
            style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-color)', borderRadius: '6px', cursor: 'pointer' }}
            disabled={uploading}
          >
            Cancel
          </button>
        )}
        <button 
          onClick={(e) => { e.stopPropagation(); handleUpload(); }}
          disabled={!file || uploading}
          style={{ 
            padding: '0.5rem 1rem', 
            background: file && !uploading ? 'var(--color-blue)' : 'var(--text-secondary)', 
            color: 'white', 
            border: 'none', 
            borderRadius: '6px', 
            cursor: file && !uploading ? 'pointer' : 'not-allowed',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}
        >
          {uploading ? <Loader2 size={16} className="animate-spin" /> : null}
          {uploading ? 'Uploading...' : 'Upload'}
        </button>
      </div>

      {toast.show && (
        <div className="toast" style={{ backgroundColor: toast.type === 'error' ? 'var(--color-red)' : 'var(--color-green)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {toast.type === 'error' ? <XCircle size={20} /> : <CheckCircle size={20} />}
            <span>{toast.message}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default Uploader;
