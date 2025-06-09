import React, { useState, useEffect } from 'react';
import { Play, Code, FileText, Globe, CheckCircle, Circle, ArrowRight, Download, Copy, RefreshCw, Terminal, AlertCircle, History, ExternalLink, X } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000/api';

const TestingFrameworkApp = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [sessionId, setSessionId] = useState(null);
  const [urlHash, setUrlHash] = useState(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [showSessionDialog, setShowSessionDialog] = useState(false);
  const [sessionDialogData, setSessionDialogData] = useState(null);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [urlHistory, setUrlHistory] = useState([]);
  const [results, setResults] = useState({
    elements: null,
    testcases: null,
    code: null,
    execution: null
  });

  // Form states
  const [elementForm, setElementForm] = useState({
    webUrl: '',
    configContent: '',
    systemPrompt: 'You are an expert UI element extraction assistant. Analyze the webpage and extract all interactive elements comprehensively.',
    userPrompt: 'Please extract all UI elements from this webpage including buttons, inputs, links, forms, and other interactive components. Use robust selectors and comprehensive extraction strategies.'
  });

  const [testcaseForm, setTestcaseForm] = useState({
    systemPrompt: 'You are an expert test case generation assistant. Create comprehensive test scenarios based on extracted UI elements.',
    userPrompt: 'Generate detailed test cases for the extracted UI elements. Include positive, negative, edge case scenarios, and user workflow tests. Focus on real-world user interactions.'
  });

  const [codeForm, setCodeForm] = useState({
    systemPrompt: 'You are an expert test automation engineer. Generate clean, executable Playwright test code.',
    userPrompt: 'Generate complete Playwright test code for the provided test cases. Include proper setup, teardown, error handling, and comprehensive assertions. Make the tests robust and maintainable.'
  });

  const [executeForm, setExecuteForm] = useState({
    executionType: 'python'
  });

  const steps = [
    { title: 'Element Extraction', icon: Globe, description: 'Extract UI elements using Playwright' },
    { title: 'Test Cases Generation', icon: FileText, description: 'Generate comprehensive test scenarios' },
    { title: 'Code Generation', icon: Code, description: 'Generate executable Playwright test code' },
    { title: 'Code Execution', icon: Terminal, description: 'Execute and validate tests' }
  ];

  // Load last session on component mount
  useEffect(() => {
    const loadLastSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/last-session`);
        if (response.ok) {
          const data = await response.json();
          if (data.session) {
            await loadSession(data.session);
          }
        }
      } catch (error) {
        console.error('Failed to load last session:', error);
      } finally {
        setInitialLoading(false);
      }
    };

    loadLastSession();
  }, []);

  const loadSession = async (session) => {
    setSessionId(session.session_id);
    setUrlHash(session.url_hash);
    
    // Restore form data
    if (session.web_url) {
      setElementForm(prev => ({
        ...prev,
        webUrl: session.web_url,
        configContent: session.config_content || ''
      }));
    }
    
    // Restore results
    setResults({
      elements: session.results.extracted_elements,
      testcases: session.results.test_cases,
      code: session.results.generated_code,
      execution: session.results.execution_result
    });
    
    // Set current step based on completed stages
    const completedStages = session.completed_stages;
    if (completedStages.includes('code_execution')) {
      setCurrentStep(3);
    } else if (completedStages.includes('code_generation')) {
      setCurrentStep(3);
    } else if (completedStages.includes('testcase_generation')) {
      setCurrentStep(2);
    } else if (completedStages.includes('element_extraction')) {
      setCurrentStep(1);
    }
  };

  const callAPI = async (endpoint, data) => {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `API call failed: ${response.statusText}`);
    }
    
    return response.json();
  };

  const checkUrlHash = async (url) => {
    try {
      const response = await callAPI('/check-url-hash', { web_url: url });
      return response;
    } catch (error) {
      console.error('Failed to check URL hash:', error);
      throw error;
    }
  };

  const handleUrlCheck = async () => {
    if (!elementForm.webUrl) return;
    
    setLoading(true);
    try {
      const hashData = await checkUrlHash(elementForm.webUrl);
      
      if (hashData.has_existing_session || hashData.existing_sessions.length > 0) {
        setSessionDialogData(hashData);
        setShowSessionDialog(true);
      } else {
        // No existing sessions, proceed directly
        await handleElementExtraction(true);
      }
    } catch (error) {
      alert(`Error checking URL: ${error.message}`);
    }
    setLoading(false);
  };

  const handleElementExtraction = async (forceNew = false) => {
    setLoading(true);
    setShowSessionDialog(false);
    
    try {
      const response = await callAPI('/extract-elements', {
        web_url: elementForm.webUrl,
        config_content: elementForm.configContent,
        system_prompt: elementForm.systemPrompt,
        user_prompt: elementForm.userPrompt,
        force_new_session: forceNew
      });
      
      setSessionId(response.session_id);
      setUrlHash(response.url_hash);
      setResults(prev => ({ ...prev, elements: response.extracted_elements }));
      
      if (response.is_new_session) {
        setCurrentStep(1);
      } else {
        // Loaded existing session, determine current step
        const session = await fetch(`${API_BASE_URL}/session/${response.session_id}`)
          .then(res => res.json());
        await loadSession(session);
      }
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const handleLoadExistingSession = async (session) => {
    setLoading(true);
    setShowSessionDialog(false);
    
    try {
      const sessionData = await fetch(`${API_BASE_URL}/session/${session.session_id}`)
        .then(res => res.json());
      await loadSession(sessionData);
    } catch (error) {
      alert(`Error loading session: ${error.message}`);
    }
    setLoading(false);
  };

  const handleTestcaseGeneration = async () => {
    setLoading(true);
    try {
      const response = await callAPI('/generate-testcases', {
        session_id: sessionId,
        extracted_elements: results.elements,
        system_prompt: testcaseForm.systemPrompt,
        user_prompt: testcaseForm.userPrompt
      });
      
      setResults(prev => ({ ...prev, testcases: response.test_cases }));
      setCurrentStep(2);
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const handleCodeGeneration = async () => {
    setLoading(true);
    try {
      const response = await callAPI('/generate-code', {
        session_id: sessionId,
        test_cases: results.testcases,
        system_prompt: codeForm.systemPrompt,
        user_prompt: codeForm.userPrompt
      });
      
      setResults(prev => ({ ...prev, code: response.generated_code }));
      setCurrentStep(3);
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const handleCodeExecution = async () => {
    setLoading(true);
    try {
      const response = await callAPI('/execute-code', {
        session_id: sessionId,
        code: results.code,
        execution_type: executeForm.executionType
      });
      
      setResults(prev => ({ ...prev, execution: response.execution_result }));
    } catch (error) {
      alert(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const loadUrlHistory = async () => {
    if (!elementForm.webUrl) return;
    
    try {
      const encodedUrl = encodeURIComponent(elementForm.webUrl);
      const response = await fetch(`${API_BASE_URL}/url-history/${encodedUrl}`);
      const data = await response.json();
      setUrlHistory(data.sessions || []);
      setShowHistoryModal(true);
    } catch (error) {
      console.error('Failed to load URL history:', error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  const resetWorkflow = () => {
    setCurrentStep(0);
    setSessionId(null);
    setUrlHash(null);
    setResults({ elements: null, testcases: null, code: null, execution: null });
    setElementForm(prev => ({ ...prev, webUrl: '', configContent: '' }));
  };

  const SessionDialog = () => {
    if (!showSessionDialog || !sessionDialogData) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-2xl w-full mx-4 max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold">Existing Sessions Found</h3>
            <button
              onClick={() => setShowSessionDialog(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={20} />
            </button>
          </div>
          
          <p className="text-gray-600 mb-4">
            Found {sessionDialogData.existing_sessions.length} existing session(s) for this URL.
            {sessionDialogData.has_existing_session && " The current page structure matches an existing session."}
          </p>
          
          <div className="space-y-3 mb-6">
            {sessionDialogData.existing_sessions.slice(0, 5).map((session) => (
              <div key={session.session_id} className="border rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">Hash: {session.url_hash}</div>
                    <div className="text-sm text-gray-600">
                      Stage: {session.current_stage} | 
                      Steps: {session.completed_stages.join(', ')}
                    </div>
                    <div className="text-xs text-gray-500">
                      Created: {new Date(session.created_at).toLocaleDateString()} |
                      Updated: {new Date(session.updated_at).toLocaleDateString()}
                    </div>
                  </div>
                  <button
                    onClick={() => handleLoadExistingSession(session)}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                  >
                    Load
                  </button>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => handleElementExtraction(true)}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
            >
              Start Fresh Session
            </button>
            <button
              onClick={() => setShowSessionDialog(false)}
              className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  };

  const HistoryModal = () => {
    if (!showHistoryModal) return null;

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-96 overflow-y-auto">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-bold">URL Testing History</h3>
            <button
              onClick={() => setShowHistoryModal(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X size={20} />
            </button>
          </div>
          
          <div className="space-y-3">
            {urlHistory.map((session) => (
              <div key={session.session_id} className="border rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="font-medium">Hash: {session.url_hash}</div>
                    <div className="text-sm text-gray-600">
                      Stage: {session.current_stage} | 
                      Elements: {session.elements_count} |
                      Steps: {session.completed_stages.join(', ')}
                    </div>
                    <div className="text-xs text-gray-500">
                      Created: {new Date(session.created_at).toLocaleString()} |
                      Updated: {new Date(session.updated_at).toLocaleString()}
                    </div>
                  </div>
                  <button
                    onClick={() => {
                      handleLoadExistingSession(session);
                      setShowHistoryModal(false);
                    }}
                    className="bg-blue-500 text-white px-3 py-1 rounded text-sm hover:bg-blue-600"
                  >
                    Load
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const StepIndicator = () => (
    <div className="flex items-center justify-center mb-8 space-x-4 overflow-x-auto">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isActive = index === currentStep;
        const isCompleted = index < currentStep || (index === currentStep && results[Object.keys(results)[index]]);
        
        return (
          <div key={index} className="flex items-center flex-shrink-0">
            <div className={`flex items-center space-x-2 p-3 rounded-lg transition-all duration-300 ${
              isActive ? 'bg-blue-100 text-blue-600' : 
              isCompleted ? 'bg-green-100 text-green-600' : 'bg-gray-100 text-gray-400'
            }`}>
              <Icon size={20} />
              <span className="font-medium whitespace-nowrap">{step.title}</span>
              {isCompleted && index !== currentStep && <CheckCircle size={16} className="text-green-500" />}
            </div>
            {index < steps.length - 1 && (
              <ArrowRight size={16} className="mx-2 text-gray-400 flex-shrink-0" />
            )}
          </div>
        );
      })}
    </div>
  );

  const ElementExtractionStep = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <Globe className="mr-2 text-blue-500" />
        Element Extraction with Playwright
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2">Web URL</label>
          <div className="flex space-x-2">
            <input
              type="url"
              value={elementForm.webUrl}
              onChange={(e) => setElementForm(prev => ({ ...prev, webUrl: e.target.value }))}
              className="flex-1 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://example.com"
              required
            />
            <button
              onClick={loadUrlHistory}
              disabled={!elementForm.webUrl}
              className="bg-gray-500 text-white p-3 rounded-lg hover:bg-gray-600 disabled:opacity-50"
              title="View URL History"
            >
              <History size={16} />
            </button>
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Configuration</label>
          <textarea
            value={elementForm.configContent}
            onChange={(e) => setElementForm(prev => ({ ...prev, configContent: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            placeholder="# Playwright configuration&#10;headless = True&#10;timeout = 30000"
          />
        </div>
        
        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-2">System Prompt</label>
          <textarea
            value={elementForm.systemPrompt}
            onChange={(e) => setElementForm(prev => ({ ...prev, systemPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        <div className="md:col-span-2">
          <label className="block text-sm font-medium mb-2">User Prompt</label>
          <textarea
            value={elementForm.userPrompt}
            onChange={(e) => setElementForm(prev => ({ ...prev, userPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>
      
      {sessionId && urlHash && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg">
          <div className="text-sm">
            <strong>Current Session:</strong> {sessionId}<br />
            <strong>URL Hash:</strong> {urlHash}
          </div>
        </div>
      )}
      
      <button
        onClick={handleUrlCheck}
        disabled={!elementForm.webUrl || loading}
        className="mt-6 bg-blue-500 text-white px-6 py-3 rounded-lg hover:bg-blue-600 disabled:opacity-50 flex items-center"
      >
        {loading ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Play className="mr-2" size={16} />}
        Extract Elements
      </button>
      
      {results.elements && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">
            Extracted Elements ({results.elements.filter(e => e.type !== 'metadata').length})
          </h3>
          <div className="max-h-40 overflow-y-auto">
            <pre className="text-sm text-gray-700">
              {JSON.stringify(results.elements.slice(0, 5), null, 2)}
              {results.elements.length > 5 && "\n... and more"}
            </pre>
          </div>
          
          {/* Show element categories */}
          {results.elements.find(e => e.type === 'metadata') && (
            <div className="mt-3 p-3 bg-white rounded border">
              <h4 className="font-medium mb-2">Element Categories:</h4>
              <div className="grid grid-cols-3 gap-2 text-sm">
                {Object.entries(results.elements.find(e => e.type === 'metadata').data.categories).map(([category, count]) => (
                  <div key={category} className="flex justify-between">
                    <span className="capitalize">{category}:</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );

  const TestcaseGenerationStep = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <FileText className="mr-2 text-green-500" />
        Test Cases Generation
      </h2>
      
      <div className="grid grid-cols-1 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2">System Prompt</label>
          <textarea
            value={testcaseForm.systemPrompt}
            onChange={(e) => setTestcaseForm(prev => ({ ...prev, systemPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">User Prompt</label>
          <textarea
            value={testcaseForm.userPrompt}
            onChange={(e) => setTestcaseForm(prev => ({ ...prev, userPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-green-500 focus:border-transparent"
          />
        </div>
      </div>
      
      <button
        onClick={handleTestcaseGeneration}
        disabled={!results.elements || loading}
        className="mt-6 bg-green-500 text-white px-6 py-3 rounded-lg hover:bg-green-600 disabled:opacity-50 flex items-center"
      >
        {loading ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Play className="mr-2" size={16} />}
        Generate Test Cases
      </button>
      
      {results.testcases && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium mb-2">Generated Test Cases ({results.testcases.length})</h3>
          <div className="max-h-40 overflow-y-auto">
            <pre className="text-sm text-gray-700">{JSON.stringify(results.testcases, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );

  const CodeGenerationStep = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <Code className="mr-2 text-purple-500" />
        Playwright Code Generation
      </h2>
      
      <div className="grid grid-cols-1 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2">System Prompt</label>
          <textarea
            value={codeForm.systemPrompt}
            onChange={(e) => setCodeForm(prev => ({ ...prev, systemPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">User Prompt</label>
          <textarea
            value={codeForm.userPrompt}
            onChange={(e) => setCodeForm(prev => ({ ...prev, userPrompt: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg h-20 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          />
        </div>
      </div>
      
      <button
        onClick={handleCodeGeneration}
        disabled={!results.testcases || loading}
        className="mt-6 bg-purple-500 text-white px-6 py-3 rounded-lg hover:bg-purple-600 disabled:opacity-50 flex items-center"
      >
        {loading ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Play className="mr-2" size={16} />}
        Generate Code
      </button>
      
      {results.code && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <h3 className="font-medium">Generated Playwright Test Code</h3>
            <button
              onClick={() => copyToClipboard(results.code)}
              className="text-blue-500 hover:text-blue-600 flex items-center text-sm"
            >
              <Copy size={16} className="mr-1" />
              Copy Code
            </button>
          </div>
          <div className="max-h-60 overflow-y-auto bg-gray-900 text-green-400 p-4 rounded font-mono text-sm">
            <pre>{results.code}</pre>
          </div>
        </div>
      )}
    </div>
  );

  const CodeExecutionStep = () => (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6 flex items-center">
        <Terminal className="mr-2 text-orange-500" />
        Code Execution
      </h2>
      
      <div className="grid grid-cols-1 gap-6">
        <div>
          <label className="block text-sm font-medium mb-2">Execution Type</label>
          <select
            value={executeForm.executionType}
            onChange={(e) => setExecuteForm(prev => ({ ...prev, executionType: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
          >
            <option value="python">Python</option>
            <option value="pytest">Pytest</option>
            <option value="playwright">Playwright</option>
          </select>
        </div>
        
        {results.code && (
          <div>
            <h3 className="font-medium mb-2">Code to Execute</h3>
            <div className="max-h-40 overflow-y-auto bg-gray-100 p-3 rounded-lg">
              <pre className="text-sm text-gray-700">{results.code.substring(0, 500)}...</pre>
            </div>
          </div>
        )}
      </div>
      
      <button
        onClick={handleCodeExecution}
        disabled={!results.code || loading}
        className="mt-6 bg-orange-500 text-white px-6 py-3 rounded-lg hover:bg-orange-600 disabled:opacity-50 flex items-center"
      >
        {loading ? <RefreshCw className="animate-spin mr-2" size={16} /> : <Terminal className="mr-2" size={16} />}
        Execute Code
      </button>
      
      {results.execution && (
        <div className="mt-6 space-y-4">
          <div className={`p-4 rounded-lg border-l-4 ${
            results.execution.success 
              ? 'bg-green-50 border-green-400' 
              : 'bg-red-50 border-red-400'
          }`}>
            <div className="flex items-center mb-2">
              {results.execution.success ? (
                <CheckCircle className="text-green-500 mr-2" size={20} />
              ) : (
                <AlertCircle className="text-red-500 mr-2" size={20} />
              )}
              <h3 className="font-medium">
                Execution {results.execution.success ? 'Successful' : 'Failed'}
              </h3>
              <span className="ml-auto text-sm text-gray-500">
                Return Code: {results.execution.returncode}
              </span>
            </div>
            
            {results.execution.stdout && (
              <div className="mb-3">
                <h4 className="text-sm font-medium text-gray-700 mb-1">Output:</h4>
                <div className="bg-gray-900 text-green-400 p-3 rounded text-sm font-mono max-h-40 overflow-y-auto">
                  <pre>{results.execution.stdout}</pre>
                </div>
              </div>
            )}
            
            {results.execution.stderr && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-1">Errors:</h4>
                <div className="bg-gray-900 text-red-400 p-3 rounded text-sm font-mono max-h-40 overflow-y-auto">
                  <pre>{results.execution.stderr}</pre>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="animate-spin mx-auto mb-4 text-blue-500" size={48} />
          <p className="text-gray-600">Loading last session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">LLM UI Testing Framework</h1>
          <p className="text-gray-600">Hash-based session management with Playwright element extraction</p>
          {sessionId && (
            <div className="mt-4 text-sm text-gray-500">
              Session: <code className="bg-gray-200 px-2 py-1 rounded">{sessionId}</code>
              {urlHash && (
                <span className="ml-2">
                  Hash: <code className="bg-gray-200 px-2 py-1 rounded">{urlHash}</code>
                </span>
              )}
              <button
                onClick={resetWorkflow}
                className="ml-4 text-blue-500 hover:text-blue-600 underline"
              >
                Start New Session
              </button>
            </div>
          )}
        </div>
        
        <StepIndicator />
        
        <div className="max-w-4xl mx-auto">
          {currentStep === 0 && <ElementExtractionStep />}
          {currentStep === 1 && <TestcaseGenerationStep />}
          {currentStep === 2 && <CodeGenerationStep />}
          {currentStep === 3 && <CodeExecutionStep />}
        </div>
        
        {currentStep === 3 && results.execution && (
          <div className="max-w-4xl mx-auto mt-8 text-center">
            <div className={`border px-4 py-3 rounded-lg ${
              results.execution.success 
                ? 'bg-green-100 border-green-400 text-green-700'
                : 'bg-yellow-100 border-yellow-400 text-yellow-700'
            }`}>
              {results.execution.success ? (
                <>
                  <CheckCircle className="inline mr-2" size={20} />
                  Workflow completed successfully! Your Playwright tests have been executed.
                </>
              ) : (
                <>
                  <AlertCircle className="inline mr-2" size={20} />
                  Workflow completed with execution issues. Check the output above for details.
                </>
              )}
            </div>
          </div>
        )}
      </div>
      
      <SessionDialog />
      <HistoryModal />
    </div>
  );
};

export default TestingFrameworkApp;