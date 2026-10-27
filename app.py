import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import joblib
import json
from datetime import datetime

from database import get_connection, init_db, seed_sample_data
from auth import authenticate_user, register_user, check_has_voted, cast_ballot

# -----------------------------------------------------------------------------
# Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="CampusVote - Online Voting Management System",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Theme CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.4rem;
    }
    .role-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-admin { background-color: #FEE2E2; color: #991B1B; }
    .badge-student { background-color: #DBEAFE; color: #1E40AF; }
    .badge-faculty { background-color: #FEF3C7; color: #92400E; }
    
    .card-box {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .card-box:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .candidate-card {
        border: 1.5px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 12px;
        background: #F8FAFC;
    }
    .receipt-box {
        background: #ECFDF5;
        border: 2px dashed #059669;
        border-radius: 10px;
        padding: 18px;
        font-family: monospace;
    }
    .stat-label {
        font-size: 0.85rem;
        color: #6B7280;
        font-weight: 500;
    }
    .stat-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #111827;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Database Setup & Session State
# -----------------------------------------------------------------------------
init_db()
seed_sample_data()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

def logout():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def get_elections_for_role(role):
    conn = get_connection()
    cursor = conn.cursor()
    if role == "admin":
        cursor.execute("SELECT * FROM elections ORDER BY id DESC")
    elif role == "student":
        cursor.execute("SELECT * FROM elections WHERE target_role IN ('student', 'all') ORDER BY id DESC")
    elif role == "faculty":
        cursor.execute("SELECT * FROM elections WHERE target_role IN ('faculty', 'all') ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_positions(election_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM positions WHERE election_id = ?", (election_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_candidates(position_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates WHERE position_id = ?", (position_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_candidates_by_election(election_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT c.*, p.title as position_title
    FROM candidates c
    JOIN positions p ON c.position_id = p.id
    WHERE c.election_id = ?
    ORDER BY p.id, c.id
    """, (election_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_election_vote_counts(election_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT 
        p.id as position_id,
        p.title as position_title,
        c.id as candidate_id,
        c.name as candidate_name,
        c.department as candidate_dept,
        c.symbol_emoji,
        COUNT(v.id) as vote_count
    FROM positions p
    JOIN candidates c ON c.position_id = p.id
    LEFT JOIN votes v ON v.candidate_id = c.id
    WHERE p.election_id = ?
    GROUP BY p.id, c.id
    ORDER BY p.id, vote_count DESC
    """, (election_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# -----------------------------------------------------------------------------
# LOGIN & REGISTRATION SCREEN (When unauthenticated)
# -----------------------------------------------------------------------------
if not st.session_state.logged_in:
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.markdown('<div class="main-title">🗳️ CampusVote Management System</div>', unsafe_allow_html=True)
        st.markdown('<div class="sub-title">Secure Multi-Role Digital Voting Management System for Students, Faculty & Administrators</div>', unsafe_allow_html=True)
    with col_hdr2:
        st.markdown("""
        <div style="text-align: right; padding-top: 10px;">
            <span class="role-badge badge-student">100% Secret Ballot</span>
            <span class="role-badge badge-admin">Zero Dataset Required</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Fast 1-Click Demo Logins for Viva/Demonstration
    st.markdown("##### ⚡ Quick Demo Logins (Instant 1-Click Access for Evaluation)")
    dcol1, dcol2, dcol3 = st.columns(3)
    
    with dcol1:
        if st.button("🛡️ Login as Admin (Administrator)", use_container_width=True):
            user = authenticate_user("admin", "admin123", "admin")
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()

    with dcol2:
        if st.button("🎓 Login as Student (Aarav Sharma)", use_container_width=True):
            user = authenticate_user("STU202601", "pass123", "student")
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()

    with dcol3:
        if st.button("🏛️ Login as Faculty (Dr. Rajesh Kulkarni)", use_container_width=True):
            user = authenticate_user("FAC101", "pass123", "faculty")
            if user:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.rerun()

    st.markdown("---")

    # Dedicated Tabs for Different Logins
    student_tab, faculty_tab, admin_tab, reg_tab = st.tabs([
        "🎓 Student Login", 
        "🏛️ Faculty Login", 
        "🛡️ Administrator Login", 
        "📝 New Voter Registration"
    ])

    # 1. Student Login Tab
    with student_tab:
        col_form, col_info = st.columns([1.5, 1])
        with col_form:
            st.markdown("### 🎓 Student Voting Portal")
            st.caption("Sign in with your Student Roll Number to cast confidential votes for Student Council elections.")
            with st.form("student_login_form"):
                ident = st.text_input("Student Roll Number", placeholder="e.g. STU202601", key="stu_ident")
                pwd = st.text_input("Password", type="password", placeholder="Enter password", key="stu_pwd")
                submit = st.form_submit_button("🎓 Log In to Student Portal", use_container_width=True, type="primary")

                if submit:
                    if not ident or not pwd:
                        st.error("Please enter both your Student Roll Number and password.")
                    else:
                        user = authenticate_user(ident, pwd, "student")
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success(f"Welcome back, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid student credentials or password. Please try again.")

        with col_info:
            st.markdown("""
            <div class="card-box">
                <h4 style="margin-top: 0; color: #1E3A8A;">🎓 Student Portal Access</h4>
                <ul style="font-size: 0.9rem; line-height: 1.6; color: #4B5563;">
                    <li><strong>Secret Ballot:</strong> Your vote is completely anonymous.</li>
                    <li><strong>Digital Receipt:</strong> Get a verifiable receipt token after voting.</li>
                    <li><strong>Manifestos:</strong> View candidate proposals & campaign emojis.</li>
                </ul>
                <div style="background: #DBEAFE; padding: 10px; border-radius: 8px; font-size: 0.85rem; color: #1E40AF;">
                    <strong>Demo Student Account:</strong><br>
                    Roll No: <code>STU202601</code><br>
                    Password: <code>pass123</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 2. Faculty Login Tab
    with faculty_tab:
        col_form, col_info = st.columns([1.5, 1])
        with col_form:
            st.markdown("### 🏛️ Faculty Senate Portal")
            st.caption("Sign in with your Faculty ID to participate in Academic Council & Senate ballots.")
            with st.form("faculty_login_form"):
                ident = st.text_input("Faculty ID", placeholder="e.g. FAC101", key="fac_ident")
                pwd = st.text_input("Password", type="password", placeholder="Enter password", key="fac_pwd")
                submit = st.form_submit_button("🏛️ Log In to Faculty Portal", use_container_width=True, type="primary")

                if submit:
                    if not ident or not pwd:
                        st.error("Please enter both your Faculty ID and password.")
                    else:
                        user = authenticate_user(ident, pwd, "faculty")
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success(f"Welcome back, Professor {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid faculty credentials. Please check your ID and password.")

        with col_info:
            st.markdown("""
            <div class="card-box">
                <h4 style="margin-top: 0; color: #92400E;">🏛️ Academic Senate Ledger</h4>
                <ul style="font-size: 0.9rem; line-height: 1.6; color: #4B5563;">
                    <li><strong>Faculty Representation:</strong> Vote on department chairs & senate proposals.</li>
                    <li><strong>Cryptographic Proof:</strong> Tamper-proof participation records.</li>
                    <li><strong>Live Senate Analytics:</strong> Departmental turnout breakdowns.</li>
                </ul>
                <div style="background: #FEF3C7; padding: 10px; border-radius: 8px; font-size: 0.85rem; color: #92400E;">
                    <strong>Demo Faculty Account:</strong><br>
                    Faculty ID: <code>FAC101</code><br>
                    Password: <code>pass123</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # 3. Administrator Login Tab
    with admin_tab:
        col_form, col_info = st.columns([1.5, 1])
        with col_form:
            st.markdown("### 🛡️ Election Commission Admin Console")
            st.caption("Authorized election commissioners only. Full oversight of ballots, candidates, and AI turnout.")
            with st.form("admin_login_form"):
                ident = st.text_input("Administrator Username", placeholder="e.g. admin", key="adm_ident")
                pwd = st.text_input("Password", type="password", placeholder="Enter admin password", key="adm_pwd")
                submit = st.form_submit_button("🛡️ Log In as Administrator", use_container_width=True, type="primary")

                if submit:
                    if not ident or not pwd:
                        st.error("Please enter admin username and password.")
                    else:
                        user = authenticate_user(ident, pwd, "admin")
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success(f"Welcome to Admin Console, {user['name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid administrator credentials.")

        with col_info:
            st.markdown("""
            <div class="card-box">
                <h4 style="margin-top: 0; color: #991B1B;">🛡️ Election Commission Controls</h4>
                <ul style="font-size: 0.9rem; line-height: 1.6; color: #4B5563;">
                    <li><strong>Election Lifecycle:</strong> Create, activate, or archive elections.</li>
                    <li><strong>AI Turnout Predictor:</strong> Random Forest model forecasting participation.</li>
                    <li><strong>Voter Audit Roll:</strong> Verify turnouts without exposing secret ballots.</li>
                </ul>
                <div style="background: #FEE2E2; padding: 10px; border-radius: 8px; font-size: 0.85rem; color: #991B1B;">
                    <strong>Demo Admin Account:</strong><br>
                    Username: <code>admin</code><br>
                    Password: <code>admin123</code>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with reg_tab:
        st.markdown("### Register New Campus Voter")
        with st.form("reg_form"):
            reg_role = st.selectbox("Registering As", ["student", "faculty"], format_func=lambda x: "Student" if x == "student" else "Faculty Member")
            r_name = st.text_input("Full Name")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                r_id = st.text_input("Roll Number / Faculty ID", help="Unique campus identification code")
                r_email = st.text_input("Campus Email Address")
            with col_r2:
                r_dept = st.selectbox("Department", [
                    "Computer Engineering", "Information Technology", "Mechanical Engineering",
                    "Civil Engineering", "Electronics", "Biotech Engineering", "Applied Sciences"
                ])
                r_tier = st.selectbox(
                    "Year / Designation",
                    ["First Year", "Second Year", "Third Year", "Final Year"] if reg_role == "student" else ["Assistant Professor", "Associate Professor", "Professor & HOD"]
                )
            r_pwd = st.text_input("Choose Password", type="password")
            r_submit = st.form_submit_button("Complete Registration", use_container_width=True)

            if r_submit:
                if not r_name or not r_id or not r_email or not r_pwd:
                    st.error("Please fill out all mandatory fields.")
                else:
                    success, msg = register_user(r_name, r_id, r_email, r_pwd, reg_role, r_dept, r_tier)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)

    st.stop()

# -----------------------------------------------------------------------------
# AUTHENTICATED WORKSPACE
# -----------------------------------------------------------------------------
user = st.session_state.user
role = user["role"]

# Sidebar Profile & Navigation
with st.sidebar:
    st.markdown("### 👤 User Profile")
    role_badge_class = f"badge-{role}"
    st.markdown(f'<span class="role-badge {role_badge_class}">{role.upper()} PORTAL</span>', unsafe_allow_html=True)
    st.markdown(f"**Name:** {user['name']}")
    st.markdown(f"**ID:** `{user['identifier']}`")
    st.markdown(f"**Department:** {user['department']}")
    st.markdown(f"**Status:** {user.get('year_or_designation', 'Active')}")
    st.markdown("---")

    if st.button("🚪 Log Out", use_container_width=True):
        logout()

    st.markdown("---")
    st.caption("CampusVote v2.4 | Academic Election Management")

# -----------------------------------------------------------------------------
# 1. 🛡️ ADMIN INTERFACE
# -----------------------------------------------------------------------------
if role == "admin":
    st.markdown('<div class="main-title">🛡️ Election Commission Admin Console</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Complete oversight of campus elections, candidate manifestos, live results, and turnout analytics.</div>', unsafe_allow_html=True)

    admin_tabs = st.tabs([
        "📊 Live Dashboard & Analytics",
        "🗳️ Election Management",
        "👥 Positions & Candidates",
        "🏆 Live Results & Tally",
        "🤖 Turnout AI Predictor",
        "📜 Voter Audit Roll"
    ])

    # Tab 1: Live Dashboard
    with admin_tabs[0]:
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        total_students = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM users WHERE role = 'faculty'")
        total_faculty = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM elections WHERE status = 'active'")
        active_elec = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM voter_records")
        total_ballots_cast = c.fetchone()[0]
        conn.close()

        total_voters = total_students + total_faculty
        overall_turnout = (total_ballots_cast / total_voters * 100) if total_voters > 0 else 0

        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            st.markdown(f"""
            <div class="card-box">
                <div class="stat-label">Total Registered Students</div>
                <div class="stat-value">{total_students}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi2:
            st.markdown(f"""
            <div class="card-box">
                <div class="stat-label">Total Registered Faculty</div>
                <div class="stat-value">{total_faculty}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi3:
            st.markdown(f"""
            <div class="card-box">
                <div class="stat-label">Active Elections</div>
                <div class="stat-value">{active_elec}</div>
            </div>
            """, unsafe_allow_html=True)
        with kpi4:
            st.markdown(f"""
            <div class="card-box">
                <div class="stat-label">Voter Turnout Rate</div>
                <div class="stat-value" style="color: #059669;">{overall_turnout:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### Department Engagement Distribution")
        conn = get_connection()
        dept_df = pd.read_sql_query("""
            SELECT department, role, COUNT(*) as count 
            FROM users 
            WHERE role != 'admin'
            GROUP BY department, role
        """, conn)
        conn.close()

        if not dept_df.empty:
            fig = px.bar(
                dept_df, x="department", y="count", color="role",
                title="Registered Voters by Department & Role",
                barmode="group",
                color_discrete_map={"student": "#3B82F6", "faculty": "#F59E0B"},
                labels={"department": "Department", "count": "Registered Voters"}
            )
            fig.update_layout(height=380, margin=dict(l=20, r=20, t=40, b=20))
            st.plotly_chart(fig, use_container_width=True)

    # Tab 2: Election Management
    with admin_tabs[1]:
        col_list, col_create = st.columns([1.6, 1.4])
        with col_list:
            st.markdown("### Existing Elections")
            elections = get_elections_for_role("admin")
            if not elections:
                st.info("No elections created yet.")
            else:
                for el in elections:
                    with st.expander(f"{el['title']} ({el['status'].upper()})", expanded=(el['status'] == 'active')):
                        st.markdown(f"**Target Voters:** `{el['target_role'].capitalize()}`")
                        st.markdown(f"**Duration:** {el['start_date']} to {el['end_date']}")
                        st.markdown(f"**Description:** {el['description']}")

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            new_status = st.selectbox(
                                "Change Status",
                                ["upcoming", "active", "closed"],
                                index=["upcoming", "active", "closed"].index(el["status"]),
                                key=f"status_sel_{el['id']}"
                            )
                            if st.button("Update Status", key=f"btn_up_{el['id']}"):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("UPDATE elections SET status = ? WHERE id = ?", (new_status, el["id"]))
                                conn.commit()
                                conn.close()
                                st.success(f"Status updated to {new_status}!")
                                st.rerun()

                        with btn_col2:
                            st.write("")
                            st.write("")
                            if st.button("🗑️ Delete Election", key=f"del_{el['id']}", type="secondary"):
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("DELETE FROM elections WHERE id = ?", (el["id"],))
                                conn.commit()
                                conn.close()
                                st.warning("Election deleted successfully.")
                                st.rerun()

        with col_create:
            st.markdown("### Create New Election")
            with st.form("create_elec_form"):
                e_title = st.text_input("Election Title", placeholder="e.g., Department Representative Election 2026")
                e_desc = st.text_area("Election Description", placeholder="Outline objective, eligibility, and rules...")
                e_target = st.selectbox("Target Voter Body", ["student", "faculty", "all"], format_func=lambda x: {
                    "student": "Students Only",
                    "faculty": "Faculty Members Only",
                    "all": "Entire Campus (Students + Faculty)"
                }[x])
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    e_start = st.date_input("Start Date", value=datetime.today())
                with col_d2:
                    e_end = st.date_input("End Date", value=datetime.today())
                e_status = st.selectbox("Initial Status", ["active", "upcoming", "closed"])

                sub_elec = st.form_submit_button("Publish Election", use_container_width=True, type="primary")
                if sub_elec:
                    if not e_title:
                        st.error("Please enter an election title.")
                    else:
                        conn = get_connection()
                        cur = conn.cursor()
                        cur.execute("""
                        INSERT INTO elections (title, description, target_role, status, start_date, end_date)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """, (e_title, e_desc, e_target, e_status, str(e_start), str(e_end)))
                        conn.commit()
                        conn.close()
                        st.success(f"Election '{e_title}' created successfully!")
                        st.rerun()

    # Tab 3: Positions & Candidates
    with admin_tabs[2]:
        elections = get_elections_for_role("admin")
        if not elections:
            st.info("Please create an election first before adding positions and candidates.")
        else:
            sel_elec = st.selectbox("Select Election to Configure", elections, format_func=lambda e: f"{e['title']} ({e['target_role'].capitalize()})")
            
            p_col1, p_col2 = st.columns([1, 1.5])
            with p_col1:
                st.markdown("#### 1. Add Position to Election")
                with st.form("add_pos_form"):
                    pos_title = st.text_input("Position Title", placeholder="e.g., Vice President, Treasurer")
                    pos_desc = st.text_area("Position Duties", placeholder="Responsibilities and role...")
                    pos_sub = st.form_submit_button("Add Position")
                    if pos_sub:
                        if not pos_title:
                            st.error("Position title required.")
                        else:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("INSERT INTO positions (election_id, title, description) VALUES (?, ?, ?)",
                                        (sel_elec["id"], pos_title, pos_desc))
                            conn.commit()
                            conn.close()
                            st.success(f"Added position: {pos_title}")
                            st.rerun()

                st.markdown("#### 2. Add Candidate to Position")
                existing_positions = get_positions(sel_elec["id"])
                if not existing_positions:
                    st.caption("No positions found. Create a position above first.")
                else:
                    with st.form("add_cand_form"):
                        cand_pos = st.selectbox("Assign to Position", existing_positions, format_func=lambda p: p["title"])
                        cand_name = st.text_input("Candidate Full Name")
                        cand_dept = st.selectbox("Candidate Department", [
                            "Computer Engineering", "Information Technology", "Mechanical Engineering",
                            "Civil Engineering", "Electronics", "Biotech Engineering", "Applied Sciences"
                        ])
                        cand_sym = st.selectbox("Campaign Symbol", ["🚀", "🌟", "⚡", "🏆", "🎯", "🎨", "🎭", "💡", "🔬", "📚", "🔥", "🤝"])
                        cand_mani = st.text_area("Key Promises / Manifesto")
                        cand_sub = st.form_submit_button("Register Candidate")

                        if cand_sub:
                            if not cand_name:
                                st.error("Candidate name is required.")
                            else:
                                conn = get_connection()
                                cur = conn.cursor()
                                cur.execute("""
                                INSERT INTO candidates (position_id, election_id, name, department, manifesto, symbol_emoji)
                                VALUES (?, ?, ?, ?, ?, ?)
                                """, (cand_pos["id"], sel_elec["id"], cand_name, cand_dept, cand_mani, cand_sym))
                                conn.commit()
                                conn.close()
                                st.success(f"Candidate {cand_name} registered successfully!")
                                st.rerun()

            with p_col2:
                st.markdown("#### Registered Positions & Candidates")
                all_cands = get_all_candidates_by_election(sel_elec["id"])
                if not all_cands:
                    st.info("No candidates registered in this election yet.")
                else:
                    positions = get_positions(sel_elec["id"])
                    for p in positions:
                        st.markdown(f"##### 📌 Position: {p['title']}")
                        c_in_p = [c for c in all_cands if c["position_id"] == p["id"]]
                        if not c_in_p:
                            st.caption("No candidates under this position yet.")
                        else:
                            for cand in c_in_p:
                                with st.container():
                                    st.markdown(f"""
                                    <div class="candidate-card">
                                        <div style="font-size: 1.15rem; font-weight: 700;">
                                            {cand['symbol_emoji']} {cand['name']} 
                                            <span style="font-size: 0.85rem; font-weight: 500; color: #4B5563;">({cand['department']})</span>
                                        </div>
                                        <div style="margin-top: 6px; font-size: 0.9rem; color: #374151;">
                                            <strong>Manifesto:</strong> {cand['manifesto']}
                                        </div>
                                    </div>
                                    """, unsafe_allow_html=True)

    # Tab 4: Results & Live Tally
    with admin_tabs[3]:
        st.markdown("### Official Live Vote Tabulation & Winners")
        elections = get_elections_for_role("admin")
        if not elections:
            st.info("No elections available.")
        else:
            sel_res_elec = st.selectbox("Select Election to View Results", elections, key="res_sel", format_func=lambda e: f"{e['title']} ({e['status'].upper()})")
            
            results = get_election_vote_counts(sel_res_elec["id"])
            if not results:
                st.info("No votes recorded yet for this election.")
            else:
                res_df = pd.DataFrame(results)
                
                # Show results grouped by position
                unique_positions = res_df["position_title"].unique()
                for pos_title in unique_positions:
                    st.markdown(f"#### 🏆 Position: {pos_title}")
                    pos_df = res_df[res_df["position_title"] == pos_title].copy()
                    
                    winner = pos_df.iloc[0]
                    if winner["vote_count"] > 0:
                        st.success(f"🥇 **Leading / Winner:** {winner['symbol_emoji']} **{winner['candidate_name']}** ({winner['candidate_dept']}) with **{winner['vote_count']} votes**!")

                    col_chart, col_tbl = st.columns([1.5, 1])
                    with col_chart:
                        fig = px.bar(
                            pos_df,
                            x="candidate_name",
                            y="vote_count",
                            color="candidate_name",
                            text="vote_count",
                            labels={"candidate_name": "Candidate", "vote_count": "Total Votes"},
                            title=f"Vote Distribution - {pos_title}"
                        )
                        fig.update_traces(textposition="outside")
                        fig.update_layout(height=320, showlegend=False, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig, use_container_width=True)

                    with col_tbl:
                        st.dataframe(
                            pos_df[["candidate_name", "candidate_dept", "vote_count"]].rename(columns={
                                "candidate_name": "Candidate",
                                "candidate_dept": "Department",
                                "vote_count": "Votes Received"
                            }),
                            hide_index=True,
                            use_container_width=True
                        )

                # Export Results to CSV
                csv_data = res_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download Official Results Audit (CSV)",
                    data=csv_data,
                    file_name=f"election_{sel_res_elec['id']}_results.csv",
                    mime="text/csv"
                )

    # Tab 5: AI Turnout Predictor
    with admin_tabs[4]:
        st.markdown("### 🤖 Machine Learning Voter Turnout & Engagement Forecaster")
        st.write("Leverage trained predictive models to forecast voter turnout probability and identify departments requiring engagement intervention.")

        models_dir = os.path.join(os.path.dirname(__file__), "models")
        metrics_file = os.path.join(models_dir, "model_metrics.json")
        clf_file = os.path.join(models_dir, "turnout_classifier.joblib")

        if os.path.exists(metrics_file):
            with open(metrics_file) as f:
                metrics = json.load(f)
            mcol1, mcol2, mcol3 = st.columns(3)
            with mcol1:
                st.metric("Model Architecture", metrics["classifier_name"])
            with mcol2:
                st.metric("Turnout Prediction Accuracy", f"{metrics['accuracy']*100:.1f}%")
            with mcol3:
                st.metric("Trained Demographic Samples", metrics["total_samples"])

        st.markdown("---")
        st.markdown("#### 🔮 Predict Turnout Likelihood for a Demographic Cohort")
        pcol1, pcol2 = st.columns(2)
        with pcol1:
            in_role = st.selectbox("Voter Category", ["Student", "Faculty"])
            in_dept = st.selectbox("Academic Department", [
                "Computer Engineering", "Information Technology", "Mechanical Engineering",
                "Civil Engineering", "Electronics", "Biotech Engineering"
            ])
            in_att = st.slider("Average Campus Attendance %", 40, 100, 82)
            in_club = st.radio("Campus Society / Club Member?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No", horizontal=True)
        with pcol2:
            in_score = st.slider("Academic Score / GPA (out of 10)", 4.0, 10.0, 8.1, 0.1)
            in_days = st.slider("Days Registered Before Election", 1, 60, 20)
            in_cand = st.radio("Has Department Candidate Running?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No", horizontal=True)
            in_past = st.radio("Voted in Previous Campus Election?", [1, 0], format_func=lambda x: "Yes" if x == 1 else "No", horizontal=True)

        if st.button("Run Turnout Prediction", type="primary"):
            if os.path.exists(clf_file):
                clf = joblib.load(clf_file)
                feature_names = joblib.load(os.path.join(models_dir, "feature_columns.joblib"))

                # Construct feature input vector
                input_dict = {col: 0 for col in feature_names}
                input_dict["attendance_pct"] = in_att
                input_dict["campus_club_member"] = in_club
                input_dict["academic_score"] = in_score
                input_dict["days_registered_before_election"] = in_days
                input_dict["has_candidate_from_dept"] = in_cand
                input_dict["past_election_voted"] = in_past

                if in_role == "Student" and "role_Student" in input_dict:
                    input_dict["role_Student"] = 1
                dept_col = f"dept_{in_dept}"
                if dept_col in input_dict:
                    input_dict[dept_col] = 1

                input_df = pd.DataFrame([input_dict])[feature_names]
                pred = clf.predict(input_df)[0]
                prob = clf.predict_proba(input_df)[0][1]

                st.markdown("---")
                res_col1, res_col2 = st.columns([1, 2])
                with res_col1:
                    if pred == 1:
                        st.success(f"### Likely to Vote! 🗳️\n**Confidence:** `{prob*100:.1f}%`")
                    else:
                        st.warning(f"### Low Turnout Risk ⚠️\n**Confidence:** `{(1-prob)*100:.1f}%`")
                with res_col2:
                    st.info(f"""
                    **Engagement Diagnostic:**
                    • **Department:** {in_dept}
                    • **Key Factor:** Attendance ({in_att}%) and Previous Voting History have the highest feature impact.
                    • **Recommendation:** { 'Cohort is active. Standard reminders sufficient.' if pred == 1 else 'Deploy mobile SMS alert & department coordinator reminder.' }
                    """)
            else:
                st.warning("Model file not found. Please run `python train_model.py` first.")

    # Tab 6: Voter Audit Roll
    with admin_tabs[5]:
        st.markdown("### 📜 Tamper-Proof Voter Audit Roll")
        st.write("Verifies which voters have participated. In accordance with the Secret Ballot principle, individual ballot selections remain cryptographically decoupled.")
        conn = get_connection()
        audit_df = pd.read_sql_query("""
            SELECT 
                vr.receipt_code as 'Receipt Token',
                u.name as 'Voter Name',
                u.identifier as 'Roll No / Faculty ID',
                u.role as 'Role',
                u.department as 'Department',
                e.title as 'Election Title',
                vr.voted_at as 'Timestamp'
            FROM voter_records vr
            JOIN users u ON vr.user_id = u.id
            JOIN elections e ON vr.election_id = e.id
            ORDER BY vr.voted_at DESC
        """, conn)
        conn.close()

        if audit_df.empty:
            st.info("No voting participation records logged yet.")
        else:
            st.dataframe(audit_df, use_container_width=True, hide_index=True)


# -----------------------------------------------------------------------------
# 2. 🎓 STUDENT INTERFACE
# -----------------------------------------------------------------------------
elif role == "student":
    st.markdown('<div class="main-title">🎓 Student Democratic Voting Portal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Welcome, <strong>{user["name"]}</strong> (Roll No: <code>{user["identifier"]}</code>, {user["department"]})</div>', unsafe_allow_html=True)

    student_tabs = st.tabs(["🗳️ Cast Your Ballot", "🧾 My Voting Receipts", "📊 Student Election Results"])

    # Tab 1: Cast Ballot
    with student_tabs[0]:
        elections = get_elections_for_role("student")
        active_elections = [e for e in elections if e["status"] == "active"]

        if not active_elections:
            st.info("There are currently no active student elections open for voting.")
        else:
            for el in active_elections:
                st.markdown(f"### 📋 {el['title']}")
                st.markdown(f"*{el['description']}*")

                has_voted, record = check_has_voted(user["id"], el["id"])

                if has_voted:
                    st.markdown(f"""
                    <div class="receipt-box">
                        <h4 style="color: #065F46; margin-top: 0;">✅ Ballot Already Cast</h4>
                        <p>You have already securely cast your confidential vote in this election.</p>
                        <p><strong>Your Cryptographic Receipt Token:</strong> <code>{record['receipt_code']}</code></p>
                        <p><strong>Timestamp:</strong> {record['voted_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.write("")
                else:
                    st.markdown("#### Select Your Candidates")
                    positions = get_positions(el["id"])
                    if not positions:
                        st.warning("No positions defined for this election yet.")
                    else:
                        with st.form(f"ballot_form_{el['id']}"):
                            user_selections = {}
                            all_selected = True

                            for pos in positions:
                                st.markdown(f"##### 📌 Position: **{pos['title']}**")
                                st.caption(pos["description"])
                                candidates = get_candidates(pos["id"])

                                if not candidates:
                                    st.info("No candidates registered for this position.")
                                else:
                                    cand_options = {
                                        c["id"]: f"{c['symbol_emoji']} {c['name']} ({c['department']}) - \"{c['manifesto']}\""
                                        for c in candidates
                                    }
                                    chosen_cand_id = st.radio(
                                        f"Choose candidate for {pos['title']}:",
                                        options=list(cand_options.keys()),
                                        format_func=lambda cid: cand_options[cid],
                                        key=f"radio_pos_{pos['id']}"
                                    )
                                    user_selections[pos["id"]] = chosen_cand_id
                                st.markdown("---")

                            cast_btn = st.form_submit_button("🔒 Submit Confidential Ballot", type="primary", use_container_width=True)

                            if cast_btn:
                                if len(user_selections) != len(positions):
                                    st.error("Please cast your vote for all available positions.")
                                else:
                                    success, msg, receipt = cast_ballot(user["id"], el["id"], user_selections)
                                    if success:
                                        st.balloons()
                                        st.success(f"{msg}\n\n**Your Secret Receipt Code:** `{receipt}`")
                                        st.rerun()
                                    else:
                                        st.error(msg)

    # Tab 2: Voting Receipts
    with student_tabs[1]:
        st.markdown("### 🧾 Official Voting Certificate & Receipt History")
        conn = get_connection()
        my_receipts = pd.read_sql_query("""
            SELECT 
                vr.receipt_code as 'Receipt Token',
                e.title as 'Election Name',
                vr.voted_at as 'Voted At'
            FROM voter_records vr
            JOIN elections e ON vr.election_id = e.id
            WHERE vr.user_id = ?
        """, conn, params=(user["id"],))
        conn.close()

        if my_receipts.empty:
            st.info("You have not cast any votes yet.")
        else:
            for idx, r in my_receipts.iterrows():
                st.markdown(f"""
                <div class="receipt-box" style="margin-bottom: 12px;">
                    <div style="font-size: 1.1rem; font-weight: 700; color: #065F46;">
                        🎓 Campus Voter Certificate of Participation
                    </div>
                    <div style="margin-top: 8px; font-size: 0.95rem;">
                        <strong>Voter:</strong> {user['name']} (Roll No: {user['identifier']})<br>
                        <strong>Election:</strong> {r['Election Name']}<br>
                        <strong>Verification Token:</strong> <code>{r['Receipt Token']}</code><br>
                        <strong>Timestamp:</strong> {r['Voted At']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # Tab 3: Results
    with student_tabs[2]:
        st.markdown("### 📊 Student Council Election Tally")
        elections = get_elections_for_role("student")
        if not elections:
            st.info("No student elections available.")
        else:
            sel_el = st.selectbox("Select Election", elections, format_func=lambda e: e["title"])
            results = get_election_vote_counts(sel_el["id"])
            if not results:
                st.info("No votes cast yet in this election.")
            else:
                res_df = pd.DataFrame(results)
                for pos in res_df["position_title"].unique():
                    p_df = res_df[res_df["position_title"] == pos]
                    fig = px.bar(
                        p_df, x="candidate_name", y="vote_count", color="candidate_name",
                        title=f"Votes for {pos}", text="vote_count"
                    )
                    fig.update_layout(height=280, showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)


# -----------------------------------------------------------------------------
# 3. 🏛️ FACULTY INTERFACE
# -----------------------------------------------------------------------------
elif role == "faculty":
    st.markdown('<div class="main-title">🏛️ Faculty Senate & Academic Council Portal</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-title">Welcome, <strong>{user["name"]}</strong> (Faculty ID: <code>{user["identifier"]}</code>, {user["department"]})</div>', unsafe_allow_html=True)

    faculty_tabs = st.tabs(["🗳️ Faculty Ballots", "🧾 Verification Receipts", "📊 Senate Results"])

    # Tab 1: Faculty Ballot
    with faculty_tabs[0]:
        elections = get_elections_for_role("faculty")
        active_elections = [e for e in elections if e["status"] == "active"]

        if not active_elections:
            st.info("There are currently no active faculty or senate elections open.")
        else:
            for el in active_elections:
                st.markdown(f"### 📋 {el['title']}")
                st.markdown(f"*{el['description']}*")

                has_voted, record = check_has_voted(user["id"], el["id"])

                if has_voted:
                    st.markdown(f"""
                    <div class="receipt-box">
                        <h4 style="color: #065F46; margin-top: 0;">✅ Faculty Ballot Confirmed</h4>
                        <p>Your confidential faculty ballot has been successfully recorded in the ledger.</p>
                        <p><strong>Receipt Token:</strong> <code>{record['receipt_code']}</code></p>
                        <p><strong>Timestamp:</strong> {record['voted_at']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    positions = get_positions(el["id"])
                    if not positions:
                        st.warning("No positions configured yet.")
                    else:
                        with st.form(f"fac_ballot_{el['id']}"):
                            selections = {}
                            for pos in positions:
                                st.markdown(f"##### 📌 Position: **{pos['title']}**")
                                st.caption(pos["description"])
                                candidates = get_candidates(pos["id"])

                                if candidates:
                                    cand_options = {
                                        c["id"]: f"{c['symbol_emoji']} {c['name']} ({c['department']}) - Proposal: \"{c['manifesto']}\""
                                        for c in candidates
                                    }
                                    chosen = st.radio(
                                        f"Cast faculty vote for {pos['title']}:",
                                        options=list(cand_options.keys()),
                                        format_func=lambda cid: cand_options[cid],
                                        key=f"fac_radio_{pos['id']}"
                                    )
                                    selections[pos["id"]] = chosen
                                st.markdown("---")

                            fac_sub = st.form_submit_button("🔒 Submit Official Faculty Ballot", type="primary", use_container_width=True)
                            if fac_sub:
                                if len(selections) != len(positions):
                                    st.error("Please vote for all required positions.")
                                else:
                                    success, msg, receipt = cast_ballot(user["id"], el["id"], selections)
                                    if success:
                                        st.balloons()
                                        st.success(f"{msg}\n\n**Faculty Token:** `{receipt}`")
                                        st.rerun()
                                    else:
                                        st.error(msg)

    # Tab 2: Receipts
    with faculty_tabs[1]:
        st.markdown("### 🧾 Official Faculty Voting Records")
        conn = get_connection()
        f_receipts = pd.read_sql_query("""
            SELECT vr.receipt_code, e.title, vr.voted_at 
            FROM voter_records vr 
            JOIN elections e ON vr.election_id = e.id 
            WHERE vr.user_id = ?
        """, conn, params=(user["id"],))
        conn.close()

        if f_receipts.empty:
            st.info("No votes cast yet.")
        else:
            for idx, r in f_receipts.iterrows():
                st.markdown(f"""
                <div class="receipt-box" style="margin-bottom: 12px;">
                    <strong>Election:</strong> {r['title']}<br>
                    <strong>Faculty Token:</strong> <code>{r['receipt_code']}</code><br>
                    <strong>Recorded At:</strong> {r['voted_at']}
                </div>
                """, unsafe_allow_html=True)

    # Tab 3: Senate Results
    with faculty_tabs[2]:
        st.markdown("### 📊 Academic Senate Results & Trends")
        elections = get_elections_for_role("faculty")
        if elections:
            sel_el = st.selectbox("Select Faculty Election", elections, format_func=lambda e: e["title"], key="fac_res_sel")
            results = get_election_vote_counts(sel_el["id"])
            if results:
                f_df = pd.DataFrame(results)
                for pos in f_df["position_title"].unique():
                    pos_sub_df = f_df[f_df["position_title"] == pos]
                    fig = px.pie(
                        pos_sub_df, names="candidate_name", values="vote_count",
                        title=f"Vote Distribution - {pos}", hole=0.4
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No votes cast yet.")
