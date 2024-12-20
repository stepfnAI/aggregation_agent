# Data Aggregation Advisor

An AI-powered data aggregation tool that intelligently analyzes your dataset and provides smart suggestions for aggregation strategies, with interactive implementation capabilities.

## 🌟 Features

- **Intelligent Column Mapping:** Automatically identifies customer ID, date, and product ID columns
- **Smart Aggregation Analysis:** Generates contextual aggregation method suggestions based on data types and patterns
- **Interactive Method Selection:** Choose between AI-suggested methods or customize your own
- **Flexible Data Input:** Supports multiple file formats (CSV, Excel, JSON, Parquet)
- **Multi-method Aggregation:** Apply multiple aggregation methods per column
- **Data Export:** Download aggregated data in CSV format

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation
1. Clone the repository:

```bash
git clone https://github.com/stepfnAI/aggregation-agent.git
cd aggregation-agent
```

2. Create and activate a virtual environment:

```bash
python -m venv myenv      # or use python3 if you have multiple Python versions
source myenv/bin/activate # Linux/Mac
.\myenv\Scripts\activate  # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:

```bash
export OPENAI_API_KEY='your_openai_api_key'
```

### Running the Application

```bash
streamlit run app.py
```

### 🔄 Workflow
1. **Data Loading**
   - Upload your dataset (CSV, Excel, JSON, or Parquet)
   - Preview the loaded data
2. **Column Mapping**
   - AI identifies key columns:
     - Customer ID
     - Date
     - Product ID (optional)
   - Review and confirm or modify mappings
3. **Aggregation Analysis**
   - AI analyzes data patterns and types
   - Suggests appropriate aggregation methods
   - Interactive method selection per column
   - Support for multiple methods per column
4. **Post Processing**
   - View aggregated data
   - Download processed dataset
   - Review aggregation summary

### 🛠️ Architecture
The application follows a modular architecture with these key components:
- **SFNAggregationAgent:** Analyzes data and suggests aggregation methods
- **SFNColumnMappingAgent:** Identifies and maps key columns
- **SFNDataLoader:** Handles data import and validation
- **SFNStreamlitView:** Manages the user interface
- **SFNSessionManager:** Handles application state

🔒 Security
- Environment variables for sensitive data
- Input validation for all user data
- Secure data handling

📊 Aggregation Features
The tool supports various aggregation methods:
- Numeric: Sum, Mean, Median, Min, Max
- Text: Mode, Last Value, Unique Count
- Date: Min, Max
- Multiple methods per column
- Custom method combinations

📝 License
MIT License

🤝 Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
1. Fork the repository
2. Create your feature branch (git checkout -b feature/AmazingFeature)
3. Commit your changes (git commit -m 'Add some AmazingFeature')
4. Push to the branch (git push origin feature/AmazingFeature)
5. Open a Pull Request

📧 Contact
Email: puneet@stepfunction.ai