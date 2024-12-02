import pandas as pd

class BoardGameMechanicsAnalyser:
    def __init__(self, dataset_path: str, api_key: str):
        self.dataset_path = dataset_path
        self.api_key = api_key

    def load_dataset_clean(self):
        try:
            self.dataset = pd.read_csv(self.dataset_path)
        except FileNotFoundError:
            raise FileNotFoundError("File not found")
        
        required_columns = ['Name', 'Year Published', 'Mechanics']
        if not all(col in self.dataset.columns for col in required_columns):
            raise ValueError("Dataset is missing required columns")
        
        cleaned_dataset = self.dataset.dropna(subset=required_columns)
        return cleaned_dataset

analyser = BoardGameMechanicsAnalyser("dataset.csv", "AIzaSyDZ3sSK2rXGWJSc-h8qZF3C2GNaiziA-do")
print(analyser.load_dataset_clean())