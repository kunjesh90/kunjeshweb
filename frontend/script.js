// ✅ Voice Assistant + Speaker Icon Enhanced Chatbot

let isProcessing = false;
let isFirstUserMessage = true;

// 🎤 Speech Recognition Setup
let recognition;
if ("webkitSpeechRecognition" in window || "SpeechRecognition" in window) {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.continuous = false;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById("user-input").value += " " + transcript;
  };

  recognition.onerror = (event) => {
    console.error("Speech recognition error", event);
  };
} else {
  console.warn("SpeechRecognition not supported");
}

// 🔊 Speech Synthesis
function speakText(text) {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

// DOM Ready Logic
window.addEventListener("DOMContentLoaded", () => {
  const chatMessages = document.getElementById("chat-messages");

  if (chatMessages.childElementCount === 0) addWelcomeMessage();

  // Collapsibles (if any)
  document.querySelectorAll(".collapsible").forEach((btn) => {
    btn.addEventListener("click", function () {
      const details = this.nextElementSibling;
      if (details && details.classList.contains("details")) {
        details.classList.toggle("show");
        this.textContent = details.classList.contains("show") ? "Hide Details" : "Show Details";
      }
    });
  });

  // Reset history
  document.getElementById("reset-history").addEventListener("click", () => {
    chatMessages.innerHTML = "";
    addWelcomeMessage();
    isFirstUserMessage = true;
  });
});

// Chat UI Toggles
document.getElementById("chat-icon").onclick = () => {
  document.getElementById("chat-window").style.display = "flex";
};
document.getElementById("close-chat").onclick = () => {
  document.getElementById("chat-window").style.display = "none";
};

// Event Bindings
const sendButton = document.getElementById("send-message");
const userInputEl = document.getElementById("user-input");
const micButton = document.getElementById("mic-button");

sendButton.addEventListener("click", sendMessage);
userInputEl.addEventListener("keypress", (e) => {
  if (e.key === "Enter") sendMessage();
});

micButton.addEventListener("mousedown", () => recognition?.start());
micButton.addEventListener("mouseup", () => recognition?.stop());
micButton.addEventListener("touchstart", () => recognition?.start());
micButton.addEventListener("touchend", () => recognition?.stop());

// Auto-scroll helper
function autoScroll() {
  const chatBody = document.getElementById("chat-body");
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Welcome greeting
function addWelcomeMessage() {
  const welcome = document.createElement("p");
  welcome.className = "bot-message welcome-message";
  welcome.textContent = "Hi! I’m the AI voice of Kunjesh. My avatar is ready to interact!";
  document.getElementById("chat-messages").appendChild(welcome);
  autoScroll();
}

// Send Message Function
async function sendMessage() {
  if (isProcessing) return;

  const userInput = userInputEl.value.trim();
  if (!userInput) return;

  isProcessing = true;
  sendButton.disabled = true;
  sendButton.classList.add("disabled-button");

  // Display user message
  const userMsg = document.createElement("p");
  userMsg.className = "user-message";
  userMsg.textContent = userInput;
  document.getElementById("chat-messages").appendChild(userMsg);
  userInputEl.value = "";
  autoScroll();

  // First-time loading notice
  if (isFirstUserMessage) {
    const notice = document.createElement("p");
    notice.className = "bot-message first-delay-notice";
    notice.textContent = "The backend systems are getting ready... Hang on.";
    document.getElementById("chat-messages").appendChild(notice);
    autoScroll();
    isFirstUserMessage = false;
  }

  try {
    const response = await fetch(`https://kunj-backend.onrender.com/ask?query=${encodeURIComponent(userInput)}`);
    const data = await response.json();

    const botText = data.response;
    const botMsg = document.createElement("div");
    botMsg.className = "bot-message";

    // Escape backticks for template safety
    const safeBotText = botText.replace(/`/g, "\\`");

    // Inject speaker icon
    botMsg.innerHTML = `
      <span>${botText}</span>
      <button class="speaker-button" onclick="speakText(\`${safeBotText}\`)">
        <i class="fas fa-volume-up"></i>
      </button>
    `;
    document.getElementById("chat-messages").appendChild(botMsg);
  } catch (error) {
    console.error("Chat error:", error);
    const errMsg = document.createElement("p");
    errMsg.className = "bot-message";
    errMsg.textContent = "Something went wrong. Please try again.";
    document.getElementById("chat-messages").appendChild(errMsg);
  } finally {
    isProcessing = false;
    sendButton.disabled = false;
    sendButton.classList.remove("disabled-button");
    autoScroll();
  }
}
