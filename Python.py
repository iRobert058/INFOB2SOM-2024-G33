import pandas as pd
import google.generativeai as genai

class BoardGameMechanicsAnalyser:
    def __init__(self, dataset_path: str, api_key: str):
        self.dataset_path = dataset_path
        self.api_key = api_key
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def load_dataset_clean(self, sep=";"):
        try:
            self.dataset = pd.read_csv(self.dataset_path, sep=sep)
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.dataset_path}")
        
        required_columns = ['Name', 'Year Published', 'Mechanics']
        if not all(col in self.dataset.columns for col in required_columns):
            raise ValueError("Dataset is missing required columns")
        
        self.cleaned_dataset = self.dataset.dropna(subset=required_columns)
        return self.cleaned_dataset
    
    def verify_mechanics_with_genai(self, game_names: list):
        # Ensure the dataset has been cleaned and loaded
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        results = []
        
        for game_name in game_names:
            # Filter to find the specific game by name
            game_row = self.cleaned_dataset[self.cleaned_dataset['Name'] == game_name]
            
            # Ensure the game exists in the dataset
            if game_row.empty:
                results.append({
                    "Game": game_name,
                    "Error": f"Game '{game_name}' not found in the dataset."
                })
                continue
            
            # Extract game information safely
            mechanics = game_row['Mechanics'].values[0]
            mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
            
            # Generate the prompt using generative AI
            prompt = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Could you tell me which of these mechanics actually apply to the game? Do not add any text formatting. Please respond with a list of applicable mechanics and a list of those that do not apply. Please give a total amount of mechanics that apply to the game, and a total amount that dont apply ending the prompt."
            
            prompt_relatable = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."

            response = self.model.generate_content(prompt)
            response_relatable = self.model.generate_content(prompt_relatable)

            # Count the number of mechanics by counting the number of commas and adding 1
            number_of_mechanics = mechanics.count(",") + 1

            # Convert the relatable response into a string
            response_relatable_text = response_relatable.text.strip()

            try:
                # Calculate accuracy
                accuracy = int(response_relatable_text) / number_of_mechanics
            except ValueError:
                accuracy = "Error calculating accuracy"

            # Collect results for the current game
            results.append({
                "Game": game_name,
                "Applicable Mechanics Response": response.text,
                "Accuracy": accuracy
            })
        
        # Output the results
        for result in results:
            print(result)
        return results

# Example usage
analyser = BoardGameMechanicsAnalyser('dataset.csv', 'AIzaSyDZ3sSK2rXGWJSc-h8qZF3C2GNaiziA-do')
analyser.load_dataset_clean()
analyser.verify_mechanics_with_genai(['Gloomhaven', 'Catan', 'Pandemic'])