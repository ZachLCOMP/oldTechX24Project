import streamlit as st
from PIL import Image
import os
import google.generativeai as genai
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
import csv
from google.cloud import bigquery
from metrics import pageMetrics

st.set_page_config(page_title="Travel Page", page_icon="✈️")



st.sidebar.header('Travel Page How-To')
st.sidebar.write("This page is dedicated to helping you plan your dream vacation. Just tell us a little bit about your travel preferences and we'll handle the rest.")

st.sidebar.markdown("**How To Use:**")
st.sidebar.write("Input information on your traveling preferences. You have three options for selecting your desired country. If you already know, great. Either input a picture of a place you'd like to travel to (i.e. a beach, forest, resort, etc) or choose a continent and list of countries. From there you'll be recommended a list of locations where you'll have the opportunity to choose you desired city. If you already know where you want to go, you can input it directly")
st.sidebar.write("From there, you'll be recommended a list of restaurants, places to stay, and excursions to enjoy during your vacation. You'll be able to save your favorites at the end.")
st.sidebar.write("Once you selected what you'll like to do during your vacation, you'll have the option to download your trip to a csv file in your computer")
st.sidebar.write("If you ever change your mind, you can change your travel preferences at any time.")

#Setting up Gemini model
genai.configure(api_key=st.secrets["API_KEY"])
generation_config = genai.GenerationConfig(
  stop_sequences = None,
  temperature=0.7,
  top_p=1.0,
  top_k=32,
  candidate_count=1,
  max_output_tokens=32,
)

textModel = genai.GenerativeModel('gemini-pro')
picModel = genai.GenerativeModel('gemini-pro-vision')

#Setting up vertex model
vertexai.init(project=st.secrets["PROJECT_ID"], location="us-east4")
imageModel = ImageGenerationModel.from_pretrained("imagegeneration@005")

#Setting up bigquery
client = bigquery.Client("sds-project-414416")

metrics = pageMetrics()


class TravelPage: 

    def __init__(self, budget = None, companions=None, duration=None, interest=None, city = None):
        self.budget = budget
        self.companions = companions
        self.duration = duration
        self.interest= interest
        self.city = city
        self.restaurauntBudget = None
        self.lodgingBudget = None
        self.excursionsBudget = None
        self.resSelections = None
        self.lodgeSelections = None
        self.funSelections = None

    #Gets the user's ideal vacation budget
    def getBudget(self): 
        self.budget = st.slider("What is Your Budget?", 0, 10000, key='user_budget')
        if self.budget: 
            self.restaurauntBudget = st.slider("How much of your budget are you willing to spend on food (in percent)", 0.00, 1.00, key="restaurant_budget")
            self.lodgingBudget = st.slider("How much of your budget are you willing to spend on lodging (in percent)", 0.00, 1.00, key="lodging_budget")
            self.excursionsBudget = st.slider("How much of your budget are you willing to spend on fun (in percent)", 0.00, 1.00, key="excursion_budget")
        
            if self.restaurauntBudget and self.lodgingBudget and self.excursionsBudget and (self.restaurauntBudget+self.lodgingBudget+self.excursionsBudget) > 1: 
                st.warning('You cannot go over your total budget')

    #Gets the user's ideal vacation budget
    def getDuration(self): 
        self.duration = st.select_slider("How Long Are You Planning On Traveling?", ['1 day', '2 days', '3 days', '4 days', '5 days', '6 days', '1 week', '2 weeks', '3 weeks', '1 month', '1 month+'])

    #Gets the user's ideal vacation budget
    def getCompanions(self): 
        self.companions = st.number_input('How Many People Do You Plan On Traveling With?', min_value=0, max_value= 100, key='user_companions')

    #Gets the user's ideal vacation budget
    def getCompanionsDescription(self): 
        describeCompanions = st.selectbox("Who Do You Plan On Traveling With?", ['Self', 'Friends', 'Family', 'Coworkers', 'Signficant Other', 'Other'])

    #Gets the user's ideal vacation budget 
    def getInterest(self): 
        self.interest = st.text_input('What Do Yo Like to Do While Traveling? Separate the items by comma (e.g. hiking, swimming, shopping))', key='user_interest')


    #If the user didn't know where they wanted to go, a list of countries they selected will be inputted and a list of city,countries will be aoutputted
    def onSubmitDontKnow(self, userCountries): 
        findLocations = "Can you suggest 3 cities to travel for someone that would like to go to the following countries: "
        for country in userCountries: 
            findLocations += country + ", "

        findLocations += "You can recommend more than one city per country. Put the results in a single sentence, separated by a semicolon, in the format of city, country for each city. Only put the city and countries in the sentence. DO NOT PUT ANYTHING ELSE."
        suggestPlaces = textModel.generate_content(findLocations)

        self.suggestionsPage(suggestPlaces.text)

    #If the user choose to upload a picture, Gemini will recommend cities that have loactions similar to the picture
    def onSubmitPic(self, img): 
        findLocations = "Can you suggest 3 cities to travel for someone that would like to go to the somewhere like this picture. Put the results in a single sentence, separated by a semicolon, in the format of city, country for each city."
            
        suggestPlaces = picModel.generate_content([findLocations, img])
        suggestPlaces.resolve()

        self.suggestionsPage(suggestPlaces.text)

    #Function to make sure that the user only inputted one selection for country output 
    def is_valid_country(self, userDontKnow, pictureUpload, userKnow): 
        if userDontKnow and not(pictureUpload or userKnow): 
            return True
        if userKnow and not(pictureUpload or userDontKnow): 
            return True
        if pictureUpload and not(userKnow or userDontKnow): 
            return True
        return False

    def is_valid_submit(self): 
        return self.budget and self.interest and self.companions and self.duration 

    #Function used to simulate the homepage
    def homePage(self): 
        if 'username' in st.session_state: 
          metrics.add_visit_travel(st.session_state.username)
          with st.sidebar.popover("Metrics"):
            st.metric(st.session_state.username + " Visits to Travel Page:", value= metrics.get_visited_travel(st.session_state.username))
            st.metric(st.session_state.username + " buttons clicked", value= metrics.get_buttons_clicked())
            if metrics.find_max_visited(st.session_state.username) == "travel":
                st.write("This is the most visited page!")
        else: 
          st.header("Your AI Travel Planner")
        st.header("Your AI Travel Planner")
        st.subheader("Tell Us a Little About Your Traveling Preferences")

        #Collect information about user travel preferences
        userKnow = st.text_input("If You Already Know Where You Want to Go, Let Us Know Here. Please Input it in City, Country Format",key='user_know')

        #User upload image
        pictureUpload = st.file_uploader("Or You Could Use An Image As Inspiration. Upload A Place You'd Like to Go Below and We'll Find A Couple Spots We Think You'll Enjoy (png or jpg format only)", type=['png', 'jpg'] )
        if pictureUpload: 
                img = Image.open(pictureUpload)

        userDontKnow = st.multiselect("If Not, Let Us Help. What Continents Would You Like to Travel?", ['Europe', 'Africa', 'Asia', 'North America', 'South America', 'Australia', 'Anarticta'], key='user_continent')

        #Create a multiselect button that will add options as the user chooses countries
        if userDontKnow: 
            countries = []
            if 'Africa' in userDontKnow: 
                countries.extend(["Algeria", "Angola", "Benin", "Botswana", "Burkina Faso", "Burundi", "Cabo Verde", "Cameroon", "Central African Republic", "Chad", "Comoros", "Congo", "Democratic Republic of the Congo", "Djibouti", "Egypt", "Equatorial Guinea", "Eritrea", "Ethiopia", "Eswatini", "Gabon", "Gambia", "Ghana", "Guinea", "Guinea-Bissau", "Ivory Coast", "Kenya", "Lesotho", "Liberia", "Libya", "Madagascar", "Malawi", "Mali", "Mauritania", "Mauritius", "Morocco", "Mozambique", "Namibia", "Niger", "Nigeria", "Rwanda", "São Tomé and Príncipe", "Senegal", "Seychelles", "Sierra Leone","Somalia", "South Africa", "South Sudan", "Sudan", "Swaziland", "Tanzania", "Togo", "Tunisia", "Uganda", "Zambia", "Zimbabwe"])
            if 'Antartica' in userDontKnow: 
                countries.append("Antartica")
            if 'Europe' in userDontKnow: 
                countries.extend(["Albania", "Andorra", "Armenia", "Austria", "Azerbaijan","Belarus", "Belgium", "Bosnia and Herzegovina", "Bulgaria", "Croatia","Cyprus", "Czech Republic", "Denmark", "Estonia", "Finland", "France","Georgia", "Germany", "Greece", "Hungary", "Iceland", "Ireland","Italy", "Kosovo", "Latvia", "Liechtenstein", "Lithuania", "Luxembourg","Malta", "Moldova", "Monaco", "Montenegro", "Netherlands", "North Macedonia","Norway", "Poland", "Portugal", "Romania", "Russia", "San Marino","Serbia", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland","Turkey", "Ukraine", "United Kingdom", "Vatican City"])
            if 'Asia' in userDontKnow: 
                countries.extend(["Afghanistan","Armenia","Azerbaijan","Bahrain","Bangladesh","Bhutan","Brunei","Cambodia","China","Cyprus","East Timor","Egypt","Georgia","India","Indonesia","Iran","Iraq","Japan","Jordan","Kazakhstan","North Korea","South Korea","Kuwait","Kyrgyzstan","Laos","Lebanon","Malaysia","Maldives","Mongolia","Myanmar","Nepal","Oman","Pakistan","Palestine","Philippines","Qatar","Russia","Saudi Arabia","Singapore","Sri Lanka","Syria","Taiwan","Tajikistan","Thailand","Turkey","Turkmenistan","United Arab Emirates","Uzbekistan","Vietnam","Yemen"])
            if 'North America' in userDontKnow: 
                countries.extend(["Canada", "Mexico", "United States", "Antigua and Barbuda", "Bahamas", "Barbados", "Belize", "Costa Rica", "Cuba", "Dominica", "Dominican Republic", "El Salvador", "Grenada", "Guatemala", "Haiti", "Honduras", "Jamaica", "Nicaragua", "Panama", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Trinidad and Tobago"])
            if 'South America' in userDontKnow: 
                countries.extend(["Argentina", "Bolivia", "Brazil", "Chile", "Colombia","Ecuador", "Guyana", "Paraguay", "Peru", "Suriname","Uruguay", "Venezuela"])
            if 'Australia' in userDontKnow: 
                countries.append("Australia")
                
            userCountries = st.multiselect("Select up to 10 countries that you would like to visit.", options=countries, key='user-countries')

            #Ensures that the user selects >=10 countries to minimize mistakes with AI
            if len(userCountries) > 10: 
                st.warning("To get the best experience out of your AI travel planner, please select no more than 10 countries")
            elif len(userCountries) == 0: 
                st.warning("Please select at least one country to visit")

        self.getBudget()
        self.getCompanions()
        self.getCompanionsDescription()
        self.getDuration()
        self.getInterest()

        #Depending on how the user put their desired vacation spot in, the submitBtn will trigger different behaviors
        if 'home_Btn' not in st.session_state: 
           st.session_state.home_Btn = st.session_state.get('home_Btn', False)

        submitBtn = st.button('Submit', key ='home_btn')

        if submitBtn:
            metrics.add_click()
            if self.is_valid_submit(): 
                st.session_state.home_Btn = True
            else: 
                st.warning("Please input all of the necessary information")

        if st.session_state.home_Btn:
            #Verifies that the user only entered one option
            if self.is_valid_country(userDontKnow, pictureUpload, userKnow): 
                if userDontKnow: 
                    self.onSubmitDontKnow(userCountries)
                elif pictureUpload: 
                    self.onSubmitPic(img)
                else: 
                    self.city = userKnow
                    self.planTrip()
            else: 
                st.warning('Please only select one input for country selection.')

    #Create components to showcase locations. Component includes name, descripition & images
    def generateContent(self, recommendations, fileName, thing): 
        col1, col2 = st.columns([0.6, 0.4])
        for rec in recommendations:
            with col1: 
                st.subheader(rec)
                recDescription = textModel.generate_content('Come up with 1-2 sentences, in paragraph form to describe ' + rec + thing, )
                if recDescription: 
                    if recDescription.text: 
                        st.write(recDescription.text)
                else: 
                    st.warning("Error generating content")
            with col2:                     
                images = imageModel.generate_images('Pull an image from the following location'+ rec)
                if images:
                    images[0].save(location=fileName)
                    st.image(fileName, width=200)
                else: 
                    st.warning("Error generating content")


    #Function use to similuate a suggestions page, based on gemini suggestions
    def suggestionsPage(self, locations): 
        st.header('Suggestion Page')
        st.subheader("Based on your suggestions we think you'll enjoy the following places. Look at the suggestions shown and choose your favorite ")
        
        cities = list(locations.split(';'))
        if 'generate_content' not in st.session_state: 
            st.session_state.generate_content = st.session_state.get('generate_content', False)

        if not st.session_state.generate_content: 
            self.generateContent(cities, 'traveling.jpg', 'city')
            st.session_state.generate_content = True
        

        self.city = st.selectbox("Choose your favorite so we can build your dream vacation:", options=cities, key='user_final_dest')

        
        st.session_state.buttons_clicked = st.session_state.get('buttons_clicked', False)

        vacationBtn = st.button("Create Vacation", key='vacation-button')

        if vacationBtn: 
            metrics.add_click()
            st.session_state.buttons_clicked = True

        if st.session_state.buttons_clicked: 
            self.planTrip()
        
    
    def getRestaurants(self):

        #Find restaurants
        finalBudget = self.budget * self.restaurauntBudget
        findRestaurants = "Can you return a list of at most 2 popular restaurants to eat at " + self.city + " for someone eating with a party of " + str(self.companions) + " and a budget of " + str(finalBudget) + "American dollars. Put the name of the places in a single sentence, separated by a semicolon. Do NOT USE ADJECTIVES TO DESCRIBE THE PLACE. Only put the names of specific places in a single sentence, separated by a semicolon. Nothing else"

        suggestFood = textModel.generate_content(findRestaurants)
        if suggestFood.text: 
            return suggestFood.text
        else: 
            st.warning('Error generating content')
        
    
    def getLodging(self): 
        finalBudget = self.budget * self.lodgingBudget
       #Find lodging
        findLodging = "Can you return a list of at most 2 popular places to stay while visitng " + self.city + " for staying with a party of " + str(self.companions) + "and a budget of " + str(finalBudget) + "American dollars. Put the name of the places in a single sentence, separated by a semicolon. Do NOT USE ADJECTIVES TO DESCRIBE THE PLACE. Only put the names of specific places in a single sentence, separated by a semicolon. Nothing else"
        suggestLodging = textModel.generate_content(findLodging)
        if suggestLodging.text: 
            return suggestLodging.text
        else: 
            st.warning('Error generating content')
 
    def getFun(self):  
        finalBudget = self.budget * self.excursionsBudget
        findExcursions = "Can you return a list of at most 2 popular things to do in " + self.city + " for someone who likes to do" 

        for interest in self.interest: 
            findExcursions += interest + ', '
            
        findExcursions += "Traveling with a party of " + str(self.companions) + " and a budget of " + str(finalBudget) + " American dollars. Do NOT USE ADJECTIVES TO DESCRIBE THE PLACE. Only put the names of specific places in a single sentence, separated by a semicolon. Nothing else"

        suggestFun = textModel.generate_content(findExcursions)

        if suggestFun.text:
            return suggestFun.text
        else: 
            st.warning('Error generating content')

    #Function that will recommend places for the user to eat, stay, and do while on vacation
    def planTrip(self): 

        if 'plan_Trip' not in st.session_state: 
             st.session_state.plan_Trip = False

        if 'got_variables' not in st.session_state: 
            st.session_state.got_variables = False
        
        if 'user_select' not in st.session_state: 
                st.session_state.user_select = False

        
        if not st.session_state.got_variables:
            resSuggest = self.getRestaurants()
            lodgeSuggest = self.getLodging()

            funSuggest = self.getFun()

            st.session_state.resSelections = list(resSuggest.split(';'))
            st.session_state.lodgeSelections = list(lodgeSuggest.split(';'))
            st.session_state.funSelections = list(funSuggest.split(';')) 

            if not st.session_state.plan_Trip: 
                #Make this into a function
                st.subheader("Based on your input, here are some restaurants we think you\'ll like")
                self.generateContent(st.session_state.resSelections, "restaurant.jpg", 'restaurant')

                st.subheader("Based on your input, here are some places to stay we think you\'ll like")
                self.generateContent(st.session_state.lodgeSelections, "lodging.jpg", 'lodging')

                st.subheader("Based on your input, here are some fun excursions we think you\'ll like")
                self.generateContent(st.session_state.funSelections, "excursions.jpg", 'place')

                st.session_state.plan_Trip = True

            st.session_state.got_variables = True
            

        restaurants = st.multiselect("Choose your favorites", options=st.session_state.resSelections)
        lodging = st.multiselect("Choose your favorites", options=st.session_state.lodgeSelections)
        fun = st.multiselect("Choose your favorites", options=st.session_state.funSelections)


        if 'final_btn' not in st.session_state: 
            st.session_state.final_btn = False

        finalSelections = st.button('Finalize trip')

        if finalSelections: 
            metrics.add_click()
            if restaurants and fun and lodging: 
                st.session_state.final_btn = True
            else: 
                st.warning("Please select at least one of each")

        if st.session_state.final_btn: 
           self.saveTrip(str(restaurants), str(lodging), str(fun))

 
    #Function that will be used to save a user's trip & save it to bigquery
    def saveTrip(self, restaurants, lodging, excursions): 
        #Insert data into Bigquery
        if 'status' not in st.session_state or st.session_state.status == 'unverified': 
            myquery = "INSERT INTO `sds-project-414416.back_to_the_future.travel_info` (location, budget, traveling_partners, trip_duration, restaurants, lodging, excursions) VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\" )" % (self.city, self.budget, self.companions, self.duration, restaurants, lodging, excursions)
        elif 'status' in st.session_state and st.session_state.status == 'verified': 
            myquery = "INSERT INTO `sds-project-414416.back_to_the_future.travel_info` (username, location, budget, traveling_partners, trip_duration, restaurants, lodging, excursions) VALUES (\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\" )" % (st.session_state.username, self.city, self.budget, self.companions, self.duration, restaurants, lodging, excursions)

            QUERY = (myquery)
            insert_job = client.query(QUERY)
            row = insert_job.result()
            st.success('Trip sucessfully saved to database')

        #Write info into file
        my_trip = [{
            "Location": self.city,
            "Budget" : self.budget, 
            "Traveling Partners" : self.companions, 
            "Trip Duration": self.duration, 
            "Restaurants" : restaurants, 
            "Lodging" : lodging, 
            "Fun" : excursions
        }]

        fields = ["Location", "Budget", "Traveling Partners", "Trip Duration", "Restaurants", "Lodging", "Fun"]

        with open('my_trip.csv', 'w') as csvfile: 
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            writer.writerows(my_trip)
        
        st.subheader('Save your trip with us to your computer')
        with open('my_trip.csv', 'r') as csvfile:
            st.download_button("Save Your Trip To Your Computer", data=csvfile, file_name='my_trip.csv', mime='text/csv')
        

#Add Big Query to check if user
if 'status' not in st.session_state: 
    user = TravelPage()
    user.homePage()
elif st.session_state.status == 'verified': 
    QUERY = "SELECT * FROM `sds-project-414416.back_to_the_future.travel_info` WHERE username = \"%s\"" % (st.session_state['username'])
    query_job = client.query(QUERY)
    row = query_job.result()
    if row.total_rows > 0:
        for r in row: 
            placeholder = st.empty()
            with placeholder.container(): 
                st.title('Welcome Back **' + st.session_state['username'] + '**') 
                st.subheader("The last time you were here you planned the following trip \n")
                st.subheader("Location: " + r.location)
                st.subheader("Budget: " + r.budget)
                st.subheader("Number of Traveling Partners: " + r.traveling_partners)
                st.subheader("Trip Duration: " + r.trip_duration)
                st.write("Would you like to download your past trip or start a new one")
                resetBtn = st.button('Start New Trip')
                downloadBtn = st.button('Download Past Trip')
            
            if downloadBtn:
                metrics.add_click() 
                placeholder.empty()
                user = TravelPage(budget=r.budget, companions=r.traveling_partners, duration=r.trip_duration, city=r.location)
                user.saveTrip(restaurants=r.restaurants, lodging=r.lodging, excursions=r.excursions) 
                
            if resetBtn: 
              metrics.add_click()
              placeholder.empty()
              user = TravelPage()
              user.homePage() 
            
    else: 
        user = TravelPage()
        user.homePage()
