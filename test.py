import json
import os

my_dict = {'name': 'John', 'age': 30, 'city': 'New York'}

# Saves dictionary as a .json given a provided 'path'
def save_dictionary_as_json(dictionary, path):
    if isinstance(dictionary, dict):
        # Save the dictionary as a JSON file
        with open(path, 'w') as json_file:
            json.dump(dictionary, json_file, indent=4)
    else:
        return "Error: The variable is not a dictionary."

my_dict = {'name': 'John', 'age': 30, 'city': 'New York'}

# Loads .json file as a dictionary
def load_dictionary_from_json(json_path, specified_name=None):
    # Check if the JSON file exists
    if not os.path.exists(json_path):
        return "Error: JSON file does not exist."

    # Load the dictionary from the JSON file
    with open(json_path, 'r') as json_file:
        dictionary = json.load(json_file)

    # Determine the dictionary's name
    if specified_name is None:
        specified_name = os.path.splitext(os.path.basename(json_path))[0]

    # Assign the loaded dictionary to a global variable with the specified name
    globals()[specified_name] = dictionary
    return f"Dictionary loaded as '{specified_name}'"

# Save the specified 'dictionary' to 'json_path'
def re_save_dictionary(dictionary, json_path):
    # Ensure the provided object is a dictionary
    if not isinstance(dictionary, dict):
        return "Error: Provided object is not a dictionary."

    # Save the dictionary to the specified JSON file
    with open(json_path, 'w') as json_file:
        json.dump(dictionary, json_file, indent=4)

    return "Dictionary saved successfully."


load_dictionary_from_json(r"C:\Users\Jeremiah\Python\Projects\FUKITUP\harry_fck\media_info.json")
media_info['hello world'] = 'stuff to save'
re_save_dictionary(media_info, r"C:\Users\Jeremiah\Python\Projects\FUKITUP\harry_fck\media_info.json")