"""
Online Voting Management System for Students & Faculty
Machine Learning Pipeline for Voter Turnout Prediction & Engagement Analysis
Trains:
1. Voter Turnout Probability Classifier (Random Forest Classifier)
2. Departmental Voter Participation Regressor (Gradient Boosting Regressor)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import accuracy_score, classification_report, r2_score, mean_absolute_error

def generate_voter_turnout_dataset(n_samples=1500, random_state=42):
    """
    Generates realistic synthetic voter engagement data across student & faculty demographics
    to model voter turnout behavior, participation likelihood, and campus engagement.
    """
    np.random.seed(random_state)

    departments = [
        "Computer Engineering", "Information Technology", "Mechanical Engineering",
        "Civil Engineering", "Electronics", "Biotech Engineering"
    ]
    roles = ["Student", "Faculty"]
    years_student = ["First Year", "Second Year", "Third Year", "Final Year"]
    designations_faculty = ["Assistant Professor", "Associate Professor", "Professor & HOD"]

    records = []
    for i in range(n_samples):
        role = np.random.choice(roles, p=[0.82, 0.18])
        dept = np.random.choice(departments)
        
        if role == "Student":
            sub_tier = np.random.choice(years_student, p=[0.25, 0.28, 0.27, 0.20])
            attendance_pct = np.clip(np.random.normal(78, 12), 45, 100)
            campus_club_member = np.random.choice([1, 0], p=[0.45, 0.55])
            academic_performance = np.clip(np.random.normal(7.6, 1.2), 4.0, 10.0) # GPA out of 10
            days_registered_before_election = np.random.randint(3, 45)
            has_candidate_from_dept = np.random.choice([1, 0], p=[0.60, 0.40])
            past_election_voted = np.random.choice([1, 0], p=[0.58, 0.42])

            # Voting probability calculation
            score = (
                0.25 * (attendance_pct / 100) +
                0.20 * campus_club_member +
                0.15 * past_election_voted +
                0.15 * has_candidate_from_dept +
                0.15 * (academic_performance / 10) +
                0.10 * (1 if sub_tier in ["Third Year", "Final Year"] else 0.5)
            )
        else:
            sub_tier = np.random.choice(designations_faculty, p=[0.50, 0.30, 0.20])
            attendance_pct = np.clip(np.random.normal(92, 5), 75, 100)
            campus_club_member = 1 # Committee member
            academic_performance = np.clip(np.random.normal(8.8, 0.8), 6.5, 10.0)
            days_registered_before_election = np.random.randint(15, 60)
            has_candidate_from_dept = np.random.choice([1, 0], p=[0.75, 0.25])
            past_election_voted = np.random.choice([1, 0], p=[0.82, 0.18])

            score = (
                0.35 * past_election_voted +
                0.25 * has_candidate_from_dept +
                0.20 * (attendance_pct / 100) +
                0.20 * (1 if sub_tier == "Professor & HOD" else 0.8)
            )

        # Probabilistic turnout outcome with slight noise
        prob = np.clip(score + np.random.normal(0, 0.08), 0.05, 0.95)
        voted = 1 if prob >= 0.50 else 0

        # Turnout hour (8 AM to 5 PM)
        turnout_hour = np.random.choice(
            [9, 10, 11, 12, 13, 14, 15, 16],
            p=[0.08, 0.18, 0.22, 0.12, 0.10, 0.14, 0.11, 0.05]
        ) if voted else 0

        records.append({
            "voter_id": f"VTR_{1000 + i}",
            "role": role,
            "department": dept,
            "tier_or_designation": sub_tier,
            "attendance_pct": round(attendance_pct, 1),
            "campus_club_member": campus_club_member,
            "academic_score": round(academic_performance, 2),
            "days_registered_before_election": days_registered_before_election,
            "has_candidate_from_dept": has_candidate_from_dept,
            "past_election_voted": past_election_voted,
            "turnout_probability": round(float(prob), 4),
            "voted": voted,
            "turnout_hour": turnout_hour
        })

    df = pd.DataFrame(records)
    return df

def train_and_save_models():
    base_dir = os.path.dirname(__file__)
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(models_dir, exist_ok=True)

    print("Generating voter demographics & turnout dataset...")
    df = generate_voter_turnout_dataset(n_samples=2000)
    dataset_path = os.path.join(data_dir, "voter_turnout_dataset.csv")
    df.to_csv(dataset_path, index=False)
    print(f"Dataset saved to: {dataset_path} (Total records: {len(df)})")
    print(f"Turnout Distribution: {df['voted'].value_counts().to_dict()}")

    # 1. Feature Preprocessing
    feature_cols = [
        "attendance_pct", "campus_club_member", "academic_score",
        "days_registered_before_election", "has_candidate_from_dept", "past_election_voted"
    ]
    
    # Categorical encodings
    role_encoded = pd.get_dummies(df["role"], prefix="role", drop_first=True)
    dept_encoded = pd.get_dummies(df["department"], prefix="dept", drop_first=True)

    X = pd.concat([df[feature_cols], role_encoded, dept_encoded], axis=1)
    y_class = df["voted"]
    y_reg = df["turnout_probability"]

    X_train, X_test, y_train_c, y_test_c, y_train_r, y_test_r = train_test_split(
        X, y_class, y_reg, test_size=0.2, random_state=42, stratify=y_class
    )

    # 2. Train Turnout Classifier (Random Forest)
    print("\n--- Training Voter Turnout Classifier (Random Forest) ---")
    clf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    clf.fit(X_train, y_train_c)
    y_pred_c = clf.predict(X_test)
    acc = accuracy_score(y_test_c, y_pred_c)
    print(f"Classifier Accuracy: {acc * 100:.2f}%")
    print(classification_report(y_test_c, y_pred_c))

    # 3. Train Turnout Likelihood Regressor (Gradient Boosting)
    print("\n--- Training Voter Turnout Probability Regressor (Gradient Boosting) ---")
    reg = GradientBoostingRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
    reg.fit(X_train, y_train_r)
    y_pred_r = reg.predict(X_test)
    r2 = r2_score(y_test_r, y_pred_r)
    mae = mean_absolute_error(y_test_r, y_pred_r)
    print(f"Regressor R² Score: {r2:.4f}")
    print(f"Regressor MAE: {mae:.4f}")

    # 4. Save Model Artifacts
    joblib.dump(clf, os.path.join(models_dir, "turnout_classifier.joblib"))
    joblib.dump(reg, os.path.join(models_dir, "turnout_regressor.joblib"))
    joblib.dump(list(X.columns), os.path.join(models_dir, "feature_columns.joblib"))

    metrics = {
        "classifier_name": "Random Forest Classifier",
        "accuracy": round(float(acc), 4),
        "regressor_name": "Gradient Boosting Regressor",
        "r2_score": round(float(r2), 4),
        "mean_absolute_error": round(float(mae), 4),
        "total_samples": len(df),
        "features": list(X.columns),
        "turnout_overall_rate": round(float(df["voted"].mean() * 100), 2)
    }

    with open(os.path.join(models_dir, "model_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=4)

    print("\nAll model artifacts and metrics successfully saved to `models/` directory.")

if __name__ == "__main__":
    train_and_save_models()
