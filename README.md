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

**Note:**

Streamlit integration does not have support for Tkinter or Turtle code, so I had to resort to using emojis for symbols of encouragement and in places where Turtle was to be utilized. Below is the prepared Turtle code that would have been used in place of the emojis if support was there:

import turtle


screen = turtle.Screen()

screen.title("MedTimer Turtle Graphics Demo")

screen.bgcolor("lightyellow")


t = turtle.Turtle()

t.pensize(3)

t.speed(5)


#heading text

t.penup()

t.goto(0, 250)

t.pendown()

t.color("black")

t.write("MedTimer Turtle Graphics Demo", align="center", font=("Arial", 16, "bold"))


# smile outline

t.penup()

t.goto(-200, 150)

t.pendown()

t.color("green")

t.circle(60)  


# eyes

t.penup()

t.goto(-225, 220)

t.pendown()

t.dot(12, "black")

t.penup()

t.goto(-175, 220)

t.pendown()

t.dot(12, "black")


# mouth

t.penup()

t.goto(-235, 190)

t.setheading(-60)

t.pendown()

t.circle(40, 120)


# smiley label

t.penup()

t.goto(-80, 150)

t.pendown()

t.color("green")

t.write("Smiley → Encouragement when adherence is high", align="left", font=("Arial", 12, "bold"))


# medal

t.penup()

t.goto(-200, 0)

t.pendown()

t.color("gold")


# Medal circle

t.begin_fill()

t.circle(50)

t.end_fill()


# blue ribbon

t.penup()

t.goto(-260, 20)

t.pendown()

t.color("blue")

t.begin_fill()

t.setheading(-90)

t.forward(50)

t.right(30)

t.forward(25)

t.right(120)

t.forward(25)

t.right(30)

t.forward(50)

t.end_fill()


# red rbbon

t.penup()

t.goto(-230, 20)

t.pendown()

t.color("red")

t.begin_fill()

t.setheading(-90)

t.forward(50)

t.left(30)

t.forward(25)

t.left(120)

t.forward(25)

t.left(30)

t.forward(50)

t.end_fill()


# medal label

t.penup()

t.goto(-80, 0)

t.pendown()

t.color("gold")

t.write("Medal → Reward for streaks/adherence success", align="left", font=("Arial", 12, "bold"))


# heart

t.penup()

t.goto(-200, -150)

t.pendown()

t.color("red")

t.begin_fill()

t.left(50)

t.forward(70)  

t.circle(30, 180)

t.right(100)

t.circle(30, 180)

t.forward(70)

t.end_fill()


# heart label

t.penup()

t.goto(-80, -150)

t.pendown()

t.color("red")

t.write("Heart → Symbol of care & motivation", align="left", font=("Arial", 12, "bold"))


# end

t.hideturtle()

turtle.done()



Here is the link to the application:

https://med-timer-nws9wyu2acajgpyhpscttf.streamlit.app/


