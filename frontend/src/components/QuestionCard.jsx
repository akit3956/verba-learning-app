import React from 'react';

import { Image as ImageIcon, Loader } from 'lucide-react';

const QuestionCard = ({ data, onAnswer, answered, selectedAnswer }) => {
    const [imgLoaded, setImgLoaded] = React.useState(false);

    // Reset loading state when data changes
    React.useEffect(() => {
        setImgLoaded(false);
    }, [data.image_url]);
    // Function to render text with Ruby tags (furigana)
    const renderRuby = (text) => {
        if (!text) return null;

        // Regex for Kanji(Furigana) or Kanji（Furigana）
        const regex = /([一-龠々ヶ々〇]+)[(（]([ぁ-んァ-ヶー]+)[)）]/g;

        const elements = [];
        let lastIndex = 0;
        let match;
        let keyCounter = 0;

        while ((match = regex.exec(text)) !== null) {
            // 1. Plain text before the match
            if (match.index > lastIndex) {
                elements.push(
                    <span key={`text-${keyCounter++}`}>
                        {text.substring(lastIndex, match.index)}
                    </span>
                );
            }

            // 2. The Ruby part
            elements.push(
                <ruby key={`ruby-${keyCounter++}`}>
                    {match[1]}
                    <rt>{match[2]}</rt>
                </ruby>
            );

            lastIndex = regex.lastIndex;
        }

        // 3. Remaining plain text after the last match
        if (lastIndex < text.length) {
            elements.push(
                <span key={`text-${keyCounter++}`}>
                    {text.substring(lastIndex)}
                </span>
            );
        }

        return elements;
    };

    const getOptionClass = (index) => {
        if (!answered) return '';
        if (index === data.correctIndex) return 'correct';
        if (index === selectedAnswer && index !== data.correctIndex) return 'incorrect';
        return '';
    };

    return (
        <div className="question-area">
            {data.passage && (
                <div className="glass-panel" style={{ marginBottom: '2rem', background: 'rgba(255,255,255,0.4)' }}>
                    <h3 style={{ marginTop: 0 }}>読み物</h3>
                    <p style={{ fontSize: '1.2rem' }}>{renderRuby(data.passage)}</p>
                </div>
            )}

            {data.image_url && (
                <div className="visual-hint" style={{ textAlign: 'center', marginBottom: '1.5rem', minHeight: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', background: '#f8fafc', borderRadius: '12px' }}>
                    <div style={{ fontSize: '0.9rem', color: '#666', marginBottom: 5, display: 'flex', alignItems: 'center' }}>
                        <ImageIcon size={14} style={{ marginRight: 5 }} />
                        Visual Hint (AI generated)
                    </div>

                    {!imgLoaded && (
                        <div style={{ padding: '2rem', color: '#64748b' }}>
                            <Loader className="spin" size={24} style={{ marginBottom: '0.5rem' }} />
                            <div>Generating illustration...</div>
                        </div>
                    )}

                    <img
                        src={data.image_url}
                        alt="Problem Context"
                        onLoad={() => setImgLoaded(true)}
                        style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '12px', display: imgLoaded ? 'block' : 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                    />
                </div>
            )}

            <div className="question-text">
                Q. {renderRuby(data.question)}
            </div>

            <div className="options-grid">
                {data.options.map((opt, idx) => (
                    <button
                        key={idx}
                        className={`option-btn ${getOptionClass(idx)}`}
                        onClick={() => !answered && onAnswer(idx)}
                        disabled={answered}
                    >
                        {renderRuby(opt)}
                    </button>
                ))}
            </div>

            {answered && (
                <div className="explanation-box">
                    <strong>【答え】{data.options[data.correctIndex]}</strong>
                    <hr style={{ margin: '10px 0', border: 'none', borderTop: '1px solid rgba(0,0,0,0.1)' }} />
                    <p>{renderRuby(data.explanation)}</p>
                </div>
            )}
        </div>
    );
};

export default QuestionCard;
