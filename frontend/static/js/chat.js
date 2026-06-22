import { chatApi, clearToken, getToken } from './api.js';

if (!getToken()) {
  window.location.href = '/';
}

let ws = null;
let currentUser = null;
let activeChatId = null;
let chats = [];
let onlineUserIds = new Set();
const unread = {};

const els = {
  myAvatar: document.getElementById('my-avatar'),
  myNameLabel: document.getElementById('my-name-label'),
  chatList: document.getElementById('chat-list'),
  messages: document.getElementById('messages'),
  chatWithName: document.getElementById('chat-with-name'),
  chatWithStatus: document.getElementById('chat-with-status'),
  chatWithAva: document.getElementById('chat-with-avatar'),
  msgInput: document.getElementById('msg-input'),
  sendBtn: document.getElementById('send-btn'),
  logoutBtn: document.getElementById('logout-btn'),
  newChatInput: document.getElementById('new-chat-input'),
  newChatBtn: document.getElementById('new-chat-btn'),
};

function initials(name) {
  return (name || '?').slice(0, 2).toUpperCase();
}

function formatTime(value) {
  const date = new Date(value);
  return date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function formatPreviewTime(value) {
  if (!value) return '';
  const date = new Date(value);
  const now = new Date();
  if (date.toDateString() === now.toDateString()) {
    return formatTime(value);
  }
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' });
}

function peerName(chat) {
  const p = chat.peer;
  return p.first_name ? `${p.first_name} ${p.last_name}` : p.username;
}

function connectWs() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  const token = encodeURIComponent(getToken());
  ws = new WebSocket(`${proto}://${location.host}/ws?token=${token}`);

  ws.addEventListener('message', (e) => {
    handleWsMessage(JSON.parse(e.data));
  });

  ws.addEventListener('close', () => {
    setTimeout(connectWs, 2500);
  });
}

function handleWsMessage(msg) {
  switch (msg.type) {
    case 'presence':
      onlineUserIds = new Set(msg.online_user_ids || []);
      chats = chats.map(c => ({
        ...c,
        peer: { ...c.peer, is_online: onlineUserIds.has(c.peer.id) },
      }));
      renderChatList();
      if (activeChatId) updateHeaderStatus();
      break;

    case 'message':
      handleIncomingMessage(msg.message);
      break;

    case 'new_chat':
      upsertChat(msg.chat);
      renderChatList();
      break;

    case 'chat_updated':
      upsertChat(msg.chat);
      renderChatList();
      break;

    case 'error':
      alert(msg.text);
      clearToken();
      window.location.href = '/';
      break;

    default:
      break;
  }
}

function upsertChat(chat) {
  const idx = chats.findIndex(c => c.id === chat.id);
  if (idx >= 0) chats[idx] = chat;
  else chats.unshift(chat);
  chats.sort((a, b) => {
    const ta = a.last_message?.created_at || a.created_at;
    const tb = b.last_message?.created_at || b.created_at;
    return tb.localeCompare(ta);
  });
}

function handleIncomingMessage(message) {
  const chat = chats.find(c => c.id === message.chat_id);
  if (chat) {
    chat.last_message = {
      id: message.id,
      text: message.text,
      sender_id: message.sender_id,
      created_at: message.created_at,
      is_mine: message.sender_id === currentUser.id,
    };
    upsertChat(chat);
  }

  if (message.chat_id === activeChatId) {
    appendBubble(message);
    scrollBottom();
  } else if (message.sender_id !== currentUser.id) {
    unread[message.chat_id] = (unread[message.chat_id] || 0) + 1;
  }

  renderChatList();
}

async function init() {
  try {
    currentUser = await chatApi.getMe();
    chats = await chatApi.getChats();
  } catch {
    clearToken();
    window.location.href = '/';
    return;
  }

  els.myNameLabel.textContent = currentUser.username;
  els.myAvatar.textContent = initials(currentUser.username);

  renderChatList();
  connectWs();
}

function renderChatList() {
  els.chatList.innerHTML = '';

  if (!chats.length) {
    const empty = document.createElement('li');
    empty.className = 'chat-list-empty';
    empty.textContent = 'Theres nothing here yet — create new chat above';
    els.chatList.appendChild(empty);
    return;
  }

  chats.forEach(chat => {
    const li = document.createElement('li');
    li.className = 'chat-list-item';
    if (chat.id === activeChatId) li.classList.add('active');
    li.dataset.chatId = chat.id;

    const ava = document.createElement('div');
    ava.className = 'avatar avatar-sm chat-list-avatar';
    ava.textContent = initials(chat.peer.username);

    const body = document.createElement('div');
    body.className = 'chat-list-body';

    const top = document.createElement('div');
    top.className = 'chat-list-top';

    const name = document.createElement('span');
    name.className = 'chat-list-name';
    name.textContent = peerName(chat);

    const time = document.createElement('span');
    time.className = 'chat-list-time';
    time.textContent = formatPreviewTime(chat.last_message?.created_at);

    top.appendChild(name);
    top.appendChild(time);

    const bottom = document.createElement('div');
    bottom.className = 'chat-list-bottom';

    const preview = document.createElement('span');
    preview.className = 'chat-list-preview';
    if (chat.last_message) {
      preview.textContent = chat.last_message.is_mine
        ? `Вы: ${chat.last_message.text}`
        : chat.last_message.text;
    } else {
      preview.textContent = 'Theres no messages';
    }

    const dot = document.createElement('span');
    dot.className = `dot ${chat.peer.is_online ? 'dot-green' : 'dot-gray'}`;

    bottom.appendChild(preview);
    bottom.appendChild(dot);

    body.appendChild(top);
    body.appendChild(bottom);
    li.appendChild(ava);
    li.appendChild(body);

    if (unread[chat.id]) {
      const badge = document.createElement('span');
      badge.className = 'notif-badge';
      badge.textContent = unread[chat.id];
      li.appendChild(badge);
    }

    li.addEventListener('click', () => openChat(chat.id));
    els.chatList.appendChild(li);
  });
}

async function openChat(chatId) {
  activeChatId = chatId;
  delete unread[chatId];

  const chat = chats.find(c => c.id === chatId);
  if (!chat) return;

  els.chatWithName.textContent = peerName(chat);
  els.chatWithAva.textContent = initials(chat.peer.username);
  updateHeaderStatus();

  els.msgInput.disabled = false;
  els.sendBtn.disabled = false;
  els.msgInput.focus();

  els.messages.innerHTML = '<div class="loading-state">Loading…</div>';

  try {
    const history = await chatApi.getMessages(chatId);
    els.messages.innerHTML = '';
    if (!history.length) {
      els.messages.innerHTML = `
        <div class="empty-state fade-in">
          <p>Start chat with <strong>${chat.peer.username}</strong></p>
        </div>`;
    } else {
      history.forEach(appendBubble);
      scrollBottom();
    }
  } catch (err) {
    els.messages.innerHTML = `<div class="empty-state"><p>${err.message}</p></div>`;
  }

  renderChatList();
}

function updateHeaderStatus() {
  const chat = chats.find(c => c.id === activeChatId);
  if (!chat) return;
  els.chatWithStatus.textContent = chat.peer.is_online ? 'Online' : 'Offline';
}

function appendBubble(message) {
  const empty = els.messages.querySelector('.empty-state, .loading-state');
  if (empty) empty.remove();

  const isMine = message.sender_id === currentUser.id;
  const wrap = document.createElement('div');
  wrap.className = `bubble-wrap ${isMine ? 'out' : 'in'} fade-in`;

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = message.text;

  const meta = document.createElement('div');
  meta.className = 'bubble-meta';
  meta.textContent = formatTime(message.created_at);

  wrap.appendChild(bubble);
  wrap.appendChild(meta);
  els.messages.appendChild(wrap);
}

function scrollBottom() {
  els.messages.scrollTop = els.messages.scrollHeight;
}

function sendMessage() {
  const text = els.msgInput.value.trim();
  if (!text || !activeChatId || !ws || ws.readyState !== WebSocket.OPEN) return;

  ws.send(JSON.stringify({ type: 'message', chat_id: activeChatId, text }));
  els.msgInput.value = '';
}

els.sendBtn.addEventListener('click', sendMessage);
els.msgInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

els.logoutBtn.addEventListener('click', () => {
  clearToken();
  ws?.close();
  window.location.href = '/';
});

async function createNewChat() {
  const username = els.newChatInput.value.trim();
  if (!username) return;

  els.newChatBtn.disabled = true;
  try {
    const chat = await chatApi.createChat(username);
    upsertChat(chat);
    renderChatList();
    els.newChatInput.value = '';
    openChat(chat.id);
  } catch (err) {
    alert(err.message);
  } finally {
    els.newChatBtn.disabled = false;
  }
}

els.newChatBtn.addEventListener('click', createNewChat);
els.newChatInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    e.preventDefault();
    createNewChat();
  }
});

init();
