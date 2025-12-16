from gpt4all import GPT4All
import json

def list_models():
    models = GPT4All.list_models()
    print(json.dumps(models, indent=2))
    
    # Filter for Qwen
    print("\n--- Qwen Models ---")
    for m in models:
        if 'qwen' in m.get('name', '').lower() or 'qwen' in m.get('filename', '').lower():
            print(f"Name: {m.get('name')}, Filename: {m.get('filename')}")

if __name__ == "__main__":
    list_models()
