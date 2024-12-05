import pandas as pd
import google.generativeai as genai
import time
from collections import Counter
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

        # Calculate accuracy
        accuracy = int(response.text.strip()) / number_of_mechanics

        # Print results
        print(f"Ai Mechanic correspondense for the game {game_name}: {response.text.strip()} applicable mechanics")
        print(f"Accuracy of mechanics validation for {game_name}: {accuracy}")
        print("")

        return accuracy

    # Retrieve the top 200 games sorted by a column
    def get_top_200_list(self, sort_by: str = "Rating Average", ascending: bool = False):
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        if sort_by not in self.cleaned_dataset.columns:
            raise ValueError(f"Column '{sort_by}' not found in the dataset.")
        
        top_200_list = (
            self.cleaned_dataset.sort_values(by=sort_by, ascending=ascending)
            .head(5) # You can change the limit here for testing
            .to_dict(orient='records')
        )

        
        return top_200_list

    #Ask GenAI to interpet the total applicable mechanics for the top 200 games and return the total
    def calculate_total_applicable_mechanics(self, top_200_list):
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")

        total_applicable_mechanics = 0

        for game in top_200_list:
            try:
                game_name = game['Name']
                mechanics = game['Mechanics']
                mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
                
                prompt = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."
                response = self.model.generate_content(prompt)
                applicable_mechanics = int(response.text.strip())  # Convert response to an integer
                total_applicable_mechanics += applicable_mechanics
                
                print(f"Processed {game_name}: found {applicable_mechanics} applicable mechanics")
                time.sleep(4)  # Avoid hitting API rate limits
            except Exception as Error:
                print(f"Error processing game '{game['Name']}': {Error}")

        # Calculate ground thruth average top 200 applicable mechanics
        total_length_top_200 = sum(len(key) for key in top_200_list)
        
        average_applicable_mechanics = total_applicable_mechanics / total_length_top_200

        # Print results
        print("\n")
        print(f"Ai found a total of applicable mechanics for top 200 games: {total_applicable_mechanics}")
        print(f"Ground truth applicable mechanics for top 200 games: {total_length_top_200}")
        print("\n")
        print(f"Average Ai correspondense with the ground truth: {average_applicable_mechanics*100} %")

        return average_applicable_mechanics
    

    def top_10_average_mechanics(self, top_200_list):
        if not hasattr(self, 'cleaned_dataset'):
            raise AttributeError("Dataset is not loaded or cleaned. Please call load_dataset_clean() first.")
        
        print("\nCalculating the top 10 and least 10 mechanics assigned by AI to the top 200 games...")

        mechanic_counter = Counter()
        all_mechanics = set()  # Track all mechanics mentioned in the dataset

        for game in top_200_list:
            try:
                game_name = game['Name']
                mechanics = game['Mechanics']
                
                # Parse mechanics into a standardized format
                all_mechanics.update(mechanics.split(","))
                mechanics_prompt = mechanics.replace(",", ", ").replace(" and ", ", ").replace(" or ", ", ")
                
                prompt = f"Verify the mechanics of the game '{game_name}'. The mechanics are {mechanics_prompt}. Please only give me the total amount that apply without any text formatting."
                response = self.model.generate_content(prompt)
                applicable_mechanics_count = int(response.text.strip())

                # Split mechanics and count those deemed applicable
                applicable_mechanics_list = mechanics.split(",")[:applicable_mechanics_count]
                mechanic_counter.update([mechanic.strip() for mechanic in applicable_mechanics_list])

                time.sleep(4)  # Avoid hitting API rate limits

            except Exception as error:
                print(f"Error processing game '{game['Name']}': {error}")
        
        # Identify the top 10 and least 10 mechanics
        print("\nTop ten mechanics AI consistently assigned:")
        top_ten_mechanics = mechanic_counter.most_common(10)
        for mechanic, count in top_ten_mechanics:
            print(f"{mechanic}: assigned {count} times")
        
        print("\nTop ten least assigned mechanics by AI:")
        least_ten_mechanics = mechanic_counter.most_common()[:-11:-1]
        for mechanic, count in least_ten_mechanics:
            print(f"{mechanic}: assigned {count} times")
        
        # Find mechanics never attributed by Gemini
        unassigned_mechanics = all_mechanics - set(mechanic_counter.keys())
        print("\nMechanics never attributed by AI:")
        for mechanic in sorted(unassigned_mechanics):
            print(mechanic)
            
        return top_ten_mechanics, least_ten_mechanics, unassigned_mechanics
    

# Example usage
if __name__ == "__main__":
    # Initialize the analyser with a dataset path and API key
    analyser = BoardGameMechanicsAnalyser('dataset.csv', 'AIzaSyDZ3sSK2rXGWJSc-h8qZF3C2GNaiziA-do')
    
    # Load and clean the dataset
    analyser.load_dataset_clean()

    # Example: Verify mechanics for a single game
    analyser.verify_mechanics_with_genai('Gloomhaven')

    # Example: Process top 200 games
    top_200_list = analyser.get_top_200_list()

    # Calculate the total applicable mechanics
    analyser.calculate_total_applicable_mechanics(top_200_list)

    analyser.top_10_average_mechanics(top_200_list)