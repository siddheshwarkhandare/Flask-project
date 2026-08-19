console.log("VOICE JS IS WORKING");

const micBtn = document.getElementById("mic-btn");
const result = document.getElementById("result");

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new SpeechRecognition();

recognition.lang = "en-IN";
recognition.continuous = false;
recognition.interimResults = true;

function speak(text) {
  console.log("JARVIS:", text);

  const speech = new SpeechSynthesisUtterance(text);

  speech.lang = "en-IN";
  speech.rate = 1;
  speech.pitch = 1;

  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(speech);
}

micBtn.addEventListener("click", () => {
  window.speechSynthesis.cancel();

  micBtn.textContent = "Listening...";

  speak("Yes, sir. What would you like me to do?");

  setTimeout(() => {
    try {
      recognition.start();
    } catch (error) {
      console.log("Microphone error:", error);
    }
  }, 1500);
});

recognition.onresult = async (event) => {
  let finalText = "";

  for (let i = event.resultIndex; i < event.results.length; i++) {
    if (event.results[i].isFinal) {
      finalText += event.results[i][0].transcript;
    }
  }

  if (!finalText) {
    return;
  }

  finalText = finalText.trim();

  console.log("USER:", finalText);

  result.textContent = finalText;

  micBtn.textContent = "Thinking...";

  try {
    const response = await fetch("/voice", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        text: finalText,
      }),
    });

    const data = await response.json();

    console.log("SERVER:", data);

    if (data.success) {
      if (data.message) {
        speak(data.message);
      }

      micBtn.textContent = "Activate JARVIS";

      setTimeout(() => {
        location.reload();
      }, 2000);
    } else {
      speak("Sorry, I couldn't complete that request.");

      micBtn.textContent = "Activate JARVIS";
    }
  } catch (error) {
    console.error("Voice request error:", error);

    speak("Sorry, I couldn't connect to the system.");

    micBtn.textContent = "Activate JARVIS";
  }
};

recognition.onstart = () => {
  console.log("Listening...");
  micBtn.textContent = "Listening...";
};

recognition.onend = () => {
  console.log("Stopped listening.");
};

recognition.onerror = (event) => {
  console.error("Speech recognition error:", event.error);
  micBtn.textContent = "Activate JARVIS";
};
