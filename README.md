# IDAI1011000466-Saarthak-Tiwari

# Unit 2 - Python Programming

# Candidate Name and Number: Saarthak Tiwari, 1000466

# CRS: Artificial Intelligence

# Course: Python Programming: Designing and Deploying Interactive Python Applications for Social Good

# School Name: Birla Open Minds International School Kollur

**Project Overview:**

My MedTimer application's target audience is inclusive of those who require aid in tracking and taking their necessary medication. This includes but is not limited to elderly people who will be able to navigate the simplistic user interface and design to accurately track their medication. It is a personalized medicine assistant designed to help users manage their daily medication routines effortlessly and consistently. Developed with Streamlit, the app enables users to set up recurring or one-time medication schedules, track daily adherence, and receive automatic audio reminders when it’s time to take their medicine. Its interface is user-friendly and visually soothing, featuring large fonts, soft colors, and a three-column layout that organizes inputs, checklists, and insights. Users can follow a color-coded checklist (green for taken, yellow for upcoming, red for missed), monitor their weekly adherence score, and receive motivational tips along with celebratory Turtle animations for staying consistent. MedTimer is perfect for individuals, caregivers, or families seeking a gentle and dependable way to manage daily health routines.

Integration Details

MedTimer is developed entirely in Python and runs on the Streamlit framework, which provides a smooth, interactive web interface. The app relies on Python’s datetime module to manage scheduling, while session_state keeps track of medication routines and user adherence across interactions. Custom WAV alert sounds are generated using the struct and math modules. When users maintain strong adherence, the app triggers celebratory animations created with Turtle graphics—these open in a separate window and work best on desktop devices.

The app allows two types of medicine entry: choosing from a preset list or manually typing a custom name. Users can set multiple daily doses, pick flexible start dates, and configure repeating schedules across selected weekdays. All reminders operate within the active app session, with automatic audio alerts playing when a dose falls within the reminder window the user defines.

Deployment Instructions (Paraphrased)

To run MedTimer locally, clone the GitHub repository and open the project folder. Install the required packages listed in requirements.txt, which includes Streamlit and other needed libraries. After installation, launch the application by running streamlit run app.py in your terminal; this will open the interface in your browser.

For cloud deployment, upload the repository to GitHub and use Streamlit Cloud to host it. Create a new app, link your GitHub account, then choose the repository and the app.py file as the entry point. Streamlit Cloud will automatically set up the environment and deploy the application. Be aware that Turtle animations may not display on cloud platforms, and audio reminders depend on browser support for autoplaying short WAV files. For best results, users should keep the app open throughout the day to receive timely reminders and track their intake.

**Important Features:"

* Downloadable CSV and PDF files logging user actions

* Weekly adherence with motivational messages and emojis

* Daily checklist of medications required

* Weekly information

* Personalized user log-in system

* Reminder system to ensure medication is taken

Here is the link to the application:

https://med-timer-nws9wyu2acajgpyhpscttf.streamlit.app/


