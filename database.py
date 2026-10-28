import sqlite3
import os
import hashlib
import uuid
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "voting_system.db")

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a fixed salt."""
    salt = "sepm_student_voting_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_db():
    """Initialize all database tables matching SEPM Report Chapter 8.2 and Appendix A."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table (Student, Candidate, Administrator, Auditor)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        identifier TEXT UNIQUE NOT NULL, -- Student Roll No / UID (e.g., 24001027), or Admin/Auditor Username
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'candidate', 'admin', 'auditor')),
        department TEXT NOT NULL,
        year TEXT NOT NULL,
        is_verified INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Elections Table (Draft, Scheduled, Open, Closed, Published)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        target_role TEXT NOT NULL DEFAULT 'student',
        status TEXT NOT NULL CHECK(status IN ('Draft', 'Scheduled', 'Open', 'Closed', 'Published')),
        start_time TEXT,
        end_time TEXT,
        created_by TEXT DEFAULT 'admin',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Posts Table (e.g. Council President, Sports Secretary, Cultural Secretary, Class Representative)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER NOT NULL,
        post_name TEXT NOT NULL,
        description TEXT,
        eligible_year TEXT DEFAULT 'All Years',
        allow_nota INTEGER DEFAULT 1,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE
    )
    """)

    # 4. Candidates Table (Nomination Workflow: Submitted, Approved, Rejected, Withdrawn)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER NOT NULL,
        election_id INTEGER NOT NULL,
        user_id INTEGER,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        year TEXT NOT NULL,
        manifesto TEXT,
        symbol_emoji TEXT DEFAULT '🗳️',
        nomination_status TEXT NOT NULL DEFAULT 'Approved' CHECK(nomination_status IN ('Submitted', 'Approved', 'Rejected', 'Withdrawn')),
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    """)

    # 5. Votes Table (ANONYMOUS secret ballot - Decoupled from voter identity)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL, -- -1 represents NOTA (None of the Above)
        ballot_token TEXT NOT NULL,
        cast_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
        FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
    )
    """)

    # 6. Voter Participation Records (Strict 1-Vote-Per-Student Enforcement)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voter_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        election_id INTEGER NOT NULL,
        receipt_code TEXT UNIQUE NOT NULL,
        voted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
        UNIQUE(user_id, election_id)
    )
    """)

    # 7. Audit Log Table (Chapter 8.2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        action TEXT NOT NULL,
        details TEXT,
        ip_address TEXT DEFAULT '127.0.0.1',
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

def log_audit_action(user_id, username, action, details="", ip="127.0.0.1"):
    """Record an immutable audit log entry."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO audit_logs (user_id, username, action, details, ip_address)
    VALUES (?, ?, ?, ?, ?)
    """, (user_id, username, action, details, ip))
    conn.commit()
    conn.close()

def seed_sample_data():
    """Seed comprehensive representation data aligned with St. Vincent Pallotti College of Engineering & Technology."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE identifier = 'admin'")
    if cursor.fetchone():
        conn.close()
        return

    # Seed Default Users
    sample_users = [
        # (Name, Identifier/UID, Email, Password, Role, Department, Year)
        ("Dr Vikas Bhowate", "admin", "vikas.bhowate@stvincentngp.edu.in", "admin123", "admin", "Department of Artificial Intelligence", "Faculty Coordinator"),
        ("Yug Meshram", "24001027", "yug.meshram@stvincentngp.edu.in", "pass123", "student", "Department of Artificial Intelligence", "3rd Year (Sem V)"),
        ("Aarav Sharma", "24001001", "aarav.sharma@stvincentngp.edu.in", "pass123", "student", "Computer Engineering", "Final Year"),
        ("Ananya Patel", "24001002", "ananya.patel@stvincentngp.edu.in", "pass123", "student", "Information Technology", "3rd Year"),
        ("Rohan Verma", "24001003", "rohan.verma@stvincentngp.edu.in", "pass123", "student", "Mechanical Engineering", "2nd Year"),
        ("Vikramaditya Roy", "24001010", "vikram.roy@stvincentngp.edu.in", "pass123", "candidate", "Computer Engineering", "Final Year"),
        ("Priya Sundaram", "24001011", "priya.sundaram@stvincentngp.edu.in", "pass123", "candidate", "Information Technology", "3rd Year"),
        ("Prof. H. R. Deshmukh", "auditor", "auditor@stvincentngp.edu.in", "audit123", "auditor", "Dean Office", "Senior Faculty Auditor")
    ]

    for u in sample_users:
        cursor.execute("""
        INSERT INTO users (name, identifier, email, password_hash, role, department, year)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (u[0], u[1], u[2], hash_password(u[3]), u[4], u[5], u[6]))

    # Seed Default Election
    cursor.execute("""
    INSERT INTO elections (title, description, target_role, status, start_time, end_time, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "SVPCET Student Council General Election 2026-27",
        "Official democratic election to elect the Student Council representatives for Council President, Sports Secretary, and Cultural Secretary.",
        "student",
        "Open",
        "2026-10-25 08:00:00",
        "2026-11-05 17:00:00",
        "admin"
    ))
    elec_id = cursor.lastrowid

    # Secondary upcoming election
    cursor.execute("""
    INSERT INTO elections (title, description, target_role, status, start_time, end_time, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "AI Department Class Representative (CR) Election",
        "Election of Semester V Class Representatives for the Department of Artificial Intelligence.",
        "student",
        "Scheduled",
        "2026-11-10 09:00:00",
        "2026-11-12 16:00:00",
        "admin"
    ))

    # Past completed election
    cursor.execute("""
    INSERT INTO elections (title, description, target_role, status, start_time, end_time, created_by)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "ACM & IEEE Student Branch Executive Committee Poll",
        "Technical student chapter leadership election for technical heads and webmasters.",
        "student",
        "Published",
        "2026-10-01 09:00:00",
        "2026-10-05 17:00:00",
        "admin"
    ))
    past_elec_id = cursor.lastrowid

    # Posts for Main Election
    cursor.execute("""
    INSERT INTO posts (election_id, post_name, description, eligible_year, allow_nota)
    VALUES (?, ?, ?, ?, ?)
    """, (elec_id, "Council President", "Lead the student body, represent students before the Academic Senate, and coordinate student welfare.", "Final Year", 1))
    pres_pos_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO posts (election_id, post_name, description, eligible_year, allow_nota)
    VALUES (?, ?, ?, ?, ?)
    """, (elec_id, "Sports Secretary", "Manage sports tournaments, campus athletic facilities, gym, and inter-collegiate teams.", "All Years", 1))
    sports_pos_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO posts (election_id, post_name, description, eligible_year, allow_nota)
    VALUES (?, ?, ?, ?, ?)
    """, (elec_id, "Cultural Secretary", "Organize annual college cultural festival, student clubs, musical events, and drama productions.", "All Years", 1))
    cult_pos_id = cursor.lastrowid

    # Candidates for Main Election
    candidates_data = [
        (pres_pos_id, elec_id, 6, "Vikramaditya Roy", "Computer Engineering", "Final Year", "Proposing 24x7 library access, upgraded high-speed campus Wi-Fi, and transparent budget allocation for student events.", "🚀", "Approved"),
        (pres_pos_id, elec_id, 7, "Priya Sundaram", "Information Technology", "3rd Year", "Focus on mental health counselling, career placement mentorship bootcamps, and subsidized cafeteria meals.", "🌟", "Approved"),
        (pres_pos_id, elec_id, None, "Kabir Mehta", "Mechanical Engineering", "Final Year", "Revitalizing tech clubs, hackathons, solar campus initiatives, and hands-on maker labs.", "⚡", "Approved"),
        
        (sports_pos_id, elec_id, None, "Arjun Deshmukh", "Civil Engineering", "3rd Year", "Renovating the campus cricket pitch, new indoor badminton synthetic mats, and sports medical emergency kits.", "🏆", "Approved"),
        (sports_pos_id, elec_id, None, "Sneha Nair", "Artificial Intelligence", "2nd Year", "Women athletics club funding, annual sports marathon, and state-level sports kit sponsorships.", "🎯", "Approved"),

        (cult_pos_id, elec_id, None, "Devika Iyer", "Information Technology", "3rd Year", "Expanded celebrity nights at annual fest, open mic Fridays, and student music band competitions.", "🎨", "Approved"),
        (cult_pos_id, elec_id, None, "Tanmay Joshi", "Computer Engineering", "Final Year", "Digital arts guild, campus e-sports gaming tournament, and acoustics upgrade in main auditorium.", "🎭", "Approved"),
        (cult_pos_id, elec_id, None, "Sahil Agrawal", "Electronics Engineering", "2nd Year", "Inter-college cultural exchange delegations, photography club darkroom, and dance workshops.", "🎸", "Submitted")
    ]

    for c in candidates_data:
        cursor.execute("""
        INSERT INTO candidates (post_id, election_id, user_id, name, department, year, manifesto, symbol_emoji, nomination_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, c)

    # Posts and results for past election
    cursor.execute("""
    INSERT INTO posts (election_id, post_name, description, eligible_year, allow_nota)
    VALUES (?, ?, ?, ?, ?)
    """, (past_elec_id, "IEEE Student Branch Chair", "Lead the technical paper submissions and workshops.", "All Years", 1))
    ieee_pos = cursor.lastrowid

    cursor.execute("""
    INSERT INTO candidates (post_id, election_id, user_id, name, department, year, manifesto, symbol_emoji, nomination_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ieee_pos, past_elec_id, None, "Neha Kulkarni", "Artificial Intelligence", "Final Year", "Promoting international conference publications and robotics competitions.", "🤖", "Approved"))
    neha_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO candidates (post_id, election_id, user_id, name, department, year, manifesto, symbol_emoji, nomination_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (ieee_pos, past_elec_id, None, "Rahul Shinde", "Computer Engineering", "Final Year", "Hosting open-source bootcamps and weekly coding meetups.", "💻", "Approved"))
    rahul_id = cursor.lastrowid

    # Seed past votes
    for _ in range(38):
        token = uuid.uuid4().hex[:12].upper()
        cursor.execute("INSERT INTO votes (election_id, post_id, candidate_id, ballot_token) VALUES (?, ?, ?, ?)", (past_elec_id, ieee_pos, neha_id, token))
    for _ in range(24):
        token = uuid.uuid4().hex[:12].upper()
        cursor.execute("INSERT INTO votes (election_id, post_id, candidate_id, ballot_token) VALUES (?, ?, ?, ?)", (past_elec_id, ieee_pos, rahul_id, token))

    # Seed initial audit log directly using same cursor
    cursor.execute("""
    INSERT INTO audit_logs (user_id, username, action, details, ip_address)
    VALUES (?, ?, ?, ?, ?)
    """, (1, "admin", "SYSTEM_INIT", "Database initialized with SVPCET sample elections and candidate rolls.", "127.0.0.1"))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_sample_data()
    print("SEPM Voting System Database initialized and seeded successfully.")
