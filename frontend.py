import streamlit as st
import requests
import PyPDF2
import io

# Define the URL for our Flask backend
BACKEND_URL = "https://automated-resume-relevance-check-system-1-v2to.onrender.com/analyze"

st.title("Automated Resume Relevance Checker")
st.subheader("Your AI-powered recruiting assistant.")

st.markdown("---")

# File uploader for the resume
st.header("Upload Resume")
uploaded_file = st.file_uploader("Choose a PDF, DOCX or TXT file", type=["pdf", "docx", "txt"])

st.markdown("---")

# Text area for the job description
st.header("Job Description")
job_description = st.text_area("Paste the job description here", height=200)

# The analyze button
if st.button("Analyze Resume"):
    if uploaded_file and job_description:
        # Check the file type and read the content
        if uploaded_file.type == "text/plain":
            resume_text = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            try:
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                resume_text = ""
                for page in pdf_reader.pages:
                    resume_text += page.extract_text() or ""
            except Exception as e:
                st.error(f"Error reading PDF file: {e}")
                resume_text = None
        else:
            st.error("This file type is not yet implemented. Please upload a PDF or TXT.")
            resume_text = None
        
        if resume_text:
            # Make a POST request to our Flask backend with the extracted text
            data = {
                "resume_text": resume_text,
                "jd_text": job_description
            }

            response = requests.post(BACKEND_URL, json=data)

            if response.status_code == 200:
                st.success("Analysis complete!")
                results = response.json()
                
                # Display the results from our backend
                st.subheader("Analysis Results")
                st.write(f"**Final Score:** {results['final_score']}%")
                st.write(f"**Hard Match Score:** {results['hard_match_score']}%")
                st.write(f"**Matched Skills:** {', '.join(results['matched_skills'])}")
                
                st.subheader("LLM Analysis")
                st.write(results["llm_analysis"])
            else:
                st.error(f"Error: Could not get a response from the backend. Status Code: {response.status_code}")
                st.error(f"Backend response: {response.text}")
    else:
        st.error("Please upload a resume and paste a job description.")