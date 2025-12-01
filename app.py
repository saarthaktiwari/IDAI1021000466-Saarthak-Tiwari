# MedTimer - Daily Medicine Companion
# Full-feature build with persistence, theme toggle, and schedule export
# Author: Saarthak

import streamlit as st
import pandas as pd
import datetime as dt
from dateutil import parser
import io, os, json
from PIL import Image
import turtle
from fpdf import FPDF

# ----------------------------
# Streamlit page config
# ----------------------------
st.set_page_config(page_title="MedTimer", page_icon="💊", layout="wide")

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
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass  # in some environments writing may be restricted

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            st.session_state.meds = data.get("meds", [])
            st.session_state.history = data.get("history", {})
            st.session_state.id_counter = data.get("id_counter", 1)
        except Exception:
            # fall back to empty state if file is corrupted
            st.session_state.meds = []
            st.session_state.history = {}
            st.session_state.id_counter = 1

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
# Theme toggle (Light / Dark / High Contrast)
# ----------------------------
mode = st.sidebar.radio("Theme mode", ["Light", "Dark", "High Contrast"])

if mode == "Dark":
    APP_PRIMARY = "#eeeeee"; APP_BG = "#212121"; APP_ACCENT = "#90caf9"
elif mode == "High Contrast":
    APP_PRIMARY = "#000000"; APP_BG = "#ffffff"; APP_ACCENT = "#ff0000"
else:
    APP_PRIMARY = "#1b5e20"; APP_BG = "#f5f7f9"; APP_ACCENT = "#4caf50"

APP_WARN = "#f9a825"; APP_ERROR = "#c62828"

# Basic CSS for readability (colors adapt to theme)
st.markdown(f"""
<style>
body {{
    background-color: {APP_BG};
}}
.big-title {{
    font-size: 36px; font-weight: 700; color: {APP_PRIMARY};
}}
.small-muted {{
    color: #607d8b;
}}
.item-pill {{
    padding: 6px 10px; border-radius: 16px; display: inline-block;
    font-weight: 600; color: white;
}}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Utilities
# ----------------------------
def parse_hhmm(time_str: str) -> dt.datetime:
    """
    Parse HH:MM or similar into today's datetime.
    """
    today = dt.date.today()
    t = parser.parse(time_str).time()
    return dt.datetime.combine(today, t)

def now_local() -> dt.datetime:
    return dt.datetime.now()

def status_color(status: str) -> str:
    return {"taken": APP_ACCENT, "upcoming": APP_WARN, "missed": APP_ERROR}.get(status, "#607d8b")

def compute_status(med) -> str:
    """
    upcoming: now < scheduled & not taken
    missed: now >= scheduled & not taken
    taken: explicitly marked
    """
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
    """
    Snapshots today's scheduled/taken into history (for weekly view).
    Call after significant changes (mark taken, etc.).
    """
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
# Turtle graphics (smiley/trophy)
# ----------------------------
def draw_turtle_trophy(pct: int) -> Image.Image:
    """
    Draw a simple reward graphic with turtle based on adherence pct.
    Converts canvas PostScript to PIL Image for display in Streamlit.
    """
    screen = turtle.Screen()
    screen.setup(width=400, height=400)
    screen.bgcolor("white")
    t = turtle.Turtle(visible=False)
    t.speed(0)
    t.pensize(4)

    if pct >= 90:
        # Trophy rectangle
        t.color("gold")
        t.penup(); t.goto(-50, -30); t.pendown()
        t.begin_fill()
        for _ in range(2):
            t.forward(100); t.left(90); t.forward(60); t.left(90)
        t.end_fill()
        # Handles
        t.color("darkgoldenrod")
        t.penup(); t.goto(-50, 30); t.pendown()
        t.circle(30, 180)
        t.penup(); t.goto(50, 30); t.pendown()
        t.circle(-30, 180)
    elif pct >= 80:
        # Smiley
        t.color("green")
        t.penup(); t.goto(0, -80); t.pendown()
        t.circle(100)
        t.penup(); t.goto(-40, 40); t.pendown(); t.dot(20)
        t.penup(); t.goto(40, 40); t.pendown(); t.dot(20)
        t.penup(); t.goto(-50, -10); t.pendown()
        t.setheading(-60); t.circle(60, 120)
    elif pct >= 70:
        # Leaf
        t.color("forestgreen")
        t.penup(); t.goto(0, -60); t.pendown()
        t.setheading(60)
        for _ in range(2):
            t.circle(80, 120)
            t.right(180)
    else:
        t.color("lightgray")
        t.penup(); t.goto(0, 0); t.pendown()
        t.dot(14)

    cv = screen.getcanvas()
    ps = io.BytesIO(cv.postscript(colormode='color').encode('utf-8'))
    img = Image.open(ps)
    turtle.bye()
    return img

# ----------------------------
# CRUD operations
# ----------------------------
def add_medicine(name: str, time_str: str, remind_min: int):
    med = {
        "id": st.session_state.id_counter,
        "name": name.strip(),
        "time_str": time_str.strip(),
        "remind_min": int(remind_min),
        "status": "upcoming",
        "taken_at": None,
    }
    st.session_state.id_counter += 1
    st.session_state.meds.append(med)
    update_all_statuses()
    save_data()

def edit_medicine(med_id: int, name: str, time_str: str, remind_min: int):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["name"] = name.strip()
            m["time_str"] = time_str.strip()
            m["remind_min"] = int(remind_min)
            break
    update_all_statuses()
    save_data()

def delete_medicine(med_id: int):
    st.session_state.meds = [m for m in st.session_state.meds if m["id"] != med_id]
    update_all_statuses()
    save_data()

def mark_taken(med_id: int):
    for m in st.session_state.meds:
        if m["id"] == med_id:
            m["status"] = "taken"
            m["taken_at"] = now_local().isoformat(timespec="minutes")
            break
    update_all_statuses()
    record_daily_history()
    save_data()

# ----------------------------
# Export functions (Today CSV/PDF)
# ----------------------------
def export_today_csv():
    if st.session_state.meds:
        df = pd.DataFrame(st.session_state.meds)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download today's schedule (CSV)", csv,
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
    st.download_button("Download today's schedule (PDF)", pdf_output,
                       file_name="medtimer_today.pdf", mime="application/pdf")

# ----------------------------
# Motivational tips (simple, supportive)
# ----------------------------
TIPS_GOOD = [
    "Consistency builds confidence. Keep it going!",
    "Your routine is your superpower.",
    "Great job—your future self is grateful."
]
TIPS_NEUTRAL = [
    "You’re on track. A small step right now helps.",
    "Take a breath and check what’s next.",
    "Even one dose taken is progress."
]
TIPS_MISSED = [
    "It happens. Reset and take the next dose when safe.",
    "No worries—refocus on the next scheduled dose.",
    "Forward is forward. You’ve got this."
]

def tip_for_status(pct: int) -> str:
    if pct >= 80:
        return TIPS_GOOD[pct % len(TIPS_GOOD)]
    elif pct >= 30:
        return TIPS_NEUTRAL[pct % len(TIPS_NEUTRAL)]
    else:
        return TIPS_MISSED[pct % len(TIPS_MISSED)]

# ----------------------------
# UI
# ----------------------------
st.markdown("<div class='big-title'>💊 MedTimer — Daily Medicine Companion</div>", unsafe_allow_html=True)
st.write(f"<span class='small-muted'>Today: {dt.date.today().strftime('%a, %d %b %Y')}</span>", unsafe_allow_html=True)

left, right = st.columns([0.62, 0.38])

# Left column: Add / Edit / Delete / Checklist
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
    if not st.session_state.meds:
        st.info("No medicines added yet. Add your first medicine above.")
    else:
        for m in sorted(st.session_state.meds, key=lambda x: parse_hhmm(x["time_str"])):
            col1, col2, col3 = st.columns([0.52, 0.24, 0.24])
            color = status_color(m["status"])

            with col1:
                st.markdown(
                    f"<span class='item-pill' style='background:{color}'>{m['name']} • {m['time_str']} • {m['status']}</span>",
                    unsafe_allow_html=True
                )
                if m.get("taken_at"):
                    st.caption(f"Taken at {m['taken_at']}")

            with col2:
                if m["status"] != "taken":
                    if st.button("Mark taken ✅", key=f"take_{m['id']}"):
                        mark_taken(m["id"])
                else:
                    # Quick edit expander when taken too (optional)
                    st.write("✅ Taken")

            with col3:
                with st.expander("Edit / Delete", expanded=False):
                    new_name = st.text_input("Name", value=m["name"], key=f"en_{m['id']}")
                    new_time = st.text_input("Time (HH:MM)", value=m["time_str"], key=f"et_{m['id']}")
                    new_remind = st.number_input("Remind (min)", min_value=0, max_value=120, value=int(m["remind_min"]), step=5, key=f"er_{m['id']}")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Save changes", key=f"save_{m['id']}"):
                            edit_medicine(m["id"], new_name, new_time, int(new_remind))
                            st.success("Updated.")
                    with c2:
                        if st.button("🗑️ Delete", key=f"del_{m['id']}"):
                            delete_medicine(m["id"])
                            st.warning("Deleted.")

# Right column: Metrics, Weekly overview, Exports, Turtle, Tips
with right:
    scheduled, taken, pct_today = adherence_today()
    st.metric(label="Today's adherence", value=f"{pct_today}%", delta=f"{taken}/{scheduled} taken")

    # Record snapshot so weekly has the latest numbers
    record_daily_history()

    df_week, weekly_pct = weekly_adherence()
    st.metric(label="Weekly adherence (avg)", value=f"{weekly_pct}%")

    st.subheader("Weekly overview")
    st.dataframe(df_week, height=240, use_container_width=True)

    st.subheader("Export")
    export_today_csv()
    export_today_pdf()

    st.subheader("Encouragement")
    tip = tip_for_status(pct_today)
    st.info(tip)

    try:
        img = draw_turtle_trophy(max(pct_today, weekly_pct))
        st.image(img, caption="Keep going—small steps, big impact!", use_container_width=True)
    except Exception:
        st.write("Turtle graphics unavailable in this environment—focus on your streak and clarity!")

# Footer
st.markdown("---")
st.caption("Designed for clarity and calm. Large fonts, gentle colors, simple actions.")
