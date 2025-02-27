from typing import List, Dict, Any
import pandas as pd
from sfn_blueprint import SFNAgent, Task, SFNAIHandler, SFNPromptManager
from aggregation_agent.config.model_config import MODEL_CONFIG
import os
import json
import re

class SFNColumnMappingAgent(SFNAgent):
    def __init__(self, llm_provider: str):
        super().__init__(name="Column Mapping Advisor", role="Data Column Mapping Advisor")
        self.llm_provider = llm_provider
        self.ai_handler = SFNAIHandler()
        self.model_config = MODEL_CONFIG["column_mapping"]
        parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        prompt_config_path = os.path.join(parent_path, 'config', 'prompt_config.json')
        self.prompt_manager = SFNPromptManager(prompt_config_path)

    def _clean_json_string(self, json_string: str) -> Dict:
        """Clean and validate JSON string from LLM response"""
        try:
            # Find the first { and last }
            start_idx = json_string.find('{')
            end_idx = json_string.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
                print("No valid JSON structure found")
                return {}
            
            # Extract just the JSON part
            json_string = json_string[start_idx:end_idx + 1]
            
            # Remove ``` if present
            json_string = re.sub(r"^\`\`\`", "", json_string)
            json_string = re.sub(r"\`\`\`$", "", json_string)

            # Remove the word "json" if present at the start
            json_string = re.sub(r"^json\s*", "", json_string, flags=re.IGNORECASE)

            # Strip leading and trailing whitespace
            json_string = json_string.strip()

            # Parse the cleaned JSON
            cleaned_dict = json.loads(json_string)
            if not isinstance(cleaned_dict, dict):
                print(f"Invalid JSON structure: {cleaned_dict}")
                return {}
            
            return cleaned_dict
        except (ValueError, json.decoder.JSONDecodeError) as e:
            print(f"JSON parsing error: {e}")
            return {}

    def execute_task(self, task: Task) -> Dict:
        """Execute the column mapping task"""
        df = task.data.get('table')
        if df is None:
            return {'customer_id': None, 'date': None, 'product_id': None}

        # Prepare data for the prompt
        task_data = {
            'columns': list(df.columns),
            'sample_data': df.head(5).to_dict()
        }

        # Get prompts
        system_prompt, user_prompt = self.prompt_manager.get_prompt(
            'column_mapping',
            llm_provider=self.llm_provider,
            **task_data
        )

        configuration = {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": self.model_config["temperature"],
            "max_tokens": self.model_config["max_tokens"],
            "n": self.model_config["n"],
            "stop": self.model_config["stop"]
        }
        response, token_cost_summary = self.ai_handler.route_to(
            llm_provider=self.llm_provider, 
            configuration=configuration, 
            model=self.model_config['model']
        )

        try:
            suggestions = self._clean_json_string(response)
            return {
                'customer_id': suggestions.get('customer_id'),
                'date': suggestions.get('date'),
                'product_id': suggestions.get('product_id')
            }
        except Exception as e:
            print(f"Error in column mapping: {e}")
            return {'customer_id': None, 'date': None, 'product_id': None}
    
    def get_validation_params(self, response: List[str], validation_task: Task) -> dict:
        """
        Generate validation prompts for the column mapping suggestions response.
        
        :param response: List of generated column mapping suggestions to validate
        :param validation_task: Task object containing validation context
        :return: Dictionary containing validation prompts
        """
        # Extract necessary data from validation task
        df = validation_task.data.get('table')
        if df is None:
            return {'customer_id': None, 'date': None, 'product_id': None}

        # Prepare context for validation
        validation_context = {
            'columns': list(df.columns),
            'sample_data': df.head(5).to_dict(),
            'actual_output': '\n'.join(response),
        }
        
        # Get validation prompts from prompt config
        validation_prompts = self.prompt_manager.get_prompt(
            agent_type='column_mapping',
            llm_provider=self.llm_provider,
            prompt_type='validation',
            **validation_context
        )
        return validation_prompts