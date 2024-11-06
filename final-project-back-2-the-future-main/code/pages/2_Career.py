import streamlit as st
import google.generativeai as genai
import PyPDF2
from google.cloud import bigquery
from PIL import Image
import csv
import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from collections import defaultdict
import sys
sys.path.append('/home/zachlunsford/final-project-back-2-the-future/code/pages')
from metrics import pageMetrics

username = ""
if not st.session_state.get('username'):
    st.session_state['username'] = "Unknown User"
else:
    username = st.session_state.username

st.set_page_config(page_title="Career Page")

# zach-api-key = AIzaSyCrrraedr3ENdniSZwCAO72qAaHJRfnGv4


genai.configure(api_key='AIzaSyAzBG2mUJT9twnSdILHGZEtZ9vZqEYEFDE')
client = bigquery.Client('valued-lambda-413923')
textModel = genai.GenerativeModel('gemini-pro')

# project=st.secrets["PROJECT_ID"]
vertexai.init(project='valued-lambda-413923', location='us-east4')
imageModel = ImageGenerationModel.from_pretrained("imagegeneration@005")

metrics = pageMetrics()

if "Submit" not in st.session_state:
    st.session_state.Submit = False
if not st.session_state.get("suggestions"):
     st.session_state.suggestions = False
if not st.session_state.get("final_careers"):
     st.session_state.final_careers = False

# Defining class to represent a career planner.
class CareerPlanner:
    def __init__(self, summary = None, subjects = None, disinterests = None, resume = None):
        self.summary = summary
        self.subjects = subjects
        self.resume = resume
        self.disinterests = disinterests

    def check_database(self, career):
        QUERY = (
            "SELECT description FROM `valued-lambda-413923.user_info.generated_careers` WHERE career = @career ")
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("career", "STRING", career), ])
        query_job = client.query(QUERY, job_config=job_config)
        rows = query_job.result()
        if rows.total_rows > 0:
            for row in rows:
                return row.description
        else:
            return ""
    
    def store_careers(self, careerDict):
        for career, description in careerDict.items():
            if not self.check_database(career):
                myquery = "INSERT INTO `valued-lambda-413923.user_info.generated_careers` (career, description) VALUES (\"%s\", \"%s\")" % (career, description)
                QUERY = (myquery)
                query_job = client.query(QUERY)
    
    def store_data(self):
        myquery = "INSERT INTO `valued-lambda-413923.user_info.user_info` (user_name, user_profile, disinterests) VALUES (\"%s\", \"%s\", \"%s\")" % (
            username, self.summary, self.disinterests)
        QUERY = (myquery)
        query_job = client.query(QUERY)
        rows = query_job.result()

    def generate_image(self, prompt):
        try:
            images = imageModel.generate_images(
                prompt=prompt, number_of_images=1)
            if images:
                images[0].save(location="careerimg.jpg")
                st.image("careerimg.jpg")
        except Exception as e:
            image = Image.open("Error shrug.jpeg")
            st.image(image, use_column_width=True)
            st.error(f"Couldnt generate image")
    
    def generate_steps(self, career):
        steps = textModel.generate_content("Create a list of a couple steps someone needs to take in order to pursue this career: " + career)
        return steps.text

    def get_summary(self):
        #Text area for the user to enter a summary of themselves.
        self.summary = st.text_area(label="Make sure you include your interests, hobbies, career experience, career goals or anything you might feel is applicable.")

    def get_subjects(self):
        #Multiselect widget for the user to select school subjects they like or are good at.
        self.subjects = st.multiselect("If you’re not in college yet, what school subjects do you like or you’re good at?", ['Mathematics', 'Science', 'History and Social Studies', 'ELA (English Language Arts)', 'Foreign Language', 'Arts and Music', 'Physical Education'])

    def get_resume(self):
        #File uploader for the user to upload their resume.
        resume = st.file_uploader(label="Do you have a resume? If so, we'd love to see it! (PDF only)", type=['pdf'])
        if resume:
            pdf_reader = PyPDF2.PdfReader(resume)
            pdf_text = ""
            for page_num in range(len(pdf_reader.pages)):
                page_text = pdf_reader.pages[page_num].extract_text()
                pdf_text += page_text
            self.resume = pdf_text
    
    def generateSuggestions(self):
        modelString = "Write a list of 3 careers based off the following users current summary and put semicolons between each entry."
        if self.summary:
            modelString += "Current user summary: " + self.summary
        if self.subjects:
            modelString += "User favorite subjects: "
            for subject in self.subjects:
                modelString += subject + " "
        if self.resume:
            modelString += "User's resume: " + self.resume
        career_response = textModel.generate_content(modelString)
        careerList = list(career_response.text.split(";"))
        careerDict = defaultdict(str)
        for career in careerList:
            description = self.check_database(career)
            if len(description) > 0:
                careerDict[career] = description +" (from previous entry)"
            else:
                careerDict[career] = str(textModel.generate_content(
                "Write a short, 3-5 sentence description of this career and why it is a good career: " + career).text)

        return careerDict, careerList
    
    def clickSubmit():
        st.session_state["Submit"] = True
        metrics.add_click()
    
    # Method to display the home page of the career planner.
    def home(self):
        careerDict = defaultdict(str)
        careerList = []
        metrics.add_visit_hobby(username)
        st.sidebar.header('Career Builder')
        st.sidebar.write("This page is dedicated to helping YOU find your ideal career path and set goals that correspond to it.")
        st.sidebar.subheader("How-To")
        st.sidebar.write("1. Tell us about yourself any way you know how. Hobbies, interests, careers, school subjects anything goes. You can even throw in your resume if you have one!\n\n"
        "2. We'll take all of that information and generate some potential careers we think you might be interested in. Just press submit to get those suggestions.\n\n"
        "3. Now if you don't like them then just click the Not interested button but otherwise save it and we can go more in-depth on that career later.")

        with st.sidebar.popover("Metrics"):
            st.metric(username + " Visits to Career Page:", value= metrics.get_total_career())
        st.title("Welcome to your Personal AI Career Planner")
        st.subheader("Tell us about yourself, what do you want to do? (If you’re not sure yet feel free to just talk about yourself!)")

        with st.form("Career Form"):
            st.subheader(
                "First, enter what currently interests you.")
            self.get_summary()
            self.get_subjects()
            self.get_resume()

            st.form_submit_button("Submit", type= "primary")

            if self.summary or self.subjects or self.resume:
                    if st.session_state.get("FormSubmitter:Career Form-Submit"):
                        careerDict, careerList = self.generateSuggestions()
                        st.session_state.suggestions = True
                        self.store_data()
            else:
                st.error("Input required for at least one field.")
        if st.session_state.suggestions == True and st.session_state["FormSubmitter:Career Form-Submit"]:
            self.suggestions(careerDict)
    
    def suggestions(self, careerDict):
        final_careers = set()
        stepsToFollow = defaultdict(str)
        st.header('Suggestion Page')
        st.subheader("So far we think you'd be interested in the following careers. Please save the ones you're interested in or indicate that you don't like them if you feel that way")

        for career, description in careerDict.items():
            steps = self.generate_steps(career)
            col1, col2 = st.columns([0.6, 0.4])

            with col1:
                st.subheader(career)
                st.write(description)

            with col2:
                self.generate_image(career)
                with open("careerimg.jpg", "rb") as file:
                    btn = st.download_button(
                        label="Download image",
                        data=file,
                        file_name="careerimg.jpg",
                        mime="image/png",
                        key=career
                    )
            st.write(steps)
            stepsToFollow[career] = steps
        if st.session_state.suggestions == True:
            self.save_careers(careerDict, stepsToFollow)
    
    def save_careers(self, careerDict, stepsToFollow):
        self.store_careers(careerDict)
        fields = ["Career", "Description", "Next Steps"]

        with open('new_careers.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(fields)
            for career, description in careerDict.items():
                steps = stepsToFollow[career]
                writer.writerow([career, description, steps])

        st.subheader("Thank you so much for using our AI Career Builder!")
        st.write("We hope you're interested in your new careers. We encourage you to check out our other fantastic pages, **Hobby Finder** and **Travel Planner.**")

        col1,col2,col3 = st.columns([0.3,0.3,0.3])
        with open('new_careers.csv', 'r') as file:
            with col2:
                if st.download_button("Download your career list!", data=file, file_name='new_careers.csv', mime='text/csv', type="primary"):
                    metrics.add_click()
        st.write("Note: downloading the file will bring you back to the landing page, eliminating any pictures that you have not saved.")
        
    
    
user = CareerPlanner()
user.home()
