from streamlit.testing.v1 import AppTest
import hmac

at = AppTest.from_file('Home.py')


#Test that the page does nothing on no contact
def testNoPassword(): 
    at.secrets['password'] = 'tester'
    at.run()
    assert at.session_state['status'] == "unverified"
    assert len(at.warning) == 0

#Test that the page displays a warning when the password is incorrect
def testWrongPassword():
    at.run()
    at.text_input(key='return_user_name').input('tester').run()
    at.text_input(key='return_password').input('wrong').run()
    at.button(key='return_button').click().run()
    assert at.session_state.status == 'incorrect_login'
    assert len(at.warning) == 1
    assert len(at.success) == 0


#Test that the page shows the correct thing when password is right
def testRightPassword(): #Look into adding username too
    at.run()
    at.text_input(key='return_user_name').input('tester').run()
    at.text_input(key='return_password').input('tester').run()
    at.button(key='return_button').click().run()
    assert at.session_state.status == 'verified'
    assert len(at.warning) == 0
    assert len(at.success) == 1

testNoInput()
testWrongPassword()
testRightPassword()
