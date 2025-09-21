import os
from flask import Flask, request, jsonify
from main import extract_text_from_file, extract_skills_from_jd, calculate_relevance_score, get_llm_analysis, combine_scores

# Initialize Flask app
app = Flask(__name__)

# Define the API endpoint
@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Handles the resume analysis request by calling all backend functions.
    """
    data = request.get_json()
    resume_text = data.get("resume_text")
    jd_text = data.get("jd_text")

    if not resume_text or not jd_text:
        return jsonify({"error": "Missing resume or job description"}), 400

    # Perform the analysis using our functions from main.py
    extracted_jd_skills = extract_skills_from_jd(jd_text)
    
    # In a real app, you would parse skills from the uploaded resume text
    # For now, we'll use our dummy skills list for demonstration
    resume_skills = ["Python", "Flask", "Django", "SQL", "PostgreSQL", "JavaScript", "HTML", "CSS"]
    
    hard_match_score, matched_skills = calculate_relevance_score(resume_skills, extracted_jd_skills)
    
    # Get the LLM analysis
    llm_analysis_output = get_llm_analysis(resume_text, jd_text)

    # Extract the Verdict from the LLM analysis
    try:
        verdict_text = llm_analysis_output.split('Verdict:')[1].split('\n')[0].strip()
    except IndexError:
        verdict_text = "N/A" # Handle cases where the LLM doesn't follow the format

    final_score = combine_scores(hard_match_score, verdict_text)

    # Return the results as a JSON object
    response = {
        "final_score": final_score,
        "hard_match_score": hard_match_score,
        "matched_skills": matched_skills,
        "llm_analysis": llm_analysis_output
    }
    
    return jsonify(response)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)