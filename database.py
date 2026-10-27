import sqlite3
import os
import hashlib
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "voting_system.db")

def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a fixed salt."""
    salt = "student_voting_salt_2026"
    return hashlib.sha256((password + salt).encode()).hexdigest()

def init_db():
    """Initialize all database tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table (Admin, Student, Faculty)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        identifier TEXT UNIQUE NOT NULL, -- Roll No (Students), Faculty ID (Faculty), or Username (Admin)
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'student', 'faculty')),
        department TEXT NOT NULL,
        year_or_designation TEXT,
        is_verified INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 2. Elections Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS elections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        target_role TEXT NOT NULL CHECK(target_role IN ('student', 'faculty', 'all')),
        status TEXT NOT NULL CHECK(status IN ('upcoming', 'active', 'closed')),
        start_date TEXT,
        end_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # 3. Positions Table (e.g. President, Vice President, Sports Secretary)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE
    )
    """)

    # 4. Candidates Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        position_id INTEGER NOT NULL,
        election_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        department TEXT NOT NULL,
        manifesto TEXT,
        symbol_emoji TEXT DEFAULT '🗳️',
        FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE
    )
    """)

    # 5. Votes Table (ANONYMOUS secret ballot)
    # Notice: It intentionally does NOT store user_id to preserve absolute secret ballot secrecy!
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        election_id INTEGER NOT NULL,
        position_id INTEGER NOT NULL,
        candidate_id INTEGER NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ballot_token TEXT NOT NULL,
        FOREIGN KEY (election_id) REFERENCES elections(id) ON DELETE CASCADE,
        FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE,
        FOREIGN KEY (candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
    )
    """)

    # 6. Voter Audit Records (Tracks who participated to strictly prevent duplicate voting)
    # Stored separately from the votes table so no one can link a student's ID to their ballot.
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

    conn.commit()
    conn.close()

def seed_sample_data():
    """Populate default demo accounts, elections, positions, and candidates."""
    conn = get_connection()
    cursor = conn.cursor()

    # Check if admin already exists
    cursor.execute("SELECT id FROM users WHERE identifier = 'admin'")
    if cursor.fetchone():
        conn.close()
        return

    # Default Users
    sample_users = [
        # (Name, Identifier, Email, Password, Role, Department, Year/Designation)
        ("Election Administrator", "admin", "admin@campus.edu", "admin123", "admin", "Administration", "Chief Election Officer"),
        ("Aarav Sharma", "STU202601", "aarav.s@campus.edu", "pass123", "student", "Computer Engineering", "Final Year"),
        ("Ananya Patel", "STU202602", "ananya.p@campus.edu", "pass123", "student", "Information Technology", "Third Year"),
        ("Rohan Verma", "STU202603", "rohan.v@campus.edu", "pass123", "student", "Mechanical Engineering", "Second Year"),
        ("Dr. Rajesh Kulkarni", "FAC101", "rajesh.k@campus.edu", "pass123", "faculty", "Computer Engineering", "Professor & HOD"),
        ("Prof. Meera Sen", "FAC102", "meera.s@campus.edu", "pass123", "faculty", "Electronics", "Associate Professor"),
        ("Dr. Sanjay Gupta", "FAC103", "sanjay.g@campus.edu", "pass123", "faculty", "Information Technology", "Assistant Professor")
    ]

    for u in sample_users:
        cursor.execute("""
        INSERT INTO users (name, identifier, email, password_hash, role, department, year_or_designation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (u[0], u[1], u[2], hash_password(u[3]), u[4], u[5], u[6]))

    # Sample Student Election
    cursor.execute("""
    INSERT INTO elections (title, description, target_role, status, start_date, end_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Annual Student Council Elections 2026",
        "Official democratic election to choose the Student Council representatives across sports, culture, and governance.",
        "student",
        "active",
        "2026-10-25",
        "2026-11-05"
    ))
    student_elec_id = cursor.lastrowid

    # Positions for Student Election
    cursor.execute("""
    INSERT INTO positions (election_id, title, description)
    VALUES (?, ?, ?)
    """, (student_elec_id, "Council President", "Lead the student body, interface with university management, and spearhead student welfare."))
    pres_pos_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO positions (election_id, title, description)
    VALUES (?, ?, ?)
    """, (student_elec_id, "Sports Secretary", "Organize inter-college sports tournaments, gym facilities, and athletic sponsorships."))
    sports_pos_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO positions (election_id, title, description)
    VALUES (?, ?, ?)
    """, (student_elec_id, "Cultural Secretary", "Direct annual cultural festival, clubs, music, drama, and youth festival delegations."))
    cult_pos_id = cursor.lastrowid

    # Candidates for Student Election
    student_candidates = [
        # (position_id, election_id, name, department, manifesto, symbol)
        (pres_pos_id, student_elec_id, "Vikramaditya Roy", "Computer Engineering", "Commitment to 24x7 library access, upgraded high-speed campus Wi-Fi, and transparent budget allocation.", "🚀"),
        (pres_pos_id, student_elec_id, "Priya Sundaram", "Information Technology", "Focus on mental health counselling, internship placement bootcamps, and subsidized cafeteria meals.", "🌟"),
        (pres_pos_id, student_elec_id, "Kabir Mehta", "Mechanical Engineering", "Revitalizing college technical societies, hackathons, and industry mentorship programs.", "⚡"),
        (sports_pos_id, student_elec_id, "Arjun Deshmukh", "Civil Engineering", "Modernizing cricket pitch, new indoor badminton synthetic mats, and sports scholarships.", "🏆"),
        (sports_pos_id, student_elec_id, "Sneha Nair", "Biotech Engineering", "Women athletics club funding, marathon events, and medical emergency staff for ground injuries.", "🎯"),
        (cult_pos_id, student_elec_id, "Devika Iyer", "Information Technology", "Expanded celebrity nights at annual fest, open mic Fridays, and photography darkroom.", "🎨"),
        (cult_pos_id, student_elec_id, "Tanmay Joshi", "Computer Engineering", "Digital arts guild, e-sports festival integration, and music studio equipment revamp.", "🎭")
    ]

    for cand in student_candidates:
        cursor.execute("""
        INSERT INTO candidates (position_id, election_id, name, department, manifesto, symbol_emoji)
        VALUES (?, ?, ?, ?, ?, ?)
        """, cand)

    # Sample Faculty Election
    cursor.execute("""
    INSERT INTO elections (title, description, target_role, status, start_date, end_date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        "Academic Senate & Faculty Welfare Election 2026",
        "Faculty committee election to elect faculty representatives for Academic Council and Research Grants.",
        "faculty",
        "active",
        "2026-10-20",
        "2026-11-10"
    ))
    faculty_elec_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO positions (election_id, title, description)
    VALUES (?, ?, ?)
    """, (faculty_elec_id, "Academic Council Representative", "Represent department faculty in curriculum upgrades and academic policy reforms."))
    fac_rep_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO positions (election_id, title, description)
    VALUES (?, ?, ?)
    """, (faculty_elec_id, "Research & Grants Coordinator", "Allocate peer-reviewed research grants, lab infrastructure, and conference travel funds."))
    fac_res_id = cursor.lastrowid

    faculty_candidates = [
        (fac_rep_id, faculty_elec_id, "Dr. Ramesh Chandra", "Computer Engineering", "Advocate for reduced administrative paperwork, AI research labs, and sabbatical flexibility.", "📚"),
        (fac_rep_id, faculty_elec_id, "Prof. Sunita Rao", "Electronics", "Streamlined grading tools, student-to-teacher ratio limits, and interdisciplinary syllabus.", "💡"),
        (fac_res_id, faculty_elec_id, "Dr. Hitesh Shah", "Chemical Engineering", "Speedier patent filing assistance, enhanced PhD stipends, and international collaboration ties.", "🔬"),
        (fac_res_id, faculty_elec_id, "Dr. Geeta Pillai", "Applied Sciences", "Central equipment maintenance fund and young faculty seed grant expansion.", "🧬")
    ]

    for fcand in faculty_candidates:
        cursor.execute("""
        INSERT INTO candidates (position_id, election_id, name, department, manifesto, symbol_emoji)
        VALUES (?, ?, ?, ?, ?, ?)
        """, fcand)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    seed_sample_data()
    print("Database initialized and seeded successfully.")
