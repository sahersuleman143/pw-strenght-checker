import streamlit as st
import re
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- Custom CSS --- 
def local_css():
    st.markdown("""
        <style>
        .main {
            background-color: #f0f2f6;
            font-family: 'Segoe UI', sans-serif;
        }
        .password-box {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
            max-width: 500px;
            margin: auto;
        }
        .password-title {
            font-size: 3rem;
            font-weight: bold;
            text-align: center;
            color: #ffffff;  /* White text */
            background-color: #2c3e50;  /* Dark background */
            padding: 10px 20px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .description {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 20px;
            font-weight: normal;
        }
        .subheading {
            font-size: 1.5rem;
            font-weight: bold;
            text-align: center;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        .strength {
            font-weight: bold;
            font-size: 1.2rem;
        }
        .tips {
            font-size: 0.95rem;
            line-height: 1.6;
        }
        @media (max-width: 600px) {
            .password-box {
                padding: 1rem;
            }
            .password-title {
                font-size: 2.5rem;
            }
            .subheading {
                font-size: 1.3rem;
            }
        }
        </style>
    """, unsafe_allow_html=True)

# --- Check Individual Criteria --- 
def get_password_tips(password):
    tips = {
        "At least 8 characters": len(password) >= 8,
        "Contains uppercase letter (A-Z)": bool(re.search(r"[A-Z]", password)),
        "Contains lowercase letter (a-z)": bool(re.search(r"[a-z]", password)),
        "Contains number (0-9)": bool(re.search(r"[0-9]", password)),
        "Contains special character (!@#$...)": bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))
    }
    return tips

# --- Password Strength Logic --- 
def check_password_strength(password):
    strength = 0
    tips = get_password_tips(password)

    for tip in tips.values():
        if tip:
            strength += 1

    if strength == 0:
        remarks = "Too Weak 😬"
        color = "red"
    elif strength <= 2:
        remarks = "Weak ⚠️"
        color = "orange"
    elif strength == 3:
        remarks = "Moderate 🟡"
        color = "gold"
    elif strength == 4:
        remarks = "Strong ✅"
        color = "green"
    else:
        remarks = "Very Strong 🔒"
        color = "darkgreen"

    return strength, remarks, color, tips

# --- Save History to CSV --- 
def save_to_csv(password, strength, remarks):
    data = {"Password": [password], "Strength": [strength], "Remarks": [remarks]}
    df = pd.DataFrame(data)
    df.to_csv("password_history.csv", mode='a', header=False, index=False)
    st.success("Exported to CSV ✅")

# --- Save History to PDF --- 
def save_to_pdf(password, strength, remarks):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Password Strength Report", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Password: {password}", ln=True)
    pdf.cell(200, 10, txt=f"Strength: {strength}/5", ln=True)
    pdf.cell(200, 10, txt=f"Remarks: {remarks}", ln=True)
    pdf.output("password_report.pdf")
    st.success("Exported to PDF ✅")

# --- Load CSS --- 
local_css()

# --- Layout Start --- 
st.markdown('<div class="password-box">', unsafe_allow_html=True)

# Heading with custom color and background
st.markdown('<div class="password-title">🔒 Password Strength Checker</div>', unsafe_allow_html=True)

# Subheading - Less Bold
st.markdown('<div class="subheading">Assess your password’s strength and enhance its security.</div>', unsafe_allow_html=True)

# Description - Even Less Bold
st.markdown('<div class="description">Check your password’s strength in real-time and receive personalized improvement tips.</div>', unsafe_allow_html=True)

password = st.text_input("Enter your password:", type="password")

if password:
    strength, remarks, color, tips = check_password_strength(password)

    # Show strength bar
    st.progress(strength / 5)

    # Show strength score and remarks
    st.markdown(f'<p class="strength" style="color:{color};">Strength Score: {strength}/5</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="strength" style="color:{color};">Result: {remarks}</p>', unsafe_allow_html=True)

    # Show password tips
    st.markdown('<hr><div class="tips"><strong>Password Tips:</strong><br>', unsafe_allow_html=True)
    for tip, status in tips.items():
        icon = "✅" if status else "❌"
        st.markdown(f"{icon} {tip}")
    st.markdown("</div>", unsafe_allow_html=True)

    # Save history
    if "history" not in st.session_state:
        st.session_state.history = []

    if st.button("Save Result"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({"password": password, "strength": strength, "remarks": remarks, "timestamp": timestamp})
        st.write("Result saved!")

    # Show history
    if len(st.session_state.history) > 0:
        st.subheader("Password Check History")
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df)

    # Export buttons
    if st.button("📥 Export to CSV"):
        save_to_csv(password, strength, remarks)

    if st.button("📄 Export to PDF"):
        save_to_pdf(password, strength, remarks)

st.markdown('</div>', unsafe_allow_html=True)
