import pandas as pd
import google.generativeai as genai
import time

class BoardGameMechanicsAnalyser:
    def __init__(self, dataset_path: str, api_key: str):
        self.dataset_path = dataset_path
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # Load and clean the dataset
    def load_dataset_clean(self, sep=";"):
        try:
            self.dataset = pd.read_csv(self.dataset_path, sep=sep)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.dataset_path}")
        
        required_columns = ['Name', 'Year Published', 'Mechanics']
        if not all(col in self.dataset.columns for col in required_columns):
            raise ValueError("Dataset is missing required columns")
        
        # Clean the data
        self.cleaned_dataset = self.dataset.dropna(subset=required_columns)
        self.cleaned_dataset = self.cleaned_dataset[self.cleaned_dataset['Year Published'] != 0]

        return self.cleaned_dataset

    # Verify mechanics using GenAI
    def verify_mechanics_with_genai(self, game_name: str):
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        game_row = self.cleaned_dataset[self.cleaned_dataset['Name'] == game_name]
        if game_row.empty:
            raise ValueError(f"Game '{game_name}' not found in the dataset.")
        
        mechanics = game_row['Mechanics'].values[0]
        mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
        
        prompt = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."
        response = self.model.generate_content(prompt)
        
        number_of_mechanics = mechanics.count(",") + 1
        accuracy = int(response.text.strip()) / number_of_mechanics

        print(f"AI response for {game_name}: {response.text.strip()}")
        print(f"Accuracy of mechanics validation for {game_name}: {accuracy}")
        return accuracy

    # Retrieve the top 200 games sorted by a column
    def get_top_200_list(self, sort_by: str = "Rating Average", ascending: bool = False):
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        if sort_by not in self.cleaned_dataset.columns:
            raise ValueError(f"Column '{sort_by}' not found in the dataset.")
        
        top_200_list = (
            self.cleaned_dataset.sort_values(by=sort_by, ascending=ascending)
            .head(200)
            .to_dict(orient='records')
        )
        return top_200_list

    # Calculate total applicable mechanics
    def calculate_average_rating(self, game_name: str):
        game_row = self.cleaned_dataset[self.cleaned_dataset['Name'] == game_name]
        if game_row.empty:
            raise ValueError(f"Game '{game_name}' not found in the dataset.")
        
        mechanics = game_row['Mechanics'].values[0]
        mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
        
        prompt_relatable_top200 = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."
        response_top200 = self.model.generate_content(prompt_relatable_top200)

        return int(response_top200.text.strip())

# Example usage
if __name__ == "__main__":
    # Initialize the analyser with a dataset path and API key
    analyser = BoardGameMechanicsAnalyser('dataset.csv', 'AIzaSyDZ3sSK2rXGWJSc-h8qZF3C2GNaiziA-do')
    
    # Load and clean the dataset
    analyser.load_dataset_clean()

    # Example: Verify mechanics for a single game
    analyser.verify_mechanics_with_genai('Gloomhaven')

    # Example: Process top 200 games
    top_200_games = analyser.get_top_200_list(sort_by='Rating Average', ascending=False)
    total_applicable_mechanics = 0

    for game in top_200_games:
        try:
            result = analyser.calculate_average_rating(game['Name'])
            total_applicable_mechanics += result
            time.sleep(4)  # Avoid rate-limiting
        except ValueError:
            raise ValueError(f"Error processing game '{game['Name']}'")



    print(f"Total applicable mechanics for top 200 games: {total_applicable_mechanics}")