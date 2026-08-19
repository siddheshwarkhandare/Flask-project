console.log("VOICE JS IS WORKING");
const micBtn = document.getElementById("mic-btn");
const result = document.getElementById("result");

const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

if (!SpeechRecognition) {
    result.textContent = "Speech recognition is not supported in this browser.";
} else {
    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.continuous = false;
    recognition.interimResults = false;

    micBtn.addEventListener("click", () => {
        recognition.start();
        micBtn.textContent = "🎤 Listening...";
    });

   recognition.onresult = async (event) => {

    let finalText = "";

    for (let i = event.resultIndex; i < event.results.length; i++) {

        if (event.results[i].isFinal) {
            finalText += event.results[i][0].transcript;
        }
    }

    if (finalText) {

        finalText = finalText.trim();

        result.textContent = finalText;

        micBtn.textContent = "🎤 Start Listening";

        const response = await fetch("/voice", {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                text: finalText
            })
        });

        const data = await response.json();

        console.log(data);
    }
};

    recognition.onerror = (event) => {
        console.log("Speech recognition error:", event.error);
        micBtn.textContent = "🎤 Start Listening";
    };

    recognition.onend = () => {
        micBtn.textContent = "🎤 Start Listening";
    };
}