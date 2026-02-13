import React from 'react';
import { CheckCircle, XCircle, RotateCcw, Sparkles } from 'lucide-react';

const ResultSummary = ({ results, earnedToken, onRetry, onRetryMistakes, onHome }) => {
    const [viewMode, setViewMode] = React.useState('student'); // 'student' or 'teacher'
    const correctCount = results.filter(r => r.isCorrect).length;
    const total = results.length;
    const percentage = Math.round((correctCount / total) * 100);
    const hasMistakes = results.some(r => !r.isCorrect);

    // Helper for Ruby
    const renderRuby = (text) => {
        if (!text) return null;
        const parts = text.split(/([一-龠々ヶ々〇]+)[(（]([ぁ-んァ-ヶー]+)[)）]/g);
        const elements = [];
        for (let i = 0; i < parts.length; i++) {
            elements.push(<span key={`text-${i}`}>{parts[i]}</span>);
            if (i + 2 < parts.length) {
                elements.push(<ruby key={`ruby-${i}`}>{parts[i + 1]}<rt>{parts[i + 2]}</rt></ruby>);
                i += 2;
            }
        }
        return elements;
    };

    // Score Analysis Logic
    const categoryStats = results.reduce((acc, curr) => {
        const cat = curr.category || 'General';
        if (!acc[cat]) acc[cat] = { total: 0, correct: 0 };
        acc[cat].total += 1;
        if (curr.isCorrect) acc[cat].correct += 1;
        return acc;
    }, {});

    return (
        <div className="glass-panel" style={{ textAlign: 'center', animation: 'fadeIn 0.5s ease-out' }}>
            <h2 style={{ fontSize: '2rem', marginBottom: '1rem' }}>
                <Sparkles style={{ color: '#f59e0b', marginRight: 10 }} />
                Results Summary
            </h2>

            <div style={{ fontSize: '4rem', fontWeight: 'bold', color: '#3182ce', margin: '1rem 0' }}>
                {correctCount} / {total}
            </div>

            {earnedToken > 0 && (
                <div style={{ fontSize: '1.2rem', color: '#718096', marginBottom: '2rem' }}>
                    Token Earned: <span style={{ color: '#38a169', fontWeight: 'bold' }}>+{earnedToken} VRB</span>
                </div>
            )}

            {/* Score Analysis Card */}
            <div style={{
                background: 'white',
                borderRadius: '12px',
                padding: '1.5rem',
                marginBottom: '2rem',
                boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
                textAlign: 'left'
            }}>
                <h3 style={{ borderBottom: '2px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem', color: '#2d3748' }}>
                    📊 Score Analysis
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                    {Object.entries(categoryStats).map(([cat, stats]) => {
                        const percentage = Math.round((stats.correct / stats.total) * 100);
                        return (
                            <div key={cat} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <div style={{ fontWeight: 'bold', color: '#4a5568', textTransform: 'capitalize' }}>
                                    {cat === 'vocab' ? '語彙 (Vocabulary)' : cat === 'grammar' ? '文法 (Grammar)' : cat === 'reading' ? '読解 (Reading)' : cat}
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flex: 1, marginLeft: '1rem' }}>
                                    <div style={{ flex: 1, height: '8px', background: '#edf2f7', borderRadius: '4px', overflow: 'hidden' }}>
                                        <div style={{
                                            width: `${percentage}%`,
                                            height: '100%',
                                            background: percentage >= 80 ? '#48bb78' : percentage >= 50 ? '#ecc94b' : '#f56565',
                                            transition: 'width 1s ease-out'
                                        }} />
                                    </div>
                                    <div style={{ minWidth: '60px', textAlign: 'right', fontWeight: 'bold', color: '#2d3748' }}>
                                        {stats.correct}/{stats.total} ({percentage}%)
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {/* View Mode Toggle */}
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '2rem', gap: '1rem' }}>
                <button
                    onClick={() => setViewMode('student')}
                    style={{
                        padding: '10px 20px',
                        borderRadius: '20px',
                        border: 'none',
                        background: viewMode === 'student' ? '#3182ce' : '#e2e8f0',
                        color: viewMode === 'student' ? 'white' : '#4a5568',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                    }}
                >
                    👨‍🎓 Student View
                </button>
                <button
                    onClick={() => setViewMode('teacher')}
                    style={{
                        padding: '10px 20px',
                        borderRadius: '20px',
                        border: 'none',
                        background: viewMode === 'teacher' ? '#805ad5' : '#e2e8f0',
                        color: viewMode === 'teacher' ? 'white' : '#4a5568',
                        fontWeight: 'bold',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                    }}
                >
                    👨‍🏫 Teacher View
                </button>
            </div>

            <div style={{ textAlign: 'left', maxHeight: '400px', overflowY: 'auto', marginBottom: '2rem' }}>
                {results.map((res, idx) => (
                    <div key={idx} style={{
                        background: 'white',
                        padding: '1rem',
                        borderRadius: '12px',
                        marginBottom: '1rem',
                        border: res.isCorrect ? '2px solid var(--correct)' : '2px solid var(--incorrect)'
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                            {res.isCorrect ? <CheckCircle color="var(--correct)" size={20} /> : <XCircle color="var(--incorrect)" size={20} />}
                            <span style={{ fontWeight: 'bold' }}>Q{idx + 1}</span>
                        </div>
                        <p style={{ marginBottom: '0.5rem' }}>{renderRuby(res.question.question)}</p>
                        <div style={{ fontSize: '0.9rem', color: 'var(--text-light)' }}>
                            正解: <span style={{ fontWeight: 'bold' }}>{renderRuby(res.question.options[res.question.correctIndex])}</span>
                            {!res.isCorrect && <span style={{ marginLeft: 10 }}> (あなたの答え: {renderRuby(res.question.options[res.userAnswer])})</span>}
                        </div>

                        {/* Dynamic Explanation Rendering */}
                        <div style={{ marginTop: '0.8rem', padding: '0.8rem', background: viewMode === 'teacher' ? '#f3e8ff' : '#f7fafc', borderRadius: '8px', fontSize: '0.9rem', color: '#4a5568' }}>
                            {viewMode === 'teacher' ? (
                                <>
                                    <div style={{ color: '#6b46c1', fontWeight: 'bold', marginBottom: '0.5rem' }}>👨‍🏫 指導ポイント (Teacher's Note)</div>
                                    {res.question.teacherExplanation ? (
                                        <div>{res.question.teacherExplanation}</div>
                                    ) : (
                                        <div style={{ fontStyle: 'italic', color: '#a0aec0' }}>
                                            ※ この問題の教師用解説は生成されていません。（通常の解説を表示します）
                                            <hr style={{ margin: '0.5rem 0', borderColor: '#cbd5e0' }} />
                                            {res.question.explanation}
                                        </div>
                                    )}
                                </>
                            ) : (
                                <>
                                    <div style={{ color: '#2b6cb0', fontWeight: 'bold', marginBottom: '0.5rem' }}>💡 解説</div>
                                    {res.question.explanation || "解説はありません。"}
                                </>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
                {hasMistakes && onRetryMistakes && (
                    <button className="generate-btn" style={{ width: 'auto', padding: '12px 30px', background: '#dd6b20' }} onClick={onRetryMistakes}>
                        <RotateCcw size={18} style={{ verticalAlign: 'middle', marginRight: 5 }} />
                        間違えた問題だけ解き直す
                    </button>
                )}
                <button className="generate-btn" style={{ width: 'auto', padding: '12px 30px' }} onClick={onRetry}>
                    <RotateCcw size={18} style={{ verticalAlign: 'middle', marginRight: 5 }} />
                    新しい問題を作る (Retry)
                </button>
                <button className="generate-btn" style={{ width: 'auto', padding: '12px 30px', background: '#a0aec0' }} onClick={onHome}>
                    トップに戻る (Home)
                </button>
            </div>
        </div >
    );
};

export default ResultSummary;
