function showChatbot() {
  const scriptTag = document.currentScript;
  const initKey = scriptTag.getAttribute('init_key');
 
  if (!initKey) {
    console.error("Chatbot init_key not provided.");
    return;
  }
 
  const API_BASE = "http://localhost:5000/api/chatbot";
 
  const chatButton = document.createElement('button');
  chatButton.textContent = '💬';
  chatButton.style = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    padding: 12px;
    background-color: #007bff;
    color: #fff;
    border: none;
    border-radius: 50%;
    font-size: 18px;
    cursor: pointer;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    z-index: 999;
  `;
  document.body.appendChild(chatButton);
 
  const chatPopup = document.createElement('div');
  chatPopup.style = `
    position: fixed;
    bottom: 80px;
    right: 20px;
    width: 400px;
    height: 550px;
    background-color: #fff;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    display: none;
    flex-direction: column;
    overflow: hidden;
    z-index: 1000;
  `;
  chatPopup.innerHTML = `
<div style="background-color: #007bff; color: #fff; padding: 10px 15px; display: flex; justify-content: space-between; align-items: center;">
<span style="font-size: 20px;">🤖 <b>CampusIQ</b></span>
<div style="display: flex; gap: 5px;">
<button id="minimize-btn" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;">_</button>
<button id="close-btn" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer;margin-top: 10px">×</button>
</div>
</div>
<div id="chat-messages" style="flex-grow: 1; padding: 10px 10px 80px 10px; overflow-y: auto;"></div>
<div id="chat-input-area" style="display: flex; padding: 10px; border-top: 1px solid #ccc; background: #fff; position: absolute; bottom: 0; width: 100%; box-sizing: border-box;">
<input id="chat-input" type="text" placeholder="Type your message..." style="flex-grow: 1; padding: 8px; border: 1px solid #ccc; border-radius: 4px; margin-right: 10px;" />
<button id="send-btn" style="background: none; border: none; color: #007bff; font-size: 24px; cursor: pointer;">🚀</button>
</div>
  `;
  document.body.appendChild(chatPopup);
 
  const closeBtn = chatPopup.querySelector('#close-btn');
  const minimizeBtn = chatPopup.querySelector('#minimize-btn');
  const chatMessages = chatPopup.querySelector('#chat-messages');
  const chatInputArea = chatPopup.querySelector('#chat-input-area');
  const chatInput = chatPopup.querySelector('#chat-input');
  const sendBtn = chatPopup.querySelector('#send-btn');
 
  closeBtn.addEventListener('click', () => {
    chatPopup.style.display = 'none';
  });
 
  minimizeBtn.addEventListener('click', () => {
    const isMinimized = chatMessages.style.display !== 'none';
    chatMessages.style.display = isMinimized ? 'none' : 'block';
    chatInputArea.style.display = isMinimized ? 'none' : 'flex';
    chatPopup.style.height = isMinimized ? '60px' : '550px';
  });
 
  function addMessage(text, sender) {
    const wrapper = document.createElement('div');
    wrapper.style = `
     
      width: 100%;
      margin-bottom: 12px;
      justify-content: ${sender === 'user' ? 'flex-end' : 'flex-start'};
      align-items: flex-end;
    `;
 
    if (sender === 'bot') {
      const avatar = document.createElement('div');
      avatar.innerHTML = '🛸';
      avatar.style = `font-size: 22px; margin-right: 8px;`;
      wrapper.appendChild(avatar);
    }
 
    const msg = document.createElement('div');
    msg.innerHTML = parseEmojis(text);
    msg.style = `
      padding: 8px;
      border-radius: 4px;
      background-color: ${sender === 'user' ? '#e2f7cb' : '#f0f0f0'};
      max-width: 87%;
      word-wrap: break-word;
      display: inline-block;
    `;
 
    const time = document.createElement('div');
    time.textContent = getTimeString();
    time.style = `
      font-size: 11px;
      color: #888;
      margin-top: 4px;
      text-align: ${sender === 'user' ? 'right' : 'left'};
    `;
 
    const msgContainer = document.createElement('div');
    msgContainer.style = `
      display: flex;
      flex-direction: column;
      align-items: ${sender === 'user' ? 'flex-end' : 'flex-start'};
      max-width: 100%;
    `;
    msgContainer.appendChild(msg);
    msgContainer.appendChild(time);
 
    wrapper.appendChild(msgContainer);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }
 
  async function sendUserMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    addMessage(text, 'user');
    chatInput.value = '';
 
    const loaderWrapper = document.createElement('div');
    loaderWrapper.className = 'bot-loader';
    loaderWrapper.style = `
      display: flex;
      margin-bottom: 12px;
      justify-content: flex-start;
      align-items: center;
    `;
    loaderWrapper.innerHTML = `
<div style="font-size: 22px; margin-right: 8px;">🤖</div>
<span class="loader" style="
        border-radius: 50%;
        width: 1.8em;
        height: 1.8em;
        animation-fill-mode: both;
        animation: bblFadInOut 1.8s infinite ease-in-out;
        color: #007bff;
        font-size: 6px;
        position: relative;
        text-indent: -9999em;
        transform: translateZ(0);
        animation-delay: -0.16s;
      "></span>
 
      <style>
        @keyframes bblFadInOut {
          0%, 80%, 100% { box-shadow: 0 1.8em 0 -1em }
          40% { box-shadow: 0 1.8em 0 0 }
        }
        .loader::before, .loader::after {
          content: '';
          position: absolute;
          top: 0;
          border-radius: 50%;
          width: 1.8em;
          height: 1.8em;
          animation-fill-mode: both;
          animation: bblFadInOut 1.8s infinite ease-in-out;
        }
        .loader::before {
          left: -2.5em;
          animation-delay: -0.32s;
        }
        .loader::after {
          left: 2.5em;
        }
</style>
    `;
    chatMessages.appendChild(loaderWrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
 
    try {
      const response = await fetch(`${API_BASE}/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': initKey
        },
        body: JSON.stringify({ message: text })
      });
 
      loaderWrapper.remove();
 
      if (!response.ok) {
        const errorText = response.status === 401
          ? "Chatbot is disabled or access denied. 😢"
          : "Something went wrong. 😢";
        addMessage(errorText, 'bot');
        return;
      }
 
      const data = await response.json();
      let reply = data?.reply?.replaceAll('```html','') || '';
      //reply+="<br> <strong>("+data.source+")</strong>";
      addMessage(reply, 'bot');
    } catch (err) {
      loaderWrapper.remove();
      console.error(err);
      addMessage("Oops! API error. 😢", 'bot');
    }
  }
 
  sendBtn.addEventListener('click', sendUserMessage);
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      sendUserMessage();
    }
  });
 
  chatButton.addEventListener('click', async () => {
    const shouldShow = chatPopup.style.display === 'none';
    chatPopup.style.display = shouldShow ? 'flex' : 'none';
 
    if (shouldShow && !chatMessages.hasChildNodes()) {
      try {
        const response = await fetch(`${API_BASE}/greeting`, {
          headers: {
            'Authorization': initKey
          }
        });
 
        if (!response.ok) {
          addMessage("Chatbot not enabled or unauthorized. 😕", 'bot');
          return;
        }
 
        const data = await response.json();
        addMessage(data.bot, 'bot');
      } catch (e) {
        console.error(e);
        addMessage("Hello! How can I help you today? 👋", 'bot');
      }
    }
  });
 
  function getTimeString() {
    const now = new Date();
    let hours = now.getHours();
    const minutes = now.getMinutes();
    const ampm = hours >= 12 ? 'PM' : 'AM';
    hours = hours % 12 || 12;
    const day = now.getDate();
    const month = now.getMonth() + 1;
    const year = now.getFullYear();
    return `${month.toString().padStart(2, '0')}/${day.toString().padStart(2, '0')}/${year} ${hours}:${minutes.toString().padStart(2, '0')} ${ampm}`;
  }
 
  function parseEmojis(text) {
    const emojiMap = {
      ':smile:': '😄',
      ':wave:': '👋',
      ':robot:': '🤖',
      ':heart:': '❤️',
      ':thumbsup:': '👍',
      ':check:': '✅'
    };
    return text.replace(/:\w+:/g, match => emojiMap[match] || match);
  }
}
 
showChatbot();