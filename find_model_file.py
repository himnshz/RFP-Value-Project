import os

def list_appdata_models():
    # Construct path to GPT4All AppData
    appdata = os.environ.get('LOCALAPPDATA')
    path = os.path.join(appdata, 'nomic.ai', 'GPT4All')
    
    output_file = "found_models.txt"
    
    with open(output_file, "w") as f:
        f.write(f"Checking directory: {path}\n")
        try:
            if os.path.exists(path):
                files = os.listdir(path)
                f.write("Files found:\n")
                for file in files:
                    f.write(f" - {file}\n")
            else:
                f.write("Directory does not exist.\n")
        except Exception as e:
            f.write(f"Error: {e}\n")
    
    print(f"List saved to {output_file}")

if __name__ == "__main__":
    list_appdata_models()
