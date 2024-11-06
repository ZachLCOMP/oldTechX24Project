import streamlit as st
from streamlit.testing.v1 import AppTest

at = AppTest.from_file('pages/1_Travel.py')

#Asserts that an error arrives if the user tries to choose cities in two different ways
def testMultipleInputs():
    at.run(timeout=10)
    at.multiselect(key='user_continent').select('Africa').run()
    at.multiselect(key='user-countries').select('South Africa')
    at.text_input(key='user_know').input('Las Vegas, Nevada').run()
    at.number_input(key='user_companions').set_value(2).run()
    at.text_input(key='user_interest').input('swim, eat, sleep').run()
    at.slider(key='user_budget').set_value(3000).run()
    at.button(key='home_btn').click().run()
    assert len(at.warning) == 1

#Asserts that an error arrives if the user tries to submit without putting in all of the necessary information
def validSubmit(): 
    at.session_state.home_Btn = False
    at.run(timeout=10)
    at.text_input(key='user_know').input('Las Vegas, Nevada').run()
    at.number_input(key='user_companions').set_value(2).run()
    at.slider(key='user_budget').set_value(3000).run()
    at.button(key='home_btn').click().run()
    assert at.session_state.home_Btn == False
    assert len(at.warning) == 1

#Asserts that an error arrives if the user tries to submit without inputting a country
def chooseCountry(): 
    at.session_state.home_Btn = False
    at.run(timeout=10)
    at.number_input(key='user_companions').set_value(2).run()
    at.text_input(key='user_interest').input('swim, shop, cook').run()
    at.slider(key='user_budget').set_value(3000).run()
    at.button(key='home_btn').click().run()
    assert len(at.warning) == 1

#Asserts the returning users get taken to the correct screen
def returningUser(): 
    at.session_state.status = 'verified'
    at.session_state['username'] = 'tester'
    at.run(timeout=10)
    assert 'Welcome Back' in at.title[0].value

#Asserts that if the user choose to select a continent, they have to choose a country from that continent
def testUserDontKnow():
    at.run(timeout=10)
    at.multiselect(key='user_continent').select('Africa').run()
    assert len(at.warning) == 1


#testMultipleInputs()
#validSubmit()
#chooseCountry()
#returningUser()
#testUserDontKnow()
