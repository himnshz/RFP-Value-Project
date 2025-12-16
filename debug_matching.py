from main import LLMService, Product
import traceback

def debug_matching():
    print("Initializing LLMService...")
    try:
        llm = LLMService()
    except Exception as e:
        print(f"Failed to init LLM: {e}")
        return

    products = [
        Product("PT-001", "Premium Exterior Gloss Paint", "Water-resistant", 45.99, 5000),
        Product("PT-002", "Industrial Anti-Corrosion Coating", "Rust-proof", 89.50, 3000)
    ]
    
    rfp_content = "Accredited painting required. Need 500L exterior gloss."
    
    print("Testing match_products...")
    try:
        matches = llm.match_products(rfp_content, products)
        print(f"Matches: {matches}")
    except Exception as e:
        print("Exception during matching:")
        traceback.print_exc()

if __name__ == "__main__":
    debug_matching()
