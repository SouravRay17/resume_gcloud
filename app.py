import streamlit as st
import os
import zipfile
import io
import PyPDF2
import asyncio
from crewai import Agent, Task, Crew
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI  # Import the OpenAI module
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_content):
    try:
        # Initialize a PDF file reader
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))

        # Extract text from each page
        text = ""
        for page_num in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page_num].extract_text()

        return text
    except Exception as e:
        print(f"An error occurred while extracting text from PDF: {e}")
        return None

# Function to extract PDF content from a ZIP file
def extract_content_from_zip(zip_file_path):
    try:
        # Open the ZIP file
        with zipfile.ZipFile(zip_file_path, "r") as zip_file:
            # Initialize a list to store resume texts
            all_resume_texts = []

            # Iterate over each file in the ZIP archive
            for file_info in zip_file.infolist():
                # Check if the file is a PDF
                if file_info.filename.endswith(".pdf"):
                    # Extract the PDF content
                    with zip_file.open(file_info) as pdf_file:
                        pdf_content = pdf_file.read()
                    
                    # Extract text from the PDF content
                    text = extract_text_from_pdf(pdf_content)
                    if text:
                        # Append the text to the list of resume texts
                        all_resume_texts.append(text)
                    else:
                        print(f"Failed to extract text from {file_info.filename}.")
            
            return all_resume_texts
    except FileNotFoundError:
        print(f"File '{zip_file_path}' not found.")
        return None
    except zipfile.BadZipFile:
        print(f"File '{zip_file_path}' is not a valid ZIP file.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def main():
    # Ensure an event loop is created
    try:
        asyncio.get_event_loop()
    except RuntimeError:
        asyncio.set_event_loop(asyncio.new_event_loop())
    
    st.title("Resume Analysis App :rocket:")

    # Sidebar
    st.sidebar.title("Uploads and Settings")
    uploaded_resume_zip = st.sidebar.file_uploader("Upload Resume ZIP", type="zip")
    uploaded_job_description_zip = st.sidebar.file_uploader("Upload Job Description ZIP", type="zip")

    # Model selection
    model_choice = st.sidebar.radio("Choose Model", ("Gemini", "OpenAI"))

    # API key input based on model selection
    if model_choice == "Gemini":
        api_key = st.sidebar.text_input("Enter Google API Key (Gemini)")
    else:
        api_key = st.sidebar.text_input("Enter OpenAI API Key")

    # Main content
    st.markdown("---")
    st.write("## Analysis Results")

    if uploaded_resume_zip and uploaded_job_description_zip and api_key:
        # Extract resume content from ZIP file
        resume_content = extract_content_from_zip(uploaded_resume_zip)
        if resume_content:
            st.write(f"Number of resumes: {len(resume_content)}")
        else:
            st.write("No resumes extracted from the ZIP file.")
        
        # Extract job description content from ZIP file
        job_description_content = extract_content_from_zip(uploaded_job_description_zip)
        if job_description_content:
            st.write(f"Number of job descriptions: {len(job_description_content)}")
        else:
            st.write("No job descriptions extracted from the ZIP file.")
        
        # Initialize the recruiter agent based on model choice
        if model_choice == "Gemini":
            recruiter = Agent(
                role="Senior Director in a company",
                goal="Recruit best tech talents in your company",
                backstory="""You work at a leading tech think tank.
                Your expertise lies in recruiting best tech talents for your firm.
                You have a knack of reading the candidate's resume and get a jist about the candidate if he/she is the best fit for the role technically""",
                verbose=False,
                allow_delegation=False,
                llm=ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=api_key)
            )
        else:
            recruiter = Agent(
                role="Senior Director in a company",
                goal="Recruit best tech talents in your company",
                backstory="""You work at a leading tech think tank.
                Your expertise lies in recruiting best tech talents for your firm.
                You have a knack of reading the candidate's resume and get a jist about the candidate if he/she is the best fit for the role technically""",
                verbose=False,
                allow_delegation=False,
                llm=ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=api_key)
            )

        # Perform analysis using CrewAI
        task2 = Task(
            description=f"""Conduct a comprehensive analysis on all the resumes {resume_content}.
            Identify which candidate is the best fit technically for which job descriptions {job_description_content}""",
            expected_output="""A report consisting only the top 5 candidates name you think will be suitable for each job description and their overall scores against the job description out of 100""",
            agent=recruiter
        )

        crew = Crew(
            agents=[recruiter],
            tasks=[task2],
            verbose=1
        )

        result = crew.kickoff()
        st.write("### Analysis Result:")
        st.write(result)

    else:
        st.warning("Please upload both the resume ZIP file, the job description ZIP file, and provide the appropriate API Key.")

if __name__ == "__main__":
    main()
