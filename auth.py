import sqlite3
import hashlib
import uuid
from datetime import datetime
from database import get_connection, hash_password, log_audit_action

def authenticate_user(identifier, password, role_expected=None):
    """
    Authenticate a user by Roll No/UID (e.g. 24001027), email, or username.
    Returns user dict if valid, None otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()

    pwd_hash = hash_password(password)

    if role_expected and role_expected != "all":
        cursor.execute("""
        SELECT * FROM users 
        WHERE (identifier = ? OR email = ?) AND password_hash = ? AND role = ?
        """, (identifier.strip(), identifier.strip(), pwd_hash, role_expected))
    else:
        cursor.execute("""
        SELECT * FROM users 
        WHERE (identifier = ? OR email = ?) AND password_hash = ?
        """, (identifier.strip(), identifier.strip(), pwd_hash))

    row = cursor.fetchone()
    conn.close()

    if row:
        user_dict = dict(row)
        log_audit_action(user_dict['id'], user_dict['identifier'], "USER_LOGIN", f"Role: {user_dict['role']} logged in.")
        return user_dict
    return None

def register_student(name, identifier, email, password, department, year):
    """Register a new student voter."""
    return _register_user_internal(name, identifier, email, password, department, year, role="student")

def register_user(name, identifier, email, password, role="student", department="", year_or_designation=""):
    """Generic registration wrapper for legacy calls."""
    return _register_user_internal(name, identifier, email, password, department, year_or_designation, role)

def _register_user_internal(name, identifier, email, password, department, year, role="student"):
    conn = get_connection()
    cursor = conn.cursor()

    # Check duplicates
    cursor.execute("SELECT id FROM users WHERE identifier = ?", (identifier.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, f"A user with UID / Roll No '{identifier}' is already registered."

    cursor.execute("SELECT id FROM users WHERE email = ?", (email.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, f"Email '{email}' is already registered."

    pwd_hash = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO users (name, identifier, email, password_hash, role, department, year, is_verified)
        VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        """, (name.strip(), identifier.strip(), email.strip(), pwd_hash, role, department.strip(), year.strip()))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        log_audit_action(user_id, identifier.strip(), "USER_REGISTER", f"New {role} registered in {department} ({year}).")
        return True, "Registration successful! You may now log in."
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}"

def check_has_voted(user_id, election_id):
    """Check if the student has already cast a ballot in this election."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, receipt_code, voted_at FROM voter_records WHERE user_id = ? AND election_id = ?", (user_id, election_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, dict(row)
    return False, None

def cast_ballot(user_id, election_id, selections, username="student"):
    """
    Cast an anonymous secret ballot (Chapter 4.4 & 8.3):
    1. Verifies student hasn't voted yet (Strict 1-Vote-Per-Student rule).
    2. Writes choices into `votes` table with random decoupled ballot token.
    3. Writes participation entry into `voter_records` (links user to election, but NOT to votes).
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Verify election is Open
    cursor.execute("SELECT status, title FROM elections WHERE id = ?", (election_id,))
    elec = cursor.fetchone()
    if not elec or elec['status'] != 'Open':
        conn.close()
        return False, "Voting is only permitted when election status is 'Open'.", None

    # Check duplicate voting
    cursor.execute("SELECT id FROM voter_records WHERE user_id = ? AND election_id = ?", (user_id, election_id))
    if cursor.fetchone():
        conn.close()
        return False, "Duplicate voting prohibited. You have already cast your ballot.", None

    try:
        ballot_token = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16].upper()
        receipt_code = f"VOTE-REC-{uuid.uuid4().hex[:8].upper()}"

        # 1. Store anonymous votes
        for pos_id, cand_id in selections.items():
            cursor.execute("""
            INSERT INTO votes (election_id, position_id, candidate_id, ballot_token)
            VALUES (?, ?, ?, ?)
            """, (election_id, int(pos_id), int(cand_id), ballot_token))

        # 2. Record voter participation
        cursor.execute("""
        INSERT INTO voter_records (user_id, election_id, receipt_code)
        VALUES (?, ?, ?)
        """, (user_id, election_id, receipt_code))

        conn.commit()
        conn.close()

        log_audit_action(user_id, username, "BALLOT_CAST", f"Election ID: {election_id}, Receipt: {receipt_code}")
        return True, "Ballot successfully cast! Your vote has been securely and anonymously recorded.", receipt_code
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Failed to cast ballot: {str(e)}", None

def update_election_status(election_id, new_status, admin_user="admin"):
    """Update election state: Draft -> Scheduled -> Open -> Closed -> Published."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE elections SET status = ? WHERE id = ?", (new_status, election_id))
    conn.commit()
    conn.close()
    log_audit_action(1, admin_user, "ELECTION_STATUS_CHANGE", f"Election {election_id} status changed to {new_status}")
    return True

def submit_nomination(user_id, election_id, post_id, name, department, year, manifesto, symbol):
    """Candidate submits a nomination."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO candidates (post_id, election_id, user_id, name, department, year, manifesto, symbol_emoji, nomination_status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Submitted')
    """, (post_id, election_id, user_id, name, department, year, manifesto, symbol))
    cand_id = cursor.lastrowid
    conn.commit()
    conn.close()
    log_audit_action(user_id, name, "NOMINATION_SUBMITTED", f"Candidate {name} nominated for Post ID {post_id}")
    return cand_id

def set_nomination_status(candidate_id, status, admin_user="admin"):
    """Admin approves or rejects nomination."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE candidates SET nomination_status = ? WHERE id = ?", (status, candidate_id))
    conn.commit()
    conn.close()
    log_audit_action(1, admin_user, "NOMINATION_REVIEW", f"Candidate ID {candidate_id} status set to {status}")
    return True
