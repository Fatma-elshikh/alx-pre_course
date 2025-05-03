pip install fpdf2
import streamlit as st
from fpdf import FPDF
import datetime

# Simulated database
USER_CREDENTIALS = {
    "doctor": {"password": "doc123", "role": "doctor"},
    "patient1": {"password": "pat123", "role": "patient"},
}

MEDICAL_RECORDS = {}

# PDF Generation functions with proper encoding
def safe_text(text):
    """Encode text to Latin-1 with replacement for PDF compatibility"""
    return text.encode('latin-1', 'replace').decode('latin-1')

def create_pdf(patient_data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.cell(200, 10, txt=safe_text("Medical Report"), ln=1, align='C')
    pdf.ln(10)
    
    # Patient Information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=safe_text("Patient Information"), ln=1)
    pdf.set_font("Arial", size=12)
    
    info = f"""
    Name: {patient_data.get('name', '')}
    Age: {patient_data.get('age', '')}
    Gender: {patient_data.get('gender', '')}
    Date: {patient_data.get('date', '')}
    """
    pdf.multi_cell(0, 10, txt=safe_text(info))
    
    # Medical Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=safe_text("Medical Details"), ln=1)
    pdf.set_font("Arial", size=12)
    
    details = f"""
    Symptoms: {patient_data.get('symptoms', '')}
    Diagnosis: {patient_data.get('diagnosis', '')}
    Prescription: {patient_data.get('prescription', '')}
    Notes: {patient_data.get('notes', '')}
    """
    pdf.multi_cell(0, 10, txt=safe_text(details))
    
    return bytes(pdf.output(dest='S'))

# Login Page
def login_page():
    st.title("Medical Login Portal")
    
    role = st.selectbox("Select Role", ["doctor", "patient"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        user = USER_CREDENTIALS.get(username)
        if user and user["password"] == password and user["role"] == role:
            st.session_state.update({
                'authenticated': True,
                'role': role,
                'username': username,
                'report_data': None
            })
            st.rerun()
        else:
            st.error("Invalid credentials or role mismatch")

# Patient Portal
def patient_portal():
    st.title(f"Welcome Patient {st.session_state['username']}")
    
    with st.form("medical_form"):
        st.header("Medical Information Form")
        name = st.text_input("Full Name")
        age = st.number_input("Age", min_value=0, max_value=150)
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        symptoms = st.text_area("Symptoms")
        diagnosis = st.text_input("Diagnosis")
        prescription = st.text_area("Prescription")
        notes = st.text_area("Additional Notes")
        date = st.date_input("Date of Visit")
        
        if st.form_submit_button("Generate Report"):
            patient_data = {
                "name": name,
                "age": age,
                "gender": gender,
                "symptoms": symptoms,
                "diagnosis": diagnosis,
                "prescription": prescription,
                "notes": notes,
                "date": str(date)
            }
            
            pdf_data = create_pdf(patient_data)
            filename = f"medical_report_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            
            MEDICAL_RECORDS[st.session_state['username']] = patient_data
            st.session_state.report_data = {
                "pdf_data": pdf_data,
                "filename": filename
            }
    
    if st.session_state.report_data:
        st.success("Report generated successfully!")
        st.download_button(
            label="Download Report",
            data=st.session_state.report_data["pdf_data"],
            file_name=st.session_state.report_data["filename"],
            mime="application/pdf"
        )
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# Doctor Portal
def doctor_portal():
    st.title(f"Welcome Doctor {st.session_state['username']}")
    st.header("Patient Records")
    
    if not MEDICAL_RECORDS:
        st.info("No patient records available")
    else:
        for username, record in MEDICAL_RECORDS.items():
            with st.expander(f"Record for {username}"):
                st.subheader(f"Patient: {record['name']}")
                cols = st.columns(2)
                cols[0].write(f"**Age:** {record['age']}")
                cols[1].write(f"**Gender:** {record['gender']}")
                st.write(f"**Date:** {record['date']}")
                st.write(f"**Symptoms:** {record['symptoms']}")
                st.write(f"**Diagnosis:** {record['diagnosis']}")
                st.write(f"**Prescription:** {record['prescription']}")
                st.write(f"**Notes:** {record['notes']}")
    
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

def main():
    if not st.session_state.get('authenticated', False):
        login_page()
    else:
        if st.session_state['role'] == 'patient':
            patient_portal()
        else:
            doctor_portal()

if __name__ == "__main__":
    main()
