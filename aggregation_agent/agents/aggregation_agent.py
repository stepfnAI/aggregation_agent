from typing import List, Dict, Union
import pandas as pd
from sfn_blueprint import SFNAgent, Task, SFNAIHandler, SFNPromptManager
from aggregation_agent.config.model_config import MODEL_CONFIG
import os
import json
import re

class SFNAggregationAgent(SFNAgent):
    def __init__(self, llm_provider: str):
        super().__init__(name="Aggregation Advisor", role="Data Aggregation Advisor")
        self.llm_provider = llm_provider
        self.ai_handler = SFNAIHandler()
        self.model_config = MODEL_CONFIG["aggregation_suggestions"]
        parent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
        prompt_config_path = os.path.join(parent_path, 'config', 'prompt_config.json')
        self.prompt_manager = SFNPromptManager(prompt_config_path)

    def execute_task(self, task: Task) -> Union[Dict, bool]:
        """Main entry point for the agent's task execution"""
        df = task.data.get('table')
        mapping_columns = task.data.get('mapping_columns', {})

        
        # First check if aggregation is needed
        needs_aggregation = self._check_aggregation_needed(df, mapping_columns)
        
        if not needs_aggregation:
            # Return a special response that indicates no aggregation needed
            return {
                "__no_aggregation_needed__": True,
                "__message__": "No aggregation needed for this dataset as there are no duplicate rows after grouping."
            }
        
        # If aggregation is needed, get suggestions with explanations
        try:
            result = self._generate_aggregation_suggestions(df, mapping_columns)
            return result
        except Exception as e:
            raise

    def _clean_json_string(self, json_string: str) -> Dict:
        """Clean and validate JSON string from LLM response"""
        try:
            # Find the first { and last }
            start_idx = json_string.find('{')
            end_idx = json_string.rfind('}')
            
            if start_idx == -1 or end_idx == -1:
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
                return {}
            
            return cleaned_dict
        except (ValueError, json.decoder.JSONDecodeError) as e:
            return {}

    def _check_aggregation_needed(self, df: pd.DataFrame, mapping_columns: Dict) -> bool:
        """Check if aggregation is needed by checking for duplicate rows after grouping"""
        groupby_cols = []
        
        # Add customer_id and date columns
        if mapping_columns.get('customer_id'):
            groupby_cols.append(mapping_columns['customer_id'])
        if mapping_columns.get('date'):
            groupby_cols.append(mapping_columns['date'])
        
        # Add product_id if present
        if mapping_columns.get('product_id'):
            groupby_cols.append(mapping_columns['product_id'])
            
        if not groupby_cols:
            return False
            
        grouped = df.groupby(groupby_cols).size().reset_index(name='count')
        result = (grouped['count'] > 1).any()
        return result

    def _generate_aggregation_suggestions(self, df: pd.DataFrame, mapping_columns: Dict) -> Dict:
        """Generate detailed aggregation suggestions with explanations"""
        
        # Prepare data type dictionary
        feature_dtype_dict = df.dtypes.astype(str).to_dict()
        
        # Prepare statistical summary for numeric columns
        df_describe_dict = df.describe().to_dict()
        
        # Prepare sample data
        sample_data_dict = df.head(5).to_dict()
        
        # Basic column descriptions (can be enhanced)
        column_text_describe_dict = {
            col: f"Column containing {dtype} type data" 
            for col, dtype in feature_dtype_dict.items()
        }
        
        # Remove groupby columns from consideration
        groupby_cols = [v for k, v in mapping_columns.items() if v is not None]
        
        for col in groupby_cols:
            if col in feature_dtype_dict:
                del feature_dtype_dict[col]
            if col in df_describe_dict:
                del df_describe_dict[col]
            if col in sample_data_dict:
                del sample_data_dict[col]
            if col in column_text_describe_dict:
                del column_text_describe_dict[col]


        # Prepare groupby message
        groupby_message = "Aggregation will be on the following fields:\n"
        
        # Add available fields to the message
        if mapping_columns.get('customer_id'):
            groupby_message += f"- {mapping_columns['customer_id']}\n"
        
        if mapping_columns.get('date'):
            groupby_message += f"- {mapping_columns['date']}\n"
        
        if mapping_columns.get('product_id'):
            groupby_message += f"- {mapping_columns['product_id']}\n"
            
        # If no fields were added, provide a default message
        if groupby_message == "Aggregation will be on the following fields:\n":
            groupby_message = "Aggregation will be performed on available groupby columns"


        task_data = {
            'feature_dtype_dict': feature_dtype_dict,
            'df_describe_dict': df_describe_dict,
            'sample_data_dict': sample_data_dict,
            'column_text_describe_dict': column_text_describe_dict,
            'groupby_message': groupby_message,
            'frequency': 'daily'  # This could be made configurable
        }

        system_prompt, user_prompt = self.prompt_manager.get_prompt(
            'aggregation_suggestions',
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
            cleaned_json = self._clean_json_string(response)
            return cleaned_json
        except Exception as e:
            return {}
        
    def get_validation_params(self, response: Union[Dict, List[str]], validation_task: Task) -> dict:
        """
        Generate validation prompts for the aggregation suggestions response.
        
        :param response: Either a dict of suggestions or a list of strings to validate
        :param validation_task: Task object containing validation context
        :return: Dictionary containing validation prompts
        """
        
        # Check for special no-aggregation-needed response
        if isinstance(response, dict) and response.get("__no_aggregation_needed__"):
            return {
                "system_prompt": "You are a simple validator that checks if aggregation is needed.",
                "user_prompt": "The dataset has no duplicate rows after grouping, so no aggregation is needed.\nRespond with TRUE"
            }
            
        # Extract necessary data from validation task
        df = validation_task.data.get('table')
        # Prepare data type dictionary
        feature_dtype_dict = df.dtypes.astype(str).to_dict()
        
        # Prepare sample data
        sample_data_dict = df.head(5).to_dict()
        
        # Basic column descriptions
        column_text_describe_dict = {
            col: f"Column containing {dtype} type data" 
            for col, dtype in feature_dtype_dict.items()
        }

        # Convert response to list if it's a dict
        response_list = list(response.keys()) if isinstance(response, dict) else response

        # Prepare context for validation
        validation_context = {
            'feature_dtype_dict': feature_dtype_dict,
            'sample_data_dict': sample_data_dict,
            'column_text_describe_dict': column_text_describe_dict,
            'actual_output': '\n'.join(response_list)
        }
        
        # Get validation prompts from prompt config
        validation_prompts = self.prompt_manager.get_prompt(
            agent_type='aggregation_suggestions',
            llm_provider=self.llm_provider,
            prompt_type='validation',
            **validation_context
        )
        return validation_prompts