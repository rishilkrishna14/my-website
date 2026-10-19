# ⚡ EduBattle: Multiplayer Syllabus Arena for Class 1 to 9

> **Gamifying School Studies for India (CBSE & State Board)**  
> Built for Hackathon Demo: Real-time Multiplayer, Buzzer Battles, Speed Quizzes, and Private Classrooms.

---

## 🌟 Overview & Problem Solved
Traditional textbook revision can feel tedious for students in Classes 1 through 9. **EduBattle** transforms the school curriculum into a high-stakes, competitive, multiplayer e-sports arena. Students can:
- Compete directly with their classmates in real-time.
- Revise exact textbook chapters mapped to **CBSE** and **State Board** standards.
- Experience arcade-style game modes: **Fast-Finger Buzzer Battles**, **Speed Quizzes**, and **Fill in the Blanks**.

---

## 🎯 Key Features

1. **Curriculum & Subtopic Mapping**:
   - Covers **Classes 1 through 9** with deep integration for **Classes 6, 7, and 8** (Science, Mathematics, Social Science).
   - Supports **CBSE** and **Tamil Nadu State Board (Samacheer Kalvi English Medium)**.
   - **Granular Subtopic Selection**: Choose a single chapter, and immediately select from its specific subtopics (e.g., *1.1 SI Units*, *4.1 Root Systems*, *3.1 Imperial Cholas*, *2.1 Pressure in Fluids*, etc.).
   - Built-in **Textbook PDF Library**: Direct chapter PDF reader and download links matching the chosen topic and subtopic.

2. **Arcade Game Modes**:
   - **🎯 Speed Quiz**: 4-option timed trivia with countdown timer and speed multipliers.
   - **🚨 Fast-Finger Buzzer Battle**: Fastest student to hit the buzzer gets an exclusive 5-second answering window! Wrong answers penalize points.
   - **✏️ Fill in the Blanks**: Rapid spelling and concept recall.

3. **Multiplayer & Networking**:
   - **👑 Private Room (Play with Friends)**: Host creates a room $\rightarrow$ shares a 5-letter Room Code. Host retains exclusive controls to adjust difficulty, timer, number of rounds, and start the match.
   - **⚡ Quick Match (Random 1v1)**: Instant matchmaking queue connecting students of the same grade.
   - **📖 Solo Practice**: On-demand practice sessions without waiting for friends.

4. **Live Leaderboard & Podium**:
   - Real-time score calculation (Base + Speed Bonus + Streak Multiplier 🔥).
   - Animated 1st, 2nd, and 3rd place podium with confetti and victory fanfare.

5. **Engaging Kid-Friendly UX**:
   - Sound effects synthesized dynamically via the Web Audio API (100% offline, zero audio loading errors).
   - Custom student avatars (🚀 Astro, 🦁 Leo, 🦉 Oliver, 🦊 Ruby, 🤖 Pixel, ⚡ Spark).
   - Real-time emoji cheer reactions (🔥, 👏, 🧠, ⚡, 🥳).

---

## 🚀 Quick Start Guide

### 1. Requirements
- Python 3.10+
- Installed packages: `fastapi`, `uvicorn`, `python-socketio`, `starlette`

### 2. Run the Application
Open PowerShell or your terminal in this directory:

```bash
cd "C:\Users\rishi\.gemini\antigravity\scratch\edubattle"
python server.py
```

### 3. Open in Browser
Visit **`http://localhost:8000`** in your browser.
- Open multiple tabs or different browser windows to simulate multiple students joining the same room!
- Test the buzzer to see real-time lock-out and scoring across tabs.
