# RoD (Rettskriving og Dialog AI Project 2025)

This repository contains **RoD**, a Human-Centered AI platform designed to bridge the gap between passive media consumption and active conversation practice for Norwegian learners.

The project features a Client-Server architecture (React Native + Python FastAPI) and introduces novel architectural patterns like **"Oracle Prompting"** for context-aware grammar correction and a **Cache-Aside Media Hub** for real-time news integration.

**➡️ Current Status: Beta v0.7 (Feature Complete)**

---

<div align="center">

<h3>RoD in Action</h3>

| **1. Opening Screen & Navigation** | **2. Adaptive Chat & Feedback** |
|:---:|:---:|
| <video src="https://i.imgur.com/VIXb7Xy.mp4" width="250" autoplay loop muted playsinline style="display:block;"></video> | <video src="https://i.imgur.com/wJ4GnvS.mp4" width="250" autoplay loop muted playsinline style="display:block;"></video>  |
| **3. The Media Hub** | **4. Gamification (Wordle)** |
| <video src="https://i.imgur.com/baSKgcN.mp4" width="250" autoplay loop muted playsinline style="display:block;"></video>  | <img src="https://i.imgur.com/r4zXQxT.gif" width="250">  |

</div>

---

## ✨ Key Features & Modules

RoD is built as an integrated ecosystem, not just a chatbot. Key modules include:

* **Adaptive Chatbot (A1-C1):** The AI persona changes dynamically based on the user's proficiency. For A1 users, it acts as a translator/guide; for B1+, it acts as a native immersion partner.
* **Asynchronous Feedback ("Shadow Tutor"):** A non-intrusive feedback system that runs in the background. It uses our custom **"Oracle Logic"** to reverse-engineer user intent from the AI's response, providing highly accurate corrections without interrupting conversation flow.
* **Real-Time Media Hub:** Fetches live news from NRK via RSS. The backend classifies article difficulty (A2-C1) using GPT-5-mini and caches results in SQLite for 0ms load times.
* **Context Injection:** Clicking "Discuss" on an article injects a system-level context note into the Chatbot, grounding the conversation in the specific news topic.
* **Gamification:** A Norwegian implementation of Wordle ("Ordle") with local dictionary validation, connected to a daily streak counter via event emitters.
* **Frictionless Identity:** Uses persistent device UUIDs (`SecureStore`) to maintain user history and levels without requiring a login screen. (Only for prototype build)

---

## 🤖 How it Works & Tech Stack

The application uses a separated Client-Server architecture to handle heavy logic on the backend and UI responsiveness on the frontend.

### 1. The "Oracle" Logic (Grammar)
Standard grammar checkers fail on short, ambiguous sentences (e.g., "Hvorfor går med du?"). RoD sends the *Chatbot's Answer* back to the Feedback Agent as context. The Agent uses the answer to deduce what the user *meant* to ask, solving the ambiguity problem.

### 2. Cache-Aside Architecture (Media)
To prevent API latency, the Media Hub never fetches live data on the read path. It serves cached articles from the SQLite database instantly. A background worker silently refreshes the RSS feed and classifies new articles with AI, updating the cache asynchronously.

### 3. Tech Stack
* **Frontend:** `React Native (Expo)`, `TypeScript`, `Expo Router`
* **Backend:** `Python`, `FastAPI`, `Uvicorn`
* **Database:** `SQLite` (Relational persistence for Users, History, Media)
* **AI APIs:** `OpenAI` (GPT-5, GPT-5-mini, GPT-5-nano, Whisper), `ElevenLabs` (TTS)
* **Tools:** `BeautifulSoup4` (Scraping), `FFMPEG` (Audio conversion)

---

## 🚀 How to Run

You need **Two Terminals** to run this project (one for Backend, one for Frontend).

### Prerequisites
* **Node.js** & **npm**
* **Python 3.10+**
* **FFMPEG:** Must be installed and added to your System PATH (Required for audio processing).

### Terminal 1: The Backend

1.  **Navigate to the backend:**
    ```bash
    cd rod_backend
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Keys:** Create a `.env` file in `rod_backend/` with your API keys:
    ```env
    OPENAI_API_KEY="sk-..."
    ELEVENLABS_API_KEY="sk-..."
    ```
4.  **Run the Server:**
    ```bash
    uvicorn main:app --reload --host 0.0.0.0
    ```

### Terminal 2: The Frontend

1.  **Navigate to the app:**
    ```bash
    cd RodApp
    ```
2.  **Install Dependencies:**
    ```bash
    npm install
    ```
3.  **Configure IP:** Open `constants/config.ts` and update `API_BASE_URL` to your computer's local IPv4 address.
4.  **Run the App:**
    ```bash
    npx expo start -c
    ```

---

## 👥 Contributors

This project was developed as a final exam delivery for **KIUA1008 (Human-Centred Design Principles for AI Systems)** at INN University.

* **Pedro**
* **Fredrik**
* **Engebret**


*November 2025*
