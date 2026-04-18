// Pollinations AI — free, no token, called directly from browser
const POLLINATIONS_URL = "https://image.pollinations.ai/prompt";

async function generateImage(prompt) {
  const full_prompt = (
    `highly detailed mandala art, ${prompt}, ` +
    "symmetrical, intricate geometric patterns, zentangle, " +
    "sacred geometry, high quality, 4k"
  );

  const encoded = encodeURIComponent(full_prompt);
  const url = `${POLLINATIONS_URL}/${encoded}?width=512&height=512&nologo=true&model=flux&seed=${Date.now()}`;

  const response = await fetch(url);
  if (!response.ok) throw new Error(`Image generation failed (${response.status})`);

  const blob = await response.blob();
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onloadend = () => resolve(reader.result); // returns data:image/png;base64,...
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}

function displayImage(src) {
  const resultImg = document.getElementById("resultImage");
  resultImg.src = src;
  resultImg.classList.remove("d-none");
  document.getElementById("actionButtons").classList.remove("d-none");
}

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

    loadingText.classList.remove("d-none");
    generateBtn.disabled = true;
    resultImg.classList.add("d-none");
    actionButtons.classList.add("d-none");
    analysisContainer.classList.add("d-none");
    analysisContainer.innerHTML = "";

    try {
      const imgSrc = await generateImage(prompt);
      displayImage(imgSrc);
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
