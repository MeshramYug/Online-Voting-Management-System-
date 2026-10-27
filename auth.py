import sqlite3
import hashlib
import uuid
from database import get_connection, hash_password

def authenticate_user(identifier, password, role_expected=None):
    """
    Authenticate a user by roll number, faculty ID, or username.
    Returns user dictionary if valid, None otherwise.
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
        return dict(row)
    return None

def register_user(name, identifier, email, password, role, department, year_or_designation):
    """
    Register a new student or faculty member.
    Returns (success: bool, message: str)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check duplicates
    cursor.execute("SELECT id FROM users WHERE identifier = ?", (identifier.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, f"A user with ID '{identifier}' is already registered."

    cursor.execute("SELECT id FROM users WHERE email = ?", (email.strip(),))
    if cursor.fetchone():
        conn.close()
        return False, f"Email '{email}' is already registered."

    pwd_hash = hash_password(password)

    try:
        cursor.execute("""
        INSERT INTO users (name, identifier, email, password_hash, role, department, year_or_designation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (name.strip(), identifier.strip(), email.strip(), pwd_hash, role, department, year_or_designation))
        conn.commit()
        conn.close()
        return True, "Registration successful! You can now log in."
    except Exception as e:
        conn.close()
        return False, f"Registration failed: {str(e)}"

def check_has_voted(user_id, election_id):
    """
    Returns True if the user has already voted in this election.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, receipt_code, voted_at FROM voter_records WHERE user_id = ? AND election_id = ?", (user_id, election_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return True, dict(row)
    return False, None

def cast_ballot(user_id, election_id, selections):
    """
    Cryptographically secure & secret ballot submission:
    1. Checks if voter already participated.
    2. Inserts anonymous vote records into `votes` table with an irreversible random ballot token.
    3. Inserts an audit record into `voter_records` (linking user_id to election_id, but NOT to the candidate choices!).
    selections: dict of {position_id: candidate_id}
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Double-check duplicate voting
    cursor.execute("SELECT id FROM voter_records WHERE user_id = ? AND election_id = ?", (user_id, election_id))
    if cursor.fetchone():
        conn.close()
        return False, "Duplicate voting detected. You have already cast your ballot in this election.", None

    try:
        # Generate random anonymous ballot token
        ballot_token = hashlib.sha256(uuid.uuid4().bytes).hexdigest()[:16].upper()
        # Generate public verification receipt for the voter
        receipt_code = f"VOTE-REC-{uuid.uuid4().hex[:8].upper()}"

        # 1. Insert anonymous votes
        for pos_id, cand_id in selections.items():
            cursor.execute("""
            INSERT INTO votes (election_id, position_id, candidate_id, ballot_token)
            VALUES (?, ?, ?, ?)
            """, (election_id, pos_id, cand_id, ballot_token))

        # 2. Record that this voter participated
        cursor.execute("""
        INSERT INTO voter_records (user_id, election_id, receipt_code)
        VALUES (?, ?, ?)
        """, (user_id, election_id, receipt_code))

        conn.commit()
        conn.close()
        return True, "Ballot successfully cast! Your vote has been securely and anonymously recorded.", receipt_code
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, f"Failed to submit ballot: {str(e)}", None
