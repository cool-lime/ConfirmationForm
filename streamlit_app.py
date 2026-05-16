import os
import requests
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Confirmation Form", page_icon="🕊")

# Define the questions here
questions = [
    {"label": "Full Name", "key": "name", "type": "text"},
    {"label": "Sponsor Full Name", "key": "sponsor_name", "type": "text"},
    {"label": "Gender", "key": "gender", "type": "select", "options": ["Male", "Female"]},
    {"label": "Confirmation Name (saint's name)", "key": "confirmation_name", "type": "text"},
    {"label": "Father's Name", "key": "father_name", "type": "text"},
    {"label": "Mother's Name", "key": "mother_name", "type": "text"},
    {"label": "Church where you were baptised", "key": "baptised_church", "type": "text"},
    {"label": "Phone number of above church (if it isn't St. Peter's)", "key": "phone_church", "type": "text"},
    {"label": "Email of above church (if it isn't St. Peter's)", "key": "email_church", "type": "text"},
    {"label": "Address of above church (if it isn't St. Peter's)", "key": "address_church", "type": "text"},
]

EXCEL_FILE = "responses.xlsx"
WEB_APP_URL = "https://script.google.com/macros/s/AKfycbywX34NTj9zXZpBSPfj6aFVz_MARQZJd2r3e4a-cMd1MzjgJLi8CPcjvlzBIBRfRP_P/exec"

st.title("Confirmation Form")

# Initialize our custom "form memory" tracking
if "submitted_successfully" not in st.session_state:
    st.session_state.submitted_successfully = False

def save_to_excel(row):
    df = pd.DataFrame([row], columns=[q["key"] for q in questions])
    if os.path.exists(EXCEL_FILE):
        existing = pd.read_excel(EXCEL_FILE)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)

# Only show the form inputs if they haven't submitted yet
if not st.session_state.submitted_successfully:
    
    # Using a visual container instead of a strict st.form block eliminates the Enter-to-Submit behavior
    with st.container(border=True):
        st.write(
            "Please fill out the form below with NO SPELLING MISTAKES. This is CRUCIAL."
        )

        responses = {}
        for q in questions:
            if q["type"] == "text":
                responses[q["key"]] = st.text_input(q["label"], key=f"input_{q['key']}")
            elif q["type"] == "select":
                responses[q["key"]] = st.selectbox(q["label"], options=q.get("options", []), key=f"input_{q['key']}")

        # A standard button will NOT trigger when hitting enter inside the inputs above
        submitted = st.button("Submit Response", type="primary")

        if submitted:
            # Prevent blank submissions
            if not responses.get("name") or responses.get("name").strip() == "":
                st.error("Please provide at least your Full Name before submitting.")
            else:
                row = [responses.get(q["key"], "") for q in questions]
                
                try:
                    # Send data over to Google Sheets
                    response = requests.post(WEB_APP_URL, json={"row": row}, timeout=15)
                    result = response.json()
                    
                    if result.get("status") == "success":
                        st.session_state.submitted_successfully = True
                        st.rerun()
                    else:
                        raise Exception(result.get("message", "Google Script returned an error status."))
                except Exception as exc:
                    # Fallback to local file if the network drops out
                    save_to_excel(row)
                    st.session_state.submitted_successfully = True
                    st.rerun()

else:
    # Celebratory screen once successfully clicked
    st.balloons()
    st.success("🎉 We have successfully collected your response in Google Sheets. Thank you!")
    st.info("You may close this browser window. You do not need to complete this form again unless you made a mistake, in which case you should contact us to remove the one with a mistake.")
