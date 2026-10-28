# 🗳️ Online Voting System for Students (SEPM Mini Project)

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Backend-Flask%203.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Bootstrap 5](https://img.shields.io/badge/Frontend-Bootstrap%205-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Developed With AI](https://img.shields.io/badge/🤖%20Developed%20With-AI%20Assistance-8A2BE2?style=for-the-badge)](#)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

> 🏛️ **Academic Institution**: St. Vincent Pallotti College of Engineering & Technology, Nagpur  
> 🎓 **Department**: Department of Artificial Intelligence  
> 📑 **Subject**: Software Engineering and Project Management (SEPM) • Practical No. 9  
> 👤 **Submitted By**: **Yug Meshram** (College UID: `24001027`, Sem V)  
> 👨‍🏫 **Guided By**: **Dr. Vikas Bhowate**  
> 🤖 **AI Disclosure**: This project and its architectures were designed and developed with **Artificial Intelligence (AI)** assistance!

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

## 🚀 How to Run Locally (NO Streamlit Cloud Deployment Needed!)

You do **not** need to deploy to Streamlit Cloud or configure remote servers. You can run the entire system directly on your PC:

### ⚡ Method A: 1-Click Double Click (Recommended)
Simply double-click the **`run_voting_system.bat`** file in this folder (or in the project root).
- It verifies the SQLite database.
- It automatically launches your default browser to **`http://127.0.0.1:5000`**.
- It starts the local Flask server immediately!

### 💻 Method B: Terminal Command
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the server
python server.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser!

---

## 📌 Implementation of SEPM Report Chapters & UI Wireframes

This software implements all design models and UI screens specified in **`Online_Voting_System_SEPM_Report.docx`**:

### 1. 🎓 Student Dashboard (**Figure 5.1**)
- Metric cards showing Active Elections, Upcoming Elections, Ballots Cast, and Published Results.
- Active Elections Table with target roles, closing times, and status badges (`Open`, `Scheduled`, `Closed`, `Published`).
- Quick actions to cast ballots or view cryptographic voter certificates.

### 2. 🗳️ Official Ballot Screen with Summary Panel (**Figure 5.2**)
- Step-by-step post ballot selection (Council President, Sports Secretary, Cultural Secretary).
- Candidate cards featuring emojis/symbols, candidate names, departments, years, and campaign manifestos.
- **NOTA (None of the Above)** option as defined in Chapter 8.2 and Appendix A.
- **Live Ballot Summary Panel**: Displays selections in real-time before confirmation.
- Irreversible confirmation modal with secret ballot guarantees.

### 3. 🛡️ Administrative Election Console (**Figure 5.3**)
- High-priority metric cards: Total Registered Students, Total Ballots Cast, Active Polls, and Pending Nominations.
- Polling Control Table: Transition election states in real-time: `Draft` ➔ `Scheduled` ➔ `Open` ➔ `Closed` ➔ `Published`.
- Candidate Nomination Approval / Rejection review workflow.
- Verified Student Voter Roll viewer.

### 4. 🧑‍💼 Candidate Nomination Panel (Chapter 1.4 & 8.2)
- Students can submit their nominations for open posts, choose election symbols, and upload their campaign manifesto.
- Live tracking of nomination status: `Submitted` ➔ `Approved` / `Rejected`.

### 5. 🏛️ Faculty Auditor Console & Decoupled Secrecy (Chapter 4.4 & 8.2)
- Inspects database decoupling: `votes` table contains **zero link** to voter identity, mathematically guaranteeing secret ballots.
- Full tamper-evident audit trail of system events, logins, and status shifts.

### 6. 🧪 Automated SEPM Test Suite Runner (Chapter 9: TC-01 through TC-09)
The application includes an interactive test suite that programmatically validates all 9 test cases from the report:
- `TC-01`: Valid Student Authentication
- `TC-02`: Invalid Password Defense
- `TC-03`: Unregistered Voter Block
- `TC-04`: Duplicate Voting Prevention (`UNIQUE(user_id, election_id)`)
- `TC-05`: Voting Window Enforcement (Only `Open` polls accept votes)
- `TC-06`: Role-Based Access Control
- `TC-07`: Tally Consistency (Ballots = Voters)
- `TC-08`: Secret Ballot Database Decoupling Verification
- `TC-09`: Turnout & Audit Log Logging

---

## 🔑 Pre-Configured Demo Credentials (For Viva & Evaluation)

For fast evaluation during practical examination, use the 1-click login buttons or enter credentials manually:

| Portal | Identifier / Roll No | Password | Role Description |
| :--- | :--- | :--- | :--- |
| **🎓 Student Voter** | `24001027` | `pass123` | **Yug Meshram** (Artificial Intelligence, Sem V) |
| **🎓 Student Voter** | `24001001` | `pass123` | Aarav Sharma (Computer Engineering, Final Year) |
| **🛡️ Election Admin** | `admin` | `admin123` | **Dr. Vikas Bhowate** (Chief Election Officer) |
| **🧑‍💼 Candidate** | `24001010` | `pass123` | Vikramaditya Roy (Presidential Candidate) |
| **🏛️ Faculty Auditor**| `auditor` | `audit123` | Prof. H. R. Deshmukh (Audit & Compliance) |

---

## 📜 License
Distributed under the **MIT License**. Created by **Yug Meshram**.
