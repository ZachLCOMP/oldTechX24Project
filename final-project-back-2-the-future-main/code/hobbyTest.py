from streamlit.testing.v1 import AppTest
import hmac
import unittest
from unittest.mock import MagicMock
from _3_Hobby import HobbyPage

at =  AppTest.from_file('3_Hobby.py')

class TestHobbyPage(unittest.TestCase):
    def setUp(self):
        self.hobby_page = HobbyPage()

    def test_check_database(self):
        # Mocking BigQuery client and its query result
        self.hobby_page.client.query = MagicMock(return_value=MagicMock(result=MagicMock(total_rows=1)))
        self.assertTrue(self.hobby_page.check_database("hobby"))
    def test_null_error(self):
        at.text_area[0].input[None]
        at.text_area[1].input[None]
        at.text_area[2].input[None]
        at.run()
        assert at.error[0].body("Please provide input for at least 1 of the fields above.")

    def test_check_radio(self):
        at.text_area[0].input["FOO"]
        at.text_area[1].input[None]
        at.text_area[2].input["BAR"]
        at.radio[0].set_value("Only expand current")
        at.run()
        assert at.error[0].body("Select a choice; Enter your current hobbies or change option to “Only Suggest New Hobbies”")
    def test_store_data(self):
        # Mocking BigQuery client
        self.hobby_page.client.query = MagicMock()
        self.hobby_page.store_data()
        self.hobby_page.client.query.assert_called_once()

    # Similarly, you can write tests for other methods like store_hobbies, generate_image, generate_suggestions, etc.

    def setUp(self):
        self.hobby_page = HobbyPage()

    def test_check_database_with_existing_hobby(self):
        # Mocking BigQuery client and its query result
        self.hobby_page.client.query = MagicMock(return_value=MagicMock(result=MagicMock(total_rows=1)))
        self.assertTrue(self.hobby_page.check_database("existing_hobby"))

    def test_check_database_with_non_existing_hobby(self):
        # Mocking BigQuery client and its query result
        self.hobby_page.client.query = MagicMock(return_value=MagicMock(result=MagicMock(total_rows=0)))
        self.assertFalse(self.hobby_page.check_database("non_existing_hobby"))

    def test_store_hobbies(self):
        # Mocking BigQuery client
        self.hobby_page.check_database = MagicMock(return_value=False)  # Mocking no existing hobbies
        self.hobby_page.client.query = MagicMock()
        hobby_dictionary = {"hobby1": "description1", "hobby2": "description2"}
        self.hobby_page.store_hobbies(hobby_dictionary)
        self.hobby_page.client.query.assert_called()

    def test_generate_image_with_valid_prompt(self):
        # Mocking ImageGenerationModel
        self.hobby_page.imageModel.generate_images = MagicMock(return_value=[MagicMock(save=MagicMock())])
        self.hobby_page.generate_image("valid_prompt")
        self.hobby_page.imageModel.generate_images.assert_called_once_with(prompt="valid_prompt", number_of_images=1)

    def test_generate_image_with_invalid_prompt(self):
        # Mocking ImageGenerationModel to raise an exception
        self.hobby_page.imageModel.generate_images = MagicMock(side_effect=Exception("Invalid prompt"))
        with self.assertRaises(Exception):
            self.hobby_page.generate_image("invalid_prompt")

    # Add more test cases for other methods like generate_suggestions, store_data, get_interests, get_hobbies, get_disinterests, get_choice, etc.


    def setUp(self):
        self.hobby_page = HobbyPage()

    def test_valid_response_with_valid_input(self):
        hobby_dictionary = {"hobby1": "description1", "hobby2": "description2"}
        self.assertTrue(self.hobby_page.valid_response(hobby_dictionary))

    def test_valid_response_with_invalid_input(self):
        hobby_dictionary = {"hobby1": "description1"}
        self.assertFalse(self.hobby_page.valid_response(hobby_dictionary))

    def test_generate_suggestions_for_new_hobbies(self):
        self.hobby_page.hobby_choice = "Only Suggest New Hobbies"
        self.hobby_page.user_current_hobbies = "current_hobby1; current_hobby2"
        self.hobby_page.user_interests = "interest1; interest2"
        self.hobby_page.user_disinterests = "disinterest1; disinterest2"

        # Mocking model.generate_content method
        self.hobby_page.model.generate_content = MagicMock(return_value=MagicMock(text="suggestion1; suggestion2"))
        
        suggestions = self.hobby_page.generate_suggestions()

        self.assertEqual(len(suggestions), 2)
        self.assertTrue(all(isinstance(value, str) for value in suggestions.values()))

    def test_generate_suggestions_for_expanded_hobbies(self):
        self.hobby_page.hobby_choice = "Only expand current"
        self.hobby_page.user_current_hobbies = "current_hobby1; current_hobby2"
        self.hobby_page.user_interests = "interest1; interest2"
        self.hobby_page.user_disinterests = "disinterest1; disinterest2"

        # Mocking model.generate_content method
        self.hobby_page.model.generate_content = MagicMock(return_value=MagicMock(text="suggestion1"))
        self.hobby_page.check_database = MagicMock(return_value="description1")

        suggestions = self.hobby_page.generate_suggestions()

        self.assertEqual(len(suggestions), 1)
        self.assertTrue(all(isinstance(value, str) for value in suggestions.values()))

    # Add more test cases for other methods like store_data, get_interests, get_hobbies, get_disinterests, get_choice, suggestion_page, final_page, etc.
