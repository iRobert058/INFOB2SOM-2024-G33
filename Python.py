import pandas as pd
import google.generativeai as genai

class BoardGameMechanicsAnalyser:
    def __init__(self, dataset_path: str, api_key: str):
        self.dataset_path = dataset_path
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    # Load the dataset
    def load_dataset_clean(self, sep=";"):
        try:
            self.dataset = pd.read_csv(self.dataset_path, sep=sep)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.dataset_path}")
        
        required_columns = ['Name', 'Year Published', 'Mechanics']
        if not all(col in self.dataset.columns for col in required_columns):
            raise ValueError("Dataset is missing required columns")
        
        #clean the data
        self.cleaned_dataset = self.dataset.dropna(subset=required_columns)
        self.cleaned_dataset = self.cleaned_dataset[self.cleaned_dataset['Year Published'] != 0]

        return self.cleaned_dataset
    
    def verify_mechanics_with_genai(self, game_name: str):
        # Ensure the dataset has been cleaned and loaded
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        # Filter to find the specific game by name
        game_row = self.cleaned_dataset[self.cleaned_dataset['Name'] == game_name]
        
        # Ensure the game exists in the dataset
        if game_row.empty:
            raise ValueError(f"Game '{game_name}' not found in the dataset.")
        
        # Extract game information safely
        mechanics = game_row['Mechanics'].values[0]
        mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
        
        # Generate the prompt using generative AI
        prompt = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Could you tell me which of these mechanics actually apply to the game? Do not add any text formatting. Please respond with a list of applicable mechanics and a list of those that do not apply. Please give a total amount of mechanics that apply to the game, and a total amount that dont apply ending the prompt."
        
        prompt_relatable = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."

        response = self.model.generate_content(prompt)
        response_relatable = self.model.generate_content(prompt_relatable)

        #count the number of mechanics by counting the number of commas and adding 1
        number_of_mechanics = mechanics.count(",") + 1

        #calculate accuracy by dividing the number of mechanics that the AI got right (and converting it into an int) by the total number of mechanics
        accuracy = (int(response_relatable.text)) / number_of_mechanics

        # Output the response
        print(response.text)
        print(f"The accuracy of the GenAi with the ground truth is {accuracy}")
        return
    
    def get_top_200_list(self, sort_by: str ="Rating Average", ascending: bool = False):
        # Retrieves the top 200 board games from the dataset based on the specified column.
        # Ensure the dataset has been cleaned and loaded

        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        if sort_by not in self.cleaned_dataset.columns:
            raise ValueError(f"Column '{sort_by}' not found in the dataset.")
        
        # Sort the dataset and get the top 200 rows
        top_200_games = self.cleaned_dataset.sort_values(by=sort_by, ascending=ascending).head(200)

        return top_200_games

# Example usage
analyser = BoardGameMechanicsAnalyser('dataset.csv', 'AIzaSyDZ3sSK2rXGWJSc-h8qZF3C2GNaiziA-do')
analyser.load_dataset_clean()
analyser.verify_mechanics_with_genai('Gloomhaven')
top_200_games = analyser.get_top_200_list(sort_by='Rating Average', ascending=False)

print(top_200_games[['Name', 'Rating Average', 'Year Published']])
    
