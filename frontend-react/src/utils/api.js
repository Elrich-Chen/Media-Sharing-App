import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create axios instance
export const api = axios.create({
  baseURL: API_URL,
});

// Add token to requests if it exists
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

/**
 * Encode text for ImageKit overlay - base64 then URL encode
 * Python: base64.b64encode(text.encode('utf-8')).decode('utf-8') -> urllib.parse.quote
 */
export const encodeTextForOverlay = (text) => {
  if (!text) return "";
  // JS btoa handles Latin1, so we need to escape for UTF-8 support
  const base64Text = btoa(unescape(encodeURIComponent(text)));
  return encodeURIComponent(base64Text);
};

/**
 * Create transformed URL for ImageKit
 */
export const createTransformedUrl = (originalUrl, transformationParams, caption = null) => {
  let params = transformationParams;

  if (caption) {
    const encodedCaption = encodeTextForOverlay(caption);
    // Add text overlay at bottom with semi-transparent background
    const textOverlay = `l-text,ie-${encodedCaption},ly-N20,lx-20,fs-100,co-white,bg-000000A0,l-end`;
    params = textOverlay;
  }

  if (!params) return originalUrl;

  const parts = originalUrl.split("/");
  // Assuming structure: https://ik.imagekit.io/id/path...
  // parts: [https:, "", domain, id, ...path]
  
  const baseUrl = parts.slice(0, 4).join("/");
  const filePath = parts.slice(4).join("/");
  
  return `${baseUrl}/tr:${params}/${filePath}`;
};