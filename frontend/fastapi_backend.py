from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import json
import asyncio
from datetime import datetime
import hashlib
import subprocess
import tempfile
import os
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import logging
from playwright.async_api import async_playwright
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LLM UI Testing Framework", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB Configuration
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = "llm_testing_framework"
COLLECTION_NAME = "sessions"

# MongoDB client
client = AsyncIOMotorClient(MONGODB_URL)
db = client[DATABASE_NAME]
sessions_collection = db[COLLECTION_NAME]

# Pydantic models
class ElementExtractionRequest(BaseModel):
    web_url: HttpUrl
    config_content: str
    system_prompt: str
    user_prompt: str
    force_new_session: bool = False

class UrlHashCheckRequest(BaseModel):
    web_url: HttpUrl

class UrlHashCheckResponse(BaseModel):
    url: str
    current_hash: str
    existing_sessions: List[Dict[str, Any]]
    has_existing_session: bool

class ElementExtractionResponse(BaseModel):
    session_id: str
    url_hash: str
    extracted_elements: List[Dict[str, Any]]
    timestamp: datetime
    is_new_session: bool

class TestcaseGenerationRequest(BaseModel):
    session_id: str
    extracted_elements: List[Dict[str, Any]]
    system_prompt: str
    user_prompt: str
    testcase_sample: Optional[str] = None

class TestcaseGenerationResponse(BaseModel):
    session_id: str
    test_cases: List[Dict[str, Any]]
    timestamp: datetime

class CodeGenerationRequest(BaseModel):
    session_id: str
    test_cases: List[Dict[str, Any]]
    system_prompt: str
    user_prompt: str

class CodeGenerationResponse(BaseModel):
    session_id: str
    generated_code: str
    timestamp: datetime

class CodeExecutionRequest(BaseModel):
    session_id: str
    code: str
    execution_type: str = "selenium"

class CodeExecutionResponse(BaseModel):
    session_id: str
    execution_result: Dict[str, Any]
    timestamp: datetime

class SessionStatus(BaseModel):
    session_id: str
    url_hash: str
    web_url: str
    current_stage: str
    completed_stages: List[str]
    results: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

# Enhanced element extraction using Playwright
async def extract_elements_with_playwright(url: str, config: dict = None) -> List[Dict[str, Any]]:
    """
    Comprehensively extract all testable elements from web page using Playwright
    """
    elements = []
    
    try:
        async with async_playwright() as p:
            # Launch browser with robust settings
            browser = await p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Set longer timeout for complex pages
            page.set_default_timeout(30000)
            
            # Navigate to URL with error handling
            try:
                await page.goto(url, wait_until='networkidle', timeout=30000)
                await page.wait_for_load_state('domcontentloaded')
                await asyncio.sleep(2)  # Allow dynamic content to load
            except Exception as e:
                logger.warning(f"Page load issue for {url}: {e}")
                # Try alternative loading strategy
                await page.goto(url, wait_until='domcontentloaded', timeout=15000)
                await asyncio.sleep(3)
            
            # Comprehensive element selectors
            selectors = {
                'buttons': [
                    'button', 'input[type="button"]', 'input[type="submit"]', 
                    'input[type="reset"]', '[role="button"]', '.btn', '.button',
                    'a[href^="javascript"]', '[onclick]'
                ],
                'inputs': [
                    'input[type="text"]', 'input[type="email"]', 'input[type="password"]',
                    'input[type="number"]', 'input[type="tel"]', 'input[type="url"]',
                    'input[type="search"]', 'input[type="date"]', 'input[type="time"]',
                    'input[type="datetime-local"]', 'input[type="month"]', 'input[type="week"]',
                    'textarea', 'input:not([type])'
                ],
                'selects': ['select', '[role="combobox"]', '[role="listbox"]'],
                'checkboxes': ['input[type="checkbox"]', '[role="checkbox"]'],
                'radios': ['input[type="radio"]', '[role="radio"]'],
                'links': ['a[href]', '[role="link"]'],
                'interactive': [
                    '[tabindex]', '[role="tab"]', '[role="menuitem"]', 
                    '[role="option"]', '[role="treeitem"]', '[contenteditable="true"]'
                ],
                'forms': ['form'],
                'images': ['img[alt]', 'img[title]', '[role="img"]'],
                'headings': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
                'landmarks': [
                    '[role="navigation"]', '[role="main"]', '[role="banner"]',
                    '[role="contentinfo"]', '[role="complementary"]', '[role="search"]'
                ]
            }
            
            # Extract elements by category
            for category, selector_list in selectors.items():
                for selector in selector_list:
                    try:
                        category_elements = await page.locator(selector).all()
                        
                        for element in category_elements:
                            try:
                                # Get comprehensive element data
                                element_data = await extract_element_data(element, category, page)
                                if element_data and element_data.get('is_visible', False):
                                    elements.append(element_data)
                                    
                            except Exception as e:
                                logger.debug(f"Error extracting element data: {e}")
                                continue
                                
                    except Exception as e:
                        logger.debug(f"Error with selector {selector}: {e}")
                        continue
            
            # Take screenshot for visual reference
            screenshot = await page.screenshot(full_page=True)
            screenshot_b64 = base64.b64encode(screenshot).decode()
            
            await browser.close()
            
            # Remove duplicates and sort elements
            unique_elements = remove_duplicate_elements(elements)
            
            # Add metadata
            metadata = {
                'total_elements': len(unique_elements),
                'extraction_timestamp': datetime.now().isoformat(),
                'url': url,
                'screenshot': screenshot_b64[:1000] + '...' if len(screenshot_b64) > 1000 else screenshot_b64,  # Truncate for hash
                'categories': {category: len([e for e in unique_elements if e.get('category') == category]) 
                             for category in selectors.keys()}
            }
            
            return unique_elements + [{'type': 'metadata', 'data': metadata}]
            
    except Exception as e:
        logger.error(f"Playwright extraction failed for {url}: {e}")
        raise HTTPException(status_code=500, detail=f"Element extraction failed: {str(e)}")

async def extract_element_data(element, category: str, page) -> Dict[str, Any]:
    """Extract comprehensive data from a single element"""
    try:
        # Check if element is visible and interactable
        is_visible = await element.is_visible()
        is_enabled = await element.is_enabled() if category in ['buttons', 'inputs', 'selects'] else True
        
        if not is_visible:
            return None
            
        # Get bounding box
        bbox = await element.bounding_box()
        
        # Get element attributes
        tag_name = await element.evaluate('el => el.tagName.toLowerCase()')
        
        # Common attributes
        attrs = {}
        for attr in ['id', 'class', 'name', 'type', 'value', 'placeholder', 'title', 'alt', 'href', 'src', 'role']:
            try:
                attr_value = await element.get_attribute(attr)
                if attr_value:
                    attrs[attr] = attr_value
            except:
                pass
        
        # Get text content
        text_content = ''
        try:
            text_content = (await element.text_content() or '').strip()
            if not text_content and category == 'inputs':
                text_content = attrs.get('placeholder', '')
        except:
            pass
        
        # Generate robust selectors
        selectors = await generate_robust_selectors(element, page)
        
        element_data = {
            'category': category,
            'tag_name': tag_name,
            'text': text_content,
            'attributes': attrs,
            'selectors': selectors,
            'bounding_box': bbox,
            'is_visible': is_visible,
            'is_enabled': is_enabled,
            'element_type': determine_element_type(tag_name, attrs, category)
        }
        
        return element_data
        
    except Exception as e:
        logger.debug(f"Error extracting element data: {e}")
        return None

async def generate_robust_selectors(element, page) -> Dict[str, str]:
    """Generate multiple robust selectors for an element"""
    selectors = {}
    
    try:
        # CSS selectors
        selectors['css'] = await element.evaluate('''
            el => {
                let selector = el.tagName.toLowerCase();
                if (el.id) selector += '#' + el.id;
                if (el.className) selector += '.' + el.className.split(' ').join('.');
                return selector;
            }
        ''')
        
        # XPath
        selectors['xpath'] = await element.evaluate('''
            el => {
                let path = '';
                while (el && el.nodeType === Node.ELEMENT_NODE) {
                    let siblingIndex = 1;
                    let sibling = el.previousSibling;
                    while (sibling) {
                        if (sibling.nodeType === Node.ELEMENT_NODE && sibling.tagName === el.tagName) {
                            siblingIndex++;
                        }
                        sibling = sibling.previousSibling;
                    }
                    path = el.tagName.toLowerCase() + '[' + siblingIndex + ']' + (path ? '/' + path : '');
                    el = el.parentNode;
                }
                return '//' + path;
            }
        ''')
        
        # Text-based selector if element has text
        text = await element.text_content()
        if text and text.strip():
            selectors['text'] = f"text='{text.strip()[:50]}'"
        
        # Attribute-based selectors
        id_attr = await element.get_attribute('id')
        if id_attr:
            selectors['id'] = f"[id='{id_attr}']"
            
        name_attr = await element.get_attribute('name')
        if name_attr:
            selectors['name'] = f"[name='{name_attr}']"
            
    except Exception as e:
        logger.debug(f"Error generating selectors: {e}")
    
    return selectors

def determine_element_type(tag_name: str, attrs: Dict, category: str) -> str:
    """Determine specific element type for testing purposes"""
    if tag_name == 'input':
        input_type = attrs.get('type', 'text')
        return f"input_{input_type}"
    elif tag_name == 'button':
        return 'button'
    elif tag_name == 'a':
        return 'link'
    elif tag_name == 'select':
        return 'dropdown'
    elif tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
        return 'heading'
    elif tag_name == 'form':
        return 'form'
    elif attrs.get('role'):
        return f"role_{attrs['role']}"
    else:
        return tag_name

def remove_duplicate_elements(elements: List[Dict]) -> List[Dict]:
    """Remove duplicate elements based on selectors and position"""
    seen = set()
    unique_elements = []
    
    for element in elements:
        # Create a unique key based on selectors and position
        selectors = element.get('selectors', {})
        bbox = element.get('bounding_box', {})
        
        key = f"{selectors.get('css', '')}-{selectors.get('xpath', '')}-{bbox.get('x', 0)}-{bbox.get('y', 0)}"
        
        if key not in seen:
            seen.add(key)
            unique_elements.append(element)
    
    return unique_elements

def calculate_url_hash(elements: List[Dict[str, Any]], url: str) -> str:
    """Calculate hash based on extracted elements and URL structure"""
    # Create a stable representation for hashing
    hash_data = {
        'url': url,
        'elements_count': len([e for e in elements if e.get('type') != 'metadata']),
        'structure': []
    }
    
    # Sort elements by position for consistent hashing
    sorted_elements = sorted(
        [e for e in elements if e.get('type') != 'metadata'],
        key=lambda x: (
            x.get('bounding_box', {}).get('y', 0),
            x.get('bounding_box', {}).get('x', 0),
            x.get('tag_name', ''),
            x.get('text', '')
        )
    )
    
    # Create structural fingerprint
    for element in sorted_elements:
        structure_item = {
            'tag': element.get('tag_name', ''),
            'type': element.get('element_type', ''),
            'text_hash': hashlib.md5((element.get('text', '') or '').encode()).hexdigest()[:8],
            'attrs_hash': hashlib.md5(str(sorted(element.get('attributes', {}).items())).encode()).hexdigest()[:8]
        }
        hash_data['structure'].append(structure_item)
    
    # Generate hash
    hash_string = json.dumps(hash_data, sort_keys=True)
    return hashlib.sha256(hash_string.encode()).hexdigest()[:16]

# Database operations with hash-based sessions
async def check_existing_sessions(url: str, current_hash: str) -> Dict[str, Any]:
    """Check for existing sessions for the given URL"""
    try:
        # Find all sessions for this URL
        cursor = sessions_collection.find(
            {"web_url": url}
        ).sort("updated_at", -1)
        
        existing_sessions = await cursor.to_list(length=50)
        
        # Check if current hash matches any existing session
        matching_session = None
        for session in existing_sessions:
            if session.get('url_hash') == current_hash:
                matching_session = session
                break
        
        return {
            'url': url,
            'current_hash': current_hash,
            'existing_sessions': [
                {
                    'session_id': session['session_id'],
                    'url_hash': session['url_hash'],
                    'current_stage': session['current_stage'],
                    'completed_stages': session['completed_stages'],
                    'created_at': session['created_at'],
                    'updated_at': session['updated_at']
                }
                for session in existing_sessions[:10]  # Limit to recent 10
            ],
            'has_matching_session': matching_session is not None,
            'matching_session': matching_session
        }
        
    except Exception as e:
        logger.error(f"Error checking existing sessions: {e}")
        return {
            'url': url,
            'current_hash': current_hash,
            'existing_sessions': [],
            'has_matching_session': False,
            'matching_session': None
        }

async def create_session_document(session_data: dict) -> str:
    """Create a new session document in MongoDB using hash as ID"""
    session_data["_id"] = session_data["session_id"]
    try:
        await sessions_collection.insert_one(session_data)
        logger.info(f"Created session: {session_data['session_id']}")
        return session_data["session_id"]
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

async def update_session_document(session_id: str, update_data: dict) -> bool:
    """Update session document in MongoDB"""
    update_data["updated_at"] = datetime.now()
    try:
        result = await sessions_collection.update_one(
            {"_id": session_id},
            {"$set": update_data}
        )
        logger.info(f"Updated session: {session_id}")
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update session")

async def get_session_document(session_id: str) -> dict:
    """Get session document from MongoDB"""
    try:
        session = await sessions_collection.find_one({"_id": session_id})
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to get session")

async def get_last_session() -> Optional[dict]:
    """Get the most recently updated session"""
    try:
        cursor = sessions_collection.find().sort("updated_at", -1).limit(1)
        sessions = await cursor.to_list(length=1)
        return sessions[0] if sessions else None
    except Exception as e:
        logger.error(f"Error getting last session: {e}")
        return None

# Mock LLM function (replace with actual LLM integration)
async def call_llm(prompt: str, context: str = "") -> str:
    """Mock LLM call - replace with actual LLM integration"""
    await asyncio.sleep(1)  # Simulate API call delay
    
    if "extract elements" in prompt.lower() or "test cases" in prompt.lower():
        return json.dumps([
            {"test_name": "Login with valid credentials", "steps": ["Enter username", "Enter password", "Click submit"], "expected": "User should be logged in"},
            {"test_name": "Login with invalid credentials", "steps": ["Enter invalid username", "Enter invalid password", "Click submit"], "expected": "Error message should appear"},
            {"test_name": "Form validation", "steps": ["Leave required fields empty", "Try to submit"], "expected": "Validation errors should appear"},
            {"test_name": "Navigation test", "steps": ["Click navigation links"], "expected": "Should navigate to correct pages"}
        ])
    else:
        return '''import pytest
from playwright.sync_api import sync_playwright, Page, Browser
import time

class TestWebPage:
    def setup_method(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.goto("''' + context.get('web_url', 'https://example.com') + '''")
        
    def test_page_elements_visible(self):
        """Test that key elements are visible and interactable"""
        try:
            # Test buttons
            buttons = self.page.locator('button, input[type="button"], input[type="submit"]').all()
            assert len(buttons) > 0, "No buttons found on page"
            
            for button in buttons[:3]:  # Test first 3 buttons
                assert button.is_visible(), f"Button not visible: {button}"
                
            # Test inputs
            inputs = self.page.locator('input[type="text"], input[type="email"], input[type="password"]').all()
            for input_elem in inputs[:3]:  # Test first 3 inputs
                assert input_elem.is_visible(), f"Input not visible: {input_elem}"
                
            print("✓ Page elements visibility test passed")
        except Exception as e:
            print(f"✗ Page elements test failed: {e}")
            raise
            
    def test_form_interactions(self):
        """Test form interactions"""
        try:
            # Find forms
            forms = self.page.locator('form').all()
            if forms:
                form = forms[0]
                inputs = form.locator('input[type="text"], input[type="email"]').all()
                
                for i, input_elem in enumerate(inputs[:2]):
                    input_elem.fill(f"test_value_{i}")
                    
                print("✓ Form interaction test passed")
            else:
                print("ℹ No forms found for testing")
        except Exception as e:
            print(f"✗ Form interaction test failed: {e}")
            
    def test_navigation_links(self):
        """Test navigation links"""
        try:
            links = self.page.locator('a[href]').all()
            working_links = 0
            
            for link in links[:5]:  # Test first 5 links
                href = link.get_attribute('href')
                if href and not href.startswith('javascript:') and not href.startswith('#'):
                    working_links += 1
                    
            assert working_links > 0, "No working navigation links found"
            print(f"✓ Navigation test passed - {working_links} working links found")
        except Exception as e:
            print(f"✗ Navigation test failed: {e}")
            
    def teardown_method(self):
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

if __name__ == "__main__":
    test = TestWebPage()
    test.setup_method()
    test.test_page_elements_visible()
    test.test_form_interactions()
    test.test_navigation_links()
    test.teardown_method()'''

async def execute_test_code(code: str, execution_type: str) -> Dict[str, Any]:
    """Execute the generated test code"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        # Execute the code
        if execution_type == "python":
            result = subprocess.run(
                ["python", temp_file_path],
                capture_output=True,
                text=True,
                timeout=120  # Increased timeout for playwright
            )
        elif execution_type == "pytest":
            result = subprocess.run(
                ["python", "-m", "pytest", temp_file_path, "-v"],
                capture_output=True,
                text=True,
                timeout=120
            )
        else:  # Default to python execution
            result = subprocess.run(
                ["python", temp_file_path],
                capture_output=True,
                text=True,
                timeout=120
            )
        
        # Clean up
        os.unlink(temp_file_path)
        
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "execution_type": execution_type
        }
    
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": "Execution timed out after 120 seconds",
            "execution_type": execution_type
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": -1,
            "stdout": "",
            "stderr": f"Execution error: {str(e)}",
            "execution_type": execution_type
        }

# API Endpoints
@app.post("/api/check-url-hash", response_model=UrlHashCheckResponse)
async def check_url_hash(request: UrlHashCheckRequest):
    """Check if URL has existing sessions and get current hash"""
    try:
        # Extract elements to calculate current hash
        elements = await extract_elements_with_playwright(str(request.web_url))
        current_hash = calculate_url_hash(elements, str(request.web_url))
        
        # Check existing sessions
        session_check = await check_existing_sessions(str(request.web_url), current_hash)
        
        return UrlHashCheckResponse(
            url=str(request.web_url),
            current_hash=current_hash,
            existing_sessions=session_check['existing_sessions'],
            has_existing_session=session_check['has_matching_session']
        )
        
    except Exception as e:
        logger.error(f"URL hash check failed: {e}")
        raise HTTPException(status_code=500, detail=f"URL hash check failed: {str(e)}")

@app.post("/api/extract-elements", response_model=ElementExtractionResponse)
async def extract_elements(request: ElementExtractionRequest):
    """Extract UI elements from the provided web URL"""
    try:
        # Extract elements using Playwright
        elements = await extract_elements_with_playwright(str(request.web_url))
        url_hash = calculate_url_hash(elements, str(request.web_url))
        
        # Check if we should use existing session or create new one
        if not request.force_new_session:
            session_check = await check_existing_sessions(str(request.web_url), url_hash)
            if session_check['has_matching_session']:
                existing_session = session_check['matching_session']
                return ElementExtractionResponse(
                    session_id=existing_session['session_id'],
                    url_hash=url_hash,
                    extracted_elements=existing_session['extracted_elements'],
                    timestamp=existing_session['updated_at'],
                    is_new_session=False
                )
        
        # Create new session with hash as ID
        session_id = url_hash
        session_data = {
            "session_id": session_id,
            "url_hash": url_hash,
            "current_stage": "element_extraction_complete",
            "completed_stages": ["element_extraction"],
            "web_url": str(request.web_url),
            "config_content": request.config_content,
            "extracted_elements": elements,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        await create_session_document(session_data)
        
        return ElementExtractionResponse(
            session_id=session_id,
            url_hash=url_hash,
            extracted_elements=elements,
            timestamp=datetime.now(),
            is_new_session=True
        )
        
    except Exception as e:
        logger.error(f"Element extraction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Element extraction failed: {str(e)}")

@app.post("/api/generate-testcases", response_model=TestcaseGenerationResponse)
async def generate_testcases(request: TestcaseGenerationRequest):
    """Generate test cases based on extracted elements"""
    session = await get_session_document(request.session_id)
    
    # Construct prompt for testcase generation
    full_prompt = f"""
    System: {request.system_prompt}
    User: {request.user_prompt}
    
    Extracted Elements: {json.dumps(request.extracted_elements[:20])}  # Limit for prompt size
    {f"Sample Testcase: {request.testcase_sample}" if request.testcase_sample else ""}
    
    Please generate comprehensive test cases for these UI elements focusing on user interactions.
    """
    
    try:
        # Call LLM to generate test cases
        llm_response = await call_llm(full_prompt)
        test_cases = json.loads(llm_response)
        
        # Update session document
        update_data = {
            "current_stage": "testcase_generation_complete",
            "completed_stages": session["completed_stages"] + ["testcase_generation"],
            "test_cases": test_cases
        }
        
        await update_session_document(request.session_id, update_data)
        
        return TestcaseGenerationResponse(
            session_id=request.session_id,
            test_cases=test_cases,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Testcase generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Testcase generation failed: {str(e)}")

@app.post("/api/generate-code", response_model=CodeGenerationResponse)
async def generate_code(request: CodeGenerationRequest):
    """Generate test code based on test cases"""
    session = await get_session_document(request.session_id)
    
    # Construct prompt for code generation
    full_prompt = f"""
    System: {request.system_prompt}
    User: {request.user_prompt}
    
    Test Cases: {json.dumps(request.test_cases)}
    Web URL: {session.get('web_url', '')}
    
    Please generate complete, executable Playwright test code for these test cases.
    """
    
    try:
        # Call LLM to generate code
        generated_code = await call_llm(full_prompt, {'web_url': session.get('web_url', '')})
        
        # Update session document
        update_data = {
            "current_stage": "code_generation_complete",
            "completed_stages": session["completed_stages"] + ["code_generation"],
            "generated_code": generated_code
        }
        
        await update_session_document(request.session_id, update_data)
        
        return CodeGenerationResponse(
            session_id=request.session_id,
            generated_code=generated_code,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Code generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code generation failed: {str(e)}")

@app.post("/api/execute-code", response_model=CodeExecutionResponse)
async def execute_code(request: CodeExecutionRequest):
    """Execute the generated test code"""
    session = await get_session_document(request.session_id)
    
    try:
        # Execute the code
        execution_result = await execute_test_code(request.code, request.execution_type)
        
        # Update session document
        update_data = {
            "current_stage": "code_execution_complete",
            "completed_stages": session["completed_stages"] + ["code_execution"],
            "execution_result": execution_result
        }
        
        await update_session_document(request.session_id, update_data)
        
        return CodeExecutionResponse(
            session_id=request.session_id,
            execution_result=execution_result,
            timestamp=datetime.now()
        )
    except Exception as e:
        logger.error(f"Code execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")

@app.get("/api/session/{session_id}", response_model=SessionStatus)
async def get_session_status(session_id: str):
    """Get current session status and results"""
    session = await get_session_document(session_id)
    
    return SessionStatus(
        session_id=session_id,
        url_hash=session["url_hash"],
        web_url=session["web_url"],
        current_stage=session["current_stage"],
        completed_stages=session["completed_stages"],
        results={
            "extracted_elements": session.get("extracted_elements"),
            "test_cases": session.get("test_cases"),
            "generated_code": session.get("generated_code"),
            "execution_result": session.get("execution_result")
        },
        created_at=session["created_at"],
        updated_at=session["updated_at"]
    )

@app.get("/api/url-history/{url_encoded}")
async def get_url_history(url_encoded: str):
    """Get session history for a specific URL"""
    try:
        # Decode URL
        import urllib.parse
        url = urllib.parse.unquote(url_encoded)
        
        cursor = sessions_collection.find(
            {"web_url": url}
        ).sort("updated_at", -1)
        
        sessions = await cursor.to_list(length=20)
        
        return {
            "url": url,
            "sessions": [
                {
                    "session_id": session["session_id"],
                    "url_hash": session["url_hash"],
                    "current_stage": session["current_stage"],
                    "completed_stages": session["completed_stages"],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "elements_count": len(session.get("extracted_elements", []))
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error getting URL history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get URL history")

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    try:
        cursor = sessions_collection.find().sort("updated_at", -1)
        sessions = await cursor.to_list(length=100)
        
        return {
            "sessions": [
                {
                    "session_id": session["session_id"],
                    "url_hash": session["url_hash"],
                    "current_stage": session["current_stage"],
                    "created_at": session["created_at"],
                    "updated_at": session["updated_at"],
                    "web_url": session.get("web_url")
                }
                for session in sessions
            ]
        }
    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to list sessions")

@app.get("/api/last-session")
async def get_last_session_endpoint():
    """Get the most recently updated session"""
    session = await get_last_session()
    if not session:
        return {"session": None}
    
    return {
        "session": {
            "session_id": session["session_id"],
            "url_hash": session["url_hash"],
            "current_stage": session["current_stage"],
            "completed_stages": session["completed_stages"],
            "results": {
                "extracted_elements": session.get("extracted_elements"),
                "test_cases": session.get("test_cases"),
                "generated_code": session.get("generated_code"),
                "execution_result": session.get("execution_result")
            },
            "web_url": session.get("web_url"),
            "config_content": session.get("config_content"),
            "created_at": session["created_at"],
            "updated_at": session["updated_at"]
        }
    }

@app.delete("/api/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        result = await sessions_collection.delete_one({"_id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test MongoDB connection
        await sessions_collection.find_one({})
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "database": "connected",
            "playwright": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "database": "disconnected",
            "error": str(e)
        }

@app.on_event("startup")
async def startup_event():
    """Initialize database indexes on startup"""
    try:
        # Create indexes for better performance
        await sessions_collection.create_index("session_id")
        await sessions_collection.create_index("url_hash")
        await sessions_collection.create_index("web_url")
        await sessions_collection.create_index("updated_at")
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating database indexes: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)