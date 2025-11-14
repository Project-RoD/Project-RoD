import { useState, useRef } from 'react';
import axios from "axios";

function App() {
  const [recording, setRecording] = useState(false);
  const [userText, setUserText] = useState("");
  const [assistantText, setAssistantText] = useState("");
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);

  const BACKEND_URL = "http://localhost:8000";

  const startRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorderRef.current = new MediaRecorder(stream);
    audioChunksRef.current = [];

    mediaRecorderRef.current.ondataavailable = (event: BlobEvent) => {
      audioChunksRef.current.push(event.data);
    };

    mediaRecorderRef.current.start();
    setRecording(true);
  };

  const stopRecording = async () => {
    return new Promise<void>((resolve) => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.onstop = () => resolve();
        mediaRecorderRef.current.stop();
      }
      setRecording(false);
    });
  };

  const sendAudio = async () => {
    await stopRecording();

    const blob = new Blob(audioChunksRef.current, {type: "audio/webm"});
    const formData = new FormData();
    formData.append("file", blob, "recording.webm");

    const response = await axios.post(`${BACKEND_URL}/core_function`, formData, {
      headers: {"Content-Type": "multipart/form-data"}
    });

    setUserText(response.data.user_text);
    setAssistantText(response.data.assistant_text);

    // Play Audio
    const audio = new Audio(`${BACKEND_URL}${response.data.reply_audio_url}`);
    audio.play();
  };

  return (
    <div style={{ padding: 20, fontFamily: "sans-serif"}}>
      <h1> Language Demo</h1>

      {!recording && (
        <button onClick={startRecording} style={{ fontSize: 18 }}>
          Start Recording
        </button>
      )}

      {recording && (
        <button onClick={sendAudio} style={{ fontSize: 18 }}>
          Stop
        </button>
      )}

      <h3>User:</h3>
      <p>{userText || ".."}</p>

      <h3>Assistant:</h3>
      <p>{assistantText || "..."}</p>

    </div>
  )
}

export default App;
