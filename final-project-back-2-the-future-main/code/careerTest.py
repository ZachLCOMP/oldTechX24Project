import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO, StringIO
from collections import defaultdict
from _2_Career import CareerPlanner


class TestCareerPlanner(unittest.TestCase):

    @patch('_2_Career.st.text_area', return_value='User summary')
    def test_get_summary(self, mock_text_area):
        planner = CareerPlanner()
        planner.get_summary()
        self.assertEqual(planner.summary, 'User summary')

    @patch('_2_Career.st.multiselect', return_value=['Mathematics', 'Science'])
    def test_get_subjects(self, mock_multiselect):
        planner = CareerPlanner()
        planner.get_subjects()
        self.assertEqual(planner.subjects, ['Mathematics', 'Science'])

    @patch('_2_Career.st.file_uploader', return_value=BytesIO(b'This is a resume'))
    def test_get_resume(self, mock_file_uploader):
        planner = CareerPlanner()
        planner.get_resume()
        self.assertEqual(planner.resume, 'This is a resume')

    @patch('_2_Career.st.text_area', return_value='User summary')
    @patch('_2_Career.st.multiselect', return_value=['Mathematics', 'Science'])
    @patch('_2_Career.st.file_uploader', return_value=BytesIO(b'This is a resume'))
    @patch('_2_Career.textModel.generate_content')
    @patch('_2_Career.bigquery.Client.query')
    @patch('_2_Career.CareerPlanner.store_data')
    def test_generate_suggestions(self, mock_store_data, mock_query, mock_generate_content, mock_file_uploader, mock_multiselect, mock_text_area):
        planner = CareerPlanner()
        planner.generateSuggestions()
        mock_query.assert_called_once()
        mock_generate_content.assert_called_once_with("Write a list of 3 careers based off the following users current summary and put semicolons between each entry.Current user summary: User summaryUser favorite subjects: Mathematics Science User's resume: This is a resume")

    @patch('_2_Career.Image.open')
    @patch('_2_Career.st.image')
    def test_generate_image(self, mock_st_image, mock_image_open):
        planner = CareerPlanner()
        planner.generate_image('Prompt')
        mock_image_open.assert_called_once_with("Error shrug.jpeg")
        mock_st_image.assert_called_once()

    def test_generate_steps(self):
        planner = CareerPlanner()
        planner.check_database = MagicMock(return_value='Description')
        planner.generate_steps('Career')
        planner.check_database.assert_called_once_with('Career')

    @patch('_2_Career.st.sidebar.popover')
    @patch('_2_Career.st.metric')
    @patch('_2_Career.st.text_area', return_value='User summary')
    @patch('_2_Career.st.multiselect', return_value=['Mathematics', 'Science'])
    @patch('_2_Career.st.file_uploader', return_value=BytesIO(b'This is a resume'))
    @patch('_2_Career.textModel.generate_content')
    @patch('_2_Career.bigquery.Client.query')
    @patch('_2_Career.CareerPlanner.store_data')
    def test_home(self, mock_store_data, mock_query, mock_generate_content, mock_file_uploader, mock_multiselect, mock_text_area, mock_metric, mock_popover):
        planner = CareerPlanner()
        planner.home()
        mock_query.assert_called_once()
        mock_generate_content.assert_called_once_with("Write a list of 3 careers based off the following users current summary and put semicolons between each entry.Current user summary: User summaryUser favorite subjects: Mathematics Science User's resume: This is a resume")

    @patch('_2_Career.CareerPlanner.generate_steps', return_value='Steps')
    @patch('_2_Career.st.write')
    @patch('_2_Career.open', create=True)
    @patch('_2_Career.st.download_button')
    def test_suggestions(self, mock_download_button, mock_open, mock_write, mock_generate_steps):
        planner = CareerPlanner()
        planner.suggestions({'Career': 'Description'})
        mock_download_button.assert_called_once()
        mock_open.assert_called_once()
        mock_write.assert_called()
        mock_generate_steps.assert_called_once_with('Career')

if __name__ == '__main__':
    unittest.main()
