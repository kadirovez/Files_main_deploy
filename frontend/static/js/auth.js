import { authApi, setToken } from './api.js';

const steps = {
  login: ['identify', 'confirm-email', 'password', 'otp', 'done'],
  emailLogin: ['identify', 'password', 'otp', 'done'],
  register: ['profile', 'otp', 'password', 'confirm-password', 'done'],
};

let mode = 'login';
let loginMethod = null;
let sessionToken = null;
let maskedEmail = null;

const els = {
  tabs: document.querySelectorAll('.auth-tab'),
  panels: document.querySelectorAll('.auth-panel'),
  title: document.getElementById('auth-title'),
  subtitle: document.getElementById('auth-subtitle'),
  error: document.getElementById('auth-error'),
  form: document.getElementById('auth-form'),
  fields: document.getElementById('auth-fields'),
  submit: document.getElementById('auth-submit'),
  back: document.getElementById('auth-back'),
  hint: document.getElementById('auth-hint'),
};

let currentStep = 'identify';

function showError(msg) {
  els.error.textContent = msg;
  els.error.classList.remove('hidden');
}

function clearError() {
  els.error.classList.add('hidden');
}

function setStep(step) {
  currentStep = step;
  renderStep();
}

function switchMode(newMode) {
  mode = newMode;
  sessionToken = null;
  loginMethod = null;
  maskedEmail = null;
  currentStep = mode === 'register' ? 'profile' : 'identify';
  els.tabs.forEach(tab => tab.classList.toggle('active', tab.dataset.mode === mode));
  els.panels.forEach(panel => panel.classList.toggle('active', panel.dataset.mode === mode));
  clearError();
  renderStep();
}

function renderStep() {
  els.fields.innerHTML = '';
  els.back.classList.toggle('hidden', currentStep === 'identify' || currentStep === 'profile');
  els.hint.textContent = '';
  els.submit.disabled = false;

  if (mode === 'login') {
    renderLoginStep();
  } else {
    renderRegisterStep();
  }
}

function addField(id, label, type = 'text', placeholder = '', attrs = {}) {
  const wrap = document.createElement('div');
  wrap.className = 'field';
  const lbl = document.createElement('label');
  lbl.textContent = label;
  lbl.htmlFor = id;
  const input = document.createElement('input');
  input.id = id;
  input.type = type;
  input.placeholder = placeholder;
  input.autocomplete = 'off';
  Object.entries(attrs).forEach(([k, v]) => input.setAttribute(k, v));
  wrap.appendChild(lbl);
  wrap.appendChild(input);
  els.fields.appendChild(wrap);
  return input;
}

function renderLoginStep() {
  switch (currentStep) {
    case 'identify':
      els.title.textContent = 'Login';
      els.subtitle.textContent = 'Enter username or email';
      addField('login', 'Login', 'text', 'username or email@mail.com');
      els.submit.textContent = 'Continue';
      break;
    case 'confirm-email':
      els.title.textContent = 'Email confirmation';
      els.subtitle.textContent = `Enter your full email address (${maskedEmail})`;
      addField('email', 'Email', 'email', 'your@email.com');
      els.submit.textContent = 'Confirm';
      break;
    case 'password':
      els.title.textContent = 'Password';
      els.subtitle.textContent = 'Enter account password';
      addField('password', 'Password', 'password', '••••••••••');
      els.submit.textContent = 'Continue';
      break;
    case 'otp':
      els.title.textContent = 'Email otp code';
      els.subtitle.textContent = 'OTP-code temporary appears in server console';
      addField('otp', 'Code', 'text', '123456', { maxlength: '6', inputmode: 'numeric' });
      els.submit.textContent = 'Log in';
      els.hint.textContent = 'After confirmation you will be redirected to chat';
      break;
    default:
      break;
  }
}

function renderRegisterStep() {
  switch (currentStep) {
    case 'profile':
      els.title.textContent = 'Registration';
      els.subtitle.textContent = 'Create new account';
      addField('username', 'Username', 'text', 'name_surname');
      addField('first_name', 'Name', 'text', 'Name');
      addField('last_name', 'Surname', 'text', 'Surname');
      addField('email', 'Email', 'email', 'example@mail.com');
      els.submit.textContent = 'Continue';
      break;
    case 'otp':
      els.title.textContent = 'Email confirmation';
      els.subtitle.textContent = 'OTP-code will appear in servers console';
      addField('otp', 'Code', 'text', '123456', { maxlength: '6', inputmode: 'numeric' });
      els.submit.textContent = 'Confirm';
      break;
    case 'password':
      els.title.textContent = 'Password';
      els.subtitle.textContent = 'Must be at least 10 characters, numbers and special symbols';
      addField('password', 'password', 'password', '••••••••••');
      els.submit.textContent = 'Continue';
      break;
    case 'confirm-password':
      els.title.textContent = 'Confirm password';
      els.subtitle.textContent = 'Enter your password again';
      addField('password2', 'password', 'password', '••••••••••');
      els.submit.textContent = 'Register';
      break;
    case 'done':
      els.title.textContent = 'All done!';
      els.subtitle.textContent = 'Account is created. Please log in using your details';
      els.fields.innerHTML = '<p class="success-msg">Registration completed successfully.</p>';
      els.submit.textContent = 'Start login';
      break;
    default:
      break;
  }
}

async function handleLoginSubmit() {
  if (currentStep === 'identify') {
    const login = document.getElementById('login').value.trim();
    if (!login) throw new Error('Enter login');
    if (!sessionToken) {
      const start = await authApi.startLogin();
      sessionToken = start.access_token;
    }
    const result = await authApi.identify(login, sessionToken);
    if (result.masked_email) {
      loginMethod = 'username';
      maskedEmail = result.masked_email;
      setStep('confirm-email');
    } else {
      loginMethod = 'email';
      setStep('password');
    }
    return;
  }

  if (currentStep === 'confirm-email') {
    const email = document.getElementById('email').value.trim();
    await authApi.confirmEmail(email, sessionToken);
    setStep('password');
    return;
  }

  if (currentStep === 'password') {
    const password = document.getElementById('password').value;
    await authApi.submitPassword(password, sessionToken);
    await authApi.sendLoginOtp(sessionToken);
    setStep('otp');
    return;
  }

  if (currentStep === 'otp') {
    const email_otp = document.getElementById('otp').value.trim();
    await authApi.confirmLoginOtp(email_otp, sessionToken);
    const token = await authApi.completeLogin(sessionToken);
    setToken(token.access_token);
    window.location.href = '/chat';
  }
}

async function handleRegisterSubmit() {
  if (currentStep === 'profile') {
    const body = {
      username: document.getElementById('username').value.trim(),
      first_name: document.getElementById('first_name').value.trim(),
      last_name: document.getElementById('last_name').value.trim(),
      email: document.getElementById('email').value.trim(),
    };
    if (!sessionToken) {
      const start = await authApi.startRegistration();
      sessionToken = start.access_token;
    }
    await authApi.submitProfile(body, sessionToken);
    await authApi.sendRegistrationOtp(sessionToken);
    setStep('otp');
    return;
  }

  if (currentStep === 'otp') {
    const email_otp = document.getElementById('otp').value.trim();
    await authApi.confirmRegistrationOtp(email_otp, sessionToken);
    setStep('password');
    return;
  }

  if (currentStep === 'password') {
    const password = document.getElementById('password').value;
    await authApi.submitRegistrationPassword(password, sessionToken);
    setStep('confirm-password');
    return;
  }

  if (currentStep === 'confirm-password') {
    const password = document.getElementById('password2').value;
    await authApi.confirmRegistrationPassword(password, sessionToken);
    await authApi.completeRegistration(sessionToken);
    setStep('done');
    return;
  }

  if (currentStep === 'done') {
    switchMode('login');
  }
}

els.form.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError();
  els.submit.disabled = true;
  try {
    if (mode === 'login') {
      await handleLoginSubmit();
    } else {
      await handleRegisterSubmit();
    }
  } catch (err) {
    showError(err.message);
  } finally {
    els.submit.disabled = false;
  }
});

els.back.addEventListener('click', () => {
  clearError();
  if (mode === 'login') {
    if (currentStep === 'otp') setStep('password');
    else if (currentStep === 'password') setStep(loginMethod === 'username' ? 'confirm-email' : 'identify');
    else if (currentStep === 'confirm-email') setStep('identify');
  } else {
    if (currentStep === 'confirm-password') setStep('password');
    else if (currentStep === 'password') setStep('otp');
    else if (currentStep === 'otp') setStep('profile');
  }
});

els.tabs.forEach(tab => {
  tab.addEventListener('click', () => switchMode(tab.dataset.mode));
});

renderStep();
