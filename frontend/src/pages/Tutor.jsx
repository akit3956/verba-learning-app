import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import API_BASE_URL from "../api_config";
import { Send, User, MessageCircle, RefreshCw, BookOpen } from 'lucide-react';

const Tutor = ({ userPlan }) => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: '<ruby>初<rt>はじ</rt></ruby>めまして、ミス・キャプラン（Miss Kaplan）です。<ruby>今日<rt>きょう</rt></ruby>はどのような<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>学習<rt>がくしゅう</rt></ruby>をしましょうか？<ruby>教案<rt>きょうあん</rt></ruby>に<ruby>基<rt>もと</rt></ruby>づいた<ruby>特別<rt>とくべつ</rt></ruby>なレッスンを<ruby>始<rt>はじ</rt></ruby>めましょう！' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);


    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/api/tutor/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ message: input })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to chat with tutor');
            }
            const data = await response.json();

            setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, { role: 'assistant', content: `エラーが発生しました: ${err.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="tutor-container" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 150px)', background: 'white', borderRadius: '16px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', overflow: 'hidden' }}>
            <div className="tutor-header" style={{ padding: '20px', background: 'var(--primary-color)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <BookOpen size={24} />
                    <div>
                        <h2 style={{ margin: 0, fontSize: '1.2rem' }}>ミス・キャプランのAI教室</h2>
                        <p style={{ margin: 0, fontSize: '0.8rem', opacity: 0.9 }}>
                            教案RAGシステム: 高精度・プロのメソッド
                        </p>
                    </div>
                </div>
            </div>

            <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px', background: '#f9f9fb' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%', display: 'flex', gap: '8px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: msg.role === 'user' ? '#9333ea' : 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', flexShrink: 0 }}>
                            {msg.role === 'user' ? <User size={18} /> : <MessageCircle size={18} />}
                        </div>
                        <div style={{ padding: '12px 16px', borderRadius: '16px', background: msg.role === 'user' ? 'white' : 'white', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.02)', color: '#2d3748', lineHeight: '1.8' }}>
                            {msg.role === 'assistant' ? (
                                <ReactMarkdown 
                                    rehypePlugins={[rehypeRaw]}
                                    className="react-markdown"
                                >
                                    {msg.content}
                                </ReactMarkdown>
                            ) : (
                                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && (
                    <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                            <RefreshCw className="spinner" size={18} />
                        </div>
                        <div style={{ padding: '12px 16px', borderRadius: '16px', background: 'white', color: '#a0aec0', fontSize: '0.9rem' }}>
                            ミス・キャプランが教案（バイブル）を確認中...
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* AI Disclaimer */}
            <div style={{ padding: '8px 20px', background: '#fff', borderTop: '1px solid #f1f5f9', textAlign: 'center' }}>
                <p style={{ margin: 0, fontSize: '0.75rem', color: '#94a3b8', fontStyle: 'italic' }}>
                    ※ ミス・キャプランはAIであり、時として不正確な情報を生成することがあります。重要な学習内容は公式教材も併せて確認してください。
                </p>
            </div>

            <form onSubmit={handleSend} style={{ padding: '20px', background: 'white', borderTop: '1px solid #e2e8f0', display: 'flex', gap: '10px' }}>
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="日本語についてミス・キャプランに聞いてみましょう..."
                    style={{ flex: 1, padding: '12px 16px', borderRadius: '12px', border: '1px solid #e2e8f0', outline: 'none', transition: 'border-color 0.2s' }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary-color)'}
                    onBlur={(e) => e.target.style.borderColor = '#e2e8f0'}
                />
                <button
                    type="submit"
                    disabled={loading || !input.trim()}
                    style={{ padding: '12px 20px', borderRadius: '12px', background: 'var(--primary-color)', color: 'white', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px', fontWeight: '500', transition: 'opacity 0.2s' }}
                >
                    <Send size={18} /> 送信
                </button>
            </form>
        </div>
    );
};

export default Tutor;
