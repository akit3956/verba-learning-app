// Determine the API Base URL based on the current hostname.
// If the app is accessed via localhost, use localhost.
// If accessed via a local network IP (e.g., 192.168.0.x), use that IP.
// This allows the app to be tested on mobile devices on the same network.

// Hardcoding the local network IP so mobile devices can reach the Mac's backend.
// Before, window.location.hostname could resolve to 'localhost' on the phone,
// causing the models fetch to fail and fallback to 'gemma2'.

const API_BASE_URL = 'https://verba-learning-app.onrender.com';

export default API_BASE_URL;
