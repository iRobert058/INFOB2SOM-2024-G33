import unittest
from main import BoardGameMechanicsAnalyser
import pandas as pd

    #status/User role software developer testing the functionality of BoardGameMechanicsAnalyser.
class TestBoardGameMechanicsAnalyser(unittest.TestCase):

        #expected ourcome, it should be a dataclass, meaning the test's answer should be OK.
    def test_if_it_is_a_dataclass(self):
        self.assertTrue(isinstance(BoardGameMechanicsAnalyser, type))

        #setup of the precondition. Valid test dataset and API key.
    def setUp(self):
        self.analyser = BoardGameMechanicsAnalyser('test_dataset.csv', 'valid_api_key')
        
        #testing whether it works to load the top 200 (no data in the dataset yet).
    def test_get_top_200_list_dataset_not_loaded(self):
        with self.assertRaises(AttributeError):
            #er moet hier een AttributeError optreden, preconditie: er is nog geen dataset geladen
            self.analyser.get_top_200_list(sort_by="Rating Average")
    
        #testing the fake cleaned_dataset with an empty table.
    def test_get_top_200_list_invalid_column(self):
        self.analyser.cleaned_dataset = pd.DataFrame({"ValidColumn": [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.analyser.get_top_200_list(sort_by="InvalidColumn")
    
        #testing cleaned_dataset after mocking it with a small amount of data.
    def test_get_top_200_list_valid(self):
        data = {
            "Name": ["Apex Legends", "Fortnite", "Minecraft", "The Witcher"],
            "Rating Average": [8.5, 9.0, 7.0, 9.5],
            "Mechanic": [1, 2, 3, 4]
        }
        self.analyser.cleaned_dataset = pd.DataFrame(data)
        
        #expected result if we sort it by "Rating Average" (based on the fake table above).
        expected_result = [
            {"Name": "The Witcher", "Rating Average": 9.5, "Mechanic": 4},
            {"Name": "Fortnite", "Rating Average": 9.0, "Mechanic": 2},
            {"Name": "Apex Legends", "Rating Average": 8.5, "Mechanic": 1},
            {"Name": "Minecraft", "Rating Average": 7.0, "Mechanic": 3}
        ][:200]#Maximum of 200, added here because in the real implementation, it caps at 200., Here, it’s just top 4 because I didn’t feel like adding more rows to the table (I’m lazy)
        
        result = self.analyser.get_top_200_list(sort_by="Rating Average", ascending=False)
        self.assertEqual(result, expected_result)
        #call the result and check if it matches using assertEqual.

if __name__ == "__main__":
    unittest.main()