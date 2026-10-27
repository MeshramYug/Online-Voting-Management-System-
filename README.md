# 🗳️ CampusVote: Online Voting Management System

[![Made with Python](https://img.shields.io/badge/Made%20with-Python%203.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Plotly](https://img.shields.io/badge/Analytics-Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![Developed With AI](https://img.shields.io/badge/🤖%20Developed%20With-AI%20Assistance-8A2BE2?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> 🤖 **AI Disclosure**: This project and its machine learning architectures were crafted and accelerated **using Artificial Intelligence (AI)** assistance!

---

## 😂 Election Day Memes & Vibes

Because democracy is serious business, but elections don't have to be boring:

| When you finally cast your vote | Watching the live vote counts roll in |
| :---: | :---: |
| ![I Voted Meme](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDExaXhkZ2FqZzlsOHBmdzlydXRsdWJvZnpsbjZtbm11dGQwdnV6dCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/3o7TKr3nzbh5WgCFxe/giphy.gif) | ![Counting Votes Meme](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExenF2N3BvZmxoc3A1dWFoMWxqb2g4OTFmNHlhZ2Uxb3VobTZ0MXh5ZCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l2JhL0Gpfbvs4Y076/giphy.gif) |
| *"Feeling like a responsible citizen!"* 🌟 | *"Waiting for the election commission results like..."* ☕ |

| When someone tries to vote twice | The Admin monitoring everything |
| :---: | :---: |
| ![Wait a minute](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWNreGZicXhzZTFzMnVzYms3cGFid3MxaXJ1am0wMjlldmFlczNxeiZlcD12MV9naWZzX3NlYXJjaCZjdD1n/l3q2K5jinAlChoCLS/giphy.gif) | ![Cat Hacker Admin](https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExZW1qNnBnbndzOHhkZTRsdmlscXlveTVzNzJ1bnlyc2Zucnl5dGVqNCZlcD12MV9naWZzX3NlYXJjaCZjdD1n/unQ3IJU2RG7DO/giphy.gif) |
| *Database Unique Constraint: "Not on my watch!"* 🚫 | *"All servers running, zero tampering detected!"* 🛡️ |

---

## 📌 Project Overview

**CampusVote** is a production-ready, digital voting management system designed for academic institutions, student councils, and faculty senates. It combines:
1. **Multi-Role Isolation**: Dedicated login tabs tailored for **Students**, **Faculty Members**, and **Election Administrators**.
2. **Tamper-Resistant Secret Ballot Architecture**: Cryptographic decoupling ensures complete voter anonymity while mathematically preventing duplicate votes.
3. **Cryptographic Voting Receipts**: Every voter receives a verifiable token code (`VOTE-REC-XXXXXXXX`) as proof of participation.
4. **AI-Powered Turnout Forecaster**: Built-in machine learning models predicting turnout likelihood to help election commissioners maximize participation.

---

## ✨ Dedicated Login Tabs & Portals

The application features dedicated, independent tabs for each stakeholder on the login screen:

```
                            ┌───────────────────────────────────┐
                            │    CampusVote Main Entrypoint     │
                            └─────────────────┬─────────────────┘
                                              │
         ┌─────────────────────────┬──────────┴──────────────┬─────────────────────────┐
         ▼                         ▼                         ▼                         ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ 🎓 Student Tab   │       │ 🏛️ Faculty Tab   │       │ 🛡️ Admin Tab     │       │ 📝 Register Tab │
├─────────────────┤       ├─────────────────┤       ├─────────────────┤       ├─────────────────┤
│ • Roll Number   │       │ • Faculty ID    │       │ • Admin User    │       │ • New Student / │
│ • Secret Ballot │       │ • Senate Vote   │       │ • Turnout AI    │       │   Faculty Setup │
│ • Live Results  │       │ • Ledger Proof  │       │ • Election DDL  │       │ • Department    │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

- **🎓 Student Portal**: Confidential ballot casting, candidate manifestos, downloadable participation certificate, live student council results.
- **🏛️ Faculty Senate Portal**: Faculty-specific elections, senate representative voting, official academic ledger receipt.
- **🛡️ Admin Console**: Complete election lifecycle management, candidate/position creation, live Plotly analytics, CSV audit export, and ML turnout forecaster.
- **📝 New Voter Registration**: Instant onboarding for eligible campus members.

---

## 🔒 Security & Secret Ballot Guarantee

- **Strict Anonymity**: The `votes` table stores **only** `election_id`, `position_id`, `candidate_id`, and a random cryptographic `ballot_token`. It **never** stores the voter's identity with their vote.
- **Duplicate Vote Prevention**: The `voter_records` table logs `user_id` and `election_id` with a database-level `UNIQUE` constraint. This verifies participation without disclosing choice.
- **Verifiable Receipt Token**: Voters receive an encrypted receipt code (`VOTE-REC-XXXXXXXX`) to verify their ballot was counted.

---

## 🧠 Machine Learning Models: Voter Turnout Prediction

Trained on 2,000 campus demographic and engagement observations:

| Model | Architecture | Objective | Metric |
| :--- | :--- | :--- | :---: |
| **Voter Turnout Classifier** | Random Forest Classifier | Classifies whether a voter will turn out to vote | **86.75% Accuracy** |
| **Turnout Regressor** | Gradient Boosting Regressor | Predicts percentage probability of turnout | **$R^2 = 0.768$** |

### Key Predictive Features:
- Campus attendance percentage
- Society / Club leadership involvement
- Cumulative GPA / Academic score
- Days registered prior to election
- Departmental candidate presence

---

## 🛠️ Tech Stack

- **Frontend & App Framework**: [Streamlit](https://streamlit.io/)
- **Backend & Database**: Python 3.11, SQLite3
- **Machine Learning**: Scikit-Learn, Joblib, NumPy, Pandas
- **Data Visualization**: Plotly Express & Plotly Graph Objects
- **Code Assistance**: Built & refined using AI

---

## 🏁 Quick Start Guide

### 1. Clone the repository
```bash
git clone https://github.com/MeshramYug/CampusVote-Online-Voting-System.git
cd CampusVote-Online-Voting-System
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Initialize Database & Seed Demo Data
```bash
python database.py
```

### 4. (Optional) Retrain ML Models
```bash
python train_model.py
```

### 5. Launch the Web Application
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser!

---

## 🔑 Demo Credentials (For Evaluation & Viva)

Instant 1-click login buttons are available on the home screen, or enter credentials manually:

| Portal Tab | Username / Identifier | Password | Access Level |
| :--- | :--- | :--- | :--- |
| **🛡️ Admin Console** | `admin` | `admin123` | Full Commission Oversight |
| **🎓 Student Portal** | `STU202601` | `pass123` | Final Year CSE Voter |
| **🎓 Student Portal** | `STU202602` | `pass123` | Third Year IT Voter |
| **🏛️ Faculty Portal** | `FAC101` | `pass123` | HOD & Senior Professor |
| **🏛️ Faculty Portal** | `FAC102` | `pass123` | Associate Professor |

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

Developed with ❤️ and 🤖 AI by **[Yug Meshram](https://github.com/MeshramYug)**.
