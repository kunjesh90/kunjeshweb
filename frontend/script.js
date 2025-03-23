document.addEventListener("DOMContentLoaded", function () {
  const collapsibles = document.querySelectorAll(".collapsible");

  collapsibles.forEach((collapsible) => {
    collapsible.addEventListener("click", function () {
      const details = this.nextElementSibling;

      if (details && details.classList.contains("details")) {
        details.classList.toggle("show");

        if (details.classList.contains("show")) {
          this.textContent = "Hide Details";
        } else {
          this.textContent = "Show Details";
        }
      }
    });
  });
});

// Chatbot JS code starts
document.getElementById("chat-icon").addEventListener("click", function () {
  document.getElementById("chat-window").style.display = "flex";
});

document.getElementById("close-chat").addEventListener("click", function () {
  document.getElementById("chat-window").style.display = "none";
});

document.getElementById("send-message").addEventListener("click", sendMessage);
document.getElementById("user-input").addEventListener("keypress", function (event) {
  if (event.key === "Enter") {
    sendMessage();
  }
});

// Function to send message to FastAPI backend and get RAG response
async function sendMessage() {
  let userInput = document.getElementById("user-input").value;
  if (userInput.trim() === "") return;
  console.log("Sending message:", userInput);  // Log the user input being sent

  // Add User Message
  let userMessage = document.createElement("p");
  userMessage.classList.add("user-message");
  userMessage.textContent = userInput;
  document.getElementById("chat-messages").appendChild(userMessage);

  document.getElementById("user-input").value = ""; // Clear input
  
  // Call the RAG system (FastAPI) for a response
  
  try {
    console.log("Making fetch request to backend...");
    const response = await fetch(
      `https://profilebck.onrender.com/ask?query=${encodeURIComponent(userInput)}`
    );
    console.log("Received response from backend:", response); // Log the response object

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    console.log("Parsed response data:", data); // Log the parsed response data

    // Display the bot's response
    let botMessage = document.createElement("p");
    botMessage.classList.add("bot-message");
    botMessage.textContent = data.response;
    document.getElementById("chat-messages").appendChild(botMessage);

    // Scroll to latest message
    document.getElementById("chat-body").scrollTop = document.getElementById("chat-body").scrollHeight;

  } catch (error) {
    console.error("Error fetching response:", error);
  }
}
// Chatbot JS code ends
