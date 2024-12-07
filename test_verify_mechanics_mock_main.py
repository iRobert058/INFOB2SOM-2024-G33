import unittest
from unittest.mock import MagicMock, patch
from main import BoardGameMechanicsAnalyser
from collections import Counter
import pandas as pd

class TestBoardGameMechanicsAnalyser(unittest.TestCase):
    def setUp(self):
        #setUp for BoardGameMechanicsAnalyser with mocks.
        self.analyser = BoardGameMechanicsAnalyser('mock_dataset.csv', 'mock_api_key')
        self.analyser.cleaned_dataset = pd.DataFrame({
            'Name': ['Chess', 'Checkers', 'Gloomhaven'],
            'Year Published': [1850, 1800, 2017],
            'Mechanics': ['Strategy, Tactics', 'Strategy', 'Roleplaying, Cooperation, Strategy']
        })
        self.analyser.model = MagicMock()
        self.analyser.model.generate_content = MagicMock()

    def test_load_dataset_clean_with_valid_data(self):
        #test that the dataset is cleaned correctly when valid data is provided.
        with patch('pandas.read_csv', return_value=self.analyser.cleaned_dataset):
            cleaned_dataset = self.analyser.load_dataset_clean()
            self.assertFalse(cleaned_dataset.empty)
            self.assertEqual(len(cleaned_dataset), 3)
            self.assertIn('Mechanics', cleaned_dataset.columns)

    def test_verify_mechanics_with_genai_valid_game(self):
       #test the verification of mechanics for a valid game.
        self.analyser.model.generate_content.return_value.text = "2"

        accuracy = self.analyser.verify_mechanics_with_genai('Chess')
        self.assertAlmostEqual(accuracy, 1.0)  #2 mechanics in dataset and response matches exactly
        self.analyser.model.generate_content.assert_called_once()

    def test_verify_mechanics_with_genai_invalid_game(self):
        #test what happens when a non-existent game is queried.
        with self.assertRaises(ValueError) as context:
            self.analyser.verify_mechanics_with_genai('NonExistentGame')
        
        self.assertIn("Game 'NonExistentGame' not found in the dataset.", str(context.exception))

    def test_verify_mechanics_with_genai_no_dataset_loaded(self):
        #testing the behavior when the dataset is not loaded or cleaned.
        
        delattr(self.analyser, 'cleaned_dataset')

        with self.assertRaises(AttributeError) as context:
            self.analyser.verify_mechanics_with_genai('Chess')

        self.assertIn("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.", str(context.exception))

if __name__ == "__main__":
    unittest.main()