import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../utils/api';

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [caption, setCaption] = useState('');
  const [uploading, setUploading] = useState(false);
  const navigate = useNavigate();

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('caption', caption);

    try {
      await api.post('/upload', formData);
      navigate('/');
    } catch (err) {
      alert("Upload failed!");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <h1 style={{ marginBottom: '30px' }}>📸 Share Something</h1>
      <div className="post-card" style={{ padding: '20px' }}>
        <form onSubmit={handleUpload}>
          <div className="form-group">
            <label>Choose Media</label>
            <input type="file" onChange={e => setFile(e.target.files[0])} accept="image/*,video/*" className="form-input" required />
          </div>
          <div className="form-group">
            <label>Caption</label>
            <textarea className="form-input" rows="3" value={caption} onChange={e => setCaption(e.target.value)} placeholder="What's on your mind?" />
          </div>
          <button className="btn btn-primary" disabled={uploading}>
            {uploading ? 'Uploading...' : 'Share'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadPage;