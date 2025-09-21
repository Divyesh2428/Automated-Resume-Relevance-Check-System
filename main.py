import os
import spacy
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains.llm import LLMChain

# This code is now a module for our server to import
# The LLM initialization is moved inside the function that uses it

def extract_text_from_file(file_path):
    """
    Extracts text from a file.
    """
    if not os.path.exists(file_path):
        return f"Error: The file '{file_path}' was not found."

    text_content = ""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text_content = file.read()
        return text_content
    except Exception as e:
        return f"An error occurred: {e}"

def extract_skills_from_jd(jd_text):
    """
    Extracts skills from a job description using a predefined list.
    """
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        print("Please run 'python -m spacy download en_core_web_sm' to download the language model.")
        return []

    doc = nlp(jd_text)

    sample_skills = ["Python", "Flask", "SQL", "JavaScript", "HTML", "CSS", "Django"]
    found_skills = [skill for skill in sample_skills if skill.lower() in jd_text.lower()]

    return found_skills

def calculate_relevance_score(resume_skills, jd_skills):
    """
    Calculates a relevance score based on keyword matching.
    """
    resume_skills_lower = [skill.lower() for skill in resume_skills]
    jd_skills_lower = [skill.lower() for skill in jd_skills]

    matched_skills = [skill for skill in jd_skills_lower if skill in resume_skills_lower]
    
    if not jd_skills:
        return 0, []
        
    score = (len(matched_skills) / len(jd_skills)) * 100
    
    return round(score, 2), matched_skills

def get_llm_analysis(resume_text, jd_text):
    """
    Uses an LLM to provide a soft match analysis with more detailed instructions.
    """
    # Initialize LLM with your API key
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
    
    prompt_template = ChatPromptTemplate.from_template(
        """
        You are an expert recruiter. Analyze the following resume against the job description.
        Your goal is to provide a comprehensive analysis that includes a verdict, a detailed breakdown of strengths and weaknesses, and actionable feedback.

        ---
        Resume:
        {resume_text}

        ---
        Job Description:
        {jd_text}

        ---
        Based on the above, provide your analysis:

        **Verdict:**
        [Provide a verdict: "High Suitability" for an excellent fit, "Medium Suitability" for a decent fit with room for improvement, or "Low Suitability" for a poor fit.]

        **Strengths:**
        [List and explain the key strengths of the resume as they relate to the job description.]

        **Weaknesses:**
        [List and explain the key weaknesses of the resume.]

        **Actionable Feedback for the Candidate:**
        [Provide a bulleted list of 3-5 specific, actionable steps the candidate can take to improve their resume for this specific role.]
        """
    )
    
    llm_chain = LLMChain(prompt=prompt_template, llm=llm)
    
    response = llm_chain.invoke({"resume_text": resume_text, "jd_text": jd_text})
    
    return response['text']
def combine_scores(hard_match_score, llm_verdict):
    """
    Combines hard and soft match scores into a single weighted score.
    """
    verdict_map = {
        "High Suitability": 95,
        "Medium Suitability": 65,
        "Low Suitability": 30
    }
    
    soft_match_score = verdict_map.get(llm_verdict, 0)
    
    # We'll use a simple 50/50 weighting
    final_score = (hard_match_score * 0.5) + (soft_match_score * 0.5)
    
    return final_score