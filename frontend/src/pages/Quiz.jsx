import API_BASE_URL from "../api_config";
import React, { useState, useEffect } from 'react';
import { BookOpen, MessageCircle, PenTool, Sparkles, RefreshCw, Layers, FileText, Settings, Lock } from 'lucide-react';
import QuestionCard from '../components/QuestionCard';
import ResultSummary from '../components/ResultSummary';


function Quiz({ userPlan, onUsageUpdate }) {
    const [level, setLevel] = useState('N4');
    const [category, setCategory] = useState('grammar');
    const [mode, setMode] = useState('single');
    const [model, setModel] = useState('gpt-4o');
    const [availableModels, setAvailableModels] = useState([]);
    const [includeImage, setIncludeImage] = useState(false); // New: Visual Hints

    const [loading, setLoading] = useState(false);
    const [questionQueue, setQuestionQueue] = useState([]);
    const [pdfImage, setPdfImage] = useState(null); // Added for PDF mock
    const [currentIndex, setCurrentIndex] = useState(0);
    const [results, setResults] = useState([]);
    const [showResults, setShowResults] = useState(false);
    const [earnedToken, setEarnedToken] = useState(0); // New state

    const [error, setError] = useState('');
    const [answered, setAnswered] = useState(false);
    const [selectedAnswer, setSelectedAnswer] = useState(null);
    // userPlan is now a prop from App.jsx

    // Fetch available models and config on mount
    useEffect(() => {
        const fetchModelsAndConfig = async () => {
            try {
                const res = await fetch(API_BASE_URL + '/models');
                if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
                const data = await res.json();
                console.log("Models fetched:", data);
                setAvailableModels(data.models || []);

                // Prefer gpt-4o if available
                const hasGPT4o = data.models?.some(m => m.name === 'gpt-4o');
                if (hasGPT4o) {
                    setModel('gpt-4o');
                } else if (data.models && data.models.length > 0) {
                    setModel(data.models[0].name);
                }
            } catch (err) {
                console.error('Failed to fetch data:', err);
                setAvailableModels([{ name: "gemma2", type: "local", size: "offline" }]);
            }
        };
        fetchModelsAndConfig();
    }, []);

    const handlePdfMockGenerate = async () => {
        if (userPlan?.toLowerCase() === 'standard') {
            if (window.confirm("🔒 Standardプランでは模擬試験（AI画像認識）は利用できません。プロプランにアップグレードしますか？")) {
                window.location.href = "http://localhost:8501"; // Redirect to LP
            }
            return;
        }
        setLoading(true);
        setError('');
        setAnswered(false);
        setSelectedAnswer(null);
        setCurrentIndex(0);
        setShowResults(false);
        setQuestionQueue([]);
        setPdfImage(null);

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(API_BASE_URL + '/api/mock-test', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ level, model })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Mock Test Failed");
            }
            const data = await res.json();

            setPdfImage(data.image_base64);
            setQuestionQueue(data.questions); // questions is a list of {question, options, answer...}
            if (onUsageUpdate) onUsageUpdate();

        } catch (err) {
            setError('模擬試験の生成に失敗しました: ' + err.message);
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerate = async () => {
        if (mode === 'mock_test' && userPlan?.toLowerCase() === 'standard') {
            alert("🔒 Standardプランでは模擬テストは利用できません。");
            return;
        }
        setLoading(true);
        setError('');
        setAnswered(false);
        setSelectedAnswer(null);
        setCurrentIndex(0);
        setShowResults(false);
        setQuestionQueue([]);
        setPdfImage(null);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(API_BASE_URL + '/generate', {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ level, category, mode, model, include_image: includeImage }),
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Generation failed');
            }
            const data = await response.json();

            setQuestionQueue(data);
            if (onUsageUpdate) onUsageUpdate();
        } catch (err) {
            setError(err.message || '問題の生成に失敗しました。サーバーを確認してください。');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = (index) => {
        setSelectedAnswer(index);
        setAnswered(true);

        const currentQ = questionQueue[currentIndex];
        const isCorrect = index === currentQ.correctIndex;

        const newResult = {
            question: currentQ,
            userAnswer: index,
            isCorrect: isCorrect,
            category: category // Inject current category for result analysis
        };

        setResults(prev => {
            const updated = [...prev];
            updated[currentIndex] = newResult;
            return updated;
        });

        // Grant reward immediately if correct
        if (isCorrect) {
            const rewardPerQuestion = 1;
            try {
                const token = localStorage.getItem('token');
                fetch(API_BASE_URL + '/api/wallet/reward', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        amount: rewardPerQuestion,
                        description: `Quiz Reward: ${category} ${level}`
                    })
                });
                setEarnedToken(prev => prev + rewardPerQuestion);
            } catch (e) {
                console.error("Instant reward failed", e);
            }
        }
    };

    const handleFinish = async () => {
        // Reward is now calculated immediately when answering correctly.
        setShowResults(true);
    };

    const handleNext = () => {
        if (currentIndex < questionQueue.length - 1) {
            setCurrentIndex(prev => prev + 1);
            setAnswered(false);
            setSelectedAnswer(null);
        } else {
            handleFinish();
        }
    };

    const handleRetryMistakes = () => {
        const mistakes = results.filter(r => !r.isCorrect).map(r => r.question);
        if (mistakes.length === 0) return;

        setQuestionQueue(mistakes);
        setResults([]);
        setCurrentIndex(0);
        setShowResults(false);
        setEarnedToken(0);
        setAnswered(false);
        setSelectedAnswer(null);
    };

    return (
        <div className="glass-panel">
            <h1>
                <Sparkles style={{ display: 'inline', marginRight: 10 }} />
                AI JLPT Master
            </h1>

            {questionQueue.length === 0 && (
                <>
                    <div className="controls">
                        <div>
                            <label>Level</label>
                            <select style={{ width: '100%' }} value={level} onChange={(e) => setLevel(e.target.value)}>
                                {['N5', 'N4', 'N3', 'N2', 'N1'].map(l => (
                                    <option key={l} value={l}>{l}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div style={{ marginBottom: '1rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Category</label>
                        <div className="mode-selector">
                            <button className={`mode-btn ${category === 'grammar' ? 'active' : ''}`} onClick={() => setCategory('grammar')}>
                                <PenTool size={18} /> 文法
                            </button>
                            <button className={`mode-btn ${category === 'vocab' ? 'active' : ''}`} onClick={() => setCategory('vocab')}>
                                <BookOpen size={18} /> 語彙
                            </button>
                            <button className={`mode-btn ${category === 'reading' ? 'active' : ''}`} onClick={() => setCategory('reading')}>
                                <MessageCircle size={18} /> 読解
                            </button>
                        </div>
                    </div>

                    <div style={{ marginBottom: '2rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>Test Mode</label>
                        <div className="mode-selector">
                            <button className={`mode-btn ${mode === 'single' ? 'active' : ''}`} onClick={() => setMode('single')}>
                                <FileText size={18} /> 一問一答
                            </button>
                            <button className={`mode-btn ${mode === 'small_test' ? 'active' : ''}`} onClick={() => setMode('small_test')}>
                                <Layers size={18} /> 小テスト (5問)
                            </button>
                            <button 
                                className={`mode-btn ${mode === 'mock_test' ? 'active' : ''} ${userPlan?.toLowerCase() === 'standard' ? 'locked' : ''}`} 
                                onClick={() => {
                                    if (userPlan?.toLowerCase() === 'standard') {
                                        if (window.confirm("🔒 Standardプランでは模擬テストは利用できません。プロプランにアップグレードしますか？")) {
                                            window.location.href = "http://localhost:8501"; // Redirect to LP
                                        }
                                    } else {
                                        setMode('mock_test');
                                    }
                                }}
                                style={{ opacity: userPlan?.toLowerCase() === 'standard' ? 0.6 : 1 }}
                            >
                                {userPlan?.toLowerCase() === 'standard' ? <Lock size={18} /> : <Layers size={18} />} 模擬テスト (10問)
                            </button>
                        </div>
                    </div>

                    <div style={{ marginBottom: '2rem' }}>
                        <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                            <Settings size={18} style={{ verticalAlign: 'middle', marginRight: 5 }} />
                            AI Model
                        </label>
                        <select style={{ width: '100%', padding: 12, borderRadius: 12, border: '1px solid #e2e8f0' }} value={model} onChange={(e) => setModel(e.target.value)}>
                            {availableModels.map(m => (
                                <option key={m.name} value={m.name}>
                                    {m.type === 'cloud' ? '☁️' : '🖥️'} {m.name} ({m.size})
                                </option>
                            ))}
                        </select>
                    </div>


                    <button
                        className="generate-btn"
                        onClick={mode === 'pdf_mock' ? handlePdfMockGenerate : handleGenerate}
                        disabled={loading}
                    >
                        {loading ? (
                            <span><RefreshCw className="spin" size={20} style={{ verticalAlign: 'middle', marginRight: 5 }} /> 生成中...</span>
                        ) : '問題を生成する (Start)'}
                    </button>

                    {loading && (
                        <div className="loading-container" style={{ marginTop: '2rem' }}>
                            <div className="loading-dots">
                                <div className="dot"></div>
                                <div className="dot"></div>
                                <div className="dot"></div>
                            </div>
                            <div className="loading-text">
                                AIが一生懸命考えています...
                            </div>
                        </div>
                    )}
                </>
            )
            }

            {error && <div style={{ color: 'red', marginTop: 20, textAlign: 'center' }}>{error}</div>}

            {/* Default Quiz View */}
            {
                mode !== 'pdf_mock' && questionQueue.length > 0 && !showResults && (
                    <div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '1rem', color: 'var(--text-light)' }}>
                            <span>Mode: {mode === 'single' ? 'Single' : mode === 'small_test' ? 'Small Test' : 'Mock Test'}</span>
                            <span style={{ fontWeight: 'bold' }}>Q {currentIndex + 1} / {questionQueue.length}</span>
                        </div>

                        <QuestionCard
                            data={questionQueue[currentIndex]}
                            onAnswer={handleAnswer}
                            answered={answered}
                            selectedAnswer={selectedAnswer}
                        />

                        {answered && (
                            <div style={{ marginTop: '2rem', textAlign: 'right', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
                                {mode === 'single' ? (
                                    <>
                                        <button className="generate-btn" style={{ width: 'auto', background: '#a0aec0' }} onClick={() => { setQuestionQueue([]); setShowResults(false); }}>
                                            終了する (Home)
                                        </button>
                                        <button className="generate-btn" style={{ width: 'auto' }} onClick={handleGenerate}>
                                            次の問題を作る (Next)
                                        </button>
                                    </>
                                ) : (
                                    <button className="generate-btn" style={{ width: 'auto', background: '#4a5568' }} onClick={handleNext}>
                                        {currentIndex < questionQueue.length - 1 ? '次の問題へ (Next) ->' : '結果を見る (Finish) ->'}
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                )
            }

            {/* PDF Mock Test View (Split View) with Interactive Selection */}
            {
                mode === 'pdf_mock' && questionQueue.length > 0 && (
                    <div className="mock-test-layout" style={{ display: 'flex', gap: '2rem', marginTop: '2rem', flexWrap: 'wrap' }}>
                        {/* Removed: Original PDF Image Viewer (Left Side) */}

                        {/* Interactive List */}
                        <div className="interactive-quiz" style={{ flex: 1, minWidth: '300px' }}>
                            <h3>Extracted Questions</h3>
                            {questionQueue.map((q, idx) => (
                                <div key={idx} className="quiz-card" style={{ background: 'white', padding: '1.5rem', borderRadius: '12px', border: '1px solid #e5e7eb', marginBottom: '1rem' }}>
                                    <div style={{ fontWeight: 'bold', marginBottom: '0.5rem' }}>Q{idx + 1}. {q.question}</div>
                                    <div className="options" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem' }}>
                                        {q.options.map((opt, i) => {
                                            const isSelected = selectedAnswer && selectedAnswer[idx] === i;
                                            return (
                                                <div
                                                    key={i}
                                                    onClick={() => setSelectedAnswer(prev => ({ ...prev, [idx]: i }))}
                                                    style={{
                                                        padding: '0.5rem',
                                                        background: isSelected ? '#3182ce' : '#f9fafb',
                                                        color: isSelected ? 'white' : 'black',
                                                        border: isSelected ? '1px solid #3182ce' : '1px solid #d1d5db',
                                                        borderRadius: '4px',
                                                        cursor: 'pointer',
                                                        transition: 'all 0.2s'
                                                    }}
                                                >
                                                    {opt}
                                                </div>
                                            );
                                        })}
                                    </div>
                                    <details style={{ marginTop: '1rem', color: '#666', cursor: 'pointer' }}>
                                        <summary>Show Answer</summary>
                                        <div style={{ marginTop: '0.5rem', color: '#10b981', fontWeight: 'bold' }}>
                                            Answer: {q.options[q.correctIndex]}
                                        </div>
                                        <div style={{ fontSize: '0.9rem' }}>{q.explanation}</div>
                                    </details>
                                </div>
                            ))}
                            <button className="generate-btn" style={{ width: '100%', marginTop: '1rem', background: '#a0aec0' }} onClick={() => { setQuestionQueue([]); setPdfImage(null); setSelectedAnswer(null); }}>
                                試験を終了する (Finish)
                            </button>
                        </div>
                    </div>
                )
            }

            {
                showResults && (
                    <ResultSummary
                        results={results}
                        earnedToken={earnedToken}
                        onRetry={handleGenerate}
                        onRetryMistakes={handleRetryMistakes}
                        onHome={() => {
                            setQuestionQueue([]);
                            setShowResults(false);
                            setEarnedToken(0);
                        }}
                    />
                )
            }
        </div >
    );
}

export default Quiz;
