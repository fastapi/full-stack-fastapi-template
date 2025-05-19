#llm_interface.py
import os
import json
import requests
from typing import Dict, Any, Optional, List, Union
import logging
import time
import base64

logger = logging.getLogger(__name__)

class LLMInterface:
    """Interface for communicating with Language Models."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM interface.
        
        Args:
            config: System configuration
        """
        self.config = config
        self.provider = config.get("llm_provider", "openai")
        self.model = config.get("llm_model", "gpt-4-vision-preview")
        self.temperature = config.get("temperature", 0.2)
        self.max_tokens = config.get("max_tokens", 4096)
        
        # API keys
        self.openai_api_key = config.get("openai_api_key", os.environ.get("OPENAI_API_KEY", ""))
        self.google_api_key = config.get("google_api_key", os.environ.get("GOOGLE_API_KEY", ""))
        
        # Rate limiting
        self.last_call_time = 0
        self.min_time_between_calls = config.get("min_time_between_calls", 0.5)  # seconds
        
        # Verify API keys
        self._verify_api_keys()
    
    def _verify_api_keys(self) -> None:
        """Verify that required API keys are available."""
        if self.provider == "openai" and not self.openai_api_key:
            raise ValueError("OpenAI API key is required but not provided")
        elif self.provider == "google" and not self.google_api_key:
            raise ValueError("Google API key is required but not provided")
    
    def _rate_limit(self) -> None:
        """Implement rate limiting for API calls."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        
        if time_since_last_call < self.min_time_between_calls:
            sleep_time = self.min_time_between_calls - time_since_last_call
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
            time.sleep(sleep_time)
        
        self.last_call_time = time.time()
    
    def _prepare_openai_payload(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        image_data: Optional[str] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Prepare payload for OpenAI API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            image_data: Base64-encoded image data (optional)
            json_mode: Whether to request JSON output
            
        Returns:
            Payload dictionary
        """
        messages = []
        
        # Add system message if provided
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        # If image is provided, create a content list with text and image
        if image_data:
            content = [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{image_data}"
                    }
                }
            ]
            messages.append({
                "role": "user",
                "content": content
            })
        else:
            # Text-only prompt
            messages.append({
                "role": "user",
                "content": prompt
            })
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # Enable JSON mode if requested
        if json_mode and "gpt-4" in self.model:
            payload["response_format"] = {"type": "json_object"}
        
        return payload
    
    def _prepare_google_payload(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        image_data: Optional[str] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Prepare payload for Google Gemini API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            image_data: Base64-encoded image data (optional)
            json_mode: Whether to request JSON output
            
        Returns:
            Payload dictionary
        """
        contents = []
        
        # Add system prompt if provided
        if system_prompt:
            contents.append({
                "role": "system",
                "parts": [{"text": system_prompt}]
            })
        
        # Handle text and optional image
        user_parts = []
        user_parts.append({"text": prompt})
        
        if image_data:
            user_parts.append({
                "inline_data": {
                    "mime_type": "image/png",
                    "data": image_data
                }
            })
        
        contents.append({
            "role": "user",
            "parts": user_parts
        })
        
        # Prepare the payload
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": self.temperature,
                "maxOutputTokens": self.max_tokens,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        return payload
    
    def query(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        image_data: Optional[str] = None,
        json_mode: bool = False,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """Query the LLM with a prompt.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            image_data: Base64-encoded image data (optional)
            json_mode: Whether to request JSON output
            retry_count: Number of retries on failure
            
        Returns:
            Response from the LLM
        """
        self._rate_limit()
        
        attempt = 0
        while attempt < retry_count:
            attempt += 1
            
            try:
                if self.provider == "openai":
                    return self._query_openai(prompt, system_prompt, image_data, json_mode)
                elif self.provider == "google":
                    return self._query_google(prompt, system_prompt, image_data, json_mode)
                else:
                    raise ValueError(f"Unsupported LLM provider: {self.provider}")
            except Exception as e:
                logger.error(f"LLM API call failed (attempt {attempt}/{retry_count}): {str(e)}")
                
                if attempt >= retry_count:
                    raise
                
                # Exponential backoff
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
    
    def _query_openai(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        image_data: Optional[str] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Query OpenAI's API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            image_data: Base64-encoded image data (optional)
            json_mode: Whether to request JSON output
            
        Returns:
            Response from OpenAI
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.openai_api_key}"
        }
        
        payload = self._prepare_openai_payload(prompt, system_prompt, image_data, json_mode)
        
        logger.debug(f"Sending request to OpenAI API: {self.model}")
        
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        result = response.json()
        
        # Extract the content
        if "choices" in result and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            
            # If JSON mode, try to parse the content
            if json_mode:
                try:
                    content = json.loads(content)
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, returning raw content")
            
            return {
                "content": content,
                "model": result.get("model", self.model),
                "usage": result.get("usage", {})
            }
        else:
            logger.error(f"Unexpected OpenAI response format: {result}")
            raise ValueError(f"Unexpected OpenAI response format: {result}")
    
    def _query_google(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        image_data: Optional[str] = None,
        json_mode: bool = False
    ) -> Dict[str, Any]:
        """Query Google's Gemini API.
        
        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            image_data: Base64-encoded image data (optional)
            json_mode: Whether to request JSON output
            
        Returns:
            Response from Google
        """
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = self._prepare_google_payload(prompt, system_prompt, image_data, json_mode)
        
        # Determine the API endpoint based on model and multimodality
        model_name = self.model.replace("gemini-", "")
        api_url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={self.google_api_key}"
        
        logger.debug(f"Sending request to Google Gemini API: {self.model}")
        
        response = requests.post(
            api_url,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            logger.error(f"Google API error: {response.status_code} - {response.text}")
            response.raise_for_status()
        
        result = response.json()
        
        # Extract the content
        if "candidates" in result and len(result["candidates"]) > 0:
            candidate = result["candidates"][0]
            if "content" in candidate and "parts" in candidate["content"]:
                parts = candidate["content"]["parts"]
                text_parts = [part["text"] for part in parts if "text" in part]
                content = "\n".join(text_parts)
                
                # If JSON mode, try to parse the content
                if json_mode:
                    try:
                        content = json.loads(content)
                    except json.JSONDecodeError:
                        logger.warning("Failed to parse JSON response, returning raw content")
                
                return {
                    "content": content,
                    "model": self.model,
                    "usage": {}  # Google doesn't provide token usage in the same way
                }
            else:
                logger.error(f"Unexpected Google response format: {result}")
                raise ValueError(f"Unexpected Google response format: {result}")
        else:
            logger.error(f"Unexpected Google response format: {result}")
            raise ValueError(f"Unexpected Google response format: {result}")
    
    def extract_elements(self, dom_content: str, screenshot_data: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract form elements from a page.
        
        Args:
            dom_content: DOM content (HTML)
            screenshot_data: Base64-encoded screenshot (optional)
            
        Returns:
            List of extracted elements
        """
        system_prompt = """You are an expert web UI analyzer. Your task is to identify and extract all interactive form elements from the provided HTML content.
For each element, determine:
1. The element type (text input, password, checkbox, radio, select, textarea, submit button, etc.)
2. The element's label or placeholder text
3. Whether the element is required
4. A robust selector for automation

Return the results as a JSON array of objects with these properties:
- type: Element type
- label: The text label or placeholder
- required: Boolean indicating if the field is required
- selector: A CSS or XPath selector that uniquely identifies this element
- form: The form ID or name this element belongs to (if applicable)
"""
        
        prompt = f"""Analyze the following HTML to extract all form elements:

{dom_content[:5000]}  # Limit to avoid token limits

Focus on form controls like text inputs, password fields, checkboxes, radio buttons, dropdowns, textareas, and submit buttons.
If the HTML is truncated, focus on the visible elements.

Return the results as a JSON array.
"""

        response = self.query(prompt, system_prompt, screenshot_data, json_mode=True)
        
        # Process the response
        try:
            elements = response["content"]
            if isinstance(elements, str):
                # Try to parse the string as JSON
                elements = json.loads(elements)
            
            if isinstance(elements, list):
                return elements
            elif isinstance(elements, dict) and "elements" in elements:
                return elements["elements"]
            else:
                logger.error(f"Unexpected elements format: {elements}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to parse elements response: {str(e)}")
            return []
    
    def suggest_actions(
        self, 
        dom_content: str, 
        screenshot_data: Optional[str] = None, 
        current_url: str = "", 
        title: str = "", 
        visited_urls: List[str] = []
    ) -> List[Dict[str, Any]]:
        """Suggest next actions to take on a page.
        
        Args:
            dom_content: DOM content (HTML)
            screenshot_data: Base64-encoded screenshot (optional)
            current_url: Current URL
            title: Page title
            visited_urls: List of already visited URLs
            
        Returns:
            List of suggested actions
        """
        system_prompt = """You are an expert web crawler assistant. Your task is to analyze the current page and suggest the next actions to take to explore the website.
Focus on:
1. Links and buttons that lead to new pages, especially those that might contain forms
2. Menu items, tabs, and navigation elements
3. Form submissions (only if they don't modify data)

Avoid:
1. External links outside the current domain
2. Logout buttons
3. Delete or destructive actions
4. Already visited URLs

Return a list of suggested actions as a JSON array, with each action having:
- action: The type of action (click, fill, select)
- target: Description of the target element
- selector: A CSS or XPath selector to target the element
- reason: Why this action is important for exploration
"""
        
        visited_urls_str = "\n".join(visited_urls[-20:])  # Limit to last 20 to avoid token limits
        
        prompt = f"""Current page: {title} ({current_url})

Already visited URLs:
{visited_urls_str}

Analyze the current page and suggest the next actions to take for website exploration. Focus on finding new pages, especially those with forms.

Page DOM content (truncated):
{dom_content[:5000]}

Return a JSON array of suggested actions, sorted by priority (most important first).
Each action should include the type, target description, selector, and reason.

Example format:
[
  {{
    "action": "click",
    "target": "Login button",
    "selector": "#login-btn",
    "reason": "To access the login form"
  }},
  ...
]
"""

        response = self.query(prompt, system_prompt, screenshot_data, json_mode=True)
        
        # Process the response
        try:
            actions = response["content"]
            if isinstance(actions, str):
                # Try to parse the string as JSON
                actions = json.loads(actions)
            
            if isinstance(actions, list):
                return actions
            elif isinstance(actions, dict) and "actions" in actions:
                return actions["actions"]
            else:
                logger.error(f"Unexpected actions format: {actions}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to parse actions response: {str(e)}")
            return []
    
    def generate_test_cases(
        self, 
        page_metadata: Dict[str, Any], 
        elements: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable test cases for a page.
        
        Args:
            page_metadata: Page metadata
            elements: Form elements on the page
            
        Returns:
            Test cases in the specified format
        """
        system_prompt = """You are an expert QA engineer specializing in behavior-driven testing.
Your task is to create comprehensive test scenarios for the specified web form.
For each form, create scenarios that cover:
1. Happy path (successful submission with valid data)
2. Validation errors (required fields, format validation)
3. Edge cases (boundary values, special characters)

Write the scenarios in Gherkin format (Given/When/Then) if requested, or as plain English step-by-step instructions otherwise.
Be specific about expected outcomes and error messages where possible.
"""
        
        # Prepare a description of the form and its elements
        elements_str = json.dumps(elements, indent=2)
        format_type = self.config.get("test_case_format", "gherkin")
        
        prompt = f"""Generate test cases for the following web form:

Page: {page_metadata.get('title', 'Unknown Page')}
URL: {page_metadata.get('url', '')}

Form elements:
{elements_str}

Create comprehensive test scenarios that cover:
1. Happy path (valid inputs)
2. Validation errors (required fields, format validation)
3. Edge cases (boundary values, special characters)

Format: {'Gherkin (Given/When/Then)' if format_type == 'gherkin' else 'Plain English step-by-step'}

Please generate realistic test cases based on the form structure.
"""

        response = self.query(prompt, system_prompt)
        
        # Return the test cases content
        return response["content"]
    
    def generate_pom_class(
        self, 
        page_metadata: Dict[str, Any], 
        elements: List[Dict[str, Any]]
    ) -> str:
        """Generate a Page Object Model class for a page.
        
        Args:
            page_metadata: Page metadata
            elements: Form elements on the page
            
        Returns:
            Python POM class code
        """
        system_prompt = """You are an expert automation engineer specializing in Page Object Model (POM) design.
Your task is to create a Python class that follows the Page Object Model pattern for a web page.
The class should:
1. Include locators for all form elements
2. Provide methods to interact with those elements
3. Include methods for common actions on the page
4. Use proper waits and error handling
5. Follow best practices for maintainability

Use clear method and variable names, include docstrings, and ensure the code is PEP8 compliant.
"""
        
        # Prepare a description of the form and its elements
        elements_str = json.dumps(elements, indent=2)
        framework = self.config.get("test_framework", "playwright")
        
        prompt = f"""Generate a Page Object Model class for the following web page:

Page: {page_metadata.get('title', 'Unknown Page')}
URL: {page_metadata.get('url', '')}

Form elements:
{elements_str}

Framework: {'Playwright' if framework == 'playwright' else 'Selenium'}

Include:
1. A constructor that takes a {'Page' if framework == 'playwright' else 'WebDriver'} object
2. Locators for all form elements as class attributes
3. Methods to interact with the form elements (fill, click, select)
4. A method to navigate to the page
5. Methods for common actions (e.g., submit form, check validation messages)

Use proper waits and error handling (prefer {'expect_* methods' if framework == 'playwright' else 'WebDriverWait'}).
"""

        response = self.query(prompt, system_prompt)
        
        # Return the POM class code
        return response["content"]
    
    def generate_test_script(
        self, 
        page_metadata: Dict[str, Any], 
        test_cases: str, 
        pom_class: str
    ) -> str:
        """Generate a test script for a page.
        
        Args:
            page_metadata: Page metadata
            test_cases: Human-readable test cases
            pom_class: POM class code
            
        Returns:
            Python test script code
        """
        system_prompt = """You are an expert test automation engineer.
Your task is to create Python test functions based on provided test cases and a Page Object Model class.
The tests should:
1. Follow the pytest framework
2. Use the POM class to interact with the page
3. Include assertions to verify expected outcomes
4. Use proper test fixtures and setup/teardown
5. Handle errors gracefully
6. Be well-commented and maintainable

Write clean, efficient code that follows best practices.
"""
        
        framework = self.config.get("test_framework", "playwright")
        
        prompt = f"""Generate test functions for the following page based on the test cases and POM class:

Page: {page_metadata.get('title', 'Unknown Page')}
URL: {page_metadata.get('url', '')}

Test Cases:
{test_cases}

POM Class:
```python
{pom_class}
```

Framework: {'Playwright' if framework == 'playwright' else 'Selenium'} with pytest

Create test functions that:
1. Use the POM class to interact with the page
2. Implement each test case as a separate function
3. Include assertions to verify the expected outcomes
4. Use pytest fixtures for setup/teardown
5. Include proper error handling and waits

Add comments to explain the test logic and expectations.
"""

# state_tracker.py
import os
import json
import hashlib
from typing import Dict, Any, Optional, List, Set
from urllib.parse import urlparse, urljoin
import logging

logger = logging.getLogger(__name__)

class StateTracker:
    """Tracks visited pages and states during crawling."""
    
    def __init__(self, config: Dict[str, Any], base_url: str):
        """Initialize the state tracker.
        
        Args:
            config: System configuration
            base_url: Base URL of the website
        """
        self.config = config
        self.base_url = base_url
        self.base_domain = urlparse(base_url).netloc
        
        # State tracking
        self.visited_urls: Set[str] = set()
        self.visited_states: Set[str] = set()
        self.form_pages: List[Dict[str, Any]] = []
        self.page_metadata: Dict[str, Dict[str, Any]] = {}
        
        # Output paths
        self.output_dir = config.get("output_dir", "outputs")
        self.metadata_dir = os.path.join(self.output_dir, "metadata")
        
        # Create directories
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def normalize_url(self, url: str) -> str:
        """Normalize a URL for consistent comparison.
        
        Args:
            url: URL to normalize
            
        Returns:
            Normalized URL
        """
        # Handle relative URLs
        if not url.startswith(('http://', 'https://')):
            url = urljoin(self.base_url, url)
        
        # Parse the URL
        parsed = urlparse(url)
        
        # Normalize
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        
        # Include query parameters if present (but sorted for consistency)
        if parsed.query:
            query_params = sorted(parsed.query.split('&'))
            normalized += f"?{'&'.join(query_params)}"
        
        # Strip trailing slash for consistency
        if normalized.endswith('/') and not normalized.endswith('//'):
            normalized = normalized[:-1]
        
        return normalized
    
    def is_same_domain(self, url: str) -> bool:
        """Check if a URL is in the same domain as the base URL.
        
        Args:
            url: URL to check
            
        Returns:
            True if in the same domain, False otherwise
        """
        if not url.startswith(('http://', 'https://')):
            return True  # Relative URL is always same domain
        
        domain = urlparse(url).netloc
        
        # Check if it's the same domain or a subdomain
        if self.config.get("include_subdomains", False):
            return domain == self.base_domain or domain.endswith(f".{self.base_domain}")
        else:
            return domain == self.base_domain
    
    def should_visit(self, url: str) -> bool:
        """Check if a URL should be visited.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL should be visited, False otherwise
        """
        # Normalize the URL
        normalized_url = self.normalize_url(url)
        
        # Skip if already visited
        if normalized_url in self.visited_urls:
            return False
        
        # Skip if not in the same domain (and external links should be ignored)
        if self.config.get("ignore_external_links", True) and not self.is_same_domain(normalized_url):
            return False
        
        # Check if it's in allowed domains (if specified)
        allowed_domains = self.config.get("allowed_domains", [])
        if allowed_domains:
            domain = urlparse(normalized_url).netloc
            if domain not in allowed_domains and self.base_domain not in allowed_domains:
                return False
        
        # Skip if it's a file (not a webpage)
        path = urlparse(normalized_url).path.lower()
        if any(path.endswith(ext) for ext in ['.pdf', '.jpg', '.png', '.gif', '.zip', '.doc', '.xls']):
            return False
        
        # Skip if it has a fragment (usually same page)
        if '#' in normalized_url and self.normalize_url(normalized_url.split('#')[0]) in self.visited_urls:
            return False
        
        # Skip URLs with specific patterns (like logout)
        if any(pattern in normalized_url.lower() for pattern in ['/logout', '/signout', '/sign-out']):
            return False
        
        return True
    
    def add_visited_url(self, url: str) -> None:
        """Add a URL to the visited list.
        
        Args:
            url: URL to add
        """
        normalized_url = self.normalize_url(url)
        self.visited_urls.add(normalized_url)
        logger.info(f"Added visited URL: {normalized_url}")
    
    def compute_state_hash(self, dom_content: str) -> str:
        """Compute a hash of the page state based on DOM content.
        
        Args:
            dom_content: DOM content
            
        Returns:
            State hash
        """
        # Remove dynamic content that might change between loads
        # This is a simple approach and might need enhancement for specific apps
        simplified_dom = dom_content
        
        # Hash the simplified DOM
        hash_obj = hashlib.sha256(simplified_dom.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def add_visited_state(self, dom_content: str, url: str, title: str) -> bool:
        """Add a page state to the visited list.
        
        Args:
            dom_content: DOM content
            url: Current URL
            title: Page title
            
        Returns:
            True if this is a new state, False if already visited
        """
        state_hash = self.compute_state_hash(dom_content)
        
        if state_hash in self.visited_states:
            logger.info(f"State already visited: {url} (hash: {state_hash[:8]})")
            return False
        
        self.visited_states.add(state_hash)
        
        # Store page metadata
        normalized_url = self.normalize_url(url)
        self.page_metadata[normalized_url] = {
            'url': normalized_url,
            'title': title,
            'state_hash': state_hash
        }
        
        logger.info(f"Added new state: {url} (hash: {state_hash[:8]})")
        return True
    
    def add_form_page(self, url: str, title: str, elements: List[Dict[str, Any]]) -> None:
        """Add a page with forms to the tracker.
        
        Args:
            url: Page URL
            title: Page title
            elements: Form elements found on the page
        """
        normalized_url = self.normalize_url(url)
        
        # Create page entry
        page_data = {
            'url': normalized_url,
            'title': title,
            'elements': elements
        }
        
        self.form_pages.append(page_data)
        
        # Save to disk
        self._save_page_metadata(normalized_url, page_data)
        
        logger.info(f"Added form page: {title} ({normalized_url}) with {len(elements)} elements")
    
    def _save_page_metadata(self, url_key: str, data: Dict[str, Any]) -> None:
        """Save page metadata to disk.
        
        Args:
            url_key: URL key (normalized)
            data: Page data
        """
        # Create a filename from the URL
        filename = url_key.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
        if len(filename) > 200:  # Limit filename length
            filename = filename[:200]
        
        filename = f"{filename}.json"
        file_path = os.path.join(self.metadata_dir, filename)
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_visited_urls(self) -> List[str]:
        """Get the list of visited URLs.
        
        Returns:
            List of visited URLs
        """
        return list(self.visited_urls)
    
    def get_form_pages(self) -> List[Dict[str, Any]]:
        """Get the list of pages with forms.
        
        Returns:
            List of form pages
        """
        return self.form_pages
    
    def get_page_metadata(self, url: str) -> Optional[Dict[str, Any]]:
        """Get metadata for a specific page.
        
        Args:
            url: Page URL
            
        Returns:
            Page metadata or None if not found
        """
        normalized_url = self.normalize_url(url)
        return self.page_metadata.get(normalized_url)
    
    def save_state(self, path: str) -> None:
        """Save the current tracker state to a file.
        
        Args:
            path: Path to save the state
        """
        state = {
            'visited_urls': list(self.visited_urls),
            'visited_states': list(self.visited_states),
            'form_pages': self.form_pages,
            'page_metadata': self.page_metadata
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved state tracker to {path}")
    
    def load_state(self, path: str) -> None:
        """Load tracker state from a file.
        
        Args:
            path: Path to load the state from
        """
        if not os.path.exists(path):
            logger.warning(f"State file not found: {path}")
            return
        
        with open(path, 'r') as f:
            state = json.load(f)
        
        self.visited_urls = set(state.get('visited_urls', []))
        self.visited_states = set(state.get('visited_states', []))
        self.form_pages = state.get('form_pages', [])
        self.page_metadata = state.get('page_metadata', {})
        
        logger.info(f"Loaded state tracker from {path}: {len(self.visited_urls)} URLs, {len(self.form_pages)} form pages")


# element_etractor.py
import os
import json
from typing import Dict, Any, Optional, List
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ElementExtractor:
    """Extracts form elements from web pages using LLM assistance."""
    
    def __init__(self, browser_controller, llm_interface, config: Dict[str, Any]):
        """Initialize the element extractor.
        
        Args:
            browser_controller: Browser controller instance
            llm_interface: LLM interface instance
            config: System configuration
        """
        self.browser = browser_controller
        self.llm = llm_interface
        self.config = config
        self.output_dir = os.path.join(config.get("output_dir", "outputs"), "metadata")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def extract_page_elements(self, url: str, title: str) -> List[Dict[str, Any]]:
        """Extract elements from a page.
        
        Args:
            url: Page URL
            title: Page title
            
        Returns:
            List of extracted elements
        """
        logger.info(f"Extracting elements from page: {title} ({url})")
        
        # Get page content
        dom_content = self.browser.get_dom_content()
        
        # Take a screenshot for visual context
        screenshot = None
        if self.config.get("use_screenshots_for_extraction", True):
            screenshot = self.browser.get_screenshot()
        
        # Use two approaches and merge results for better accuracy
        elements_from_llm = self._extract_elements_with_llm(dom_content, screenshot)
        elements_from_dom = self._extract_elements_with_dom(dom_content)
        
        # Merge results (prioritizing LLM results but adding any extra from DOM)
        merged_elements = self._merge_element_results(elements_from_llm, elements_from_dom)
        
        # Add page context to each element
        for element in merged_elements:
            element["page_url"] = url
            element["page_title"] = title
        
        # Save metadata to file
        self._save_elements_metadata(url, title, merged_elements)
        
        return merged_elements
    
    def _extract_elements_with_llm(self, dom_content: str, screenshot: Optional[str] = None) -> List[Dict[str, Any]]:
        """Extract elements using LLM analysis.
        
        Args:
            dom_content: DOM content
            screenshot: Screenshot data (base64 encoded)
            
        Returns:
            List of elements
        """
        logger.info("Extracting elements with LLM")
        
        try:
            # Extract elements using LLM
            elements = self.llm.extract_elements(dom_content, screenshot)
            
            # Process elements to standardize format
            processed_elements = []
            for element in elements:
                # Ensure required fields
                processed_element = {
                    "type": element.get("type", "unknown"),
                    "label": element.get("label", ""),
                    "selector": element.get("selector", ""),
                    "required": element.get("required", False),
                    "form": element.get("form", "")
                }
                
                # Add optional fields if present
                if "id" in element:
                    processed_element["id"] = element["id"]
                if "name" in element:
                    processed_element["name"] = element["name"]
                if "placeholder" in element:
                    processed_element["placeholder"] = element["placeholder"]
                
                processed_elements.append(processed_element)
            
            logger.info(f"Found {len(processed_elements)} elements with LLM")
            return processed_elements
            
        except Exception as e:
            logger.error(f"Error extracting elements with LLM: {str(e)}")
            return []
    
    def _extract_elements_with_dom(self, dom_content: str) -> List[Dict[str, Any]]:
        """Extract elements using direct DOM parsing.
        
        Args:
            dom_content: DOM content
            
        Returns:
            List of elements
        """
        logger.info("Extracting elements with DOM parsing")
        
        try:
            soup = BeautifulSoup(dom_content, 'html.parser')
            elements = []
            
            # Find all forms
            forms = soup.find_all('form')
            form_count = len(forms)
            
            # Process forms
            if form_count > 0:
                for i, form in enumerate(forms):
                    form_id = form.get('id') or form.get('name') or f"form_{i+1}"
                    elements.extend(self._process_form(form, form_id))
            else:
                # If no forms, look for form elements at page level
                elements.extend(self._process_form(soup, "page_level"))
            
            logger.info(f"Found {len(elements)} elements with DOM parsing")
            return elements
            
        except Exception as e:
            logger.error(f"Error extracting elements with DOM parsing: {str(e)}")
            return []
    
    def _process_form(self, container, form_id: str) -> List[Dict[str, Any]]:
        """Process a form or container to extract form elements.
        
        Args:
            container: Form or page container (BeautifulSoup object)
            form_id: Form identifier
            
        Returns:
            List of form elements
        """
        elements = []
        
        # Find all input elements
        inputs = container.find_all('input')
        for input_elem in inputs:
            input_type = input_elem.get('type', 'text')
            
            # Skip hidden inputs
            if input_type == 'hidden':
                continue
            
            # Get element ID and name
            element_id = input_elem.get('id', '')
            element_name = input_elem.get('name', '')
            
            # Try to find a label
            label_text = self._find_label_text(container, element_id, element_name)
            
            # If no label found, use placeholder or name
            if not label_text:
                label_text = input_elem.get('placeholder', '') or element_name
            
            # Check if required
            required = input_elem.get('required') is not None or input_elem.get('aria-required') == 'true'
            
            # Generate a selector
            selector = self._generate_selector(input_elem)
            
            elements.append({
                'type': f"input_{input_type}",
                'label': label_text or f"Unlabeled {input_type}",
                'id': element_id,
                'name': element_name,
                'required': required,
                'form': form_id,
                'selector': selector,
                'placeholder': input_elem.get('placeholder', '')
            })
        
        # Find all select elements
        selects = container.find_all('select')
        for select_elem in selects:
            element_id = select_elem.get('id', '')
            element_name = select_elem.get('name', '')
            
            # Try to find a label
            label_text = self._find_label_text(container, element_id, element_name)
            
            # If no label found, use name
            if not label_text:
                label_text = element_name
            
            # Check if required
            required = select_elem.get('required') is not None or select_elem.get('aria-required') == 'true'
            
            # Generate a selector
            selector = self._generate_selector(select_elem)
            
            # Get options
            options = []
            for option in select_elem.find_all('option'):
                if option.get('value'):
                    options.append({
                        'value': option.get('value', ''),
                        'text': option.text.strip()
                    })
            
            elements.append({
                'type': 'select',
                'label': label_text or 'Unlabeled select',
                'id': element_id,
                'name': element_name,
                'required': required,
                'form': form_id,
                'selector': selector,
                'options': options
            })
        
        # Find all textarea elements
        textareas = container.find_all('textarea')
        for textarea_elem in textareas:
            element_id = textarea_elem.get('id', '')
            element_name = textarea_elem.get('name', '')
            
            # Try to find a label
            label_text = self._find_label_text(container, element_id, element_name)
            
            # If no label found, use placeholder or name
            if not label_text:
                label_text = textarea_elem.get('placeholder', '') or element_name
            
            # Check if required
            required = textarea_elem.get('required') is not None or textarea_elem.get('aria-required') == 'true'
            
            # Generate a selector
            selector = self._generate_selector(textarea_elem)
            
            elements.append({
                'type': 'textarea',
                'label': label_text or 'Unlabeled textarea',
                'id': element_id,
                'name': element_name,
                'required': required,
                'form': form_id,
                'selector': selector,
                'placeholder': textarea_elem.get('placeholder', '')
            })
        
        # Find all button elements
        buttons = container.find_all(['button', 'input[type="submit"]', 'input[type="button"]'])
        for button_elem in buttons:
            element_id = button_elem.get('id', '')
            element_name = button_elem.get('name', '')
            
            # Get button text
            if button_elem.name == 'button':
                button_text = button_elem.text.strip()
            else:
                button_text = button_elem.get('value', '')
            
            # If no text, use name or a default
            if not button_text:
                button_text = element_name or 'Submit'
            
            # Generate a selector
            selector = self._generate_selector(button_elem)
            
            # Determine button type
            if button_elem.name == 'input':
                button_type = button_elem.get('type', 'button')
            else:
                button_type = button_elem.get('type', 'button') 
            
            elements.append({
                'type': f"button_{button_type}",
                'label': button_text,
                'id': element_id,
                'name': element_name,
                'form': form_id,
                'selector': selector
            })
        
        return elements
    
    def _find_label_text(self, container, element_id: str, element_name: str) -> Optional[str]:
        """Find the label text for an element.
        
        Args:
            container: Form or page container (BeautifulSoup object)
            element_id: Element ID
            element_name: Element name
            
        Returns:
            Label text or None if not found
        """
        # Try to find a label with a 'for' attribute
        if element_id:
            label = container.find('label', attrs={'for': element_id})
            if label:
                return label.text.strip()
        
        # Try to find a label with a 'for' attribute matching the name
        if element_name:
            label = container.find('label', attrs={'for': element_name})
            if label:
                return label.text.strip()
        
        # Try to find a label that wraps the element
        if element_id:
            element = container.find(attrs={'id': element_id})
            if element and element.parent.name == 'label':
                return element.parent.text.strip().replace(element.text.strip(), '')
        
        # Try to find adjacent labels
        if element_id:
            element = container.find(attrs={'id': element_id})
            if element:
                # Check previous sibling
                prev_sib = element.previous_sibling
                if prev_sib and prev_sib.name == 'label':
                    return prev_sib.text.strip()
                
                # Check next sibling
                next_sib = element.next_sibling
                if next_sib and next_sib.name == 'label':
                    return next_sib.text.strip()
        
        return None
    
    def _generate_selector(self, element) -> str:
        """Generate a robust selector for an element.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            CSS or XPath selector
        """
        # Try ID first (most reliable)
        element_id = element.get('id')
        if element_id:
            return f"#{element_id}"
        
        # Try name attribute
        element_name = element.get('name')
        if element_name:
            tag_name = element.name
            return f"{tag_name}[name='{element_name}']"
        
        # Try data attributes
        for attr in element.attrs:
            if attr.startswith('data-'):
                return f"[{attr}='{element[attr]}']"
        
        # Generate an XPath based on element type and position
        if hasattr(element, 'sourceline') and hasattr(element, 'sourcepos'):
            return f"xpath=//{element.name}[{self._find_element_position(element)}]"
        
        # Fallback
        return f"{element.name}"
    
    def _find_element_position(self, element) -> int:
        """Find the position of an element among siblings of the same type.
        
        Args:
            element: BeautifulSoup element
            
        Returns:
            Position (1-based)
        """
        position = 1
        for sibling in element.find_previous_siblings(element.name):
            position += 1
        return position
    
    def _merge_element_results(
        self, 
        llm_elements: List[Dict[str, Any]], 
        dom_elements: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Merge element results from LLM and DOM parsing.
        
        Args:
            llm_elements: Elements found by LLM
            dom_elements: Elements found by DOM parsing
            
        Returns:
            Merged elements list
        """
        # Start with LLM elements (usually more accurate for complex pages)
        merged = llm_elements.copy()
        
        # Create lookup of elements by selector for easy matching
        merged_selectors = {elem.get("selector", ""): True for elem in merged}
        
        # Add DOM elements that weren't found by LLM
        for dom_elem in dom_elements:
            selector = dom_elem.get("selector", "")
            if selector and selector not in merged_selectors:
                merged.append(dom_elem)
                merged_selectors[selector] = True
        
        return merged
    
    def _save_elements_metadata(self, url: str, title: str, elements: List[Dict[str, Any]]) -> None:
        """Save elements metadata to a file.
        
        Args:
            url: Page URL
            title: Page title
            elements: Extracted elements
        """
        # Create a safe filename from the URL
        filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
        if len(filename) > 200:  # Limit filename length
            filename = filename[:200]
        
        filename = f"{filename}_elements.json"
        file_path = os.path.join(self.output_dir, filename)
        
        data = {
            "url": url,
            "title": title,
            "elements": elements
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved elements metadata to {file_path}")
    
    def verify_element_selectors(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Verify element selectors by checking if they exist in the DOM.
        
        Args:
            elements: List of element dictionaries
            
        Returns:
            Updated elements list with verified selectors
        """
        verified_elements = []
        
        for element in elements:
            selector = element.get("selector", "")
            if not selector:
                logger.warning(f"Element missing selector: {element}")
                verified_elements.append(element)
                continue
            
            # Check if selector exists in the DOM
            try:
                locator = self.browser.page.locator(selector)
                count = locator.count()
                
                if count == 0:
                    logger.warning(f"Selector not found in DOM: {selector}")
                    # Try to find a better selector
                    element["original_selector"] = selector
                    element["selector"] = self._find_alternative_selector(element)
                elif count > 1:
                    logger.warning(f"Selector matches multiple elements: {selector}")
                    # Make the selector more specific
                    element["original_selector"] = selector
                    element["selector"] = self._make_selector_unique(selector, element)
                
                # Verify the selector works for the element type
                if "type" in element:
                    element_type = element["type"]
                    tag_name = locator.evaluate("el => el.tagName.toLowerCase()")
                    
                    if element_type.startswith("input_") and tag_name != "input":
                        logger.warning(f"Selector element type mismatch: {selector} is {tag_name}, expected input")
                    elif element_type == "select" and tag_name != "select":
                        logger.warning(f"Selector element type mismatch: {selector} is {tag_name}, expected select")
                    elif element_type == "textarea" and tag_name != "textarea":
                        logger.warning(f"Selector element type mismatch: {selector} is {tag_name}, expected textarea")
                
            except Exception as e:
                logger.error(f"Error verifying selector {selector}: {str(e)}")
                # Keep the original selector
            
            verified_elements.append(element)
        
        return verified_elements
    
    def _find_alternative_selector(self, element: Dict[str, Any]) -> str:
        """Find alternative selector for an element when the original doesn't work.
        
        Args:
            element: Element dictionary
            
        Returns:
            Alternative selector
        """
        # Try finding by label text if available
        label = element.get("label", "")
        if label:
            try:
                # Try to find label element with this text
                label_locator = self.browser.page.locator(f"label:has-text('{label}')")
                if label_locator.count() > 0:
                    # Check if the label has a 'for' attribute
                    for_attr = label_locator.first.get_attribute("for")
                    if for_attr:
                        return f"#{for_attr}"
                
                # Try to find element near the label
                placeholder = element.get("placeholder", "")
                if placeholder:
                    return f"input[placeholder='{placeholder}']"
                
                # Try by name or ID if available
                name = element.get("name", "")
                if name:
                    element_type = element.get("type", "")
                    if element_type.startswith("input_"):
                        input_type = element_type.replace("input_", "")
                        return f"input[type='{input_type}'][name='{name}']"
                    elif element_type == "select":
                        return f"select[name='{name}']"
                    elif element_type == "textarea":
                        return f"textarea[name='{name}']"
            except Exception:
                pass
        
        # Fallback to a generic selector based on element type
        element_type = element.get("type", "")
        if element_type.startswith("input_"):
            input_type = element_type.replace("input_", "")
            return f"input[type='{input_type}']"
        elif element_type == "select":
            return "select"
        elif element_type == "textarea":
            return "textarea"
        elif element_type.startswith("button_"):
            button_text = element.get("label", "")
            if button_text:
                return f"button:has-text('{button_text}')"
            return "button"
        
        # Last resort
        return element.get("original_selector", "")
    
    def _make_selector_unique(self, selector: str, element: Dict[str, Any]) -> str:
        """Make a selector more specific to match only one element.
        
        Args:
            selector: Original selector
            element: Element dictionary
            
        Returns:
            More specific selector
        """
        # Try to make the selector more specific using element attributes
        element_type = element.get("type", "")
        label = element.get("label", "")
        name = element.get("name", "")
        placeholder = element.get("placeholder", "")
        
        try:
            # Get all matching elements
            locators = self.browser.page.locator(selector).all()
            
            # Try to find a unique identifier
            for i, locator in enumerate(locators):
                # Check if this locator matches the element description
                if element_type.startswith("input_"):
                    input_type = element_type.replace("input_", "")
                    if locator.get_attribute("type") == input_type:
                        # Check other attributes
                        if name and locator.get_attribute("name") == name:
                            return f"{selector}[name='{name}']"
                        if placeholder and locator.get_attribute("placeholder") == placeholder:
                            return f"{selector}[placeholder='{placeholder}']"
                
                # If we can't make it more specific by attributes, use position
                return f"({selector})[{i+1}]"
            
        except Exception:
            pass
        
        # If all else fails, try an XPath with position
        if not selector.startswith("xpath="):
            # Convert CSS to XPath and add position
            tag = selector.split('[')[0].split('#')[0].split('.')[0]
            if not tag:
                tag = "*"
            return f"xpath=//{tag}[{selector}][1]"
        
        return selector


# test_generator.py

import os
import json
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class TestGenerator:
    """Generates human-readable test cases from form elements."""
    
    def __init__(self, llm_interface, config: Dict[str, Any]):
        """Initialize the test generator.
        
        Args:
            llm_interface: LLM interface instance
            config: System configuration
        """
        self.llm = llm_interface
        self.config = config
        self.output_dir = os.path.join(config.get("output_dir", "outputs"), "test_cases")
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_test_cases(self, page_metadata: Dict[str, Any], elements: List[Dict[str, Any]]) -> str:
        """Generate human-readable test cases for a page.
        
        Args:
            page_metadata: Page metadata
            elements: Form elements on the page
            
        Returns:
            Generated test cases
        """
        logger.info(f"Generating test cases for page: {page_metadata.get('title', 'Unknown')}")
        
        # Filter out elements that don't belong to forms if needed
        if self.config.get("focus_on_forms", True):
            form_elements = [elem for elem in elements if 
                             (elem.get("form") or 
                              elem.get("type", "").startswith("input_") or 
                              elem.get("type") in ["select", "textarea"])]
        else:
            form_elements = elements
        
        if not form_elements:
            logger.warning(f"No form elements found on page: {page_metadata.get('title', 'Unknown')}")
            return "No form elements found on this page."
        
        # Group elements by form
        forms = self._group_elements_by_form(form_elements)
        
        all_test_cases = []
        
        # Generate test cases for each form
        for form_id, form_elements in forms.items():
            form_name = self._get_form_name(form_id, page_metadata.get('title', 'Unknown'))
            
            logger.info(f"Generating test cases for form: {form_name} with {len(form_elements)} elements")
            
            test_cases = self.llm.generate_test_cases(page_metadata, form_elements)
            
            # Add form header
            form_test_cases = f"# Test Cases for {form_name}\n\n{test_cases}"
            all_test_cases.append(form_test_cases)
        
        # Combine all test cases
        test_cases_content = "\n\n".join(all_test_cases)
        
        # Save to file
        self._save_test_cases(page_metadata.get('url', ''), page_metadata.get('title', 'Unknown'), test_cases_content)
        
        return test_cases_content
    
    def _group_elements_by_form(self, elements: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group elements by form.
        
        Args:
            elements: List of form elements
            
        Returns:
            Dictionary of form_id -> elements
        """
        forms = {}
        
        for element in elements:
            form_id = element.get("form", "")
            
            if not form_id:
                form_id = "default_form"
            
            if form_id not in forms:
                forms[form_id] = []
            
            forms[form_id].append(element)
        
        return forms
    
    def _get_form_name(self, form_id: str, page_title: str) -> str:
        """Get a human-readable name for a form.
        
        Args:
            form_id: Form ID
            page_title: Page title
            
        Returns:
            Form name
        """
        if form_id == "default_form":
            return f"{page_title} Form"
        
        # If form_id starts with 'form_', remove it
        if form_id.startswith("form_"):
            form_id = form_id[5:]
        
        # Capitalize and convert underscores to spaces
        form_name = form_id.replace("_", " ").title()
        
        return f"{form_name} Form on {page_title}"
    
    def _save_test_cases(self, url: str, title: str, test_cases: str) -> None:
        """Save test cases to a file.
        
        Args:
            url: Page URL
            title: Page title
            test_cases: Generated test cases
        """
        # Create a safe filename from the URL
        filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
        if len(filename) > 200:  # Limit filename length
            filename = filename[:200]
        
        # Use markdown for Gherkin format, plain text otherwise
        format_type = self.config.get("test_case_format", "gherkin")
        extension = "md" if format_type == "gherkin" else "txt"
        filename = f"{filename}_test_cases.{extension}"
        file_path = os.path.join(self.output_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(f"# Test Cases for {title}\n\n")
            f.write(f"URL: {url}\n\n")
            f.write(test_cases)
        
        logger.info(f"Saved test cases to {file_path}")
    
    def generate_all_test_cases(self, form_pages: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate test cases for all pages with forms.
        
        Args:
            form_pages: List of pages with forms
            
        Returns:
            Dictionary of page URL -> test cases
        """
        results = {}
        
        for page in form_pages:
            url = page.get('url', '')
            title = page.get('title', 'Unknown Page')
            elements = page.get('elements', [])
            
            logger.info(f"Generating test cases for page: {title} ({url})")
            
            test_cases = self.generate_test_cases(page, elements)
            results[url] = test_cases
        
        return results

# code_generator.py

import os
import json
from typing import Dict, Any, Optional, List
import logging
import re

logger = logging.getLogger(__name__)

class CodeGenerator:
    """Generates Python test scripts using Page Object Model."""
    
    def __init__(self, llm_interface, config: Dict[str, Any]):
        """Initialize the code generator.
        
        Args:
            llm_interface: LLM interface instance
            config: System configuration
        """
        self.llm = llm_interface
        self.config = config
        self.output_dir = os.path.join(config.get("output_dir", "outputs"), "test_scripts")
        self.pages_dir = os.path.join(self.output_dir, "pages")
        self.tests_dir = os.path.join(self.output_dir, "tests")
        
        # Create directories
        os.makedirs(self.pages_dir, exist_ok=True)
        os.makedirs(self.tests_dir, exist_ok=True)
    
    def generate_page_class(self, page_metadata: Dict[str, Any], elements: List[Dict[str, Any]]) -> str:
        """Generate a Page Object Model class for a page.
        
        Args:
            page_metadata: Page metadata
            elements: Form elements on the page
            
        Returns:
            Generated POM class code
        """
        logger.info(f"Generating POM class for page: {page_metadata.get('title', 'Unknown')}")
        
        # Filter out elements that don't belong to forms if needed
        if self.config.get("focus_on_forms", True):
            form_elements = [elem for elem in elements if 
                            (elem.get("form") or 
                             elem.get("type", "").startswith("input_") or 
                             elem.get("type") in ["select", "textarea"])]
        else:
            form_elements = elements
        
        if not form_elements:
            logger.warning(f"No form elements found on page: {page_metadata.get('title', 'Unknown')}")
            # Generate a minimal page class
            class_code = self._generate_minimal_page_class(page_metadata)
        else:
            # Generate the page class using LLM
            class_code = self.llm.generate_pom_class(page_metadata, form_elements)
        
        # Save to file
        class_name = self._get_class_name(page_metadata.get('title', 'Unknown'))
        self._save_page_class(class_name, class_code)
        
        return class_code
    
    def generate_test_script(self, page_metadata: Dict[str, Any], test_cases: str, pom_class: str) -> str:
        """Generate a test script for a page.
        
        Args:
            page_metadata: Page metadata
            test_cases: Human-readable test cases
            pom_class: POM class code
            
        Returns:
            Generated test script code
        """
        logger.info(f"Generating test script for page: {page_metadata.get('title', 'Unknown')}")
        
        # Generate the test script using LLM
        test_code = self.llm.generate_test_script(page_metadata, test_cases, pom_class)
        
        # Save to file
        class_name = self._get_class_name(page_metadata.get('title', 'Unknown'))
        self._save_test_script(class_name, test_code)
        
        return test_code
    
    def generate_all_code(self, form_pages: List[Dict[str, Any]], test_cases: Dict[str, str]) -> Dict[str, Dict[str, str]]:
        """Generate all code for pages with forms.
        
        Args:
            form_pages: List of pages with forms
            test_cases: Dictionary of page URL -> test cases
            
        Returns:
            Dictionary of page URL -> {pom_class, test_script}
        """
        results = {}
        
        # First generate all page classes
        page_classes = {}
        for page in form_pages:
            url = page.get('url', '')
            title = page.get('title', 'Unknown Page')
            elements = page.get('elements', [])
            
            logger.info(f"Generating POM class for page: {title} ({url})")
            
            pom_class = self.generate_page_class(page, elements)
            page_classes[url] = pom_class
        
        # Generate conftest.py for test fixtures
        self._generate_conftest()
        
        # Then generate test scripts
        for page in form_pages:
            url = page.get('url', '')
            title = page.get('title', 'Unknown Page')
            
            if url in test_cases and url in page_classes:
                logger.info(f"Generating test script for page: {title} ({url})")
                
                test_script = self.generate_test_script(page, test_cases[url], page_classes[url])
                
                results[url] = {
                    'pom_class': page_classes[url],
                    'test_script': test_script
                }
        
        # Generate __init__.py files
        self._generate_init_files()
        
        return results
    
    def _generate_minimal_page_class(self, page_metadata: Dict[str, Any]) -> str:
        """Generate a minimal page class for a page without forms.
        
        Args:
            page_metadata: Page metadata
            
        Returns:
            Minimal page class code
        """
        title = page_metadata.get('title', 'Unknown Page')
        url = page_metadata.get('url', '')
        class_name = self._get_class_name(title)
        
        framework = self.config.get("test_framework", "playwright")
        if framework == "playwright":
            return f"""from playwright.sync_api import Page

class {class_name}:
    \"\"\"Page object for {title}.\"\"\"
    
    def __init__(self, page: Page):
        \"\"\"Initialize the page object.
        
        Args:
            page: Playwright Page object
        \"\"\"
        self.page = page
        self.url = "{url}"
    
    def navigate(self):
        \"\"\"Navigate to the page.
        
        Returns:
            Self for method chaining
        \"\"\"
        self.page.goto(self.url)
        return self
    
    def get_title(self) -> str:
        \"\"\"Get the page title.
        
        Returns:
            Page title
        \"\"\"
        return self.page.title()
"""
        else:  # Selenium
            return f"""from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class {class_name}:
    \"\"\"Page object for {title}.\"\"\"
    
    def __init__(self, driver):
        \"\"\"Initialize the page object.
        
        Args:
            driver: Selenium WebDriver
        \"\"\"
        self.driver = driver
        self.url = "{url}"
    
    def navigate(self):
        \"\"\"Navigate to the page.
        
        Returns:
            Self for method chaining
        \"\"\"
        self.driver.get(self.url)
        return self
    
    def get_title(self) -> str:
        \"\"\"Get the page title.
        
        Returns:
            Page title
        \"\"\"
        return self.driver.title
"""
    
    def _get_class_name(self, title: str) -> str:
        """Generate a class name from page title.
        
        Args:
            title: Page title
            
        Returns:
            Class name
        """
        # Remove special characters
        class_name = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        
        # Replace spaces with nothing
        class_name = class_name.replace(' ', '')
        
        # Ensure it starts with a letter
        if not class_name or not class_name[0].isalpha():
            class_name = 'Page' + class_name
        
        # Ensure first letter is uppercase (PascalCase)
        class_name = class_name[0].upper() + class_name[1:]
        
        # Add "Page" suffix if not already there
        if not class_name.endswith('Page'):
            class_name += 'Page'
        
        return class_name
    
    def _save_page_class(self, class_name: str, class_code: str) -> None:
        """Save a page class to a file.
        
        Args:
            class_name: Class name
            class_code: Class code
        """
        # Convert class name to snake_case for filename
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        filename = f"{filename}.py"
        file_path = os.path.join(self.pages_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(class_code)
        
        logger.info(f"Saved page class to {file_path}")
    
    def _save_test_script(self, class_name: str, test_code: str) -> None:
        """Save a test script to a file.
        
        Args:
            class_name: Class name (for filename)
            test_code: Test code
        """
        # Convert class name to snake_case for filename
        filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
        filename = f"test_{filename[:-5]}.py"  # Remove 'page' suffix
        file_path = os.path.join(self.tests_dir, filename)
        
        with open(file_path, 'w') as f:
            f.write(test_code)
        
        logger.info(f"Saved test script to {file_path}")
    
    def _generate_conftest(self) -> None:
        """Generate conftest.py for test fixtures."""
        framework = self.config.get("test_framework", "playwright")
        
        if framework == "playwright":
            conftest_code = """import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_type():
    """Return the browser type to use."""
    return "chromium"  # Can be "firefox", "webkit"

@pytest.fixture(scope="session")
def browser(browser_type):
    """Launch browser once per session."""
    playwright = sync_playwright().start()
    
    if browser_type == "firefox":
        browser = playwright.firefox.launch(headless=True)
    elif browser_type == "webkit":
        browser = playwright.webkit.launch(headless=True)
    else:  # Default to chromium
        browser = playwright.chromium.launch(headless=True)
    
    yield browser
    
    browser.close()
    playwright.stop()

@pytest.fixture
def context(browser):
    """Create a new browser context for each test."""
    context = browser.new_context(viewport={"width": 1280, "height": 720})
    yield context
    context.close()

@pytest.fixture
def page(context):
    """Create a new page for each test."""
    page = context.new_page()
    page.set_default_timeout(30000)
    yield page
"""
        else:  # Selenium
            conftest_code = """import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def browser_type():
    """Return the browser type to use."""
    return "chrome"  # Can be "firefox", "edge"

@pytest.fixture
def driver(browser_type):
    """Set up WebDriver."""
    if browser_type == "firefox":
        from selenium.webdriver.firefox.service import Service
        from webdriver_manager.firefox import GeckoDriverManager
        from selenium.webdriver.firefox.options import Options
        
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(
            service=Service(GeckoDriverManager().install()),
            options=options
        )
    elif browser_type == "edge":
        from selenium.webdriver.edge.service import Service
        from webdriver_manager.microsoft import EdgeChromiumDriverManager
        from selenium.webdriver.edge.options import Options
        
        options = Options()
        options.headless = True
        driver = webdriver.Edge(
            service=Service(EdgeChromiumDriverManager().install()),
            options=options
        )
    else:  # Default to Chrome
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )
    
    driver.implicitly_wait(10)
    driver.set_window_size(1280, 720)
    
    yield driver
    
    driver.quit()
"""
        
        file_path = os.path.join(self.tests_dir, "conftest.py")
        with open(file_path, 'w') as f:
            f.write(conftest_code)
        
        logger.info(f"Generated conftest.py at {file_path}")
    
    def _generate_init_files(self) -> None:
        """Generate __init__.py files for the package structure."""
        # Create __init__.py in output directory
        with open(os.path.join(self.output_dir, "__init__.py"), 'w') as f:
            f.write("")
        
        # Create __init__.py in pages directory
        with open(os.path.join(self.pages_dir, "__init__.py"), 'w') as f:
            f.write("")
        
        # Create __init__.py in tests directory
        with open(os.path.join(self.tests_dir, "__init__.py"), 'w') as f:
            f.write("")
        
        logger.info("Generated __init__.py files for package structure")

        response = self.query(prompt, system_prompt)
        
        # Return the test script code
        return response["content"]

# orchestrator.py

import os
import json
import time
from typing import Dict, Any, Optional, List, Set
import logging
from urllib.parse import urlparse

from browser_controller import BrowserController
from llm_interface import LLMInterface
from state_tracker import StateTracker
from element_extractor import ElementExtractor
from test_generator import TestGenerator
from code_generator import CodeGenerator

logger = logging.getLogger(__name__)

class Orchestrator:
    """Main orchestrator for the LLM-powered UI testing system."""
    
    def __init__(self, config: Dict[str, Any], root_url: str):
        """Initialize the orchestrator.
        
        Args:
            config: System configuration
            root_url: Root URL of the website to test
        """
        self.config = config
        self.root_url = root_url
        
        # Initialize components
        self.browser = BrowserController(config)
        self.llm = LLMInterface(config)
        self.state_tracker = StateTracker(config, root_url)
        
        # These components will be initialized after browser starts
        self.element_extractor = None
        self.test_generator = None
        self.code_generator = None
        
        # Crawling settings
        self.max_pages = config.get("max_pages", 100)
        self.max_depth = config.get("max_depth", 5)
        
        # Logging and output
        self.output_dir = config.get("output_dir", "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # URL queue and visited tracking
        self.url_queue = []
        self.current_depth = 0
        self.pages_visited = 0
    
    def start(self) -> None:
        """Start the orchestrator and run the main workflow."""
        try:
            # Start browser
            logger.info("Starting browser")
            self.browser.start()
            
            # Initialize components that need browser
            self.element_extractor = ElementExtractor(self.browser, self.llm, self.config)
            self.test_generator = TestGenerator(self.llm, self.config)
            self.code_generator = CodeGenerator(self.llm, self.config)
            
            # Main workflow
            self._crawl_website()
            self._generate_artifacts()
            
        except Exception as e:
            logger.error(f"Orchestrator error: {str(e)}", exc_info=True)
        finally:
            # Clean up
            self.browser.stop()
            logger.info("Orchestrator finished")
    
    def _crawl_website(self) -> None:
        """Crawl the website, discover pages and forms."""
        logger.info(f"Starting website crawl at {self.root_url}")
        
        # Add root URL to queue
        self.url_queue.append((self.root_url, 0))  # (url, depth)
        
        # Process queue
        while self.url_queue and self.pages_visited < self.max_pages:
            # Get next URL from queue
            url, depth = self.url_queue.pop(0)
            
            # Skip if depth exceeds max
            if depth > self.max_depth:
                logger.info(f"Skipping {url}, depth {depth} exceeds max depth {self.max_depth}")
                continue
            
            # Skip if URL should not be visited
            if not self.state_tracker.should_visit(url):
                logger.info(f"Skipping {url}, already visited or excluded")
                continue
            
            # Navigate to URL
            logger.info(f"Navigating to {url} (depth {depth}, page {self.pages_visited+1}/{self.max_pages})")
            if not self.browser.navigate(url):
                logger.warning(f"Failed to navigate to {url}")
                continue
            
            # Get page info
            current_url = self.browser.get_current_url()
            title = self.browser.get_current_title()
            dom_content = self.browser.get_dom_content()
            
            # Mark as visited
            self.state_tracker.add_visited_url(current_url)
            self.pages_visited += 1
            
            # Check if this is a new state
            is_new_state = self.state_tracker.add_visited_state(dom_content, current_url, title)
            
            if is_new_state:
                # Extract form elements
                logger.info(f"Extracting elements from {title} ({current_url})")
                elements = self.element_extractor.extract_page_elements(current_url, title)
                
                # If form elements found, add to form pages
                if elements and any(self._is_form_element(element) for element in elements):
                    logger.info(f"Found form page: {title} ({current_url})")
                    self.state_tracker.add_form_page(current_url, title, elements)
            
            # Find next actions
            screenshot = None
            if self.config.get("use_screenshots_for_navigation", True):
                screenshot = self.browser.get_screenshot()
            
            actions = self.llm.suggest_actions(
                dom_content, 
                screenshot, 
                current_url, 
                title, 
                self.state_tracker.get_visited_urls()
            )
            
            # Process suggested actions
            self._process_actions(actions, depth)
            
            # Add a short delay to avoid overwhelming the server
            time.sleep(self.config.get("crawl_delay", 1))
        
        logger.info(f"Crawl completed: {self.pages_visited} pages visited, {len(self.state_tracker.get_form_pages())} form pages found")
    
    def _is_form_element(self, element: Dict[str, Any]) -> bool:
        """Check if an element is a form element.
        
        Args:
            element: Element dictionary
            
        Returns:
            True if element is a form element, False otherwise
        """
        element_type = element.get("type", "")
        return (element_type.startswith("input_") or 
                element_type in ["select", "textarea"] or 
                element_type.startswith("button_"))
    
    def _process_actions(self, actions: List[Dict[str, Any]], current_depth: int) -> None:
        """Process suggested actions from LLM.
        
        Args:
            actions: List of actions
            current_depth: Current crawl depth
        """
        # First pass: collect new URLs
        for action in actions:
            action_type = action.get("action", "")
            
            if action_type == "click":
                # Check if it's a link with an href
                target = action.get("target", "")
                if "link" in target.lower() and "href" in action:
                    href = action["href"]
                    # Add to queue if not visited
                    if self.state_tracker.should_visit(href):
                        logger.info(f"Queueing URL: {href}")
                        self.url_queue.append((href, current_depth + 1))
        
        # Second pass: perform in-page actions (if configured)
        if self.config.get("perform_in_page_actions", True):
            for action in actions[:3]:  # Limit to top 3 actions to avoid infinite loops
                action_type = action.get("action", "")
                selector = action.get("selector", "")
                
                if not selector:
                    continue
                
                if action_type == "click" and not "link" in action.get("target", "").lower():
                    # Click a button or other element
                    logger.info(f"Clicking element: {action.get('target', selector)}")
                    if self.browser.click(selector, wait_for_navigation=False):
                        # Check if we landed on a new page after the click
                        new_url = self.browser.get_current_url()
                        if new_url != self.browser.get_current_url():
                            # Add to queue if not visited
                            if self.state_tracker.should_visit(new_url):
                                logger.info(f"Found new URL after click: {new_url}")
                                self.url_queue.append((new_url, current_depth + 1))
    
    def _generate_artifacts(self) -> None:
        """Generate test artifacts from crawled data."""
        logger.info("Generating test artifacts")
        
        # Get form pages
        form_pages = self.state_tracker.get_form_pages()
        
        if not form_pages:
            logger.warning("No form pages found, nothing to generate")
            return
        
        # Generate test cases
        logger.info(f"Generating test cases for {len(form_pages)} pages")
        test_cases = self.test_generator.generate_all_test_cases(form_pages)
        
        # Generate code
        logger.info(f"Generating code for {len(form_pages)} pages")
        code_results = self.code_generator.generate_all_code(form_pages, test_cases)
        
        # Generate summary report
        self._generate_summary_report(form_pages, test_cases, code_results)
        
        logger.info("Artifact generation completed")
    
    def _generate_summary_report(
        self, 
        form_pages: List[Dict[str, Any]], 
        test_cases: Dict[str, str], 
        code_results: Dict[str, Dict[str, str]]
    ) -> None:
        """Generate a summary report.
        
        Args:
            form_pages: List of form pages
            test_cases: Dictionary of page URL -> test cases
            code_results: Dictionary of page URL -> {pom_class, test_script}
        """
        report_path = os.path.join(self.output_dir, "summary_report.md")
        
        with open(report_path, 'w') as f:
            f.write("# UI Testing System Summary Report\n\n")
            
            # Crawl statistics
            f.write("## Crawl Statistics\n\n")
            f.write(f"- **Total Pages Visited**: {self.pages_visited}\n")
            f.write(f"- **Form Pages Found**: {len(form_pages)}\n")
            f.write(f"- **Root URL**: {self.root_url}\n\n")
            
            # Form pages summary
            f.write("## Form Pages\n\n")
            for i, page in enumerate(form_pages, 1):
                url = page.get('url', '')
                title = page.get('title', 'Unknown Page')
                elements = page.get('elements', [])
                form_elements = [e for e in elements if self._is_form_element(e)]
                
                f.write(f"### {i}. {title}\n")
                f.write(f"- **URL**: {url}\n")
                f.write(f"- **Form Elements**: {len(form_elements)}\n")
                
                # List of element types
                element_types = {}
                for element in form_elements:
                    element_type = element.get("type", "unknown")
                    if element_type not in element_types:
                        element_types[element_type] = 0
                    element_types[element_type] += 1
                
                f.write("- **Element Types**:\n")
                for element_type, count in element_types.items():
                    f.write(f"  - {element_type}: {count}\n")
                
                f.write("\n")
            
            # Generated artifacts
            f.write("## Generated Artifacts\n\n")
            
            # Test cases
            f.write("### Test Cases\n\n")
            for url, _ in test_cases.items():
                page_title = next((p.get('title', 'Unknown') for p in form_pages if p.get('url', '') == url), "Unknown")
                
                # Create a safe filename from the URL
                filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
                if len(filename) > 200:  # Limit filename length
                    filename = filename[:200]
                
                format_type = self.config.get("test_case_format", "gherkin")
                extension = "md" if format_type == "gherkin" else "txt"
                relative_path = f"test_cases/{filename}_test_cases.{extension}"
                
                f.write(f"- **{page_title}**: [Test Cases]({relative_path})\n")
            
            f.write("\n")
            
            # Code files
            f.write("### Code Files\n\n")
            for url, code in code_results.items():
                page_title = next((p.get('title', 'Unknown') for p in form_pages if p.get('url', '') == url), "Unknown")
                class_name = self._get_class_name_from_title(page_title)
                
                # Convert class name to snake_case for filename
                import re
                filename = re.sub(r'(?<!^)(?=[A-Z])', '_', class_name).lower()
                
                page_path = f"test_scripts/pages/{filename}.py"
                test_path = f"test_scripts/tests/test_{filename[:-5]}.py"  # Remove 'page' suffix
                
                f.write(f"- **{page_title}**:\n")
                f.write(f"  - [Page Object]({page_path})\n")
                f.write(f"  - [Test Script]({test_path})\n")
            
            f.write("\n")
            
            # How to run tests
            f.write("## Running the Tests\n\n")
            framework = self.config.get("test_framework", "playwright")
            
            f.write("### Setup\n\n")
            f.write("1. Install dependencies:\n")
            f.write("```bash\n")
            if framework == "playwright":
                f.write("pip install pytest playwright pytest-playwright\n")
                f.write("playwright install\n")
            else:
                f.write("pip install pytest selenium webdriver-manager\n")
            f.write("```\n\n")
            
            f.write("### Running Tests\n\n")
            f.write("To run all tests:\n")
            f.write("```bash\n")
            f.write("cd " + self.output_dir + "\n")
            f.write("pytest test_scripts/tests/\n")
            f.write("```\n\n")
            
            f.write("To run a specific test:\n")
            f.write("```bash\n")
            f.write("pytest test_scripts/tests/test_specific_page.py\n")
            f.write("```\n\n")
            
            f.write("### Configuration\n\n")
            f.write("Test configuration can be modified in `test_scripts/tests/conftest.py`.\n")
        
        logger.info(f"Generated summary report at {report_path}")
    
    def _get_class_name_from_title(self, title: str) -> str:
        """Generate a class name from page title.
        
        Args:
            title: Page title
            
        Returns:
            Class name
        """
        # Remove special characters
        import re
        class_name = re.sub(r'[^a-zA-Z0-9\s]', '', title)
        
        # Replace spaces with nothing
        class_name = class_name.replace(' ', '')
        
        # Ensure it starts with a letter
        if not class_name or not class_name[0].isalpha():
            class_name = 'Page' + class_name
        
        # Ensure first letter is uppercase (PascalCase)
        class_name = class_name[0].upper() + class_name[1:]
        
        # Add "Page" suffix if not already there
        if not class_name.endswith('Page'):
            class_name += 'Page'
        
        return class_name

# main.py

#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import json
from config import Config
from orchestrator import Orchestrator

def setup_logging(log_level=logging.INFO, log_file=None):
    """Set up logging configuration.
    
    Args:
        log_level: Logging level
        log_file: Path to log file (optional)
    """
    handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )

def parse_arguments():
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='LLM-Powered Automated UI Testing System')
    
    parser.add_argument('url', help='Root URL of the website to test')
    
    parser.add_argument(
        '--config', 
        type=str, 
        help='Path to configuration file (JSON)'
    )
    
    parser.add_argument(
        '--output-dir', 
        type=str, 
        default='outputs',
        help='Output directory for generated artifacts'
    )
    
    parser.add_argument(
        '--llm-provider', 
        type=str, 
        choices=['openai', 'google'], 
        help='LLM provider (openai or google)'
    )
    
    parser.add_argument(
        '--headless', 
        action='store_true', 
        default=True,
        help='Run browser in headless mode'
    )
    
    parser.add_argument(
        '--no-headless', 
        action='store_false', 
        dest='headless',
        help='Run browser in visible mode'
    )
    
    parser.add_argument(
        '--max-pages', 
        type=int, 
        help='Maximum number of pages to crawl'
    )
    
    parser.add_argument(
        '--max-depth', 
        type=int, 
        help='Maximum depth for crawling'
    )
    
    parser.add_argument(
        '--test-framework', 
        type=str, 
        choices=['playwright', 'selenium'], 
        help='Test framework to use'
    )
    
    parser.add_argument(
        '--auth-username', 
        type=str, 
        help='Username for authentication'
    )
    
    parser.add_argument(
        '--auth-password', 
        type=str, 
        help='Password for authentication'
    )
    
    parser.add_argument(
        '--log-level', 
        type=str, 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help='Logging level'
    )
    
    parser.add_argument(
        '--log-file', 
        type=str, 
        help='Path to log file'
    )

    return parser.parse_args()

def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set up logging
    log_level = getattr(logging, args.log_level)
    log_file = args.log_file
    setup_logging(log_level, log_file)
    
    logger = logging.getLogger(__name__)
    logger.info("Starting LLM-Powered Automated UI Testing System")
    
    # Load configuration
    config_path = args.config
    config = Config(config_path)
    
    # Override configuration with command line arguments
    if args.output_dir:
        config.set("output_dir", args.output_dir)
    
    if args.llm_provider:
        config.set("llm_provider", args.llm_provider)
    
    if args.headless is not None:
        config.set("headless", args.headless)
    
    if args.max_pages:
        config.set("max_pages", args.max_pages)
    
    if args.max_depth:
        config.set("max_depth", args.max_depth)
    
    if args.test_framework:
        config.set("test_framework", args.test_framework)
    
    if args.auth_username:
        config.set("auth_required", True)
        config.set("auth_username", args.auth_username)
    
    if args.auth_password:
        config.set("auth_password", args.auth_password)
    
    # Print configuration
    logger.info(f"Configuration: {json.dumps(config.to_dict(), indent=2)}")
    
    # Create orchestrator
    orchestrator = Orchestrator(config.to_dict(), args.url)
    
    # Start orchestrator
    try:
        orchestrator.start()
        logger.info("Testing completed successfully")
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# utils.py
import os
import json
import re
import hashlib
import logging
from typing import Dict, Any, Optional, List, Union
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

def sanitize_filename(url: str, max_length: int = 200) -> str:
    """Sanitize a URL to use as a filename.
    
    Args:
        url: URL to sanitize
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename
    """
    # Replace invalid characters
    filename = url.replace('://', '_').replace('/', '_').replace('?', '_').replace('&', '_')
    filename = re.sub(r'[^a-zA-Z0-9_\-.]+', '_', filename)
    
    # Limit length
    if len(filename) > max_length:
        filename = filename[:max_length]
    
    return filename

def normalize_url(url: str, base_url: str) -> str:
    """Normalize a URL for consistent comparison.
    
    Args:
        url: URL to normalize
        base_url: Base URL for resolving relative URLs
        
    Returns:
        Normalized URL
    """
    # Handle relative URLs
    if not url.startswith(('http://', 'https://')):
        url = urljoin(base_url, url)
    
    # Parse the URL
    parsed = urlparse(url)
    
    # Normalize
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Include query parameters if present (but sorted for consistency)
    if parsed.query:
        query_params = sorted(parsed.query.split('&'))
        normalized += f"?{'&'.join(query_params)}"
    
    # Strip trailing slash for consistency
    if normalized.endswith('/') and not normalized.endswith('//'):
        normalized = normalized[:-1]
    
    return normalized

def is_same_domain(url: str, base_domain: str, include_subdomains: bool = False) -> bool:
    """Check if a URL is in the same domain as the base domain.
    
    Args:
        url: URL to check
        base_domain: Base domain
        include_subdomains: Whether to include subdomains
        
    Returns:
        True if in the same domain, False otherwise
    """
    if not url.startswith(('http://', 'https://')):
        return True  # Relative URL is always same domain
    
    domain = urlparse(url).netloc
    
    # Check if it's the same domain or a subdomain
    if include_subdomains:
        return domain == base_domain or domain.endswith(f".{base_domain}")
    else:
        return domain == base_domain

def clean_html(html: str) -> str:
    """Clean HTML content to reduce token size for LLM.
    
    Args:
        html: HTML content
        
    Returns:
        Cleaned HTML
    """
    # Parse HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove scripts
    for script in soup.find_all('script'):
        script.decompose()
    
    # Remove styles
    for style in soup.find_all('style'):
        style.decompose()
    
    # Remove comments
    for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
        comment.extract()
    
    # Remove meta
    for meta in soup.find_all('meta'):
        meta.decompose()
    
    # Remove hidden elements
    for hidden in soup.find_all(style=lambda value: value and 'display:none' in value):
        hidden.decompose()
    
    # Remove very large attribute values
    for tag in soup.find_all(True):
        for attr in list(tag.attrs.keys()):
            if isinstance(tag[attr], str) and len(tag[attr]) > 1000:
                tag[attr] = tag[attr][:1000] + "..."
    
    return str(soup)

def extract_domain(url: str) -> str:
    """Extract domain from a URL.
    
    Args:
        url: URL
        
    Returns:
        Domain
    """
    return urlparse(url).netloc

def hash_content(content: str) -> str:
    """Generate a hash of content.
    
    Args:
        content: Content to hash
        
    Returns:
        Content hash
    """
    hash_obj = hashlib.sha256(content.encode('utf-8'))
    return hash_obj.hexdigest()

def save_json(data: Any, filepath: str) -> None:
    """Save data to a JSON file.
    
    Args:
        data: Data to save
        filepath: Path to save to
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(filepath: str) -> Any:
    """Load data from a JSON file.
    
    Args:
        filepath: Path to load from
        
    Returns:
        Loaded data
    """
    if not os.path.exists(filepath):
        return None
    
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_form_elements(soup: BeautifulSoup) -> List[Dict[str, Any]]:
    """Extract form elements from BeautifulSoup object.
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of form elements
    """
    elements = []
    
    # Find all forms
    forms = soup.find_all('form')
    
    for form_index, form in enumerate(forms):
        form_id = form.get('id') or form.get('name') or f"form_{form_index + 1}"
        
        # Process inputs
        for input_elem in form.find_all('input'):
            input_type = input_elem.get('type', 'text')
            
            # Skip hidden inputs
            if input_type == 'hidden':
                continue
            
            element_id = input_elem.get('id', '')
            element_name = input_elem.get('name', '')
            
            # Find label
            label = None
            if element_id:
                label = soup.find('label', attrs={'for': element_id})
            
            if not label and element_name:
                label = soup.find('label', attrs={'for': element_name})
            
            label_text = label.get_text().strip() if label else input_elem.get('placeholder', '') or element_name or f"Unlabeled {input_type}"
            
            elements.append({
                'type': f"input_{input_type}",
                'id': element_id,
                'name': element_name,
                'label': label_text,
                'required': input_elem.get('required') is not None,
                'form': form_id
            })
        
        # Process selects
        for select_elem in form.find_all('select'):
            element_id = select_elem.get('id', '')
            element_name = select_elem.get('name', '')
            
            # Find label
            label = None
            if element_id:
                label = soup.find('label', attrs={'for': element_id})
            
            if not label and element_name:
                label = soup.find('label', attrs={'for': element_name})
            
            label_text = label.get_text().strip() if label else element_name or "Unlabeled select"
            
            # Get options
            options = []
            for option in select_elem.find_all('option'):
                if option.get('value'):
                    options.append({
                        'value': option.get('value', ''),
                        'text': option.get_text().strip()
                    })
            
            elements.append({
                'type': 'select',
                'id': element_id,
                'name': element_name,
                'label': label_text,
                'required': select_elem.get('required') is not None,
                'form': form_id,
                'options': options
            })
        
        # Process textareas
        for textarea_elem in form.find_all('textarea'):
            element_id = textarea_elem.get('id', '')
            element_name = textarea_elem.get('name', '')
            
            # Find label
            label = None
            if element_id:
                label = soup.find('label', attrs={'for': element_id})
            
            if not label and element_name:
                label = soup.find('label', attrs={'for': element_name})
            
            label_text = label.get_text().strip() if label else textarea_elem.get('placeholder', '') or element_name or "Unlabeled textarea"
            
            elements.append({
                'type': 'textarea',
                'id': element_id,
                'name': element_name,
                'label': label_text,
                'required': textarea_elem.get('required') is not None,
                'form': form_id
            })
        
        # Process buttons
        for button_elem in form.find_all(['button', 'input[type="submit"]', 'input[type="button"]']):
            element_id = button_elem.get('id', '')
            element_name = button_elem.get('name', '')
            
            # Get button text
            if button_elem.name == 'button':
                button_text = button_elem.get_text().strip()
            else:
                button_text = button_elem.get('value', '')
            
            if not button_text:
                button_text = element_name or 'Submit'
            
            elements.append({
                'type': 'button',
                'id': element_id,
                'name': element_name,
                'label': button_text,
                'form': form_id
            })
    
    return elements

def generate_class_name(title: str) -> str:
    """Generate a class name from a title.
    
    Args:
        title: Title
        
    Returns:
        Class name
    """
    # Remove special characters
    class_name = re.sub(r'[^a-zA-Z0-9\s]', '', title)
    
    # Replace spaces with nothing
    class_name = class_name.replace(' ', '')
    
    # Ensure it starts with a letter
    if not class_name or not class_name[0].isalpha():
        class_name = 'Page' + class_name
    
    # Ensure first letter is uppercase (PascalCase)
    class_name = class_name[0].upper() + class_name[1:]
    
    # Add "Page" suffix if not already there
    if not class_name.endswith('Page'):
        class_name += 'Page'
    
    return class_name

def convert_to_snake_case(camel_case: str) -> str:
    """Convert a CamelCase string to snake_case.
    
    Args:
        camel_case: CamelCase string
        
    Returns:
        snake_case string
    """
    snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_case).lower()
    return snake_case

# prompts/__init__.py
"""
Prompt templates for LLM interaction in the UI testing system.
Each class defines a specific type of prompt with corresponding
system prompts, query templates, and example formats.
"""

class NavigationPrompts:
    """Prompts for navigation and action suggestions."""
    
    SYSTEM_PROMPT = """You are an expert web crawler assistant. Your task is to analyze the current page 
and suggest the next actions to take to explore the website.

Focus on:
1. Links and buttons that lead to new pages, especially those that might contain forms
2. Menu items, tabs, and navigation elements
3. Form submissions (only if they don't modify data)

Avoid:
1. External links outside the current domain
2. Logout buttons
3. Delete or destructive actions
4. Already visited URLs

Return a list of suggested actions as a JSON array, with each action having:
- action: The type of action (click, fill, select)
- target: Description of the target element
- selector: A CSS or XPath selector to target the element
- reason: Why this action is important for exploration
"""
    
    NAVIGATION_PROMPT_TEMPLATE = """Current page: {title} ({url})

Already visited URLs:
{visited_urls}

Analyze the current page and suggest the next actions to take for website exploration. Focus on finding new pages, especially those with forms.

Page DOM content (truncated):
{dom_content}

Return a JSON array of suggested actions, sorted by priority (most important first).
Each action should include the type, target description, selector, and reason.

Example format:
[
  {{
    "action": "click",
    "target": "Login button",
    "selector": "#login-btn",
    "reason": "To access the login form"
  }},
  ...
]
"""
    
    @staticmethod
    def format_navigation_prompt(title: str, url: str, dom_content: str, visited_urls: list) -> str:
        """Format the navigation prompt.
        
        Args:
            title: Page title
            url: Current URL
            dom_content: DOM content (will be truncated)
            visited_urls: List of visited URLs
            
        Returns:
            Formatted prompt
        """
        # Truncate DOM content to avoid token limits
        truncated_dom = dom_content[:5000] + "..." if len(dom_content) > 5000 else dom_content
        
        # Format visited URLs as a string (last 20 only)
        visited_urls_str = "\n".join(visited_urls[-20:]) if visited_urls else "None"
        
        return NavigationPrompts.NAVIGATION_PROMPT_TEMPLATE.format(
            title=title,
            url=url,
            dom_content=truncated_dom,
            visited_urls=visited_urls_str
        )


class ElementExtractionPrompts:
    """Prompts for extracting form elements from a page."""
    
    SYSTEM_PROMPT = """You are an expert web UI analyzer. Your task is to identify and extract all interactive form elements from the provided HTML content.
For each element, determine:
1. The element type (text input, password, checkbox, radio, select, textarea, submit button, etc.)
2. The element's label or placeholder text
3. Whether the element is required
4. A robust selector for automation

Return the results as a JSON array of objects with these properties:
- type: Element type
- label: The text label or placeholder
- required: Boolean indicating if the field is required
- selector: A CSS or XPath selector that uniquely identifies this element
- form: The form ID or name this element belongs to (if applicable)
"""
    
    ELEMENT_EXTRACTION_TEMPLATE = """Analyze the following HTML to extract all form elements:

{dom_content}

Focus on form controls like text inputs, password fields, checkboxes, radio buttons, dropdowns, textareas, and submit buttons.
If the HTML is truncated, focus on the visible elements.

Return the results as a JSON array.
"""
    
    @staticmethod
    def format_element_extraction_prompt(dom_content: str) -> str:
        """Format the element extraction prompt.
        
        Args:
            dom_content: DOM content (will be truncated)
            
        Returns:
            Formatted prompt
        """
        # Truncate DOM content to avoid token limits
        truncated_dom = dom_content[:5000] + "..." if len(dom_content) > 5000 else dom_content
        
        return ElementExtractionPrompts.ELEMENT_EXTRACTION_TEMPLATE.format(
            dom_content=truncated_dom
        )


class TestCasePrompts:
    """Prompts for generating human-readable test cases."""
    
    SYSTEM_PROMPT = """You are an expert QA engineer specializing in behavior-driven testing.
Your task is to create comprehensive test scenarios for the specified web form.
For each form, create scenarios that cover:
1. Happy path (successful submission with valid data)
2. Validation errors (required fields, format validation)
3. Edge cases (boundary values, special characters)

Write the scenarios in Gherkin format (Given/When/Then) if requested, or as plain English step-by-step instructions otherwise.
Be specific about expected outcomes and error messages where possible.
"""
    
    TEST_CASE_TEMPLATE = """Generate test cases for the following web form:

Page: {page_title}
URL: {page_url}

Form elements:
{elements_json}

Create comprehensive test scenarios that cover:
1. Happy path (valid inputs)
2. Validation errors (required fields, format validation)
3. Edge cases (boundary values, special characters)

Format: {format_type}

Please generate realistic test cases based on the form structure.
"""
    
    @staticmethod
    def format_test_case_prompt(page_title: str, page_url: str, elements: list, format_type: str = "Gherkin (Given/When/Then)") -> str:
        """Format the test case generation prompt.
        
        Args:
            page_title: Page title
            page_url: Page URL
            elements: List of form elements
            format_type: Format type (Gherkin or Plain English)
            
        Returns:
            Formatted prompt
        """
        import json
        elements_json = json.dumps(elements, indent=2)
        
        return TestCasePrompts.TEST_CASE_TEMPLATE.format(
            page_title=page_title,
            page_url=page_url,
            elements_json=elements_json,
            format_type=format_type
        )


class CodeGenerationPrompts:
    """Prompts for generating code (POM classes and test scripts)."""
    
    POM_SYSTEM_PROMPT = """You are an expert automation engineer specializing in Page Object Model (POM) design.
Your task is to create a Python class that follows the Page Object Model pattern for a web page.
The class should:
1. Include locators for all form elements
2. Provide methods to interact with those elements
3. Include methods for common actions on the page
4. Use proper waits and error handling
5. Follow best practices for maintainability

Use clear method and variable names, include docstrings, and ensure the code is PEP8 compliant.
"""
    
    POM_TEMPLATE = """Generate a Page Object Model class for the following web page:

Page: {page_title}
URL: {page_url}

Form elements:
{elements_json}

Framework: {framework}

Include:
1. A constructor that takes a {'Page' if framework == 'playwright' else 'WebDriver'} object
2. Locators for all form elements as class attributes
3. Methods to interact with the form elements (fill, click, select)
4. A method to navigate to the page
5. Methods for common actions (e.g., submit form, check validation messages)

Use proper waits and error handling (prefer {'expect_* methods' if framework == 'playwright' else 'WebDriverWait'}).
"""
    
    TEST_SCRIPT_SYSTEM_PROMPT = """You are an expert test automation engineer.
Your task is to create Python test functions based on provided test cases and a Page Object Model class.
The tests should:
1. Follow the pytest framework
2. Use the POM class to interact with the page
3. Include assertions to verify expected outcomes
4. Use proper test fixtures and setup/teardown
5. Handle errors gracefully
6. Be well-commented and maintainable

Write clean, efficient code that follows best practices.
"""
    
    TEST_SCRIPT_TEMPLATE = """Generate test functions for the following page based on the test cases and POM class:

Page: {page_title}
URL: {page_url}

Test Cases:
{test_cases}

POM Class:
```python
{pom_class}
```

Framework: {framework} with pytest

Create test functions that:
1. Use the POM class to interact with the page
2. Implement each test case as a separate function
3. Include assertions to verify the expected outcomes
4. Use pytest fixtures for setup/teardown
5. Include proper error handling and waits

Add comments to explain the test logic and expectations.
"""
    
    @staticmethod
    def format_pom_prompt(page_title: str, page_url: str, elements: list, framework: str = "playwright") -> str:
        """Format the POM class generation prompt.
        
        Args:
            page_title: Page title
            page_url: Page URL
            elements: List of form elements
            framework: Test framework (playwright or selenium)
            
        Returns:
            Formatted prompt
        """
        import json
        elements_json = json.dumps(elements, indent=2)
        
        return CodeGenerationPrompts.POM_TEMPLATE.format(
            page_title=page_title,
            page_url=page_url,
            elements_json=elements_json,
            framework=framework
        )
    
    @staticmethod
    def format_test_script_prompt(page_title: str, page_url: str, test_cases: str, pom_class: str, framework: str = "playwright") -> str:
        """Format the test script generation prompt.
        
        Args:
            page_title: Page title
            page_url: Page URL
            test_cases: Test cases
            pom_class: POM class code
            framework: Test framework (playwright or selenium)
            
        Returns:
            Formatted prompt
        """
        return CodeGenerationPrompts.TEST_SCRIPT_TEMPLATE.format(
            page_title=page_title,
            page_url=page_url,
            test_cases=test_cases,
            pom_class=pom_class,
            framework=framework
        )

# requirements.txt
playwright>=1.35.0
pytest>=7.3.1
pytest-playwright>=0.4.0
beautifulsoup4>=4.12.2
requests>=2.31.0

# README.md
# LLM-Powered Automated UI Testing

This project leverages large language models (LLMs) alongside browser automation to intelligently crawl web applications, identify form elements, and generate robust test artifacts.

## Features

- **Intelligent Web Crawling**: Recursively explores web applications, identifying forms and interactive elements
- **Form Element Extraction**: Identifies and extracts metadata about form fields, buttons, and controls
- **Test Case Generation**: Creates human-readable test scenarios covering happy paths and edge cases
- **Code Generation**: Produces maintainable test scripts using the Page Object Model pattern
- **Multimodal Analysis**: Combines DOM analysis with visual understanding to comprehensively test UIs
- **Authentication Support**: Handles login forms, including basic auth and form-based authentication
- **Shadow DOM Support**: Works with modern web components and shadow DOM elements

## Installation

### Requirements

- Python 3.12+
- Playwright or Selenium
- Access to a Language Model API (OpenAI GPT-4 or Google Gemini)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/llm-ui-tester.git
cd llm-ui-tester
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install Playwright browsers:
```bash
playwright install
```

4. Set up your API keys:
```bash
export OPENAI_API_KEY=your_api_key
# or
export GOOGLE_API_KEY=your_api_key
```

## Usage

### Basic Usage

```bash
python main.py https://example.com --output-dir ./test_results
```

### Options

```
usage: main.py [-h] [--config CONFIG] [--output-dir OUTPUT_DIR]
               [--llm-provider {openai,google}] [--headless] [--no-headless]
               [--max-pages MAX_PAGES] [--max-depth MAX_DEPTH]
               [--test-framework {playwright,selenium}]
               [--auth-username AUTH_USERNAME] [--auth-password AUTH_PASSWORD]
               [--log-level {DEBUG,INFO,WARNING,ERROR}] [--log-file LOG_FILE]
               url

LLM-Powered Automated UI Testing System

positional arguments:
  url                   Root URL of the website to test

optional arguments:
  -h, --help            show this help message and exit
  --config CONFIG       Path to configuration file (JSON)
  --output-dir OUTPUT_DIR
                        Output directory for generated artifacts
  --llm-provider {openai,google}
                        LLM provider (openai or google)
  --headless            Run browser in headless mode
  --no-headless         Run browser in visible mode
  --max-pages MAX_PAGES
                        Maximum number of pages to crawl
  --max-depth MAX_DEPTH
                        Maximum depth for crawling
  --test-framework {playwright,selenium}
                        Test framework to use
  --auth-username AUTH_USERNAME
                        Username for authentication
  --auth-password AUTH_PASSWORD
                        Password for authentication
  --log-level {DEBUG,INFO,WARNING,ERROR}
                        Logging level
  --log-file LOG_FILE   Path to log file
```

### Configuration File

You can also provide a configuration file in JSON format:

```bash
python main.py https://example.com --config config.json
```

Example configuration:

```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4-vision-preview",
  "temperature": 0.2,
  "headless": true,
  "max_pages": 50,
  "max_depth": 3,
  "test_framework": "playwright",
  "auth_required": true,
  "auth_username": "testuser",
  "auth_password": "password123",
  "auth_type": "form"
}
```

## Output Artifacts

The system generates several artifacts:

1. **JSON Metadata**: Structured information about all form elements discovered
2. **Test Cases**: Human-readable test scenarios in Gherkin or plain text format
3. **Test Scripts**: Python code with Page Object Model classes and pytest functions
4. **Summary Report**: Overview of crawled pages, forms, and generated artifacts

## Project Structure

```
llm_ui_tester/
├── __init__.py
├── config.py                    # Configuration handling
├── main.py                      # Entry point
├── orchestrator.py              # AI Orchestrator
├── browser_controller.py        # Playwright browser handling
├── llm_interface.py             # LLM API communication
├── state_tracker.py             # Page state and visited tracking  
├── element_extractor.py         # Form element extraction
├── test_generator.py            # Human-readable test case generation
├── code_generator.py            # Python test script generation
├── utils.py                     # Utility functions
├── prompts/                     # Prompt templates
│   └── __init__.py
├── outputs/                     # Generated artifacts
│   ├── metadata/                # JSON metadata of elements
│   ├── test_cases/              # Human-readable test cases
│   └── test_scripts/            # Generated Python test scripts
│       ├── pages/               # Page Object Model classes
│       └── tests/               # Test functions
└── tests/                       # Tests for the tester itself
    └── __init__.py
```

## Running the Generated Tests

Once the tests are generated, you can run them using pytest:

```bash
cd outputs
pytest test_scripts/tests/
```

To run a specific test:

```bash
pytest test_scripts/tests/test_login_page.py
```

## Limitations

- For best results, the system should be run on a test environment to avoid modifying production data
- The system won't attempt to solve CAPTCHAs (by design)
- Performance may be slow due to API calls to LLM services
- Test coverage depends on the completeness of the crawl and the quality of the LLM responses

## License

MIT


# notes
Key Components

Orchestrator: The central coordination component that controls the workflow
Browser Controller: Handles browser automation using Playwright
LLM Interface: Communicates with language model APIs (OpenAI or Google)
State Tracker: Keeps track of visited pages and states
Element Extractor: Identifies form elements using LLM and DOM analysis
Test Generator: Creates human-readable test cases
Code Generator: Generates POM-based Python test scripts

Generated Artifacts
The system produces three main outputs:

JSON Metadata: Structured information about all discovered form elements
Human-Readable Test Cases: In Gherkin or plain text format
Executable Test Scripts: Python code following the Page Object Model pattern
