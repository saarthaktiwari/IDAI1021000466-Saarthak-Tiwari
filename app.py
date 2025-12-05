# MedTimer - Daily Medicine Companion
# Author: Saarthak

import streamlit as st
import pandas as pd
import datetime as dt
from dateutil import parser
import os, json
from fpdf import FPDF

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(page_title="MedTimer", page_icon="💊", layout="wide")

# ----------------------------
# Persistence
# ----------------------------
DATA_FILE = "medtimer_data.json"

def save_data():
    data = {
        "meds": st.session_state.meds,
        "history": st.session_state.history,
        "id_counter": st.session_state.id_counter
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except:
        pass

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            st.session_state.meds = data.get("meds", [])
            st.session_state.history = data.get("history", {})
            st.session_state.id_counter = data.get("id_counter", 1)
        except:
            st.session_state.meds = []
            st.session_state.history = {}
            st.session_state.id_counter = 1

# ----------------------------
# Init state
# ----------------------------
def init_state():
    if "username" not in st.session_state:
        st.session_state.username = None
    if "meds" not in st.session_state:
        st.session_state.meds = []
    if "history" not in st.session_state:
        st.session_state.history = {}
    if "id_counter" not in st.session_state:
        st.session_state.id_counter = 1

init_state()
load_data()

# ----------------------------
# Login screen
# ----------------------------
if not st.session_state.username:
    st.title("💊 Welcome to MedTimer")
    st.subheader("Your daily health companion")
    st.write("A gentle, focused space to keep your medicines on track.")

    with st.form("login_form"):
        name = st.text_input("Please enter your name to begin:")
        submitted = st.form_submit_button("Continue")

    if submitted:
        if name.strip():
            st.session_state.username = name.strip()
            st.success(f"Welcome, {st.session_state.username}! Let’s set you up.")
            st.rerun()   # <-- fixed here
        else:
            st.warning("Name can't be empty.")
    st.stop()

# ----------------------------
# Utilities
# ----------------------------
def parse_hhmm(time_str: str) -> dt.datetime:
    today = dt.date.today()
    t = parser.parse(time_str).time()
    return dt.datetime.combine(today, t)

def now_local() -> dt.datetime:
    return dt.datetime.now()

def status_color(status: str) -> str:
    return {"taken": "#4caf50", "upcoming": "#f9a825", "missed": "#c62828"}.get(status, "#607d8b")

def compute_status(med) -> str:
    if med.get("status") == "taken":
        return "taken"
    target = parse_hhmm(med["time_str"])
    return "upcoming" if now_local() < target else "missed"

def update_all_statuses():
    for med in st.session_state.meds:
        med["status"] = compute_status(med)

def adherence_today():
    scheduled = len(st.session_state.meds)
    taken = sum(1 for m in st.session_state.meds if m.get("status") == "taken")
    pct = int((taken / scheduled) * 100) if scheduled else 0
    return scheduled, taken, pct

def record_daily_history():
    date_key = dt.date.today().isoformat()
    scheduled, taken, _ = adherence_today()
    st.session_state.history[date_key] = {"scheduled": scheduled, "taken": taken}
    save_data()

def weekly_adherence():
    today = dt.date.today()
    rows = []
    for i in range(7):
        d = (today - dt.timedelta(days=i)).isoformat()
        rec = st.session_state.history.get(d, {"scheduled": 0, "taken": 0})
        pct = int((rec["taken"]/rec["scheduled"]*100)) if rec["scheduled"] else 0
        rows.append({"date": d, "scheduled": rec["scheduled"], "taken": rec["taken"], "adherence_%": pct})
    rows.reverse()
    df = pd.DataFrame(rows)
    weekly_pct = int(df["adherence_%"].mean()) if not df.empty else 0
    return df, weekly_pct

def current_streak():
    today = dt.date.today()
    streak = 0
    for i in range(30):
        d = (today - dt.timedelta(days=i)).isoformat()
        rec = st.session_state.history.get(d)
        if not rec or rec["scheduled"] == 0 or rec["taken"] < rec["scheduled"]:
            break
        streak += 1
    return streak

# ----------------------------
# Encouragement
# ----------------------------
def encouragement_for(pct: int) -> str:
    if pct >= 90:
        return "🏆 Fantastic consistency! You're building a winning streak."
    elif pct >= 80:
        return "😊 Great job! Your routine is strong."
    elif pct >= 70:
        return "🍃 Good effort — keep nurturing your health."
    else:
        return "✨ Every step counts. Tomorrow is a fresh chance."

TIPS_GOOD = [
    "🌟 Consistency builds confidence. Keep it going!",
    "💪 Your routine is your superpower.",
    "🙌 Great job — your future self is grateful."
]
TIPS_NEUTRAL = [
    "✨ You’re on track. A small step right now helps.",
    "🌱 Take a breath and check what’s next.",
    "📈 Even one dose taken is progress."
]
TIPS_MISSED = [
    "💖 It happens. Reset and take the next dose when safe.",
    "🔄 No worries — refocus on the next scheduled dose.",
    "➡️ Forward is forward. You’ve got this."
]

def tip_for_status(pct: int) -> str:
    if pct >= 80:
        return TIPS_GOOD[pct % len(TIPS_GOOD)]
    elif pct >= 30:
        return TIPS_NEUTRAL[pct % len(TIPS_NEUTRAL)]
    else:
        return TIPS_MISSED[pct % len(TIPS_MISSED)]

# ----------------------------
# CRUD
# ----------------------------
def add_medicine(name, time_str, remind_min):
    med = {
        "id": st.session_state.id_counter,
        "name": name.strip(),
        "time_str": time_str.strip(),
        "remind_min": int(remind_min),
        "status": "upcoming",
        "taken_at": None
    }
    st.session_state.id_counter += 1
    st.session_state.meds.append(med)
    update_all_statuses()
    save_data()

def edit_medicine(med_id, name, time_str, remind_min):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["name"] = name.strip()
            m["time_str"] = time_str.strip()
            m["remind_min"] = int(remind_min)
            break
    update_all_statuses()
    save_data()

def delete_medicine(med_id):
    st.session_state.meds = [m for m in st.session_state.meds if m["id"] != med_id]
    update_all_statuses()
    save_data()

def mark_taken(med_id):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["status"] = "taken"
            m["taken_at"] = now_local().isoformat(timespec="minutes")
            break
    update_all_statuses()
    record_daily_history()
    save_data()

# ----------------------------
# Export
# ----------------------------
def export_today_csv():
    if st.session_state.meds:
        df = pd.DataFrame(st.session_state.meds)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download today's schedule (CSV)", csv,
                           file_name="medtimer_today.csv", mime="text/csv")
    else:
        st.info("No medicines added yet.")

def export_today_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MedTimer - Today's Schedule", ln=True, align="C")
    pdf.ln(5)
    if st.session_state.meds:
        for m in sorted(st.session_state.meds, key=lambda x: parse_hhmm(x["time_str"])):
            pdf.cell(200, 10, txt=f"{m['name']} at {m['time_str']} → {m['status']}", ln=True)
    else:
        pdf.cell(200, 10, txt="No medicines added.", ln=True)
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button("⬇️ Download today's schedule (PDF)", pdf_output,
                       file_name="med
