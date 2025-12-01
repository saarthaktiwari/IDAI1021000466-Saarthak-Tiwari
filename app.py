import streamlit as st
import pandas as pd
import datetime as dt
from dateutil import parser
import io, os, json
from PIL import Image
import turtle
from fpdf import FPDF

# ----------------------------
# Persistence helpers
# ----------------------------
DATA_FILE = "medtimer_data.json"

def save_data():
    data = {
        "meds": st.session_state.meds,
        "history": st.session_state.history,
        "id_counter": st.session_state.id_counter
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        st.session_state.meds = data.get("meds", [])
        st.session_state.history = data.get("history", {})
        st.session_state.id_counter = data.get("id_counter", 1)

# ----------------------------
# Init state
# ----------------------------
def init_state():
    if "meds" not in st.session_state:
        st.session_state.meds = []
    if "history" not in st.session_state:
        st.session_state.history = {}
    if "id_counter" not in st.session_state:
        st.session_state.id_counter = 1
init_state()
load_data()

# ----------------------------
# Theme toggle
# ----------------------------
mode = st.sidebar.radio("Theme mode", ["Light", "Dark", "High Contrast"])

if mode == "Dark":
    APP_PRIMARY = "#eeeeee"; APP_BG = "#212121"; APP_ACCENT = "#90caf9"
elif mode == "High Contrast":
    APP_PRIMARY = "#000000"; APP_BG = "#ffffff"; APP_ACCENT = "#ff0000"
else:
    APP_PRIMARY = "#1b5e20"; APP_BG = "#f5f7f9"; APP_ACCENT = "#4caf50"

APP_WARN = "#f9a825"; APP_ERROR = "#c62828"

st.set_page_config(page_title="MedTimer", page_icon="💊", layout="wide")

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
    return {"taken": APP_ACCENT, "upcoming": APP_WARN, "missed": APP_ERROR}.get(status, "#607d8b")

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

# ----------------------------
# Turtle graphics
# ----------------------------
def draw_turtle_trophy(pct: int) -> Image.Image:
    screen = turtle.Screen()
    screen.setup(width=400, height=400)
    screen.bgcolor("white")
    t = turtle.Turtle(visible=False); t.speed(0); t.pensize(4)
    if pct >= 90:
        t.color("gold"); t.begin_fill()
        for _ in range(2): t.forward(100); t.left(90); t.forward(60); t.left(90)
        t.end_fill()
    elif pct >= 80:
        t.circle(100)
    else:
        t.dot(20, "lightgray")
    cv = screen.getcanvas()
    ps = io.BytesIO(cv.postscript(colormode='color').encode('utf-8'))
    img = Image.open(ps)
    turtle.bye()
    return img

# ----------------------------
# CRUD
# ----------------------------
def add_medicine(name, time_str, remind_min):
    med = {"id": st.session_state.id_counter, "name": name, "time_str": time_str,
           "remind_min": int(remind_min), "status": "upcoming", "taken_at": None}
    st.session_state.id_counter += 1
    st.session_state.meds.append(med)
    update_all_statuses(); save_data()

def edit_medicine(med_id, name, time_str, remind_min):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["name"], m["time_str"], m["remind_min"] = name, time_str, int(remind_min)
    update_all_statuses(); save_data()

def delete_medicine(med_id):
    st.session_state.meds = [m for m in st.session_state.meds if m["id"] != med_id]
    update_all_statuses(); save_data()

def mark_taken(med_id):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["status"] = "taken"; m["taken_at"] = now_local().isoformat(timespec="minutes")
    update_all_statuses(); record_daily_history(); save_data()

# ----------------------------
# Export functions
# ----------------------------
def export_today_csv():
    df = pd.DataFrame(st.session_state.meds)
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download today's schedule (CSV)", csv,
                       file_name="medtimer_today.csv", mime="text/csv")

def export_today_pdf():
    pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="MedTimer - Today's Schedule", ln=True, align="C")
    for m in st.session_state.meds:
        pdf.cell(200, 10, txt=f"{m['name']} at {m['time_str']} → {m['status']}", ln=True)
    pdf_output = pdf.output(dest="S").encode("latin-1")
    st.download_button("Download today's schedule (PDF)", pdf_output,
                       file_name="medtimer_today.pdf", mime="application/pdf")

# ----------------------------
# UI
# ----------------------------
st.title("💊 MedTimer — Daily Medicine Companion")
st.write(f"Today: {dt.date.today().strftime('%a, %d %b %Y')}")

left, right = st.columns([0.6, 0.4])

with left:
    st.subheader("Add medicine")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Medicine name")
        time_str = st.text_input("Scheduled time (HH:MM)", placeholder="08:00")
        remind_min = st.number_input("Remind minutes before", min_value=0, max_value=120, value=15, step=5)
        submitted = st.form_submit_button("Add")
        if submitted and name and time_str:
            add_medicine(name, time_str, remind_min)
            st.success("Added medicine.")

    update_all_statuses()
    st.subheader("Today's checklist")
    for m in sorted(st.session_state.meds, key=lambda x: parse_hhmm(x["time_str"])):
        col1, col2, col3 = st.columns([0.5, 0.25, 0.25])
        color = status_color(m["status"])
        with col1:
            st.markdown(f"<span style='color:{color}; font-weight:600'>{m['name']} at {m['time_str']} → {m['status']}</span>", unsafe_allow_html=True)
        with col2:
            if m["status"] != "taken":
                if st.button("Mark taken ✅", key=f"take_{m['id']}"):
                    mark_taken(m["id"])
            else:
                st.write(f"Taken at {m.get('taken_at','')}")
        with col3:
            if st.button("🗑️ Delete", key=f"del_{m['id']}"):
               
