from sfn_blueprint import MODEL_CONFIG

MODEL_CONFIG["aggregation_advisor"] = {
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 1000,
    "n": 1,
    "stop": None
}

MODEL_CONFIG["column_mapping"] = {
    "model": "gpt-4",
    "temperature": 0.3,
    "max_tokens": 500,
    "n": 1,
    "stop": None
}