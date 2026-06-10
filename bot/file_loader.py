from fileinput import filename

def load_instructions_file(filename:str, default:str="") -> str:
    try:
        # attempt to opent the file in read mode with UTF-8 encoding
        with open(filename, 'r', encoding='utf-8') as file:
            # read the entire content of the file
            return file.read()
    except FileNotFoundError:
            # log a warning if the file is not found
            print(f"Warning: File '{filename}' not found. Using default instructions.")
    except Exception as e:
            # log a warning if there's an error reading the file
            print(f"Error: Error reading file '{filename}': {e}. Using default instructions.")     

    return default