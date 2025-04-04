// Run once DOM is fully loaded
document.addEventListener("DOMContentLoaded", function () {
  const chatMessages = document.getElementById("chat-messages");

  // Ensure no duplicate welcome message
  if (chatMessages.childElementCount === 0) {
    addWelcomeMessage();
  }

  // Collapsible logic for show/hide details
  const collapsibles = document.querySelectorAll(".collapsible");
  collapsibles.forEach((collapsible) => {
    collapsible.addEventListener("click", function () {
      const details = this.nextElementSibling;
      if (details && details.classList.contains("details")) {
        details.classList.toggle("show");
        this.textContent = details.classList.contains("show") ? "Hide Details" : "Show Details";
      }
    });
  });

  // Reset Chat History
  document.getElementById("reset-history").addEventListener("click", function () {
    chatMessages.innerHTML = ""; // Clear messages
    addWelcomeMessage(); // Add welcome message again
  });
});

// Open chat window
document.getElementById("chat-icon").addEventListener("click", function () {
  document.getElementById("chat-window").style.display = "flex";
});

// Close chat window
document.getElementById("close-chat").addEventListener("click", function () {
  document.getElementById("chat-window").style.display = "none";
});

// Send message events
document.getElementById("send-message").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
  if (event.key === "Enter") sendMessage();
});

// Auto-scroll to latest message
function autoScroll() {
  let chatBody = document.getElementById("chat-body");
  chatBody.scrollTop = chatBody.scrollHeight;
}

// Function to add the welcome message (avoid duplication)
function addWelcomeMessage() {
  const chatMessages = document.getElementById("chat-messages");

  // Ensure welcome message is not added twice
  if (!document.querySelector(".welcome-message")) {
    let welcomeMessage = document.createElement("p");
    welcomeMessage.classList.add("bot-message", "welcome-message");
    welcomeMessage.textContent = "Hi! I’m the AI voice of Kunjesh. My avatar is loading soon — stay tuned!";
    chatMessages.appendChild(welcomeMessage);
    autoScroll();
  }
}

// Function to send message to backend
async function sendMessage() {
  let userInput = document.getElementById("user-input").value.trim();
  if (userInput === "") return;

  // Add user message
  let userMessage = document.createElement("p");
  userMessage.classList.add("user-message");
  userMessage.textContent = userInput;
  document.getElementById("chat-messages").appendChild(userMessage);
  document.getElementById("user-input").value = ""; // Clear input

  autoScroll();

  // Fetch response from FastAPI backend
  try {
    const response = await fetch(`https://kunj-backend.onrender.com/ask?query=${encodeURIComponent(userInput)}`);
    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    // Add bot response
    let botMessage = document.createElement("p");
    botMessage.classList.add("bot-message");
    botMessage.textContent = data.response;
    document.getElementById("chat-messages").appendChild(botMessage);

    autoScroll();
  } catch (error) {
    console.error("Error fetching response:", error);

    // Show fallback error message
    let errorMessage = document.createElement("p");
    errorMessage.classList.add("bot-message");
    errorMessage.textContent = "Sorry, something went wrong while fetching my response. Please try again later.";
    document.getElementById("chat-messages").appendChild(errorMessage);

    autoScroll();
  }
}
