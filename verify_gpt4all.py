from gpt4all import GPT4All
import sys

def verify_model():
    print("Attempting to load GPT4All model...")
    try:
        # Use filename found in AppData and explicit path
        import os
        model_path = os.path.join(os.environ['LOCALAPPDATA'], 'nomic.ai', 'GPT4All')
        print(f"Loading model from: {model_path}")
        
        # Explicit filename found in found_models.txt
        model = GPT4All("qwen2-0_5b-instruct-q4_0.gguf", model_path=model_path, allow_download=False)
        print("Model loaded successfully.")
        
        print("Running test generation...")
        response = model.generate("Say 'Hello, World!'", temp=0.1)
        print(f"Response: {response}")
        
        if response:
            print("Verification PASSED.")
            return True
        else:
            print("Verification FAILED (No response).")
            return False
            
    except Exception as e:
        print(f"Verification FAILED (Exception): {e}")
        return False

if __name__ == "__main__":
    success = verify_model()
    sys.exit(0 if success else 1)
