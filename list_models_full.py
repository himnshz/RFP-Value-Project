from gpt4all import GPT4All
import json

def list_models():
    models = GPT4All.list_models()
    with open("model_list.json", "w") as f:
        json.dump(models, f, indent=2)
    print("Model list saved to model_list.json")
    
    # Proactive search
    print("Searching for Qwen...")
    for m in models:
        name = m.get('name', '').lower()
        filename = m.get('filename', '').lower()
        if 'qwen' in name or 'qwen' in filename:
            print(f"Match: {m.get('name')} -> {m.get('filename')}")

if __name__ == "__main__":
    list_models()
