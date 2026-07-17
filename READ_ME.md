# Cyber Intelligence Platform

## Introduction

The Cyber Intelligence Platform is a web-based application developed using Python and Streamlit. It provides an integrated environment for managing cybersecurity incidents, dataset metadata, IT support tickets, and user accounts while incorporating an AI assistant powered by the Google Gemini API.

The platform demonstrates secure authentication, database management, interactive dashboards, role-based access control, and AI-assisted querying of organisational data.


## Features

- Secure user authentication using bcrypt password hashing
- Role-based access control for administrators
- Cybersecurity incident management
- Dataset metadata management
- IT ticket management
- Interactive dashboards and data visualisation
- AI assistant capable of answering questions using organisational data
- SQLite database integration
- Modular application architecture



## Technologies Used

- Python 3
- Streamlit
- SQLite
- Pandas
- bcrypt
- Google Gemini API



## Project Structure

Cyber-Intelligence-Platform/
│
├── app_model/
│   ├── cyber_incidents.py
│   ├── db.py
│   ├── it_tickets.py
│   ├── metadata.py
│   ├── schema.py
│   └── users.py
│
├── pages/
│   ├── Dashboard.py
│   ├── AI_Assistant.py
│   ├── Profile.py
│   └── Admin_Management.py
│
├── DATA/
│   ├── project_data.db
│   └── users.txt
│
├── .streamlit/
│   └── secrets.toml
│
├── hashing.py
├── configpath.py
├── Home.py
├── main.py
└── requirements.txt



## Database Tables

The SQLite database contains four tables:

### users

Stores registered user accounts.

- id
- username
- password_hash
- role

### cyber_incidents

Stores cybersecurity incident records.

- incident_id
- timestamp
- severity
- category
- status
- description

### datasets_metadata

Stores metadata describing uploaded datasets.

- dataset_id
- name
- rows
- columns
- uploaded_by
- upload_date

### it_tickets

Stores IT support ticket information.

- ticket_id
- priority
- description
- status
- assigned_to
- created_at
- resolution_time_hours



## Installation

Clone the repository

bash
git clone <https://github.com/anel-andrew/CW2_M01119174_CST1510.git
>


Navigate to the project folder

bash
cd Cyber-Intelligence-Platform


Create a virtual environment
in your VS code terminal type

bash
python -m venv .venv


Activate the virtual environment

Windows

bash
.venv\Scripts\activate


macOS/Linux

bash
source .venv/bin/activate


Install the required packages

bash
pip install -r requirements.txt streamlit pandas




## Configure the Gemini API Key

Create a file named

.streamlit/secrets.toml

Add your Gemini API key

toml
GEMINI_API_KEY = "YOUR_API_KEY"


Do **not** commit this file to GitHub.



## Running the Application

Launch the Streamlit application

bash
streamlit run Home.py

The application will open automatically in your default web browser.

## Register yourself as user
- enter your username of choice
- enter your password of choice (Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.)
- click the register button

## User Login
- enter your username
- enter your password


## Administrator Access

Only users with the **admin** role can access the Administrator Management page.

Admin username : Manager
Admin password : Admin1!Admin1!

Administrators can:

- Promote users
- Demote users
- Reset user passwords
- Delete users
- Add cyber incidents
- Delete cyber incidents
- Add dataset metadata
- Delete dataset metadata
- Add IT tickets
- Delete IT tickets


## AI Assistant

The AI Assistant uses the Google Gemini API.

When a user submits a question:

1. Gemini determines whether the question requires database access.
2. If required, Gemini generates a SQLite SQL query.
3. Python executes the SQL query.
4. The database returns the results.
5. Gemini explains the results in natural language.

This approach ensures calculations are performed by SQLite rather than by the language model.


## Security

The platform incorporates several security mechanisms:

- Passwords are hashed using bcrypt.
- API keys are stored securely using Streamlit Secrets.
- Parameterised SQL queries reduce SQL injection risks.
- Session State maintains authenticated user sessions.
- Role-based authorisation protects administrator functions.



## Author

Anel Andrew Temu

BSc Computer Science (Systems Engineering)

Middlesex University Mauritius



## Licence

This project was developed for academic coursework purposes.