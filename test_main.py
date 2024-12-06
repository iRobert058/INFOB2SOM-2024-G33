import unittest
from main import BoardGameMechanicsAnalyser
import pandas as pd

    #Status/User role: Softwareontwikkelaar die de functionaliteit van BoardGameMechanicsAnalyser test.
class TestBoardGameMechanicsAnalyser(unittest.TestCase):

        #verwachte uitkomst is dat het een dataclass is aka antwoord op de test moet OK zijn
    def test_if_it_is_a_dataclass(self):
        self.assertTrue(isinstance(BoardGameMechanicsAnalyser, type))

        #precondities: geldige testdataset en API-key
    def setUp(self):
        self.analyser = BoardGameMechanicsAnalyser('test_dataset.csv', 'valid_api_key')
        
        #testen of het werkt om top 200 te laden (nog geen data in de set) 
    def test_get_top_200_list_dataset_not_loaded(self):
        with self.assertRaises(AttributeError):
            #er moet hier een AttributeError optreden, preconditie: er is nog geen dataset geladen
            self.analyser.get_top_200_list(sort_by="Rating Average")
    
        #Testen van de neppe cleaned_dataset bij een leeg lege tabel
    def test_get_top_200_list_invalid_column(self):
        self.analyser.cleaned_dataset = pd.DataFrame({"ValidColumn": [1, 2, 3]})
        
        with self.assertRaises(ValueError):
            self.analyser.get_top_200_list(sort_by="InvalidColumn")
    
        #cleaned_dataset na apen met kleine hoeveelheid data
    def test_get_top_200_list_valid(self):
        data = {
            "Name": ["Apex Legends", "Fortnite", "Minecraft", "The Witcher"],
            "Rating Average": [8.5, 9.0, 7.0, 9.5],
            "Mechanic": [1, 2, 3, 4]
        }
        self.analyser.cleaned_dataset = pd.DataFrame(data)
        
        #verwachte resultaat als we het op "Rating Average" gaan sorteren (afhankelijk van de nep tabel hier boven)
        expected_result = [
            {"Name": "The Witcher", "Rating Average": 9.5, "Mechanic": 4},
            {"Name": "Fortnite", "Rating Average": 9.0, "Mechanic": 2},
            {"Name": "Apex Legends", "Rating Average": 8.5, "Mechanic": 1},
            {"Name": "Minecraft", "Rating Average": 7.0, "Mechanic": 3}
        ][:200]#max tot 200, erbij gedaan omdat we in t echte tot max 200 doen, ook al is het hier maar top 4 want geen zin om meer toe te voegen in de tabel (ben lui)
        
        result = self.analyser.get_top_200_list(sort_by="Rating Average", ascending=False)
        self.assertEqual(result, expected_result)
        #Oproepen van het resultaat en kijken of het overeenkomt via de assertEqual

if __name__ == "__main__":
    unittest.main()