import unittest
from unittest.mock import patch
import pandas as pd
from main import BoardGameMechanicsAnalyser 

class TestBoardGameMechanicsAnalyser(unittest.TestCase):
    def setUp(self):
        #setUp for mocking the data
        
        self.dataset_path = 'mock_dataset.csv'
        self.api_key = 'mock_api_key'
        self.analyser = BoardGameMechanicsAnalyser(self.dataset_path, self.api_key)

    def test_load_dataset_file_not_found(self):
        #Testing the behavior when the dataset file is not found.
        with patch('pandas.read_csv', side_effect=FileNotFoundError):
            with self.assertRaises(FileNotFoundError) as context:
                self.analyser.load_dataset_clean()
            self.assertIn("File not found", str(context.exception))

    def test_load_dataset_missing_columns(self):
        #Testing the behavior when the dataset is missing required columns.
       
        mock_dataset = pd.DataFrame({'Name': ['Game1'], 'Year Published': [2020]})
        with patch('pandas.read_csv', return_value=mock_dataset):
            with self.assertRaises(ValueError) as context:
                self.analyser.load_dataset_clean()
            self.assertIn("Dataset is missing required columns", str(context.exception))

    def test_load_dataset_valid(self):
        #Test loading and cleaning a valid dataset.
        
        mock_dataset = pd.DataFrame({
            'Name': ['Chess', 'Checkers'],
            'Year Published': [1850, 1800],
            'Mechanics': ['Strategy, Tactics', 'Strategy']
        })
        with patch('pandas.read_csv', return_value=mock_dataset):
            cleaned_dataset = self.analyser.load_dataset_clean()
            self.assertEqual(len(cleaned_dataset), 2)
            self.assertIn('Mechanics', cleaned_dataset.columns)
            self.assertNotIn(0, cleaned_dataset['Year Published'].values)

    def test_load_dataset_with_invalid_year(self):
        #Test that rows with invalid 'Year Published' values (e.g., 0) are excluded.
        
        # Mock a dataset with an invalid 'Year Published'
        mock_dataset = pd.DataFrame({
            'Name': ['Game1', 'Game2'],
            'Year Published': [2020, 0],
            'Mechanics': ['Strategy', 'Tactics']
        })
        with patch('pandas.read_csv', return_value=mock_dataset):
            cleaned_dataset = self.analyser.load_dataset_clean()
            self.assertEqual(len(cleaned_dataset), 1)
            self.assertNotIn(0, cleaned_dataset['Year Published'].values)

    #Should give a dataset unavailable due to file read failure
    def test_load_dataset_file_read_error(self):
        #Simulates a failure scenario where the dataset file can't be read due to a permission error.
        with patch('pandas.read_csv', side_effect=PermissionError("Permission denied")):
            
            with self.assertRaises(PermissionError) as context:
                self.analyser.load_dataset_clean()
            self.assertIn("Permission denied", str(context.exception))

if __name__ == "__main__":
    unittest.main()