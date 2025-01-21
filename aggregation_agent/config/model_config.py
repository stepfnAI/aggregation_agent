from sfn_blueprint import MODEL_CONFIG

DEFAULT_LLM_PROVIDER='openai'
DEFAULT_LLM_MODEL='gpt-4o-mini' 

MODEL_CONFIG["aggregation_suggestions"] = {
    "model": DEFAULT_LLM_MODEL,
    "temperature": 0.3,
    "max_tokens": 1000,
    "n": 1,
    "stop": None
}

MODEL_CONFIG["column_mapping"] = {
    "model": DEFAULT_LLM_MODEL,
    "temperature": 0.3,
    "max_tokens": 500,
    "n": 1,
    "stop": None
}