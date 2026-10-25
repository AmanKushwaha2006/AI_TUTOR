/* ==========================================================================
   ORION: Next-Gen AI Tutor Web UI Controller
   Features: Multi-agent query, Offline Voice Recognition, RAG Integration,
             Topic Selection, Clipboard copying, Audio playback.
   ========================================================================== */

document.addEventListener("DOMContentLoaded", function () {
  // Enter key event listener on input field
  const userInput = document.getElementById("user-input");
  if (userInput) {
    userInput.addEventListener("keydown", handleTextareaInput);
  }

  // Clear session on fresh page load/refresh
  clearSession();
});

// Global state
let isListening = false;

// Scroll chat viewport to bottom
function scrollToBottom() {
  const chatBox = document.getElementById("chat-box");
  const viewport = document.querySelector(".chat-viewport");
  if (chatBox) chatBox.scrollTop = chatBox.scrollHeight;
  if (viewport) viewport.scrollTop = viewport.scrollHeight;
}

// Clear session when page is refreshed or new chat started
function clearSession() {
  fetch("/clear-session", {
    method: "POST",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Session cleared:", data.message);
      updateRagStatus(false);
    })
    .catch((error) => {
      console.error("Error clearing session:", error);
    });
}

// Start New Chat (Reset UI and state)
function startNewChat() {
  const chatBox = document.getElementById("chat-box");
  if (chatBox) chatBox.innerHTML = "";

  const heroSection = document.getElementById("hero-section");
  if (heroSection) heroSection.classList.remove("collapsed");

  const input = document.getElementById("user-input");
  if (input) {
    input.value = "";
    input.style.height = "auto";
  }

  clearSession();
  stopSpeech();

  setTimeout(() => {
    showWelcomeMessage();
  }, 350);
}

// Triggered when user clicks a topic card
function selectTopic(queryText) {
  const input = document.getElementById("user-input");
  if (input) {
    input.value = queryText;
  }
  const heroSection = document.getElementById("hero-section");
  if (heroSection) {
    heroSection.classList.add("collapsed");
  }
  sendMessage();
}

// Triggered from Document RAG topic card
function triggerPdfUploadPrompt() {
  const fileInput = document.getElementById("pdf-files");
  if (fileInput) fileInput.click();
}

// Copy AI response text to clipboard
function copyMessageText(btn) {
  const aiMessage = btn.closest(".ai-message");
  if (!aiMessage) return;
  const bodyText = aiMessage.querySelector(".ai-body")?.innerText || "";

  navigator.clipboard
    .writeText(bodyText)
    .then(() => {
      const originalHtml = btn.innerHTML;
      btn.innerHTML = `<i class="fa-solid fa-check"></i> <span>Copied!</span>`;
      btn.style.color = "#34d399";
      setTimeout(() => {
        btn.innerHTML = originalHtml;
        btn.style.color = "";
      }, 1800);
    })
    .catch((err) => {
      console.error("Failed to copy:", err);
    });
}

// Speak specific message
function speakMessageText(btn) {
  const aiMessage = btn.closest(".ai-message");
  if (!aiMessage) return;
  const bodyText = aiMessage.querySelector(".ai-body")?.innerText || "";
  fetch("/text-to-speech", {
    method: "POST",
    body: JSON.stringify({ text: bodyText }),
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .catch((error) => console.error("Error speaking message:", error));
}

// Display uploaded files badge in chat
function displayFileNames(files) {
  const chatBox = document.getElementById("chat-box");
  const fileNameDisplay = document.createElement("div");
  fileNameDisplay.className = "file-name-display";

  const fileNames = Array.from(files)
    .map((file) => `📄 ${file.name}`)
    .join(", ");
  fileNameDisplay.innerHTML = `<strong>ORION:</strong> Loading study documents: ${fileNames}`;
  chatBox.appendChild(fileNameDisplay);
  scrollToBottom();
}

// Handle single or multiple PDF file uploads
function handleFileUpload(files) {
  if (!files || files.length === 0) return;

  const heroSection = document.getElementById("hero-section");
  if (heroSection) heroSection.classList.add("collapsed");

  displayFileNames(files);

  const chatBox = document.getElementById("chat-box");
  const initializingMessage = document.createElement("div");
  initializingMessage.className = "ai-message";
  initializingMessage.innerHTML = `
    <div class="ai-header">
      <div class="ai-author">
        <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
        <span>ORION</span>
        <span class="ai-badge">RAG SYSTEM</span>
      </div>
    </div>
    <div class="ai-body"><p>Initializing RAG system with uploaded PDF documents...</p></div>
  `;
  chatBox.appendChild(initializingMessage);
  scrollToBottom();

  // Show loading overlay
  const loadingIndicator = document.getElementById("loading-indicator");
  if (loadingIndicator) loadingIndicator.classList.remove("hidden");

  const formData = new FormData();
  Array.from(files).forEach((file) => {
    formData.append("files", file);
  });

  fetch("/initialize-rag", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");

      const ragMessage = document.createElement("div");
      ragMessage.className = "ai-message";

      if (data.success) {
        ragMessage.innerHTML = `
          <div class="ai-header">
            <div class="ai-author">
              <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
              <span>ORION</span>
              <span class="ai-badge">RAG ACTIVE</span>
            </div>
          </div>
          <div class="ai-body"><p>✅ <strong>RAG initialized successfully!</strong> You can now ask questions directly grounded in your uploaded documents.</p></div>
        `;
        updateRagStatus(true);
      } else {
        ragMessage.innerHTML = `
          <div class="ai-header">
            <div class="ai-author">
              <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
              <span>ORION</span>
            </div>
          </div>
          <div class="ai-body"><p>❌ Failed to initialize RAG. Falling back to standard live research mode.</p></div>
        `;
        updateRagStatus(false);
      }

      chatBox.appendChild(ragMessage);
      scrollToBottom();
    })
    .catch((error) => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");
      console.error("RAG initialization error:", error);

      const errorMessage = document.createElement("div");
      errorMessage.className = "ai-message";
      errorMessage.innerHTML = `
        <div class="ai-header">
          <div class="ai-author">
            <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
            <span>ORION</span>
          </div>
        </div>
        <div class="ai-body"><p>❌ Error initializing RAG. Falling back to standard live research mode.</p></div>
      `;
      chatBox.appendChild(errorMessage);
      scrollToBottom();
      updateRagStatus(false);
    });
}

// Handle folder uploads
function handleFolderUpload(files) {
  if (!files || files.length === 0) return;

  const heroSection = document.getElementById("hero-section");
  if (heroSection) heroSection.classList.add("collapsed");

  const folderName = files[0].webkitRelativePath.split("/")[0];
  const chatBox = document.getElementById("chat-box");

  const folderNameDisplay = document.createElement("div");
  folderNameDisplay.className = "file-name-display";
  folderNameDisplay.innerHTML = `<strong>ORION:</strong> Loading folder documents: 📁 ${folderName}`;
  chatBox.appendChild(folderNameDisplay);
  scrollToBottom();

  const loadingIndicator = document.getElementById("loading-indicator");
  if (loadingIndicator) loadingIndicator.classList.remove("hidden");

  const formData = new FormData();
  formData.append("folder", folderName);

  fetch("/initialize-rag", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");

      const ragMessage = document.createElement("div");
      ragMessage.className = "ai-message";

      if (data.success) {
        ragMessage.innerHTML = `
          <div class="ai-header">
            <div class="ai-author">
              <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
              <span>ORION</span>
              <span class="ai-badge">RAG ACTIVE</span>
            </div>
          </div>
          <div class="ai-body"><p>✅ <strong>RAG initialized successfully with folder documents!</strong> You can now ask questions about the uploaded material.</p></div>
        `;
        updateRagStatus(true);
      } else {
        ragMessage.innerHTML = `
          <div class="ai-header">
            <div class="ai-author">
              <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
              <span>ORION</span>
            </div>
          </div>
          <div class="ai-body"><p>❌ Failed to initialize RAG with folder documents.</p></div>
        `;
        updateRagStatus(false);
      }

      chatBox.appendChild(ragMessage);
      scrollToBottom();
    })
    .catch((error) => {
      if (loadingIndicator) loadingIndicator.classList.add("hidden");
      console.error("RAG folder initialization error:", error);

      const errorMessage = document.createElement("div");
      errorMessage.className = "ai-message";
      errorMessage.innerHTML = `
        <div class="ai-header">
          <div class="ai-author">
            <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
            <span>ORION</span>
          </div>
        </div>
        <div class="ai-body"><p>❌ Error initializing RAG with folder.</p></div>
      `;
      chatBox.appendChild(errorMessage);
      scrollToBottom();
      updateRagStatus(false);
    });
}

// Update Header Status Badge
function updateRagStatus(isActive) {
  const statusDot = document.querySelector(".status-dot");
  const statusText = document.querySelector(".status-text");

  if (statusDot && statusText) {
    if (isActive) {
      statusDot.classList.remove("inactive");
      statusDot.classList.add("active");
      statusText.textContent = "📚 Document RAG Active";
    } else {
      statusDot.classList.remove("active");
      statusDot.classList.add("inactive");
      statusText.textContent = "🌐 Web Research Mode";
    }
  }
}

// Render animated thinking / synthesis indicator
function setAIMessageToThinking(messageElement) {
  messageElement.innerHTML = `
    <div class="thinking-box">
      <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
      <span>ORION is synthesizing knowledge</span>
      <div class="thinking-dots">
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
        <div class="thinking-dot"></div>
      </div>
    </div>
  `;
}

// Send Message
function sendMessage() {
  const inputElem = document.getElementById("user-input");
  let userInput = inputElem.value.trim();
  if (userInput === "") return;

  // Collapse hero section
  const heroSection = document.getElementById("hero-section");
  if (heroSection) {
    heroSection.classList.add("collapsed");
  }

  const chatBox = document.getElementById("chat-box");

  // Display user message (Right-aligned)
  const userMessage = document.createElement("div");
  userMessage.className = "user-message";
  userMessage.innerHTML = `<strong>You:</strong> ${userInput.replace(/</g, "&lt;").replace(/>/g, "&gt;")}`;
  chatBox.appendChild(userMessage);

  // Clear input field and reset height
  inputElem.value = "";
  inputElem.style.height = "auto";

  // Create and show thinking state
  const thinkingMessage = document.createElement("div");
  thinkingMessage.className = "ai-message";
  setAIMessageToThinking(thinkingMessage);
  chatBox.appendChild(thinkingMessage);

  scrollToBottom();

  // Send request to backend
  fetch("/ask", {
    method: "POST",
    body: JSON.stringify({ query: userInput }),
    headers: { "Content-Type": "application/json" },
  })
    .then((response) => response.json())
    .then((data) => {
      // Remove thinking message
      if (thinkingMessage.parentNode === chatBox) {
        chatBox.removeChild(thinkingMessage);
      }

      // Display AI response
      const aiMessage = document.createElement("div");
      aiMessage.className = "ai-message";
      let renderedHtml =
        typeof marked !== "undefined" && marked.parse
          ? marked.parse(data.response)
          : data.response.replace(/\n/g, "<br>");

      aiMessage.innerHTML = `
        <div class="ai-header">
          <div class="ai-author">
            <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
            <span>ORION</span>
            <span class="ai-badge">AI TUTOR</span>
          </div>
          <div class="ai-actions">
            <button class="copy-btn" onclick="copyMessageText(this)" title="Copy Response">
              <i class="fa-regular fa-copy"></i>
              <span>Copy</span>
            </button>
            <button class="copy-btn" onclick="speakMessageText(this)" title="Read Aloud">
              <i class="fa-solid fa-volume-high"></i>
              <span>Listen</span>
            </button>
          </div>
        </div>
        <div class="ai-body">${renderedHtml}</div>
      `;
      chatBox.appendChild(aiMessage);

      // Scraped information accordion
      if (data.hasScraping && data.scraped) {
        const scrapedInfo = document.createElement("div");
        scrapedInfo.className = "scraped-info";
        scrapedInfo.innerHTML = `
          <details>
            <summary><i class="fa-solid fa-globe"></i> View Web Research Citations</summary>
            <div class="scraped-content">${data.scraped}</div>
          </details>
        `;
        chatBox.appendChild(scrapedInfo);
      }

      // Retrieval information accordion
      if (data.hasRetrieval && data.retrieved) {
        const retrievalInfo = document.createElement("div");
        retrievalInfo.className = "retrieval-info";
        retrievalInfo.innerHTML = `
          <details>
            <summary><i class="fa-solid fa-book-bookmark"></i> View Document Evidence (RAG)</summary>
            <div class="retrieved-content">${data.retrieved}</div>
          </details>
        `;
        chatBox.appendChild(retrievalInfo);
      }

      scrollToBottom();
    })
    .catch((error) => {
      if (thinkingMessage.parentNode === chatBox) {
        chatBox.removeChild(thinkingMessage);
      }

      const errorMessage = document.createElement("div");
      errorMessage.className = "ai-message";
      errorMessage.innerHTML = `
        <div class="ai-header">
          <div class="ai-author">
            <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
            <span>ORION</span>
          </div>
        </div>
        <div class="ai-body"><p>⚠️ Sorry, I encountered an error processing your question. Please verify your connection or try again.</p></div>
      `;
      chatBox.appendChild(errorMessage);
      console.error("Error sending message:", error);
      scrollToBottom();
    });
}

// Voice input controls (Offline Vosk Speech-to-Text)
function toggleVoiceInput() {
  if (isListening) {
    stopVoiceInput();
  } else {
    startVoiceInput();
  }
}

function startVoiceInput() {
  if (isListening) {
    stopVoiceInput();
    return;
  }

  const popup = document.getElementById("listening-popup");
  const micButton = document.querySelector(".mic-button");
  const listeningText = document.getElementById("listening-text");

  isListening = true;
  if (micButton) micButton.classList.add("active");
  if (popup) popup.classList.remove("hidden");
  if (listeningText) listeningText.textContent = "Listening to your sentence...";

  fetch("/speech-to-text", { method: "POST" })
    .then((response) => response.json())
    .then((data) => {
      closeListeningUI();

      if (data.query && data.query.trim() !== "") {
        const userInput = document.getElementById("user-input");
        if (userInput) {
          userInput.value = data.query;
          sendMessage();
        }
      } else {
        console.log("No speech transcribed");
      }
    })
    .catch((error) => {
      console.error("Speech recognition error:", error);
      closeListeningUI();
    });
}

function stopVoiceInput() {
  if (!isListening) return;

  const listeningText = document.getElementById("listening-text");
  if (listeningText) {
    listeningText.textContent = "Finalizing your sentence...";
  }

  fetch("/stop-listening", { method: "POST" })
    .then((response) => response.json())
    .then((data) => console.log("Stop listening acknowledged:", data))
    .catch((error) => console.error("Error signaling stop listening:", error));
}

function closeListeningUI() {
  isListening = false;
  const popup = document.getElementById("listening-popup");
  const micButton = document.querySelector(".mic-button");
  const listeningText = document.getElementById("listening-text");

  if (micButton) micButton.classList.remove("active");
  if (popup) popup.classList.add("hidden");
  if (listeningText) listeningText.textContent = "Listening to your sentence...";
}

// Key listener for listening popup
document.addEventListener("keydown", function (event) {
  if (isListening && (event.key === "Escape" || event.key === "Enter")) {
    event.preventDefault();
    stopVoiceInput();
  }
});

// Stop audio speech output
function stopSpeech() {
  if (isListening) {
    stopVoiceInput();
    return;
  }

  const stopBtn = document.querySelector(".stop-button");
  const originalHtml = stopBtn ? stopBtn.innerHTML : "";
  if (stopBtn) {
    stopBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> <span class="btn-label">Stopping...</span>`;
  }

  fetch("/stop-speech", {
    method: "POST",
    headers: { "Cache-Control": "no-cache" },
  })
    .then((response) => response.json())
    .then((data) => {
      if (stopBtn) {
        stopBtn.innerHTML = `<i class="fa-solid fa-check"></i> <span class="btn-label">Stopped</span>`;
        setTimeout(() => {
          stopBtn.innerHTML = originalHtml;
        }, 800);
      }
    })
    .catch((error) => {
      console.error("Error stopping speech:", error);
      if (stopBtn) stopBtn.innerHTML = originalHtml;
    });
}

// Auto-resize and handle Enter key in textarea
function handleTextareaInput(event) {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendMessage();
    return;
  }

  const textarea = event.target;
  textarea.style.height = "auto";
  const newHeight = Math.min(textarea.scrollHeight, 140);
  textarea.style.height = newHeight + "px";
}

// Welcome message
function showWelcomeMessage() {
  const chatBox = document.getElementById("chat-box");
  if (!chatBox) return;

  const welcomeMessage = document.createElement("div");
  welcomeMessage.className = "ai-message";
  const welcomeText =
    "Hello! I'm ORION, your intelligent AI Tutor. Ask me any question, explore the topic cards, or upload PDF notes to get document-grounded answers. How can I help you learn today?";

  welcomeMessage.innerHTML = `
    <div class="ai-header">
      <div class="ai-author">
        <div class="ai-author-icon"><i class="fa-solid fa-atom"></i></div>
        <span>ORION</span>
        <span class="ai-badge">AI TUTOR</span>
      </div>
      <div class="ai-actions">
        <button class="copy-btn" onclick="copyMessageText(this)" title="Copy Welcome">
          <i class="fa-regular fa-copy"></i>
          <span>Copy</span>
        </button>
      </div>
    </div>
    <div class="ai-body"><p>${welcomeText}</p></div>
  `;
  chatBox.appendChild(welcomeMessage);
  scrollToBottom();
}

// Page load initialization
window.onload = function () {
  setTimeout(() => {
    showWelcomeMessage();

    // Spoken welcome greeting
    const welcomeGreeting =
      "Hello! I'm ORION your AI Tutor. How can I help you today?";
    fetch("/text-to-speech", {
      method: "POST",
      body: JSON.stringify({ text: welcomeGreeting }),
      headers: { "Content-Type": "application/json" },
    })
      .then((response) => response.json())
      .catch((err) => console.log("Welcome speech suppressed or skipped"));
  }, 400);
};