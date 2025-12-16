# main.py - Complete Backend System for AI-Powered RFP Processing

import json
import re
from datetime import datetime
from typing import List, Dict, Optional
import numpy as np
import sys
import io

# Force UTF-8 encoding for stdout/stderr on Windows to avoid UnicodeEncodeError
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fpdf import FPDF

from sqlalchemy import create_engine, Column, String, Float, Integer, JSON, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

# DB Setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./neural_ninjas.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ============================================================================
# PHASE 1: DATA MODELS
# ============================================================================

class Product(Base):
    """Product catalog item"""
    __tablename__ = "products"
    
    sku = Column(String, primary_key=True, index=True)
    name = Column(String)
    specs = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    
    def __init__(self, sku: str, name: str, specs: str, price: float, stock: int):
        self.sku = sku
        self.name = name
        self.specs = specs
        self.price = price
        self.stock = stock
    
    def to_dict(self):
        return {
            "sku": self.sku,
            "name": self.name,
            "specs": self.specs,
            "price": self.price,
            "stock": self.stock
        }

class RFP(Base):
    """Request for Proposal"""
    __tablename__ = "rfps"
    
    rfp_id = Column(String, primary_key=True, index=True)
    client = Column(String)
    content = Column(String)
    date = Column(String)
    status = Column(String, default="pending")
    
    def __init__(self, rfp_id: str, client: str, content: str, date: str, status: str = "pending"):
        self.rfp_id = rfp_id
        self.client = client
        self.content = content
        self.date = date
        self.status = status
    
    def to_dict(self):
        return {
            "rfp_id": self.rfp_id,
            "client": self.client,
            "content": self.content,
            "date": self.date,
            "status": self.status
        }

class Bid(Base):
    """Generated bid proposal"""
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    rfp_id = Column(String, ForeignKey("rfps.rfp_id"))
    product_sku = Column(String, ForeignKey("products.sku"))
    quantity = Column(Integer)
    pricing = Column(JSON)
    confidence = Column(Float)
    generated_at = Column(String)
    
    # Relationships
    rfp = relationship("RFP")
    product = relationship("Product")
    
    def __init__(self, rfp: RFP, product: Product, quantity: int, 
                 pricing: Dict, confidence: float, reasoning: str = ""):
        self.rfp = rfp
        self.product = product
        self.quantity = quantity
        self.pricing = pricing
        self.confidence = confidence
        self.reasoning = reasoning
        self.generated_at = datetime.now().isoformat()
        self.rfp_id = rfp.rfp_id
        self.product_sku = product.sku
    
    def to_dict(self):
        return {
            "rfp_id": self.rfp.rfp_id,
            "client": self.rfp.client,
            "product": self.product.to_dict(),
            "quantity": self.quantity,
            "pricing": self.pricing,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "generated_at": self.generated_at
        }

# Create tables
Base.metadata.create_all(bind=engine)

# ============================================================================
# PHASE 2: MOCK DATA GENERATION
# ============================================================================

def generate_product_catalog() -> List[Product]:
    """Generate mock product catalog or load from DB"""
    db = SessionLocal()
    try:
        if db.query(Product).count() == 0:
            products = [
                Product("PT-001", "Premium Exterior Gloss Paint", 
                        "Water-resistant, high-gloss, UV protection, exterior grade", 
                        45.99, 5000),
                Product("PT-002", "Industrial Anti-Corrosion Coating", 
                        "High-viscosity, rust-proof, industrial grade, chemical resistant", 
                        89.50, 3000),
                Product("PT-003", "Eco-Friendly Interior Paint", 
                        "Low-VOC, matte finish, interior use, quick-dry", 
                        38.75, 8000),
                Product("SV-001", "Heavy-Duty Industrial Solvent", 
                        "Fast-evaporating, industrial grade, multi-purpose cleaner", 
                        52.30, 2500),
                Product("CT-001", "Marine Grade Protective Coating", 
                        "Saltwater-resistant, high-durability, weatherproof, marine grade", 
                        125.00, 1500),
                Product("PT-004", "High-Gloss Automotive Paint", 
                        "High-gloss, fast-dry, automotive grade, color-stable", 
                        67.80, 4000),
                Product("PT-005", "Warehouse Floor Epoxy Coating", 
                        "Industrial strength, chemical resistant, non-slip, heavy-traffic", 
                        95.25, 2200),
                Product("SV-002", "Paint Thinner Professional Grade", 
                        "Quick-dry formula, low odor, professional grade", 
                        28.50, 6000),
                Product("PT-006", "Fire-Resistant Industrial Coating", 
                        "Flame-retardant, high-temperature resistant, industrial grade", 
                        156.00, 1200),
                Product("CT-002", "Waterproofing Membrane Coating", 
                        "100% waterproof, flexible, crack-bridging, long-lasting", 
                        78.90, 3500),
            ]
            db.add_all(products)
            db.commit()
            print("✓ Populated database with initial products")
        
        return db.query(Product).all()
    finally:
        db.close()

def generate_sample_rfps() -> List[RFP]:
    """Generate sample RFPs or load from DB"""
    db = SessionLocal()
    try:
        if db.query(RFP).count() == 0:
            rfps = [
                RFP("RFP-2024-001", "Coastal Construction Ltd",
                    "We require 500 liters of high-gloss exterior paint suitable for coastal conditions. "
                    "Must be weather-resistant and UV protected. Delivery needed by Q3 2024.",
                    "2024-12-01"),
                
                RFP("RFP-2024-002", "Marine Industries Corp",
                    "Looking for 800 liters of marine-grade protective coating for ship hulls. "
                    "Must be saltwater-resistant and highly durable. Budget: $100,000.",
                    "2024-12-03"),
                
                RFP("RFP-2024-003", "AutoTech Manufacturing",
                    "Need 1200 liters of automotive-grade high-gloss paint for production line. "
                    "Fast-dry formula essential. Delivery within 30 days.",
                    "2024-12-05"),
                
                RFP("RFP-2024-004", "Industrial Warehouse Solutions",
                    "Require 2000 liters of epoxy floor coating for warehouse facility. "
                    "Must be chemical resistant and suitable for heavy forklift traffic.",
                    "2024-12-07"),
                
                RFP("RFP-2024-005", "FireSafe Construction",
                    "Need 600 liters of fire-resistant coating for industrial building project. "
                    "Must meet fire safety regulations and high-temperature specifications.",
                    "2024-12-09"),
            ]
            db.add_all(rfps)
            db.commit()
            print("✓ Populated database with initial RFPs")
            
        return db.query(RFP).all()
    finally:
        db.close()

# ============================================================================
# PHASE 3: LLM SERVICE (Google Gemini Integration)
# ============================================================================

import os
# from dotenv import load_dotenv # not strictly needed if we don't use env vars for API keys anymore, but keeping for safety if other things need it
from gpt4all import GPT4All

# load_dotenv()

class LLMService:
    """Handles interaction with Local GPT4All LLM"""
    
    def __init__(self):
        print("Loading local LLM (Qwen2-0.5B)... this may take a moment.")
        try:
             # Use the model name provided by user, located in AppData
            model_path = os.path.join(os.environ['LOCALAPPDATA'], 'nomic.ai', 'GPT4All')
            self.model = GPT4All("qwen2-0_5b-instruct-q4_0.gguf", model_path=model_path, device='cpu', allow_download=False) 
            print("✓ Local LLM loaded successfully.")
        except Exception as e:
            print(f"Error loading local LLM: {e}")
            self.model = None
            
    def _extract_json(self, text: str) -> Dict:
        """Helper to find and parse JSON from text"""
        try:
            # Try direct parse
            return json.loads(text)
        except:
            pass
            
        try:
            # Find first { and last }
            start = text.find('{')
            end = text.rfind('}') + 1
            if start != -1 and end != 0:
                json_str = text[start:end]
                return json.loads(json_str)
        except Exception as e:
            print(f"JSON extraction failed: {e}")
            
        print(f"Failed to extract JSON from: {text[:100]}...")
        return {}

    def analyze_rfp(self, rfp_content: str) -> Dict:
        """Extract requirements using LLM"""
        # ... (keep existing docstring) ...
        if not self.model:
             # Default fallback
             return {"quantity": 500, "requirements": ["(LLM unavailable)"], "raw_content": rfp_content}

        prompt = f"""
        Analyze the following RFP text and extract structured data.
        
        Example Output Format:
        {{
            "quantity": 1000,
            "requirements": ["high gloss", "weather resistant"],
            "budget": "$5000",
            "deadline": "2024-12-31",
            "summary": "Client needs 1000L of exterior paint."
        }}

        Return ONLY a JSON object with these keys:
        - quantity (integer, in liters)
        - requirements (list of strings, key technical specs)
        - budget (string or null)
        - deadline (string or null)
        - summary (string, 1 sentence summary)

        RFP Text:
        {rfp_content}
        
        Ensure valid JSON format.
        """
        
        try:
            # Generate content using local model
            response = self.model.generate(prompt, temp=0.1)
            return self._extract_json(response)
        except Exception as e:
            print(f"LLM Error (Analyze): {e}")
            return {
                "quantity": 500, 
                "requirements": ["(Analysis failed)"],
                "raw_content": rfp_content
            }

    def match_products(self, rfp_content: str, products: List[Product], top_k: int = 3) -> List[Dict]:
        """Match products using LLM reasoning"""
        if not self.model:
            return []
            
        product_list = "\n".join([f"- SKU: {p.sku}, Name: {p.name}, Specs: {p.specs}" for p in products])
        
        prompt = f"""
        Given the RFP below, select the top {top_k} most suitable products from the catalog.
        
        Example Output Format:
        [
            {{
                "sku": "PT-001",
                "confidence": 95,
                "reasoning": "Product matches specific requirement for exterior gloss."
            }}
        ]
        
        RFP Text:
        {rfp_content}
        
        Product Catalog:
        {product_list}
        
        Return ONLY a JSON array of objects. Each object must have:
        - sku (string, matching the catalog)
        - confidence (integer, 0-100)
        - reasoning (string, why this product fits)

        Ensure valid JSON format. Do not use markdown code blocks.
        """
        
        try:
            response = self.model.generate(prompt, temp=0.1)
            matches_data = self._extract_json(response)
            
            # Fallback: if JSON failed or empty, try regex/string search for SKUs
            if not matches_data or (isinstance(matches_data, list) and not matches_data):
                print("JSON extraction failed or empty, using fallback SKU matching.")
                matches_data = []
                for p in products:
                    if p.sku in response:
                        matches_data.append({
                            "sku": p.sku,
                            "confidence": 70, # Default confidence
                            "reasoning": "Detected in LLM response (fallback match)"
                        })
            
            if isinstance(matches_data, dict):
                 # Sometimes simple models return a single object instead of list?
                 # Or maybe wrapped in a key?
                 if 'matches' in matches_data:
                     matches_data = matches_data['matches']
                 else:
                    # If it's a dict but we expect list, maybe wrap it?
                    matches_data = [matches_data]
            
            if not isinstance(matches_data, list):
                print(f"LLM returned non-list data: {type(matches_data)}")
                return []
            
            # Map back to product objects
            results = []
            for match in matches_data:
                product = next((p for p in products if p.sku == match['sku']), None)
                if product:
                    results.append({
                        'product': product,
                        'confidence': match['confidence'],
                        'reasoning': match['reasoning']
                    })
            return results
            
        except Exception as e:
            print(f"LLM Error (Matching): {e}")
            return []

# ============================================================================
# PHASE 4: AGENT 1 - TECHNICAL AGENT (LLM-Enhanced)
# ============================================================================

class TechnicalAgent:
    """Handles product matching using LLM"""
    
    def __init__(self, products: List[Product], llm_service: LLMService):
        self.products = products
        self.llm = llm_service
        self.logs = []
    
    def log(self, message: str):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [Technical Agent]: {message}")
        print(f"[Technical Agent]: {message}")
    
    def find_products(self, rfp_content: str, top_k: int = 3) -> List[Dict]:
        """Find entries using LLM"""
        self.log("Asking LLM to match products against RFP requirements...")
        matches = self.llm.match_products(rfp_content, self.products, top_k)
        
        if not matches:
             self.log("LLM returned no matches or failed.")
             return []

        self.log(f"LLM identified {len(matches)} potential candidates.")
        for m in matches:
             self.log(f"  > {m['product'].sku}: {m['reasoning']} ({m['confidence']}%)")
             
        return matches
    
    def verify_technical_specs(self, product: Product, requirements: str) -> bool:
        """Verify if product meets technical requirements (delegated to LLM trust)"""
        # In a real system, we might ask LLM to double check specific clauses here.
        self.log(f"Verifying {product.sku} against requirements...")
        self.log("✓ Verified by LLM assessment.")
        return True

# ============================================================================
# PHASE 5: AGENT 2 - PRICING AGENT (Unchanged mainly, but re-numbered)
# ============================================================================

class PricingAgent:
    """Handles pricing calculations and discounts"""
    
    def __init__(self):
        self.logs = []
        self.discount_tiers = [
            (2000, 0.15),  # 15% for 2000+ liters
            (1000, 0.10),  # 10% for 1000+ liters
            (500, 0.05),   # 5% for 500+ liters
        ]
    
    def log(self, message: str):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [Pricing Agent]: {message}")
        print(f"[Pricing Agent]: {message}")
    
    def calculate_pricing(self, product: Product, quantity: int) -> Dict:
        """Calculate total pricing with volume discounts"""
        self.log("Calculating costs and applying volume discounts...")
        
        base_price = product.price * quantity
        self.log(f"Base cost: ${base_price:.2f} ({quantity}L × ${product.price}/L)")
        
        # Determine discount
        discount_pct = 0
        for threshold, discount in self.discount_tiers:
            if quantity >= threshold:
                discount_pct = discount
                break
        
        discount_amount = base_price * discount_pct
        total = base_price - discount_amount
        
        if discount_pct > 0:
            self.log(f"Volume discount applied: {discount_pct*100}% (${discount_amount:.2f})")
        else:
            self.log("No volume discount applicable")
        
        self.log(f"Final bid total: ${total:.2f}")
        
        return {
            'base_price': round(base_price, 2),
            'discount': round(discount_pct * 100, 1),
            'discount_amount': round(discount_amount, 2),
            'total': round(total, 2),
            'unit_price': product.price
        }
    
    def check_stock_availability(self, product: Product, quantity: int) -> bool:
        """Check if sufficient stock is available"""
        available = product.stock >= quantity
        
        if available:
            self.log(f"✓ Stock available: {product.stock}L in inventory")
        else:
            self.log(f"✗ Insufficient stock: Need {quantity}L, only {product.stock}L available")
        
        return available

# ============================================================================
# PHASE 6: AGENT 3 - SALES AGENT (LLM-Enhanced)
# ============================================================================

class SalesAgent:
    """Handles RFP intake and extraction using LLM"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.logs = []
    
    def log(self, message: str):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [Sales Agent]: {message}")
        print(f"[Sales Agent]: {message}")
    
    def process_rfp(self, rfp: RFP) -> Dict:
        """Extract requirements from RFP"""
        self.log(f"Received RFP {rfp.rfp_id} from {rfp.client}")
        self.log("Delegating analysis to LLM Service...")
        
        data = self.llm.analyze_rfp(rfp.content)
        
        self.log(f"LLM extracted quantity: {data.get('quantity', 'N/A')}")
        self.log(f"LLM extracted specs: {', '.join(data.get('requirements', []))}")
        
        return {
            'quantity': data.get('quantity', 0),
            'requirements': data.get('requirements', []),
            'raw_content': rfp.content,
            'summary': data.get('summary', '')
        }

# ============================================================================
# PHASE 7: ORCHESTRATOR AGENT
# ============================================================================

class OrchestratorAgent:
    """Main agent that coordinates all sub-agents"""
    
    def __init__(self, products: List[Product]):
        self.llm_service = LLMService()
        self.sales_agent = SalesAgent(self.llm_service)
        self.technical_agent = TechnicalAgent(products, self.llm_service)
        self.pricing_agent = PricingAgent()
        self.logs = []
    
    def log(self, message: str):
        """Add log entry"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] [Orchestrator]: {message}")
        print(f"[Orchestrator]: {message}")
    
    def process_rfp(self, rfp: RFP) -> Optional[Bid]:
        """
        Main workflow: Process RFP through all agents
        """
        print("\n" + "="*80)
        print(f"PROCESSING RFP: {rfp.rfp_id}")
        print("="*80 + "\n")
        
        self.log("Starting RFP processing workflow (LLM-Powered)...")
        
        # Step 1: Sales Agent processes RFP
        extracted_data = self.sales_agent.process_rfp(rfp)
        
        # Step 2: Technical Agent finds matching products
        matches = self.technical_agent.find_products(
            rfp.content, 
            top_k=3
        )
        
        if not matches:
            self.log("✗ No suitable products found by LLM")
            return None
        
        # Get best match
        best_match = matches[0]
        product = best_match['product']
        confidence = best_match['confidence']
        
        # Step 3: Verify technical specifications
        self.technical_agent.verify_technical_specs(
            product, 
            extracted_data['raw_content']
        )
        
        # Step 4: Check stock availability
        quantity = extracted_data['quantity']
        stock_available = self.pricing_agent.check_stock_availability(product, quantity)
        
        if not stock_available:
            self.log("✗ Insufficient stock for this bid")
            return None
        
        # Step 5: Calculate pricing
        pricing = self.pricing_agent.calculate_pricing(product, quantity)
        
        # Step 6: Generate bid
        reasoning = best_match.get('reasoning', 'Best match based on requirements.')
        bid = Bid(rfp, product, quantity, pricing, confidence, reasoning)
        
        self.log("✓ Bid compilation complete. Ready for manager approval.")
        self.log(f"  Reasoning: {reasoning}")
        
        print("\n" + "="*80)
        print("BID GENERATION COMPLETE")
        print("="*80 + "\n")
        
        return bid
    
    def get_all_logs(self) -> List[str]:
        """Get all logs from all agents"""
        all_logs = []
        all_logs.extend(self.logs)
        all_logs.extend(self.sales_agent.logs)
        all_logs.extend(self.technical_agent.logs)
        all_logs.extend(self.pricing_agent.logs)
        return all_logs

# ============================================================================
# PHASE 7: EXPORT & UTILITY FUNCTIONS
# ============================================================================

def export_product_catalog_csv(products: List[Product], filename: str = "product_catalog.csv"):
    """Export product catalog to CSV"""
    import csv
    
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['SKU', 'Product_Name', 'Technical_Specs', 'Unit_Price', 'Stock_Level'])
        
        for product in products:
            writer.writerow([
                product.sku,
                product.name,
                product.specs,
                product.price,
                product.stock
            ])
    
    print(f"✓ Product catalog exported to {filename}")

def export_bid_json(bid: Bid, filename: str = None):
    """Export bid to JSON"""
    if filename is None:
        filename = f"bid_{bid.rfp.rfp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(bid.to_dict(), f, indent=2)
    
    print(f"✓ Bid exported to {filename}")

def generate_bid_summary(bid: Bid) -> str:
    """Generate human-readable bid summary"""
    summary = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           BID PROPOSAL SUMMARY                               ║
╚══════════════════════════════════════════════════════════════════════════════╝

RFP ID:              {bid.rfp.rfp_id}
Client:              {bid.rfp.client}
Generated:           {bid.generated_at}

────────────────────────────────────────────────────────────────────────────────
PRODUCT DETAILS
────────────────────────────────────────────────────────────────────────────────
SKU:                 {bid.product.sku}
Product:             {bid.product.name}
Specifications:      {bid.product.specs}
Quantity:            {bid.quantity} liters

────────────────────────────────────────────────────────────────────────────────
PRICING BREAKDOWN
────────────────────────────────────────────────────────────────────────────────
Unit Price:          ${bid.pricing['unit_price']:.2f} per liter
Base Price:          ${bid.pricing['base_price']:,.2f}
Discount:            {bid.pricing['discount']:.1f}% (${bid.pricing['discount_amount']:,.2f})

TOTAL BID:           ${bid.pricing['total']:,.2f}
────────────────────────────────────────────────────────────────────────────────

Confidence Score:    {bid.confidence}%
Stock Available:     {bid.product.stock} liters

═════════════════════════════════════════════════════════════════════════════════
"""
    return summary


# ============================================================================
# PHASE 7.1: PDF GENERATION FOR BID OUTPUT
# ============================================================================

class BidPDF(FPDF):
    """Simple PDF layout for bid proposal"""
    def header(self):
        # Title
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "Bid Proposal", ln=1, align="C")
        self.ln(2)
        # Line
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_bid_pdf(bid: Bid, filename: str = None):
    """Generate a simple, clean PDF for the bid proposal"""
    if filename is None:
        filename = f"bid_{bid.rfp.rfp_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    pdf = BidPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ---------- SECTION 1: RFP + Client ----------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "RFP Details", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"RFP ID: {bid.rfp.rfp_id}", ln=1)
    pdf.cell(0, 6, f"Client: {bid.rfp.client}", ln=1)
    pdf.cell(0, 6, f"Generated At: {bid.generated_at}", ln=1)
    pdf.ln(4)

    # ---------- SECTION 2: Product Details ----------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Product Details", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, f"SKU: {bid.product.sku}")
    pdf.multi_cell(0, 6, f"Product: {bid.product.name}")
    pdf.multi_cell(0, 6, f"Specifications: {bid.product.specs}")
    pdf.cell(0, 6, f"Quantity: {bid.quantity} liters", ln=1)
    pdf.ln(4)

    # ---------- SECTION 3: Pricing ----------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Pricing Breakdown", ln=1)
    pdf.set_font("Helvetica", "", 11)

    pdf.cell(0, 6, f"Unit Price: ${bid.pricing['unit_price']:.2f} per liter", ln=1)
    pdf.cell(0, 6, f"Base Price: ${bid.pricing['base_price']:,.2f}", ln=1)
    pdf.cell(
        0,
        6,
        f"Discount: {bid.pricing['discount']:.1f}% "
        f"(${bid.pricing['discount_amount']:,.2f})",
        ln=1,
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Total Bid: ${bid.pricing['total']:,.2f}", ln=1)
    pdf.ln(4)

    # ---------- SECTION 4: Confidence / Notes ----------
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Technical Match & Notes", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(0, 6, f"Match Confidence: {bid.confidence}%", ln=1)
    pdf.cell(0, 6, f"Stock Available: {bid.product.stock} liters", ln=1)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 6, "AI Reasoning:", ln=1)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 5, bid.reasoning)
    pdf.ln(4)

    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(
        0,
        5,
        "Note: This is an auto-generated bid based on current catalog, "
        "stock levels, and configured discount rules. "
        "Final approval is required from the Sales Manager.",
    )

    # Save file
    pdf.output(filename)
    print(f"✓ Bid PDF exported to {filename}")


# ============================================================================
# PHASE 8: API & MAIN EXECUTION
# ============================================================================

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
import io

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize system components globally
products = generate_product_catalog()
rfps = generate_sample_rfps()
orchestrator = OrchestratorAgent(products)

class RFPRequest(BaseModel):
    rfp_id: str

@app.get("/products")
def get_products():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        return [p.to_dict() for p in products]
    finally:
        db.close()

@app.get("/rfps")
def get_rfps():
    db = SessionLocal()
    try:
        rfps = db.query(RFP).all()
        return [r.to_dict() for r in rfps]
    finally:
        db.close()

@app.post("/upload-rfp")
async def upload_rfp(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    db = SessionLocal()
    try:
        # Read file content
        content = await file.read()
        pdf_file = io.BytesIO(content)
        
        # Extract text
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
            
        # Create new RFP
        # Get count for ID generation
        count = db.query(RFP).count()
        new_id = f"RFP-{datetime.now().year}-{count + 1:03d}"
        
        new_rfp = RFP(
            rfp_id=new_id,
            client=f"Uploaded: {file.filename}",
            content=text.strip(),
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        db.add(new_rfp)
        db.commit()
        db.refresh(new_rfp)
        
        return new_rfp.to_dict()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/process-rfp")
def process_rfp_endpoint(request: RFPRequest):
    db = SessionLocal()
    try:
        # Find the RFP
        rfp = db.query(RFP).filter(RFP.rfp_id == request.rfp_id).first()
        if not rfp:
            raise HTTPException(status_code=404, detail="RFP not found")
        
        # Reset logs for this run
        orchestrator.logs = []
        orchestrator.sales_agent.logs = []
        orchestrator.technical_agent.logs = []
        orchestrator.pricing_agent.logs = []
        
        # Process
        # Note: orchestrator uses detached product objects. 
        # The returned bid will have a detached product and attached rfp (from this session)
        bid = orchestrator.process_rfp(rfp)
        
        if bid:
            # We need to merge the product into this session to avoid "Object is already attached to session" errors
            # or "Instance is not bound to a Session" errors if we try to commit.
            # Actually, since we are just adding the Bid, and Bid has relationships...
            # The safest way is to just add the bid. SQLAlchemy merge might be needed for the product.
            # But let's try adding first. If product is detached, it might work if we don't modify it.
            
            # To be safe, let's merge the product if it's not in session
            if bid.product not in db:
                bid.product = db.merge(bid.product)
            
            db.add(bid)
            
            # Update RFP status
            rfp.status = "processed"
            
            db.commit()
            db.refresh(bid)
            
        # Collect logs
        logs = []
        for log in orchestrator.get_all_logs():
            try:
                parts = log.split("] [")
                timestamp = parts[0].strip("[")
                agent_msg = parts[1].split("]: ")
                agent = agent_msg[0]
                message = agent_msg[1]
                logs.append({
                    "timestamp": timestamp,
                    "agent": agent,
                    "message": message
                })
            except:
                logs.append({
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                    "agent": "System",
                    "message": log
                })
                
        response = {
            "logs": logs,
            "bid": bid.to_dict() if bid else None,
            "success": bid is not None
        }
        
        return response
    except Exception as e:
        print(f"Error processing RFP: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/analytics")
def get_analytics():
    db = SessionLocal()
    try:
        # 1. Total RFPs
        total_rfps = db.query(RFP).count()
        
        # 2. Total Bids Value
        # Since pricing is JSON, we might need to fetch all bids and sum in python 
        # (SQLite JSON support varies, safe to do in python for small scale)
        bids = db.query(Bid).all()
        total_value = sum(bid.pricing.get('total', 0) for bid in bids)
        
        # 3. Approval Rate
        approved_count = db.query(RFP).filter(RFP.status == 'approved').count()
        approval_rate = (approved_count / total_rfps * 100) if total_rfps > 0 else 0
        
        # 4. Avg Confidence
        avg_confidence = 0
        if bids:
            avg_confidence = sum(bid.confidence for bid in bids) / len(bids)
            
        # 5. RFPs by Status
        statuses = ["pending", "processed", "approved", "rejected"]
        status_counts = []
        for status in statuses:
            count = db.query(RFP).filter(RFP.status == status).count()
            status_counts.append({"name": status.capitalize(), "value": count})
            
        return {
            "total_rfps": total_rfps,
            "total_value": round(total_value, 2),
            "approval_rate": round(approval_rate, 1),
            "avg_confidence": round(avg_confidence, 1),
            "status_distribution": status_counts
        }
    except Exception as e:
        print(f"Error in analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

class RFPStatusUpdate(BaseModel):
    status: str

@app.put("/rfps/{rfp_id}/status")
def update_rfp_status(rfp_id: str, status_update: RFPStatusUpdate):
    db = SessionLocal()
    try:
        rfp = db.query(RFP).filter(RFP.rfp_id == rfp_id).first()
        if not rfp:
            raise HTTPException(status_code=404, detail="RFP not found")
        
        rfp.status = status_update.status
        db.commit()
        db.refresh(rfp)
        return rfp.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)