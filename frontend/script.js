// DOM Elements
const emergencyBtn = document.getElementById('emergency-btn');
const emergencyPanel = document.getElementById('emergency-panel');
const closeEmergency = document.getElementById('close-emergency');
const scannerCard = document.getElementById('scanner-card');
const assistantCard = document.getElementById('assistant-card');
const scannerSection = document.getElementById('scanner-section');
const assistantSection = document.getElementById('assistant-section');
const backBtns = document.querySelectorAll('.back-btn');
const docUpload = document.getElementById('doc-upload');
const uploadedImage = document.getElementById('uploaded-image');
const docAnalysis = document.getElementById('doc-analysis');
const analysisResults = document.getElementById('analysis-results');
const whatIfBtn = document.getElementById('what-if-btn');
const whatIfModal = document.getElementById('what-if-modal');
const closeModal = document.getElementById('close-modal');
const startListeningBtn = document.getElementById('start-listening');
const listeningIndicator = document.getElementById('listening-indicator');
const voiceQuery = document.getElementById('voice-query');
const submitQuery = document.getElementById('submit-query');
const assistantResponse = document.getElementById('assistant-response');
const responseContent = document.getElementById('response-content');
const promptBtns = document.querySelectorAll('.prompt-btn');
const scenarioSelect = document.getElementById('scenario-select');
const simulateBtn = document.getElementById('simulate-btn');
const simulationResult = document.getElementById('simulation-result');
const resultText = document.getElementById('result-text');
const visaProgress = document.getElementById('visa-progress');

// Mock data
const mockAnalysis = [
    { text: "✅ Photo: Valid", status: "valid" },
    { text: "✅ Name: Matches passport", status: "valid" },
    { text: "⚠️ Expiry: 14 days remaining!", status: "warning" },
    { text: "ℹ️ You need to apply for renewal now", status: "info" }
];

const mockResponses = {
    "help me write to my landlord": "Here's a polite message to your landlord:\n\nDear [Landlord],\n\nI wanted to bring to your attention an issue with [specific problem]. I would appreciate it if you could address this matter at your earliest convenience.\n\nThank you for your attention to this issue.\n\nSincerely,\n[Your Name]",
    "translate medical emergency": "Here are translations for 'medical emergency':\n\n- Spanish: Emergencia médica\n- French: Urgence médicale\n- Arabic: طوارئ طبية\n- Chinese: 医疗紧急情况",
    "check my visa requirements": "Based on your current Work Visa status, here are upcoming requirements:\n\n1. Renewal application due in 14 days\n2. Recent pay stubs (last 3 months)\n3. Employer verification letter\n\nI can help you prepare these documents if needed."
};

const mockSimulations = {
    "marriage": "If you marry a citizen, your visa process would change significantly:\n\n- Immediate eligibility for marriage-based green card\n- Processing time: 6-12 months\n- Requirements: Marriage certificate, joint financial documents, interview\n\nNote: Marriage must be bona fide (real).",
    "job": "With a new job offer:\n\n- You may qualify for an employment-based visa\n- Your employer would need to sponsor you\n- Processing time varies by visa type (H1B, L1, etc.)\n\nI can help review your offer letter for visa eligibility.",
    "student": "Enrolling in university would allow you to apply for a student visa (F-1):\n\n- Must be accepted at SEVP-approved school\n- Proof of financial support required\n- Can work on-campus up to 20 hours/week\n\nStudent visas are temporary but can lead to work opportunities."
};

// Initialize the app
function initApp() {
    // Animate visa progress number
    animateValue(visaProgress, 0, 60, 1500);
    
    // Emergency panel toggle
    emergencyBtn.addEventListener('click', () => {
        emergencyPanel.classList.toggle('active');
    });
    
    closeEmergency.addEventListener('click', () => {
        emergencyPanel.classList.remove('active');
    });
    
    // Feature cards navigation
    scannerCard.addEventListener('click', () => {
        document.querySelector('.hero').classList.add('hidden');
        document.querySelector('.features-grid').classList.add('hidden');
        scannerSection.classList.remove('hidden');
    });
    
    assistantCard.addEventListener('click', () => {
        document.querySelector('.hero').classList.add('hidden');
        document.querySelector('.features-grid').classList.add('hidden');
        assistantSection.classList.remove('hidden');
    });
    
    backBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            scannerSection.classList.add('hidden');
            assistantSection.classList.add('hidden');
            document.querySelector('.hero').classList.remove('hidden');
            document.querySelector('.features-grid').classList.remove('hidden');
        });
    });
    
    // Document upload handling
    docUpload.addEventListener('change', handleDocumentUpload);
    
    // What If Simulator
    whatIfBtn.addEventListener('click', () => {
        whatIfModal.classList.add('active');
    });
    
    closeModal.addEventListener('click', () => {
        whatIfModal.classList.remove('active');
    });
    
    // Voice assistant
    startListeningBtn.addEventListener('click', toggleVoiceRecognition);
    submitQuery.addEventListener('click', processQuery);
    voiceQuery.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') processQuery();
    });
    
    // Quick prompts
    promptBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const prompt = btn.textContent;
            voiceQuery.value = prompt;
            processQuery(prompt);
        });
    });
    
    // Simulator
    simulateBtn.addEventListener('click', runSimulation);
}

// Animate number counting up
function animateValue(element, start, end, duration) {
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        element.innerHTML = Math.floor(progress * (end - start) + start) + '%';
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

// Handle document upload
function handleDocumentUpload(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            uploadedImage.src = event.target.result;
            uploadedImage.classList.remove('hidden');
            analyzeDocument();
        };
        reader.readAsDataURL(file);
    }
}

// Mock document analysis
function analyzeDocument() {
    // In a real app, you would send image to OCR service
    analysisResults.innerHTML = '';
    mockAnalysis.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item.text;
        li.className = item.status;
        analysisResults.appendChild(li);
    });
    
    docAnalysis.classList.remove('hidden');
}

// Voice recognition toggle
function toggleVoiceRecognition() {
    if (startListeningBtn.classList.contains('listening')) {
        // Stop listening
        startListeningBtn.classList.remove('listening');
        listeningIndicator.classList.add('hidden');
        voiceQuery.placeholder = "Type your question here...";
    } else {
        // Start listening
        startListeningBtn.classList.add('listening');
        listeningIndicator.classList.remove('hidden');
        voiceQuery.placeholder = "Listening... Speak now";
        
        // Mock recognition - in real app use Web Speech API
        setTimeout(() => {
            const mockQueries = Object.keys(mockResponses);
            const randomQuery = mockQueries[Math.floor(Math.random() * mockQueries.length)];
            voiceQuery.value = randomQuery;
            processQuery(randomQuery);
            startListeningBtn.classList.remove('listening');
            listeningIndicator.classList.add('hidden');
        }, 2000);
    }
}

// Process user query
function processQuery(query) {
    query = query || voiceQuery.value;
    if (!query.trim()) return;
    
    // In a real app, you would send query to your backend/OpenAI
    const response = mockResponses[query.toLowerCase()] || 
        `I'm still learning. For "${query}", please check our help center or try rephrasing.`;
    
    responseContent.textContent = response;
    assistantResponse.classList.add('visible');
    
    // Scroll to response
    setTimeout(() => {
        assistantResponse.scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

// Run simulation
function runSimulation() {
    const scenario = scenarioSelect.value;
    const result = mockSimulations[scenario];
    
    resultText.textContent = result;
    simulationResult.classList.add('visible');
    
    // Scroll to result
    setTimeout(() => {
        simulationResult.scrollIntoView({ behavior: 'smooth' });
    }, 300);
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);