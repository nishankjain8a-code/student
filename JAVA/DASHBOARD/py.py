import streamlit as s
import pandas as pd
import numpy as np
from fpdf import FPDF
import plotly.express as px
import plotly.graph_objects as go

# ===============================================================
# PAGE CONFIG
# ===============================================================
st.set_page_config(page_title="Student Success Hub", page_icon="🎓", layout="wide")

# ===============================================================
# ===============================================================
# LOAD DATA
# ===============================================================
import pathlib
DATA = pathlib.Path(__file__).parent / "cleaned_data.csv"
df = pd.read_csv(DATA)


# ===============================================================
# AUTO-DETECT SUBJECT COLUMNS
# ===============================================================
subject_cols = [
    c for c in df.columns
    if any(k in c.lower() for k in ["score", "marks"]) and "average" not in c.lower()
]

# ===============================================================
# THEME SETTINGS
# ===============================================================
if "theme" not in st.session_state:
    st.session_state["theme"] = "Default"
if "accent" not in st.session_state:
    st.session_state["accent"] = "#4CAF50"

def apply_theme(theme, accent):
    bg = "#FFFFFF"; text = "#000000"; card = "#F5F5F5"

    if theme == "Dark":
        bg = "#0E1117"; text = "#FAFAFA"; card = "#1E1E1E"
    elif theme == "Minimal":
        bg = "#FFFFFF"; text = "#222222"; card = "#FAFAFA"

    st.markdown(
        f"""
        <style>
        .stApp {{ background-color: {bg}; color: {text}; }}
        .metric-card {{
            background-color: {card};
            padding: 1rem;
            border-radius: 12px;
            border-left: 4px solid {accent};
            margin-bottom: 12px;
        }}
        .peer-card {{
            background-color: {card};
            padding: 0.8rem;
            border-radius: 12px;
            margin-bottom: 10px;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ===============================================================
# SIDEBAR
# ===============================================================
st.sidebar.title("Dashboard Settings")

user = st.session_state.get("username", "User")
st.sidebar.header(f"👋 Hello, {user}")

theme_choice = st.sidebar.radio("Theme", ["Default", "Dark", "Minimal"])
accent_choice = st.sidebar.color_picker("Accent Color", st.session_state["accent"])

st.session_state["theme"] = theme_choice
st.session_state["accent"] = accent_choice
apply_theme(theme_choice, accent_choice)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Smart Filters (Cascading)")

# ===============================================================
# SMART CASCADING FILTERS
# ===============================================================

casc_df = df.copy()

# 1. Grade
grade_options = sorted(casc_df["Grade"].unique())
grade = st.sidebar.selectbox("Grade", ["All"] + grade_options)
if grade != "All":
    casc_df = casc_df[casc_df["Grade"] == grade]

# 2. City (depends on grade)
city_options = sorted(casc_df["City"].unique())
city = st.sidebar.selectbox("City", ["All"] + city_options)
if city != "All":
    casc_df = casc_df[casc_df["City"] == city]

# 3. Section (depends on grade + city)
section_options = sorted(casc_df["Section"].unique())
section = st.sidebar.selectbox("Section", ["All"] + section_options)
if section != "All":
    casc_df = casc_df[casc_df["Section"] == section]

# 4. Student (depends on all above)
student_options = sorted(casc_df["Name"].unique())
student = st.sidebar.selectbox("Student Name", ["All"] + student_options)

# Final dataframe
filtered_df = casc_df.copy()
if student != "All":
    filtered_df = filtered_df[filtered_df["Name"] == student]

# ===============================================================
# SESSION VARIABLES
# ===============================================================
if "peer_wall" not in st.session_state:
    st.session_state["peer_wall"] = []
if "mood_meter" not in st.session_state:
    st.session_state["mood_meter"] = {}

# ===============================================================
# HEADER
# ===============================================================
st.title("🎓 Student Success Hub Dashboard")
st.caption("AI-powered • Smart Filters • Gamified Experience")

# ===============================================================
# TABS
# ===============================================================
tab_map, tab_insights, tab_gamify, tab_personal, tab_compare, tab_pdf, tab_ai = st.tabs([
    "🗺 Progress Map",
    "📊 Insights",
    "🎮 Gamification",
    "💙 Personalization",
    "🆚 Compare",
    "📄 PDF Report",
    "🤖 AI Recommendations"
])

# ===============================================================
# TAB 1 — MAP
# ===============================================================
with tab_map:
    st.subheader("🗺 Student Location Map")

    city_coords = {
        "Delhi": (28.61, 77.20),
        "Mumbai": (19.07, 72.87),
        "Chennai": (13.08, 80.27),
        "Kolkata": (22.57, 88.36),
        "Hyderabad": (17.38, 78.48),
        "Bengaluru": (12.97, 77.59)
    }

    map_df = filtered_df.groupby("City").agg(
        Count=("StudentID", "count"),
        AvgMarks=("AverageMarks", "mean")
    ).reset_index()

    map_df["lat"] = map_df["City"].apply(lambda c: city_coords.get(c, (20.5, 78.9))[0])
    map_df["lon"] = map_df["City"].apply(lambda c: city_coords.get(c, (20.5, 78.9))[1])

    st.map(map_df[["lat", "lon"]])
    st.dataframe(map_df)

# ===============================================================
# TAB 2 — INSIGHTS
# ===============================================================
with tab_insights:
    st.subheader("📊 Insights & Trends")

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Avg GPA", f"{filtered_df['GPA'].mean():.2f}")
    with c2: st.metric("Attendance %", f"{filtered_df['AttendancePercent'].mean():.1f}")
    with c3: st.metric("Study Hours", f"{filtered_df['StudyHoursPerWeek'].mean():.1f}")
    with c4: st.metric("Assignments", f"{filtered_df['AssignmentsSubmitted'].mean():.1f}")

    st.markdown("### 📈 Animated Marks Chart")
    try:
        fig = px.bar(
            filtered_df,
            x="Name",
            y="AverageMarks",
            animation_frame="Grade",
            color="AverageMarks",
            title="Performance Progress Across Grades"
        )
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.info("Not enough data to render animated chart.")

    st.markdown("### 📚 Subject Analysis")
    subject = st.selectbox("Choose Subject", subject_cols)

    left, right = st.columns(2)
    with left: st.bar_chart(filtered_df, y=subject)
    with right:
        st.write("Average:", filtered_df[subject].mean())
        st.write("Max:", filtered_df[subject].max())
        st.write("Min:", filtered_df[subject].min())

# ===============================================================
# TAB 3 — GAMIFICATION
# ===============================================================
with tab_gamify:
    st.subheader("🎮 Gamification Zone")

    if len(filtered_df) == 0:
        st.warning("No student matches the selected filters.")
    else:
        stu = st.selectbox("Select Student", filtered_df["Name"].unique(), key="gamify_student_select")
        s = filtered_df[filtered_df["Name"] == stu].iloc[0]

        def rank(gpa):
            if gpa >= 9: return "🏆 Legend"
            if gpa >= 8: return "🥇 Pro"
            if gpa >= 7: return "🥈 Achiever"
            return "🥉 Beginner"

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.markdown(f"<div class='metric-card'><h4>Rank</h4><h2>{rank(s['GPA'])}</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='metric-card'><h4>GPA</h4><h2>{s['GPA']}</h2></div>", unsafe_allow_html=True)
        with c3: st.markdown(f"<div class='metric-card'><h4>Attendance</h4><h2>{s['AttendancePercent']}%</h2></div>", unsafe_allow_html=True)
        with c4: st.markdown(f"<div class='metric-card'><h4>Assignments</h4><h2>{s['AssignmentsSubmitted']}</h2></div>", unsafe_allow_html=True)

        best_sub = max(subject_cols, key=lambda c: s[c])
        st.markdown(
            f"<div class='metric-card'>📸 <b>Memory Lane</b><br>{stu} scored <b>{s[best_sub]}</b> in <b>{best_sub}</b>.</div>",
            unsafe_allow_html=True
        )

# ===============================================================
# TAB 4 — PERSONALIZATION
# ===============================================================
with tab_personal:
    st.subheader("💙 Personalization Features")
#TAB 5
with tab_compare:
    st.subheader("🆚 Student Comparison")

    if "Name" not in df.columns or not subject_cols:
        st.info("Need Name and subject marks columns for comparison.")
    else:
        names = sorted(df["Name"].dropna().unique().tolist())
        c1, c2 = st.columns(2)
        stu1 = c1.selectbox("Student A", names)
        stu2 = c2.selectbox("Student B", names, index=min(1, len(names)-1))

        if stu1 == stu2:
            st.warning("Choose two different students to compare.")
        else:
            s1 = df[df["Name"] == stu1].iloc[0]
            s2 = df[df["Name"] == stu2].iloc[0]
            comp_df = pd.DataFrame({
                "Subject": subject_cols,
                stu1: [s1[sub] for sub in subject_cols],
                stu2: [s2[sub] for sub in subject_cols],
            })
            st.markdown("### 📊 Subject-wise Comparison")
            st.bar_chart(comp_df.set_index("Subject"))

            st.markdown("### 🕸 Radar View")
            fig  = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=comp_df[stu1], theta=comp_df["Subject"],
                fill='toself', name=stu1
            ))
            fig.add_trace(go.Scatterpolar(
                r=comp_df[stu2], theta=comp_df["Subject"],
                fill='toself', name=stu2
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True)))
            st.plotly_chart(fig)

# ===============================================================
# TAB 5 — PDF REPORT
# ===============================================================
with tab_pdf:
    st.subheader("📄 Download Student PDF Report")

    stu = st.selectbox("Choose Student", df["Name"].unique())
    row = df[df["Name"] == stu].iloc[0]

    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=14)
        pdf.cell(200, 10, txt="Student Performance Report", ln=True, align="C")
        pdf.ln(10)

        for col in df.columns:
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 8, txt=f"{col}: {row[col]}", ln=True)

        pdf.output("report.pdf")

        with open("report.pdf", "rb") as f:
            st.download_button("Download PDF", f, file_name=f"{stu}_report.pdf")

# ===============================================================
# TAB 6 — AI RECOMMENDATIONS
# ===============================================================
with tab_ai:
    st.subheader("🤖 AI Recommendations")

    stu = st.selectbox("Select Student", df["Name"].unique(), key="ai_recs_student_select")
    s = df[df["Name"] == stu].iloc[0]

    recs = []

    if s["AttendancePercent"] < 75:
        recs.append("📌 Improve attendance to stabilize learning.")
    if s["StudyHoursPerWeek"] < 10:
        recs.append("⏳ Increase study hours to at least 10/week.")
    weak = min(subject_cols, key=lambda c: s[c])
    recs.append(f"📚 Focus more on {weak} — weakest subject.")
    if s["GPA"] < 7:
        recs.append("🎯 Follow a structured daily revision plan.")

    for r in recs:
        st.write("- " + r)





