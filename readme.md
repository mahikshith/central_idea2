# 💡 C&S Think Tank

> **"Innovation is a numbers game. Out of 10 ideas, 6 might look good on paper, 2 might seem unconventional, and 1 might be impossible. But that remaining 1 idea holds the potential to transform our operations. To find that spark, we must first share all 10."**

![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/Frontend-React-61DAFB?style=for-the-badge&logo=react&logoColor=black)
![Gemini AI](https://img.shields.io/badge/AI-Google_Gemini-8E75B2?style=for-the-badge&logo=googlegemini&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Styling-Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white)

C&S Think Tank is a collaborative innovation platform built for employees of C&S Wholesale Grocers. It bridges the gap between frontline ingenuity and leadership visibility, allowing every team member to contribute to a common vision.

---

## ✨ Key Features

### 🚀 Innovation Engine
* **Reddit-Style Feed**: Upvote and discuss ideas to surface the most impactful solutions.
* **Unique Idea Tracking**: Every submission generates a unique ID (e.g., `IDEA-A7F2`) for professional tracking and reference.
* **Threaded Conversations**: Engage in deep, nested discussions to troubleshoot and refine process improvements.
* **Multimedia Attachments**: Support your case by attaching images or documentation directly to ideas and replies.

### 🤖 Gemini AI Integration
* **AI Conversation Summaries**: Using **Gemini 2.5 Flash**, the system distills long conversation threads into 3-4 sentence takeaways at the click of a button.
* **Semantic Natural Language Search**: Search for ideas using intent rather than just keywords. Our AI understands the context of your query to find relevant historical or current discussions.

### 🏢 Corporate Transparency
* **Leadership Newsletters**: A dedicated space for executives to share strategic thoughts and vision with instant employee feedback.
* [cite_start]**How Business Works**: An interactive section educating employees on C&S history—from the first building on Winter Street in 1918 [cite: 7, 30] [cite_start]to reaching $27 billion in sales in 2018[cite: 99].

---

## 🛠 Technology Stack

* **Backend**: Python FastAPI (Asynchronous, High-Performance)
* **Frontend**: React.js with Tailwind CSS
* **AI Models**: 
    * `gemini-2.5-flash` (Summarization)
    * `text-embedding-004` / `embedding-001` (Semantic Search)
* **Storage**: Persistent JSON-based storage for rapid local development and demo portability.

---

## 🚦 Local Setup

### 1. Prerequisites
* Python 3.10+
* A **Gemini API Key** from [Google AI Studio](https://aistudio.google.com/)

### 2. Installation
```bash
# Clone the repository
git clone [https://github.com/mahikshith/cs-think-tank.git](https://github.com/mahikshith/cs-think-tank.git)
cd cs-think-tank

# Install dependencies
pip install -r requirements.txt

### 3. Environment Configuration

Create a .env file in the root directory:
```
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Start the Application
```bash

uvicorn main:app --reload

Visit http://localhost:8000 to start innovating.