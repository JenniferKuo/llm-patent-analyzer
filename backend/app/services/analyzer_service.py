import requests
import os
from typing import Dict, List, Union, Literal
import json
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

class AnalyzerError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class InfringementAnalysis(BaseModel):
    product_name: str
    infringement_score: float
    infringement_likelihood: Literal["High", "Moderate", "Low"]
    relevant_claims: List[str]
    explanation: str
    specific_features: List[str]

class InfringementResults(BaseModel):
    products: List[InfringementAnalysis]

class AnalyzerService:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
        self.model = os.getenv("MODEL_NAME", "phi")
        print(f"Ollama host: {self.ollama_host}")
        print(f"Model: {self.model}")
        # Token limits for different models
        self.token_limits = {
            "phi": 2048,
            "mistral": 8192,  # mistral supports longer context
        }
        # Default timeout setting
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "300.0"))  # 5 minutes timeout

    def _truncate_prompt(self, prompt: str, max_length: int = 2048) -> str:
        """Truncate prompt to meet token limit"""
        # Simple character count method, should use tokenizer in production
        if len(prompt) > max_length:
            print(f"Warning: Truncating prompt from {len(prompt)} to {max_length} characters")
            return prompt[:max_length]
        return prompt

    def analyze_multiple_products(self, patent: Dict, products: List[Dict]) -> Dict:
        """
        Analyze multiple products for patent infringement in a single request
        """
        try:
            prompt = self._create_multiple_products_prompt(patent, products)
            print("prompt:")
            print(prompt)
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "stream": False,
                    "format": InfringementResults.model_json_schema(),
                    "prompt": prompt,
                },
                headers={"Content-Type": "application/json"},
                timeout=300.0
            )
            
            # Handle HTTP errors
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise AnalyzerError(f"API request failed: {str(e)}", 503)
            
            # Parse response
            try:
                result = response.json()["response"]
                analysis = InfringementResults.model_validate_json(result)
                
                # Sort and limit results
                sorted_results = sorted(
                    analysis.products,
                    key=lambda x: x.infringement_score,
                    reverse=True
                )
                
                return {
                    "status_code": 200,
                    "data": [result.model_dump() for result in sorted_results[:2]]
                }
                
            except (KeyError, json.JSONDecodeError) as e:
                raise AnalyzerError(f"Failed to parse API response: {str(e)}", 502)
                
        except AnalyzerError as e:
            return {
                "status_code": e.status_code,
                "error": e.message
            }
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Unexpected error: {str(e)}"
            }

    def analyze_single_product(self, patent: Dict, product: Dict) -> Dict:
        """
        Analyze a single product for patent infringement
        Returns a dictionary with status code and either results or error message
        """
        try:
            prompt = self._create_single_product_prompt(patent, product)
            print("prompt:")
            print(prompt)
            response = requests.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.model,
                    "stream": False,
                    "format": InfringementAnalysis.model_json_schema(),
                    "prompt": prompt,
                },
                headers={"Content-Type": "application/json"},
                timeout=self.timeout  # 使用配置的超時時間
            )
            
            # Handle HTTP errors
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError as e:
                raise AnalyzerError(f"API request failed: {str(e)}", 503)
            
            # Parse response
            try:
                result = response.json()["response"]
                analysis = InfringementAnalysis.model_validate_json(result)
                return {
                    "status_code": 200,
                    "data": analysis.model_dump()
                }
            except (KeyError, json.JSONDecodeError) as e:
                raise AnalyzerError(f"Failed to parse API response: {str(e)}", 502)
            
        except AnalyzerError as e:
            return {
                "status_code": e.status_code,
                "error": e.message
            }
        except Exception as e:
            return {
                "status_code": 500,
                "error": f"Unexpected error: {str(e)}"
            }

    def _create_single_product_prompt(self, patent: Dict, product: Dict) -> str:
        """
        Create a comprehensive analysis prompt using full patent information
        """
        prompt = f"""You are a strict patent analysis expert. Analyze the product's potential patent infringement carefully and critically.

        Patent Information:
        Patent Number: {patent["publication_number"]}
        Patent Title: {patent["title"]}
        Abstract: {patent["abstract"]}
        
        Product to Analyze:
        Name: {product["name"]}
        Description: {product["description"]}
        
        Patent Claims:
        {self._format_claims(patent["claims"])}
        
        ANALYSIS GUIDELINES:
        1. Compare the product against ALL patent claims
        2. Look for EXACT matches to claim elements
        3. Consider the technical implementation details
        4. Be conservative in infringement assessment
        5. Require strong evidence for "High" likelihood
        
        Scoring criteria:
        - High (75-100): Product clearly implements ALL elements of at least one claim
        - Moderate (40-74): Product matches SOME key elements but lacks others
        - Low (0-39): Product has minimal or no overlap with patent claims
        
        RESPONSE FORMAT:
        Return a JSON object with these EXACT fields:
        {{
            "product_name": "MUST use the exact product name from the input above",
            "infringement_score": number (0-100),
            "infringement_likelihood": "High"/"Moderate"/"Low",
            "relevant_claims": ["claim numbers"],
            "explanation": "Detailed technical explanation of matching/non-matching elements",
            "specific_features": ["List specific features that match or differ"]
        }}

        CRITICAL REQUIREMENTS:
        - Be skeptical and thorough in analysis
        - Default to lower scores unless clear evidence exists
        - Provide specific technical reasons for your assessment
        - Consider both matching and non-matching features
        - Return valid JSON object only, no additional text
        """
        # 獲取當前模型的 token 限制
        token_limit = self.token_limits.get(self.model, 2048)
        return self._truncate_prompt(prompt, token_limit)

    def _format_claims(self, claims_data: Union[str, List[Dict]]) -> str:
        """
        Format patent claims data into readable text
        """
        try:
            # If input is a string, clean up Unicode characters first
            if isinstance(claims_data, str):
                # Remove outer quotes if present
                claims_text = claims_data.strip('"')
                
                # First round of Unicode cleanup
                try:
                    # Try to decode as JSON first
                    claims_data = json.loads(claims_text)
                except json.JSONDecodeError:
                    # If JSON decode fails, try to clean up the string
                    claims_text = claims_text.encode('latin1').decode('unicode_escape')
                    claims_data = json.loads(claims_text)
                
                # Define common Unicode character replacements
                unicode_replacements = {
                    '\u00e2\u0080\u009c': '"',  # left double quotation
                    '\u00e2\u0080\u009d': '"',  # right double quotation
                    '\u00e2\u0080\u0098': "'",  # left single quotation
                    '\u00e2\u0080\u0099': "'",  # right single quotation
                    '\u00e2\u0080\u009e': '"',  # double low-9 quotation
                    '\u00e2\u0080\u009f': '"',  # double high-reversed-9 quotation
                    '\u00e2\u0080\u0094': '-',  # em dash
                    'â': '"',                    # fallback for any remaining â
                    'â': '-',                    # fallback for any remaining â
                }
                
                # Process each claim's text
                if isinstance(claims_data, list):
                    for claim in claims_data:
                        if 'text' in claim:
                            text = claim['text']
                            # Apply Unicode replacements
                            for old, new in unicode_replacements.items():
                                text = text.replace(old, new)
                            claim['text'] = text
            
            # Ensure data is in list format
            if not isinstance(claims_data, list):
                raise ValueError("Claims data must be a list")
            
            # Format each claim
            formatted_claims = []
            for claim in claims_data:
                claim_text = claim.get("text", "")
                formatted_claims.append(f"Claim {claim.get('num', '?')}: {claim_text}")
            
            return "\n\n".join(formatted_claims)
            
        except Exception as e:
            print(f"Error formatting claims: {str(e)}")
            print(f"Claims data type: {type(claims_data)}")
            if isinstance(claims_data, str):
                print(f"Raw claims string: {claims_data}")
            return "Error: Unable to format claims data"

    def _parse_llm_response(self, response: str) -> Dict:
        """Parse LLM response into structured data"""
        try:
            analysis = InfringementAnalysis.model_validate_json(response)
            return analysis.model_dump()
        except Exception as e:
            print(f"Error parsing LLM response: {str(e)}")
            return {
                "infringement_likelihood": "Error",
                "infringement_score": 0,
                "relevant_claims": [],
                "explanation": "Failed to parse analysis",
                "specific_features": []
            }

    def _create_error_response(self, product_name: str, error_message: str) -> Dict:
        """Create an error response for failed analysis"""
        return {
            "product_name": product_name,
            "infringement_likelihood": "Error",
            "infringement_score": 0,
            "relevant_claims": [],
            "explanation": error_message,
            "specific_features": []
        }

    def _create_multiple_products_prompt(self, patent: Dict, products: List[Dict]) -> str:
        """
        Create a prompt for analyzing multiple products at once
        """
        # Format all product information
        products_text = "\n\n".join([
        f"{i+1}:\nName: {product['name']}\nDescription: {product['description']}"
        for i, product in enumerate(products)
    ])
        
        prompt = f"""You are a strict patent analysis expert. Analyze each product's potential patent infringement carefully and critically.

        Patent Information:
        Patent Number: {patent["publication_number"]}
        Patent Title: {patent["title"]}
        Abstract: {patent["abstract"]}
        
        Products to Analyze:
        {products_text}
        
        Patent Claims:
        {self._format_claims(patent["claims"])}
        
        ANALYSIS GUIDELINES:
        1. Compare each product against ALL patent claims
        2. Look for EXACT matches to claim elements
        3. Consider the technical implementation details
        4. Be conservative in infringement assessment
        5. Require strong evidence for "High" likelihood
        
        Scoring criteria:
        - High (75-100): Product clearly implements ALL elements of at least one claim
        - Moderate (40-74): Product matches SOME key elements but lacks others
        - Low (0-39): Product has minimal or no overlap with patent claims
        
        IMPORTANT: Return ONLY the TWO products with the highest infringement scores.
        
        RESPONSE FORMAT:
        Return a JSON array with EXACTLY TWO objects (highest scoring products) where each object has:
        {{
            "product_name": "MUST use the exact product name from the input list above",
            "infringement_score": number (0-100),
            "infringement_likelihood": "High"/"Moderate"/"Low",
            "relevant_claims": ["claim numbers"],
            "explanation": "Detailed technical explanation of matching/non-matching elements",
            "specific_features": ["List specific features that match or differ"]
        }}

        CRITICAL REQUIREMENTS:
        - Use EXACT product names from the input list (e.g. "Walmart Shopping App", not "Product A")
        - Analyze ALL products but return only the top 2 by infringement score
        - Be skeptical and thorough in analysis
        - Default to lower scores unless clear evidence exists
        - Provide specific technical reasons for your assessment
        - Consider both matching and non-matching features
        - Return valid JSON array with exactly 2 items
        - Sort results by infringement score (highest first)
        """
        # 獲取當前模型的 token 限制
        token_limit = self.token_limits.get(self.model, 2048)
        return self._truncate_prompt(prompt, token_limit)

    def _parse_bulk_llm_response(self, response: str, products: List[Dict]) -> List[Dict]:
        """Parse the LLM response for multiple products"""
        try:
            analysis = InfringementResults.model_validate_json(response)
            
            # Sort results by infringement score
            sorted_results = sorted(
                analysis.products,
                key=lambda x: x.infringement_score,
                reverse=True
            )
            
            return [result.model_dump() for result in sorted_results[:2]]
            
        except Exception as e:
            print(f"Error parsing bulk response: {str(e)}")
            print(f"Raw response: {response}")
            return [
                self._create_error_response(product["name"], "Failed to parse analysis results")
                for product in products[:2]
            ]
