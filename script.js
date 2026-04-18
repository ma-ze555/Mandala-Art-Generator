// All requests go to our local Python proxy (server.py)
const HEADERS = { "Content-Type": "application/json" };

// Generate image via local proxy → Hugging Face API
async function generateImage(prompt) {
  const response = await fetch("/api/generate", {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ prompt })
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || `Request failed (${response.status})`);
  }
  return data;
}

// Display the base64 image returned from the server
function displayImage(data) {
  const b64 = data.image;
  if (!b64) throw new Error("No image data in response");

  const resultImg = document.getElementById("resultImage");
  resultImg.src = b64.startsWith("data:") ? b64 : `data:image/png;base64,${b64}`;
  resultImg.classList.remove("d-none");
  document.getElementById("actionButtons").classList.remove("d-none");
}

// Download the generated image
function downloadImage() {
  const resultImg = document.getElementById("resultImage");
  if (!resultImg.src || resultImg.src === window.location.href) return;
  const link = document.createElement("a");
  link.href = resultImg.src;
  link.download = `mandala_${Date.now()}.png`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Share via Web Share API
function shareImage() {
  const resultImg = document.getElementById("resultImage");
  if (!resultImg.src || resultImg.src === window.location.href) return;
  if (navigator.share) {
    fetch(resultImg.src)
      .then(r => r.blob())
      .then(blob => {
        const file = new File([blob], "mandala.png", { type: "image/png" });
        navigator.share({ title: "My Mandala Art", files: [file] })
          .catch(err => console.error("Share failed:", err));
      });
  } else {
    alert("Sharing is not supported on this browser.");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Style chip selection
  const optionChips = document.querySelectorAll(".option-chip");
  let selectedStyle = "Monochrome";
  if (optionChips.length > 0) optionChips[0].classList.add("active");

  optionChips.forEach(chip => {
    chip.addEventListener("click", function () {
      optionChips.forEach(c => c.classList.remove("active"));
      this.classList.add("active");
      selectedStyle = this.textContent.trim();
    });
  });

  const generateBtn       = document.getElementById("generateBtn");
  const loadingText       = document.getElementById("loadingText");
  const resultImg         = document.getElementById("resultImage");
  const analysisContainer = document.getElementById("analysis");
  const actionButtons     = document.getElementById("actionButtons");

  generateBtn.addEventListener("click", async function () {
    const rawPrompt = document.getElementById("prompt").value.trim();
    if (!rawPrompt) {
      alert("Please enter a concept to generate a Mandala!");
      return;
    }

    const prompt = `${rawPrompt} in ${selectedStyle.toLowerCase()} style`;

    // Reset UI
    loadingText.classList.remove("d-none");
    generateBtn.disabled = true;
    resultImg.classList.add("d-none");
    actionButtons.classList.add("d-none");
    analysisContainer.classList.add("d-none");
    analysisContainer.innerHTML = "";

    try {
      const result = await generateImage(prompt);
      displayImage(result);
    } catch (error) {
      console.error("Generation error:", error);
      alert(`Error: ${error.message}`);
    } finally {
      loadingText.classList.add("d-none");
      generateBtn.disabled = false;
    }
  });

  document.getElementById("downloadBtn")?.addEventListener("click", downloadImage);
  document.getElementById("shareBtn")?.addEventListener("click", shareImage);
  document.getElementById("regenerateBtn")?.addEventListener("click", () => generateBtn.click());
});
