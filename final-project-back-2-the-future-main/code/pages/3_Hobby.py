import streamlit as st
import google.generativeai as genai
from google.cloud import bigquery
from PIL import Image
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from collections import defaultdict
from metrics import pageMetrics
import csv


API_KEY = 'AIzaSyC_w0m3syV9Yno8jqYQ5GOIxJnTUpV7Wvk'
username = "Daye"  # user will be fetched from bigquery, this is a temp name

st.set_page_config(page_title="Hobby Page")
# Gemini Set up
genai.configure(api_key=st.secrets["DAYE_API_KEY"])
model = genai.GenerativeModel('gemini-pro')

# BigQuery Set up
client = bigquery.Client()  # To be expanded upon
# Landing page for hobby tracker

vertexai.init(project=st.secrets["PROJECT_ID"], location="us-east4")
imageModel = ImageGenerationModel.from_pretrained("imagegeneration@005")


metrics = pageMetrics()

if "Submit" not in st.session_state:
    st.session_state.Submit = False
if not st.session_state.get("suggestions"):
     st.session_state.suggestions = False
if not st.session_state.get("final_hobbies"):
     st.session_state.final_hobbies = False

class HobbyPage:

    def __init__(self, user_interests=None, user_current_hobbies=None, user_disinterests=None, hobby_choice=None, final_hobbies=None, hobby_list=None):
        self.user_interests = user_interests
        self.user_current_hobbies = user_current_hobbies
        self.user_disinterests = user_disinterests
        self.hobby_choice = hobby_choice
        self.final_hobbies = final_hobbies
        self.hobby_list = hobby_list
        self.hobby_num = hobby_num

    # Checks to see if there is an entry to a given database and returns the query

    def check_database(self, hobby):
        QUERY = (
            "SELECT description FROM `dayekaribiwhytetechx2024.hobby_data.generated_hobbies` WHERE hobby = @hobby ")
        job_config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("hobby", "STRING", hobby), ])
        query_job = client.query(QUERY, job_config=job_config)
        rows = query_job.result()
        if rows.total_rows > 0:
            for row in rows:
                return row.description
        else:
            return ""

    # Stores hobbies into the hobby table if there is no current entry for that hobby
    def store_hobbies(self, hobby_dictionary):
        if self.valid_response(self, hobby_dictionary, self.hobby_num):
            for hobby, description in hobby_dictionary.items():
                if not self.check_database(self, hobby):
                    myquery = "INSERT INTO `dayekaribiwhytetechx2024.hobby_data.generated_hobbies` (hobby, description) VALUES (\"%s\", \"%s\")" % (
                        hobby, description)
                    QUERY = (myquery)
                    query_job = client.query(QUERY)

    # Stores user input in the user data table
    def store_data(self):
        myquery = "INSERT INTO `dayekaribiwhytetechx2024.hobby_data.hobby_inputs` (user_name, user_interests, user_hobbies, user_disinterests) VALUES (\"%s\", \"%s\", \"%s\", \"%s\")" % (
            username, self.user_interests, self.user_current_hobbies, self.user_disinterests)
        QUERY = (myquery)
        query_job = client.query(QUERY)
        rows = query_job.result()
    # Generates images for a given prompt

    def generate_image(self, prompt):
        try:
            images = imageModel.generate_images(
                prompt=prompt, number_of_images=1)
            if images:
                images[0].save(location="hobbyimg.jpg")
                st.image("hobbyimg.jpg")
        except Exception as e:
            image = Image.open("Error shrug.jpeg")
            st.image(image, use_column_width=True)
            st.error(f"Couldn't generate image")
    # Returns a boolean if the hobby dictionary is at the needed capacity

    def valid_response(self, hobby_dictionary, num):
        return len(hobby_dictionary) == self.hobby_num

    def generate_nextSteps(self, hobby):
        nextSteps = model.generate_content("Create a list of a couple steps someone needs to take in order to pursue this hobby: " + hobby)
        return nextSteps.text

    def generate_suggestions(self):
        if not self.hobby_choice:
            st.error("Please select an option.")
            return
        if self.hobby_choice == 'Only expand current':
            hobby_response = model.generate_content(
                "Write a list of " + str(self.hobby_num) + " extended hobbies based off the following users current hobbies and put semicolons between each entry. Use the users interests and disinterest to find hobbies that are better suited for them. These suggested hobbies should not include any of the user current hobby entries. Do not number or use any bulllet points. user's current hobbies: " + self.user_current_hobbies + "; user's interests: " + self.user_interests + "; user's disinterests: " + self.user_disinterests)
        else:
            hobby_response = model.generate_content("Write a list of " + str(self.hobby_num) + " new hobbies based off the following users current hobbies and put semicolons between each entry. If any are none, then come up with some random hobbies: Current hobbies: " +
                                                    self.user_current_hobbies + " User disinterests: " + self.user_disinterests + "Interests: " + self.user_interests)
        hobby_list = list(hobby_response.text.split(";"))
        hobby_dictionary = defaultdict(str)
        if self.hobby_choice == 'Only expand current':
            for hobby in hobby_list:
                description = self.check_database(self, hobby)
                if len(description) > 0:
                    hobby_dictionary[hobby] = description +" (from previous entry)"
                else:
                    hobby_dictionary[hobby] = str(model.generate_content(
                        "Write a short, 3-5 sentence description of the current hobby and how it relates to one of the current hobbies. current hobbies:" + self.user_current_hobbies + "; suggested hobby: " + hobby).text)
        else:
            for hobby in hobby_list:
                description = self.check_database(self, hobby)
                if len(description) > 0:
                    hobby_dictionary[hobby] = description +" (from previous entry)"
                else:
                    hobby_dictionary[hobby] = str(model.generate_content(
                    "Write a short, 3-5 sentence description of the current hobby and why it is a good hobby: " + hobby).text)

        return hobby_dictionary, hobby_list

    def get_interests(self):
        self.user_interests = st.text_area(label="Interests:", max_chars=300,
                                           help="Enter your interests in the field below. (300 character Maximum)")

    def get_hobbies(self):
        self.user_current_hobbies = st.text_area(label="Current Hobbies:", max_chars=300,
                                                 help="Enter your current hobbies in the field below. (300 character Maximum)")

    def get_disinterests(self):
        self.user_disinterests = st.text_area(label="Disinterests:", max_chars=300,
                                              help="Enter your disinterests in the field below. (300 character Maximum)")

    def get_number(self):
        self.hobby_num = st.select_slider("Number of Hobbies you wish to generate:", options=[5,6,7,8,9,10,11,12,13,14,15])

    def get_choice(self):
        self.hobby_choice = st.radio("Suggest new hobbies or expand on current hobbies?", [
            "Only Suggest New Hobbies", "Only expand current"], help="Select an option. This will effect your final hobby selections.", horizontal=True)
        st.write(
            "Note: you must have input in “Current hobbies” if selecting “Only expand on current hobbies”.")
        if not self.hobby_choice:
            st.session_state["choice"] = False
        else:
            st.session_state["choice"] = True

    # Landing page for hobby tracker

    def click_submit():
      st.session_state["Submit"] = True 
      metrics.add_click()

    def click_remove(remove_btn_key):
        st.session_state[remove_btn_key] = True

    def click_save(save_btn_key):
        st.session_state[save_btn_key] = True

    def landing_page(self):
        hobby_dictionary = defaultdict(str)
        hobby_list = []
        metrics.add_visit_hobby(username)
        st.sidebar.header('Hobby Tracker How-To')
        st.sidebar.write("This page will help you track and locate new hobbies! \nSteps:\n 1. Enter your interests, current hobbies, and/or disinterests in the fields provided. \n 2. Choose whether you want strictly new hobbies or extensions of your current.\n 3. press submit. \n 4. Watch as our AI Hobby Finder generates unique hobbies for you! \n 5. Download the list of new hobbies as a csv file for easy reference.")
        #st.sidebar.write(st.session_state)
        with st.sidebar.popover("Metrics"):
            st.metric(username + " Visits to Hobby Page:", value= metrics.get_total_hobby())
        image = Image.open('Hobbies.png')
        st.title("Your AI Hobby Tracker")
        st.header(
            "Welcome to the AI Hobby Finder! Get ready to embark on a journey to find a hobby!")
        st.image(image)
        with st.form("Hobby Form"):
            st.subheader(
                "First, enter what currently interests you, excluding your current hobbies.")
            self.get_interests(self)

            st.subheader(
                "Now enter any hobbies that you currently do (and enjoy), if applicable.")
            self.get_hobbies(self)

            st.subheader(
                "Enter any activities that disinterest you, if applicable.")
            self.get_disinterests(self)
            self.get_number(self)
            self.get_choice(self)

            st.form_submit_button("Submit", type= "primary")

            if self.user_current_hobbies or self.user_disinterests or self.user_interests:
                if self.hobby_choice == "Only expand current" and not self.user_current_hobbies:
                        st.error(
                            "Select a choice; Enter your current hobbies or change option to “Only Suggest New Hobbies”")              
                else:
                    if st.session_state.get("FormSubmitter:Hobby Form-Submit"):
                        hobby_dictionary, hobby_list = self.generate_suggestions(self)
                        if not self.valid_response(self, hobby_dictionary, self.hobby_num):
                            st.error(
                                    "There may have not enough information provided, Please enter more in the fields above or press submit again")
                        else:
                            st.session_state.suggestions = True
                            self.store_data(self)
                        

            else:
                    st.error(
                        "Please provide input for at least 1 of the fields above.")
        if st.session_state.suggestions == True and st.session_state["FormSubmitter:Hobby Form-Submit"]:
            self.suggestion_page(self, hobby_dictionary)
    # Suggestion page

    def suggestion_page(self, hobby_dictionary):
        final_hobbies = set()
        st.title("Your Hobby Suggestions")
        st.write("Based on your interests, here are some hobby suggestions:")
        count = 0
        nextStep_dicitonary = defaultdict(str)
        for hobby, description in hobby_dictionary.items():
            next_steps = self.generate_nextSteps(self, hobby)
            col1, col2 = st.columns([0.6, 0.4])

            with col1:
                if self.hobby_choice == 'Only expand current':
                    st.subheader(
                        "Expansion of Current Hobbies: " + hobby + "!")
                else:
                    st.subheader("New Hobby: " + hobby + "!")
                st.write(description)
            with col2:
                self.generate_image(self, hobby)
                # with open("hobbyimg.jpg", "rb") as file:
                #     btn = st.download_button(
                #         label="Download image",
                #         data=file,
                #         file_name="hobbyimg.jpg",
                #         mime="image/png",
                #         key=hobby
                #     )
            st.write(next_steps)
            st.link_button(
                    "Learn More", "https://en.wikipedia.org/wiki/" + hobby.replace(" ", "_"), type="primary", use_container_width=True)
            nextStep_dicitonary[hobby] = next_steps
        if st.session_state.suggestions == True: 
            self.save_hobbies(self, hobby_dictionary, nextStep_dicitonary)
        
        
    # Final page
    # Final page to display selected hobbies and give the user steps in how they can get started with that hobby
    def save_hobbies(self, hobby_dictionary, nextStep_dicitonary):
        self.store_hobbies(self, hobby_dictionary)
        fields = ["Hobby", "Description", "Next Steps"]

        with open('new_hobbies.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            
            writer.writerow(fields)
            for hobby, description in hobby_dictionary.items():
                next_steps = nextStep_dicitonary[hobby]
                writer.writerow([hobby, description, next_steps])

        st.subheader("Thank you so much for using our AI Hobby Finder!")
        st.write("We hope you enjoy your new hobbies! Feel free to check out our other amazing pages, **Travel Planner** and **Career Planner.**")

        col1,col2,col3 = st.columns([0.3,0.3,0.3])
        with open('new_hobbies.csv', 'r') as file:
            with col2:
                st.download_button("Save your hobby list to your computer!", data=file, file_name='new_hobbies.csv', mime='text/csv', type="primary")
        st.write("Note: downloading the file will bring you back to the landing page, eliminating any pictures that you have not saved.")
        


# Will be used later to navigate to other pages
user = HobbyPage
user.landing_page(user)