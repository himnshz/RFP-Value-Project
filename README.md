
# AI-Powered RFP Processing System (Neural Ninjas)

This project is an intelligent system designed to automatically analyze Request for Proposal (RFP) documents, match them with products from a catalog, and generate bids with explainable AI reasoning.

It consists of:
- **Backend**: A FastAPI-powered Python application using **GPT4All** (Local LLM) for intelligent processing.
- **Frontend**: A generic React + Vite web dashboard to visualize RFPs, Bids, and Analytics.

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Node.js & npm** (for the frontend)
3.  **GPT4All Model**: The system is configured to use the `Qwen2-0.5B-Instruct` model.
    - The backend expects the model file (`qwen2-0_5b-instruct-q4_0.gguf`) to be present in your local GPT4All directory (typically `%LOCALAPPDATA%\nomic.ai\GPT4All` on Windows).

---

## 🚀 Setup Instructions

### 1. Backend Setup (Python)

1.  **Navigate to the project root** (where `main.py` is located).

2.  **Create and activate a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Start the Backend Server**:
    ```bash
    python main.py
    ```
    - The API will be available at `http://localhost:8000`.
    - API Docs: `http://localhost:8000/docs`.

    > **Note**: On the first run, the system will initialize the SQLite database (`neural_ninjas.db`) and populate it with mock product data and sample RFPs.

### 2. Frontend Setup (React)

1.  **Open a new terminal** and navigate to the frontend directory:
    ```bash
    cd neural-ninjas-demo
    ```

2.  **Install Node Dependencies**:
    ```bash
    npm install
    ```

3.  **Start the Development Server**:
    ```bash
    npm run dev
    ```
    - The dashboard will typically run at `http://localhost:5173`.

---

## 📖 Usage

1.  **Dashboard**: Open the frontend URL (e.g., `http://localhost:5173`) in your browser.
2.  **View RFPs**: You should see a list of pre-populated RFPs.
3.  **Generate Bids**: Click on "Process" or "Generate Bid" for an RFP. The backend technical agents will:
    - Analyze the RFP text using the local LLM.
    - Match it against the product catalog.
    - Calculate pricing with dynamic discounts.
    - Generate a PDF bid proposal.
4.  **Upload PDF**: You can also upload a new RFP PDF via the dashboard to process custom requirements (requires `pypdf` which is included).

---

## 🛠 Troubleshooting

-   **LLM Not Loading / "Error loading local LLM"**:
    -   Ensure you have the `qwen2-0_5b-instruct-q4_0.gguf` model downloaded.
    -   Verify the path in `main.py` matches your local GPT4All model directory.
    -   If the model is missing, you can start the GPT4All desktop application to download it, or manually place the `.gguf` file in `%LOCALAPPDATA%\nomic.ai\GPT4All`.

-   **Backend/Frontend Connection Issues**:
    -   Ensure the backend is running on port `8000`.
    -   Check the browser console (F12) for CORS errors (CORS is enabled in `main.py` for all origins `*`).

-   **Missing Dependencies**:
    -   If you see `ModuleNotFoundError`, run `pip install -r requirements.txt` again.

---

## 📂 Project Structure

-   `main.py`: Main backend entry point, defines Agents (Sales, Technical, Pricing, Orchestrator) and API endpoints.
-   `neural-ninjas-demo/`: Frontend React application.
-   `neural_ninjas.db`: SQLite database (auto-created).
-   `found_models.txt`: (Generated) Logs of found LLM models.
-   `requirements.txt`: Python package dependencies.

