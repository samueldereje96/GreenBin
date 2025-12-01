# GreenBin

**GreenBin** is a smart waste management system designed to optimize urban waste collection, monitor bin status in real-time, and quantify environmental impact. It serves as a digital twin for waste management infrastructure, enabling data-driven decisions.

## Key Features

*   **Real-time Dashboard**: Monitor bin fill levels, types, and locations on an interactive map.
*   **Smart Dispatch**: Process collection requests based on priority and proximity.
*   **Environmental Impact**: Track CO2 savings achieved through optimized routing using the Haversine algorithm.
*   **Undo/Redo**: Robust safety mechanism to revert accidental changes to bins or requests.
*   **Precise Geolocation**: Support for exact GPS coordinates for accurate mapping.

## Tech Stack

*   **Language**: Python 3.12+
*   **Frontend**: [Streamlit](https://streamlit.io/)
*   **Visualization**: Plotly Express
*   **Data Structures**: Custom implementations of Linked Lists, Stacks, and Queues.
*   **Storage**: JSON-based persistence.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/samueldereje96/greenbin.git
    cd greenbin
    ```

2.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv green
    source green/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install streamlit pandas plotly
    ```

## Usage

Run the application using Streamlit:

```bash
streamlit run app.py
```

The dashboard will open automatically in your browser at `http://localhost:8501`.

## Documentation

For detailed technical information, including system architecture, data structure analysis, and UML diagrams, please refer to:

*   **[Technical Documentation (PDF/LaTeX)](documentation.tex)**: Comprehensive system report.
*   **[System Design (UML)](design.md)**: Class and Sequence diagrams.

## Project Structure

```
GreenBin/
├── app.py                  # Main entry point
├── data/                   # JSON data storage
├── data_structures/        # Custom DSA implementations (LinkedList, Stack, Queue)
├── models/                 # Data models
├── services/               # Business logic services
├── views/                  # Streamlit UI pages
└── utils/                  # Helper functions
```

---
*Built for the Advanced Agentic Coding project.*
