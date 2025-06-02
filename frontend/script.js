// SentimentFlow Frontend - API Integration

const API_BASE_URL = "http://localhost:8000";

// DOM elements
const textInput = document.getElementById("text-input");
const modelSelect = document.getElementById("model-select");
const analyzeBtn = document.getElementById("analyze-btn");
const loadingDiv = document.getElementById("loading");
const resultsDiv = document.getElementById("results");
const errorDiv = document.getElementById("error");

// Result elements
const sentimentLabel = document.getElementById("sentiment-label");
const sentimentEmoji = document.getElementById("sentiment-emoji");
const confidenceFill = document.getElementById("confidence-fill");
const confidenceScore = document.getElementById("confidence-score");
const modelUsed = document.getElementById("model-used");
const errorMessage = document.getElementById("error-message");

// Sentiment emojis mapping
const sentimentEmojis = {
  positive: "😊",
  negative: "😞",
  neutral: "😐",
};

// Main function to analyze sentiment
async function analyzeSentiment() {
  const text = textInput.value.trim();

  if (!text) {
    showError("Please enter some text to analyze.");
    return;
  }

  // Update UI state
  hideAllSections();
  showLoading();
  disableButton();

  try {
    // Prepare request data
    const requestData = {
      text: text,
    };

    // Add model if selected
    const selectedModel = modelSelect.value;
    if (selectedModel) {
      requestData.model_name = selectedModel;
    }

    // Make API call
    const response = await fetch(`${API_BASE_URL}/api/v1/sentiment/analyze`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(
        errorData.detail || `HTTP ${response.status}: ${response.statusText}`
      );
    }

    const result = await response.json();
    showResults(result);
  } catch (error) {
    console.error("Error analyzing sentiment:", error);
    showError(`Failed to analyze sentiment: ${error.message}`);
  } finally {
    enableButton();
  }
}

// Display results
function showResults(data) {
  hideAllSections();

  // Extract sentiment data from API response structure
  const result = data.result;
  const sentiment = result.sentiment.toLowerCase();
  const confidence = Math.round(result.confidence * 100);
  const model = result.model_name || "Unknown";

  // Update sentiment display
  sentimentLabel.textContent = sentiment;
  sentimentLabel.className = `sentiment-${sentiment}`;
  sentimentEmoji.textContent = sentimentEmojis[sentiment] || "🤔";

  // Update confidence bar
  confidenceFill.style.width = `${confidence}%`;
  confidenceScore.textContent = `${confidence}%`;

  // Update model info
  modelUsed.textContent = getModelDisplayName(model);

  // Show results
  resultsDiv.classList.remove("hidden");
}

// Show error message
function showError(message) {
  hideAllSections();
  errorMessage.textContent = message;
  errorDiv.classList.remove("hidden");
}

// Show loading state
function showLoading() {
  hideAllSections();
  loadingDiv.classList.remove("hidden");
}

// Hide all result sections
function hideAllSections() {
  resultsDiv.classList.add("hidden");
  errorDiv.classList.add("hidden");
  loadingDiv.classList.add("hidden");
}

// Button state management
function disableButton() {
  analyzeBtn.disabled = true;
  analyzeBtn.textContent = "Analyzing...";
}

function enableButton() {
  analyzeBtn.disabled = false;
  analyzeBtn.textContent = "Analyze Sentiment";
}

// Get friendly model names
function getModelDisplayName(modelId) {
  const modelNames = {
    "distilbert-base-uncased-finetuned-sst-2-english": "DistilBERT (Default)",
    "cardiffnlp/twitter-roberta-base-sentiment": "RoBERTa (Twitter-optimized)",
    "nlptown/bert-base-multilingual-uncased-sentiment": "BERT (Multilingual)",
  };

  return modelNames[modelId] || modelId;
}

// Event listeners
analyzeBtn.addEventListener("click", analyzeSentiment);

// Allow Enter key to trigger analysis
textInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && event.ctrlKey) {
    event.preventDefault();
    analyzeSentiment();
  }
});

// Auto-clear results when input changes
textInput.addEventListener("input", () => {
  hideAllSections();
});

modelSelect.addEventListener("change", () => {
  hideAllSections();
});

// Add some sample texts for testing
const sampleTexts = [
  "I absolutely love this product! It's amazing and works perfectly.",
  "This is the worst experience I've ever had. Completely disappointed.",
  "The weather is okay today, nothing special but not bad either.",
  "🎉 Just got promoted at work! So excited and grateful!",
  "Traffic was terrible this morning, made me late for the meeting.",
];

// Add a hint about sample texts
window.addEventListener("load", () => {
  const placeholder = textInput.getAttribute("placeholder");
  textInput.setAttribute(
    "placeholder",
    placeholder +
      "\n\nTip: Try different types of text - positive, negative, or neutral!"
  );
});

// Simple error handling for network issues
window.addEventListener("online", () => {
  console.log("Connection restored");
});

window.addEventListener("offline", () => {
  showError("No internet connection. Please check your network and try again.");
});
