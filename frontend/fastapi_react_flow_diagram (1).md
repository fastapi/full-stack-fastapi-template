# LLM UI Testing Framework - Enhanced Flow Diagram (Hash-based Sessions)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                    REACT FRONTEND                                       │
│                                 (http://localhost:3000)                                 │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                            ENHANCED UI COMPONENTS & STATE                               │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │   Step Indicator │  │   Element Form  │  │  Testcase Form  │  │   Code Form     │    │
│  │   ┌─┬─┬─┬─┐      │  │   • Web URL +   │  │   • Enhanced    │  │   • Playwright  │    │
│  │   │1│2│3│4│      │  │     History btn │  │     Prompts     │  │     Code Gen    │    │
│  │   └─┴─┴─┴─┘      │  │   • Config      │  │   • Test Cases  │  │   • Robust      │    │
│  └──────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐    │
│  │ Execute Form    │  │ Session Dialog  │  │ History Modal   │  │ Hash Management │    │
│  │ • Playwright    │  │ • Load Previous │  │ • URL Sessions  │  │ • URL Hash      │    │
│  │ • Python/Pytest │  │ • Start Fresh   │  │ • Timeline      │  │ • Session ID    │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘    │
│                                            │                                           │
│  ┌─────────────────────────────────────────┼─────────────────────────────────────────┐  │
│  │               ENHANCED SESSION MGMT     │              RESULTS DISPLAY            │  │
│  │   • currentStep: number (0-3)           │   • elements: Comprehensive JSON       │  │
│  │   • sessionId: string (URL Hash)        │   • testcases: Enhanced scenarios      │  │
│  │   • urlHash: string (Content Hash)      │   • code: Playwright test code         │  │
│  │   • sessionDialogData: Object           │   • execution: Detailed results        │  │
│  │   • urlHistory: Array                   │   • element categories & metadata      │  │
│  └─────────────────────────────────────────┴─────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
       ┌───────────────┬───────────────────┼───────────────────┬───────────────┐
       │               │                   │                   │               │
       ▼               ▼                   ▼                   ▼               ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│    POST     │ │    POST     │ │    POST     │ │    POST     │ │     GET     │ │     GET     │
│/check-url-  │ │/extract-    │ │/generate-   │ │/generate-   │ │/execute-    │ │/url-history/│
│hash         │ │elements     │ │testcases    │ │code         │ │code         │ │{url}        │
│             │ │             │ │             │ │             │ │             │ │             │
│ • Hash calc │ │ • Playwright│ │ • Enhanced  │ │ • Playwright│ │ • Enhanced  │ │ • Session   │
│ • Session   │ │ • Elements  │ │   test cases│ │   code gen  │ │   execution │ │   history   │
│   check     │ │ • Hash-based│ │ • Context   │ │ • Context   │ │ • Timeout   │ │ • Timeline  │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
       │               │                   │                   │               │
       └───────────────┼───────────────────┼───────────────────┼───────────────┘
                       │                   │                   │
                       └───────────────────┼───────────────────┘
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                 ENHANCED FASTAPI BACKEND                                │
│                                (http://localhost:8000)                                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                         ENHANCED API ENDPOINTS                                  │    │
│  │                                                                                 │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────┐ │    │
│  │  │ /check-url-  │ │ /extract-    │ │ /generate-   │ │ /generate-   │ │/execute│ │    │
│  │  │ hash         │ │ elements     │ │ testcases    │ │ code         │ │-code   │ │    │
│  │  │              │ │              │ │              │ │              │ │        │ │    │
│  │  │ • Calculate  │ │ • Playwright │ │ • Enhanced   │ │ • Playwright │ │• 120s  │ │    │
│  │  │   hash       │ │   extraction │ │   prompts    │ │   code gen   │ │timeout │ │    │
│  │  │ • Find       │ │ • Hash calc  │ │ • Context    │ │ • Context    │ │• Result│ │    │
│  │  │   existing   │ │ • Session    │ │   aware      │ │   aware      │ │detail  │ │    │
│  │  │   sessions   │ │   mgmt       │ │              │ │              │ │        │ │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └────────┘ │    │
│  │                                                                                 │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │    │
│  │  │ /url-history/│ │ /session/    │ │ /sessions    │ │ /last-       │            │    │
│  │  │ {url}        │ │ {id}         │ │              │ │ session      │            │    │
│  │  │              │ │              │ │              │ │              │            │    │
│  │  │ • URL-based  │ │ • Hash-based │ │ • All        │ │ • Recent     │            │    │
│  │  │   history    │ │   lookup     │ │   sessions   │ │   session    │            │    │
│  │  │ • Timeline   │ │ • Complete   │ │ • Pagination │ │ • Auto-load  │            │    │
│  │  │   view       │ │   data       │ │              │ │              │            │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘            │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                             │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                      ENHANCED REQUEST PROCESSING                                │    │
│  │                                                                                 │    │
│  │  1. ┌─────────────────┐  2. ┌─────────────────┐  3. ┌─────────────────┐         │    │
│  │     │ URL Hash Check  │ ──> │ Playwright      │ ──> │ LLM/Execution   │         │    │
│  │     │                 │     │ Extraction      │     │ Services        │         │    │
│  │     │ • Extract with  │     │                 │     │                 │         │    │
│  │     │   Playwright    │     │ • Comprehensive │     │ • Context-aware │         │    │
│  │     │ • Calculate     │     │   element scan  │     │   prompts       │         │    │
│  │     │   content hash  │     │ • Robust        │     │ • Enhanced code │         │    │
│  │     │ • Check         │     │   selectors     │     │   generation    │         │    │
│  │     │   existing      │     │ • Categories    │     │ • Secure        │         │    │
│  │     │   sessions      │     │ • Metadata      │     │   execution     │         │    │
│  │     └─────────────────┘     └─────────────────┘     └─────────────────┘         │    │
│  │                                        │                       │                │    │
│  │  4. ┌─────────────────┐  5. ┌─────────────────┐                │                │    │
│  │     │ Hash-based      │ <── │ Process Results │ <──────────────┘                │    │
│  │     │ Session Update  │     │                 │                                 │    │
│  │     │                 │     │ • Validate data │                                 │    │
│  │     │ • Use hash as   │     │ • Format output │                                 │    │
│  │     │   session ID    │     │ • Error         │                                 │    │
│  │     │ • Track UI      │     │   handling      │                                 │    │
│  │     │   changes       │     │ • Logging       │                                 │    │
│  │     │ • Maintain      │     │                 │                                 │    │
│  │     │   history       │     │                 │                                 │    │
│  │     └─────────────────┘     └─────────────────┘                                 │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                             │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    ENHANCED MONGODB DATABASE STORAGE                            │    │
│  │                     (mongodb://localhost:27017)                                │    │
│  │                                                                                 │    │
│  │  Database: llm_testing_framework                                               │    │
│  │  Collection: sessions                                                           │    │
│  │                                                                                 │    │
│  │  Enhanced Document Schema:                                                      │    │
│  │  {                                                                              │    │
│  │    "_id": "url_content_hash_16_chars",  # Hash as primary key                  │    │
│  │    "session_id": "url_content_hash_16_chars",                                  │    │
│  │    "url_hash": "url_content_hash_16_chars",                                    │    │
│  │    "web_url": "https://example.com",                                           │    │
│  │    "current_stage": "code_execution_complete",                                 │    │
│  │    "completed_stages": ["element_extraction", "testcase_generation",          │    │
│  │                         "code_generation", "code_execution"],                 │    │
│  │    "config_content": "playwright_config...",                                  │    │
│  │    "extracted_elements": [                                                     │    │
│  │      {                                                                         │    │
│  │        "category": "buttons",                                                  │    │
│  │        "tag_name": "button",                                                   │    │
│  │        "text": "Submit",                                                       │    │
│  │        "attributes": {"id": "submit-btn", "class": "btn primary"},            │    │
│  │        "selectors": {                                                          │    │
│  │          "css": "button#submit-btn.btn.primary",                              │    │
│  │          "xpath": "//button[@id='submit-btn'][1]",                            │    │
│  │          "text": "text='Submit'",                                             │    │
│  │          "id": "[id='submit-btn']"                                             │    │
│  │        },                                                                      │    │
│  │        "bounding_box": {"x": 100, "y": 200, "width": 80, "height": 30},      │    │
│  │        "is_visible": true,                                                     │    │
│  │        "is_enabled": true,                                                     │    │
│  │        "element_type": "button"                                                │    │
│  │      },                                                                        │    │
│  │      ... more elements ...,                                                   │    │
│  │      {                                                                         │    │
│  │        "type": "metadata",                                                     │    │
│  │        "data": {                                                               │    │
│  │          "total_elements": 45,                                                 │    │
│  │          "extraction_timestamp": "2025-06-08T...",                            │    │
│  │          "url": "https://example.com",                                        │    │
│  │          "screenshot": "base64_truncated...",                                 │    │
│  │          "categories": {                                                       │    │
│  │            "buttons": 8, "inputs": 12, "links": 15,                          │    │
│  │            "forms": 2, "selects": 3, "checkboxes": 5                         │    │
│  │          }                                                                     │    │
│  │        }                                                                       │    │
│  │      }                                                                         │    │
│  │    ],                                                                          │    │
│  │    "test_cases": [                                                             │    │
│  │      {                                                                         │    │
│  │        "test_name": "Enhanced form submission test",                          │    │
│  │        "steps": ["Fill form fields", "Validate inputs", "Submit form"],      │    │
│  │        "expected": "Form should submit successfully with validation"          │    │
│  │      }                                                                         │    │
│  │    ],                                                                          │    │
│  │    "generated_code": "import pytest\nfrom playwright.sync_api import...",     │    │
│  │    "execution_result": {                                                      │    │
│  │      "success": true,                                                         │    │
│  │      "returncode": 0,                                                         │    │
│  │      "stdout": "Playwright test execution output...",                        │    │
│  │      "stderr": "",                                                            │    │
│  │      "execution_type": "python"                                               │    │
│  │    },                                                                          │    │
│  │    "created_at": "2025-06-08T...",                                            │    │
│  │    "updated_at": "2025-06-08T..."                                             │    │
│  │  }                                                                             │    │
│  │                                                                                │    │
│  │  Enhanced Indexes: session_id, url_hash, web_url, updated_at                  │    │
│  │  Motor AsyncIO Client for high-performance async operations                   │    │
│  │  URL-based session grouping for historical tracking                           │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                        ENHANCED PLAYWRIGHT & LLM SERVICES                               │
│                           (Comprehensive Extraction + Code Generation)                  │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    PLAYWRIGHT ELEMENT EXTRACTION ENGINE                         │    │
│  │                                                                                 │    │
│  │  async def extract_elements_with_playwright(url, config):                      │    │
│  │                                                                                 │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │ Browser Launch  │  │ Comprehensive   │  │ Element Data    │                  │    │
│  │  │                 │  │ Element Scan    │  │ Extraction      │                  │    │
│  │  │ • Chromium      │  │                 │  │                 │                  │    │
│  │  │ • No sandbox    │  │ • Buttons       │  │ • Tag name      │                  │    │
│  │  │ • 1920x1080     │  │ • Inputs (all)  │  │ • Text content  │                  │    │
│  │  │ • User agent    │  │ • Selects       │  │ • Attributes    │                  │    │
│  │  │ • 30s timeout   │  │ • Checkboxes    │  │ • Bounding box  │                  │    │
│  │  │                 │  │ • Radios        │  │ • Visibility    │                  │    │
│  │  │                 │  │ • Links         │  │ • Enabled state │                  │    │
│  │  │                 │  │ • Interactive   │  │ • Element type  │                  │    │
│  │  │                 │  │ • Forms         │  │                 │                  │    │
│  │  │                 │  │ • Images        │  │                 │                  │    │
│  │  │                 │  │ • Headings      │  │                 │                  │    │
│  │  │                 │  │ • Landmarks     │  │                 │                  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │    │
│  │                                                                                 │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │ Robust Selector │  │ Duplicate       │  │ Hash Calculation│                  │    │
│  │  │ Generation      │  │ Removal         │  │                 │                  │    │
│  │  │                 │  │                 │  │ • URL structure │                  │    │
│  │  │ • CSS selector  │  │ • Position-     │  │ • Element count │                  │    │
│  │  │ • XPath         │  │   based         │  │ • Structural    │                  │    │
│  │  │ • Text-based    │  │ • Selector-     │  │   fingerprint   │                  │    │
│  │  │ • ID-based      │  │   based         │  │ • Content hash  │                  │    │
│  │  │ • Name-based    │  │ • Unique key    │  │ • SHA256 (16)   │                  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                             │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                       ENHANCED LLM SERVICE INTEGRATION                          │    │
│  │                                                                                 │    │
│  │  async def call_llm(prompt, context):                                          │    │
│  │                                                                                 │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │ Test Case       │  │ Playwright Code │  │ Context-Aware   │                  │    │
│  │  │ Generation      │  │ Generation      │  │ Processing      │                  │    │
│  │  │                 │  │                 │  │                 │                  │    │
│  │  │ Returns:        │  │ Returns:        │  │ • Element       │                  │    │
│  │  │ Enhanced JSON   │  │ Complete        │  │   categories    │                  │    │
│  │  │ test scenarios  │  │ Playwright code │  │ • URL context   │                  │    │
│  │  │                 │  │                 │  │ • Test focus    │                  │    │
│  │  │ [               │  │ import pytest   │  │ • Robust        │                  │    │
│  │  │   {             │  │ from playwright │  │   selectors     │                  │    │
│  │  │     "test_name":│  │ ...             │  │ • Error         │                  │    │
│  │  │     "steps":    │  │ class TestPage: │  │   handling      │                  │    │
│  │  │     "expected": │  │   def setup():  │  │                 │                  │    │
│  │  │     "priority": │  │   def test_():  │  │                 │                  │    │
│  │  │   }             │  │   def teardown()│  │                 │                  │    │
│  │  │ ]               │  │                 │  │                 │                  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                             │
│                                           ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────────────┐    │
│  │                    ENHANCED CODE EXECUTION ENGINE                               │    │
│  │                                                                                 │    │
│  │  async def execute_test_code(code, execution_type):                            │    │
│  │                                                                                 │    │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │    │
│  │  │ Secure File     │  │ Enhanced        │  │ Detailed        │                  │    │
│  │  │ Handling        │  │ Execution       │  │ Results         │                  │    │
│  │  │                 │  │                 │  │                 │                  │    │
│  │  │ • Temp file     │  │ subprocess.run( │  │ {               │                  │    │
│  │  │   creation      │  │   ["python",    │  │   "success":    │                  │    │
│  │  │ • Write code    │  │    temp_file],  │  │   "returncode": │                  │    │
│  │  │ • Permission    │  │   capture=True, │  │   "stdout":     │                  │    │
│  │  │   handling      │  │   timeout=120   │  │   "stderr":     │                  │    │
│  │  │ • Auto cleanup  │  │ )               │  │   "exec_type":  │                  │    │
│  │  │                 │  │                 │  │   "timestamp":  │                  │    │
│  │  │                 │  │ Types:          │  │ }               │                  │    │
│  │  │                 │  │ • python        │  │                 │                  │    │
│  │  │                 │  │ • pytest        │  │                 │                  │    │
│  │  │                 │  │ • playwright    │  │                 │                  │    │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │    │
│  │                                                                                 │    │
│  │  Security: 120s timeout, temp file cleanup, sandboxed subprocess execution     │    │
│  │  Error handling: Timeout, permission, execution errors with detailed logging   │    │
│  └─────────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              ENHANCED DATA FLOW SUMMARY                                 │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  1. INTELLIGENT SESSION MANAGEMENT                                                      │
│     │                                                                                   │
│     ├─► URL Input & Hash Check                                                          │
│     │   • User enters URL                                                               │
│     │   • POST /api/check-url-hash                                                      │
│     │   • Playwright extracts elements comprehensively                                  │
│     │   • Calculate content-based hash (SHA256)                                         │
│     │   • Check existing sessions for URL                                               │
│     │   • Return hash + existing session list                                           │
│     │                                                                                   │
│     ├─► Smart Session Dialog                                                            │
│     │   • If existing sessions found, show dialog                                       │
│     │   • User can choose: Load Previous or Start Fresh                                 │
│     │   • Display session metadata (stages, dates, elements count)                      │
│     │   • Hash-based session identification                                             │
│     │                                                                                   │
│  2. ENHANCED 4-STEP WORKFLOW                                                            │
│     │                                                                                   │
│     ├─► Step 1: Enhanced Element Extraction                                             │
│     │   • Playwright comprehensive scan (10+ element types)                             │
│     │   • Robust selector generation (CSS, XPath, Text, ID)                             │
│     │   • Element categorization and metadata                                           │
│     │   • Content hash calculation for session ID                                       │
│     │   • Store in MongoDB with hash as primary key                                     │
│     │                                                                                   │
│     ├─► Step 2: Context-Aware Test Case Generation                                      │
│     │   • Enhanced prompts with element context                                         │
│     │   • Comprehensive test scenarios (positive/negative/edge)                         │
│     │   • User workflow and interaction testing                                         │
│     │   • Priority-based test case organization                                         │
│     │                                                                                   │
│     ├─► Step 3: Playwright Code Generation                                              │
│     │   • Generate production-ready Playwright test code                                │
│     │   • Robust error handling and assertions                                          │
│     │   • Context-aware selectors from extraction                                       │
│     │   • Setup, teardown, and configuration management                                 │
│     │                                                                                   │
│     └─► Step 4: Enhanced Code Execution                                                 │
│         • Support for Python, Pytest, Playwright execution                             │
│         • 120-second timeout for complex tests                                          │
│         • Detailed execution results with stdout/stderr                                 │
│         • Secure temporary file handling                                                │
│                                                                                         │
│  3. INTELLIGENT HISTORY & VERSION TRACKING                                              │
│     • Hash-based session identification enables UI change tracking                      │
│     • URL history shows evolution of page structure over time                           │
│     • Historical sessions preserved for comparison and analysis                         │
│     • Timeline view of testing sessions for each URL                                    │
│                                                                                         │
│  4. PRODUCTION-READY FEATURES                                                           │
│     • MongoDB with optimized indexes for hash and URL-based queries                    │
│     • Playwright browser automation with comprehensive element detection                │
│     • Secure code execution with timeout and sandboxing                                │
│     • Enhanced error handling and detailed logging                                      │
│     • Session restoration and state management                                          │
│     • Responsive UI with loading states and progress indicators                         │
│                                                                                         │
│  5. ADDITIONAL ENHANCED ENDPOINTS                                                       │
│     • POST /api/check-url-hash - Intelligent session detection                          │
│     • GET /api/url-history/{url} - URL-specific session history                         │
│     • GET /api/session/{hash} - Hash-based session retrieval                            │
│     • Enhanced session management with automated cleanup                                │
│     • Health checks including Playwright and database connectivity                      │
└─────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                          ENHANCED TECHNOLOGY STACK & FEATURES                           │
├─────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                         │
│  FRONTEND (Enhanced React)          │  BACKEND (Enhanced FastAPI)                      │
│  ├─ React 18 with advanced hooks    │  ├─ FastAPI with async/await                     │
│  ├─ Smart session management        │  ├─ Playwright for element extraction            │
│  ├─ Hash-based session detection    │  ├─ Hash-based session management                │
│  ├─ URL history and timeline        │  ├─ Motor AsyncIO MongoDB driver                 │
│  ├─ Session loading dialogs         │  ├─ Enhanced subprocess execution                │
│  ├─ Enhanced error handling         │  ├─ Comprehensive element categorization         │
│  ├─ Real-time progress indicators   │  ├─ Robust selector generation                   │
│  ├─ Element category visualization  │  ├─ Context-aware LLM integration                │
│  ├─ Copy-to-clipboard functionality │  ├─ Content-based hash calculation               │
│  ├─ Responsive design with modals   │  ├─ URL-based session grouping                   │
│  └─ Auto-session restoration        │  └─ Enhanced logging and monitoring              │
│                                     │                                                  │
│  DATABASE (Enhanced MongoDB)        │  SECURITY & EXECUTION (Enhanced)                │
│  ├─ Hash-based primary keys         │  ├─ Playwright browser sandboxing               │
│  ├─ URL-based session grouping      │  ├─ 120-second execution timeout                │
│  ├─ Element metadata storage        │  ├─ Secure temporary file handling              │
│  ├─ Comprehensive indexing          │  ├─ Input validation with enhanced Pydantic     │
│  ├─ Historical session tracking     │  ├─ Detailed error logging and monitoring       │
│  ├─ Optimized query performance     │  ├─ Database connection health monitoring       │
│  └─ Automatic cleanup policies      │  └─ Hash-based session security                 │
│                                     │                                                  │
│  DEPENDENCIES (Enhanced)            │  INSTALLATION (Enhanced)                        │
│  Frontend:                          │  Backend:                                        │
│  ├─ react, lucide-react            │  ├─ pip install fastapi uvicorn                 │
│  ├─ tailwindcss                    │  ├─ pip install playwright motor pymongo        │
│  └─ Enhanced state management      │  ├─ pip install pydantic python-multipart      │
│                                     │  ├─ playwright install chromium                 │
│  Backend (Enhanced):                │  └─ MongoDB server with optimized config       │
│  ├─ fastapi, uvicorn               │                                                  │
│  ├─ playwright (async)             │  MongoDB (Enhanced):                             │
│  ├─ motor, pymongo                 │  ├─ Default port: 27017                         │
│  ├─ pydantic, python-multipart     │  ├─ Database: llm_testing_framework             │
│  └─ hashlib, base64, logging       │  ├─ Collection: sessions (hash-indexed)         │
│                                     │  └─ Optimized indexes for performance          │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```