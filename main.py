
import streamlit as st
import pandas as pd
import datetime
from io import BytesIO

# Set page config
st.set_page_config(page_title="S2M Portal", layout="wide")

# Load data
login_df = pd.read_csv("Login tracking.csv")
tracking_df = pd.read_csv("Tracking Sample (1).csv")

# Set styles
st.markdown("""
    <style>
        .stTextInput>div>div>input {
            border: 2px solid black;
        }
        .stPasswordInput>div>div>input {
            border: 2px solid black;
        }
        body {
            background-color: #e6f2ff;
        }
    </style>
""", unsafe_allow_html=True)

# Logo and title
st.image("s2m-logo.png", width=200)
st.markdown("<h2 style='color: #3399ff;'>S2M Health Private Ltd</h2>", unsafe_allow_html=True)

# Session state init
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'emp_id' not in st.session_state:
    st.session_state.emp_id = None
if 'submitted_data' not in st.session_state:
    st.session_state.submitted_data = []

# Login Page
if not st.session_state.logged_in:
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("password", type="password")
    if st.button("Login"):
        with st.spinner("Authenticating..."):
            auth = login_df[(login_df["Username"] == username) & (login_df["password"] ==password)]
            if not auth.empty:
                st.session_state.logged_in = True
                st.session_state.emp_id = auth.iloc[0]["Emp ID"]
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")

# Form Page
if st.session_state.logged_in:
    st.subheader("Chart Entry Form")

    emp_id = st.session_state.emp_id
    emp_name_row = tracking_df[tracking_df["Emp Id"] == emp_id]
    emp_name = emp_name_row["Emp Name"].iloc[0] if not emp_name_row.empty else ""

    with st.form("entry_form"):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", datetime.date.today())
            emp_id_input = st.text_input("Emp Id", emp_id, disabled=True)
            emp_name_input = st.text_input("Emp Name", emp_name)
            project = st.selectbox("Project", ["Elevance MA", "Elevance ACA", "Health OS"])
            project_category = st.selectbox("Project Category", ["Entry", "Recheck", "QA"])
            login_id = st.text_input("Login Id", emp_id, disabled=True)
        with col2:
            login_name = st.multiselect("Login Name", tracking_df["Login name"].dropna().unique())
            team_lead = emp_name_row["Team lead name"].iloc[0] if not emp_name_row.empty else ""
            team_lead_input = st.text_input("Team Lead Name", team_lead)
            chart_id = st.text_input("Chart Id")
            page_no = st.text_input("Page No")
            dos = st.text_input("No of DOS")
            codes = st.text_input("No of codes")
            error_type = st.text_input("Error Type")
            error_comments = st.text_input("Error Comments")
            no_errors = st.text_input("No of errors")
            chart_status = st.text_input("Chart Status")
            auditor_emp_id = st.text_input("Auditor Emp Id")
            auditor_emp_name = st.text_input("Auditor Emp Name")

        submitted = st.form_submit_button("Submit")
        if submitted:
            new_entry = {
                "Date": date,
                "Emp Id": emp_id_input,
                "Emp Name": emp_name_input,
                "Project": project,
                "Project category": project_category,
                "Login Id": login_id,
                "Login name": login_name,
                "Team lead name": team_lead_input,
                "Chart id": chart_id,
                "Page no": page_no,
                "No of Dos": dos,
                "No of codes": codes,
                "Error type": error_type,
                "Error comments": error_comments,
                "No of errors": no_errors,
                "Chart status": chart_status,
                "Auditor emp id": auditor_emp_id,
                "Auditor Emp name": auditor_emp_name
            }
            st.session_state.submitted_data.append(new_entry)
            st.success("Form submitted successfully!")

    if st.session_state.submitted_data:
        df_submitted = pd.DataFrame(st.session_state.submitted_data)
        st.write("### Submitted Data")
        st.dataframe(df_submitted)

        buffer = BytesIO()
        df_submitted.to_excel(buffer, index=False)
        st.download_button("Download Excel", buffer.getvalue(), file_name="submitted_data.xlsx")

# Dashboard Page
if st.session_state.logged_in and st.session_state.submitted_data:
    st.subheader("Dashboard")

    df_dash = pd.DataFrame(st.session_state.submitted_data)
    working_days = df_dash["Date"].nunique()
    num_charts = df_dash["Chart id"].nunique()
    num_dos = df_dash["No of Dos"].astype(str).apply(lambda x: len(x.split(',')) if x else 0).sum()
    num_icd = df_dash["No of codes"].astype(str).apply(lambda x: len(x.split(',')) if x else 0).sum()
    cph = round(num_charts / working_days, 2) if working_days else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Working Days", working_days)
    col2.metric("No. of Charts", num_charts)
    col3.metric("No. of DOS", num_dos)
    col4.metric("No. of ICD", num_icd)
    col5.metric("CPH", cph)
