const API_BASE = '/api/v1';

function getToken() {
  return localStorage.getItem('access_token');
}

function setToken(token) {
  localStorage.setItem('access_token', token);
}

function clearToken() {
  localStorage.removeItem('access_token');
}

async function apiRequest(method, path, body = null, token = null) {
  const headers = { 'Content-Type': 'application/json' };
  const authToken = token ?? getToken();
  if (authToken) headers['Authorization'] = `Bearer ${authToken}`;

  const options = { method, headers };
  if (body !== null) options.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE}${path}`, options);
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    const detail = data.detail;
    const message = typeof detail === 'string'
      ? detail
      : Array.isArray(detail)
        ? detail.map(d => d.msg || d).join(', ')
        : 'Request failed';
    throw new Error(message);
  }

  return data;
}

export const authApi = {
  startLogin: (token) => apiRequest('GET', '/login/start', null, token),
  identify: (login, token) => apiRequest('POST', '/login/identification', { login }, token),
  confirmEmail: (email, token) => apiRequest('POST', '/login/confirm-email', { email }, token),
  submitPassword: (password, token) => apiRequest('POST', '/login/password', { password }, token),
  sendLoginOtp: (token) => apiRequest('GET', '/login/send-email-otp', null, token),
  confirmLoginOtp: (email_otp, token) => apiRequest('POST', '/login/confirm-email-otp', { email_otp }, token),
  completeLogin: (token) => apiRequest('POST', '/login/complete-login', null, token),

  startRegistration: (token) => apiRequest('GET', '/registration/start', null, token),
  submitProfile: (data, token) => apiRequest('POST', '/registration/personal-data', data, token),
  sendRegistrationOtp: (token) => apiRequest('GET', '/registration/send-email-otp', null, token),
  confirmRegistrationOtp: (email_otp, token) => apiRequest('POST', '/registration/confirm-email-otp', { email_otp }, token),
  submitRegistrationPassword: (password, token) => apiRequest('POST', '/registration/password', { password }, token),
  confirmRegistrationPassword: (password, token) => apiRequest(
    'POST', '/registration/confirm-password', { confirm_password: password }, token
  ),
  completeRegistration: (token) => apiRequest('POST', '/registration/complete-registration', null, token),
};

export const chatApi = {
  getMe: () => apiRequest('GET', '/me/'),
  getChats: () => apiRequest('GET', '/chats/'),
  createChat: (username) => apiRequest('POST', '/chats/', { username }),
  getMessages: (chatId) => apiRequest('GET', `/chats/${chatId}/messages`),
};

export { getToken, setToken, clearToken, apiRequest };
