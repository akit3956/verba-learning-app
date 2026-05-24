import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import API_BASE_URL from "../api_config";
import { Send, User, MessageCircle, RefreshCw, BookOpen, Gift, MessageSquare } from 'lucide-react';

const Tutor = ({ userPlan, onUsageUpdate }) => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: '<ruby>初<rt>はじ</rt></ruby>めまして、ミス・キャプラン（Miss Kaplan）です。<ruby>今日<rt>きょう</rt></ruby>はどのような<ruby>日本語<rt>にほんご</rt></ruby>の<ruby>学習<rt>がくしゅう</rt></ruby>をしましょうか？<ruby>教案<rt>きょうあん</rt></ruby>に<ruby>基<rt>もと</rt></ruby>づいた<ruby>特別<rt>とくべつ</rt></ruby>なレッスンを<ruby>始<rt>はじ</rt></ruby>めましょう！' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    
    // --- 90s UX & KPI States ---
    const [showSafetyMsg, setShowSafetyMsg] = useState(false);
    const [showDiscordCTA, setShowDiscordCTA] = useState(false);
    const [earnedTokens, setEarnedTokens] = useState(0);
    const [showTokenAnim, setShowTokenAnim] = useState(false);

    const kpiRef = useRef({
        firstMsgTime: null,
        lastBotReplyTime: null,
        consecutiveTurns: 0,
        messagesWithin90s: 0,
        replyLengths: [],
        totalEmojiCount: 0,
        totalChars: 0,
        responseSpeeds: []
    });

    const messagesEndRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, showSafetyMsg, showDiscordCTA]);

    // Timer for 90s Community CTA
    useEffect(() => {
        if (kpiRef.current.firstMsgTime && !showDiscordCTA) {
            const timer = setTimeout(() => {
                setShowDiscordCTA(true);
            }, 90000); // 90 seconds
            return () => clearTimeout(timer);
        }
    }, [kpiRef.current.firstMsgTime, showDiscordCTA]);


    const countEmojis = (str) => {
        const emojiRegex = /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu;
        return (str.match(emojiRegex) || []).length;
    };

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim() || loading) return;

        const now = Date.now();
        const kpis = kpiRef.current;

        // KPI: First message time
        if (!kpis.firstMsgTime) {
            kpis.firstMsgTime = now;
        }

        // KPI: Messages within 90s
        if (now - kpis.firstMsgTime <= 90000) {
            kpis.messagesWithin90s += 1;
        }

        // KPI: Response Speed (Time from last bot reply to user send)
        if (kpis.lastBotReplyTime) {
            const speed = (now - kpis.lastBotReplyTime) / 1000;
            kpis.responseSpeeds.push(speed);
        }

        // KPI: Length and Emojis
        const len = input.length;
        kpis.replyLengths.push(len);
        kpis.totalChars += len;
        kpis.totalEmojiCount += countEmojis(input);
        kpis.consecutiveTurns += 1;

        // Log KPIs to console for Vee
        const avgSpeed = kpis.responseSpeeds.length ? (kpis.responseSpeeds.reduce((a, b) => a + b, 0) / kpis.responseSpeeds.length).toFixed(1) : 0;
        const avgLen = (kpis.replyLengths.reduce((a, b) => a + b, 0) / kpis.replyLengths.length).toFixed(1);
        const emojiRatio = kpis.totalChars ? ((kpis.totalEmojiCount / kpis.totalChars) * 100).toFixed(1) : 0;
        
        console.log(`📊 [KPI Tracking]
        - 連続ターン数: ${kpis.consecutiveTurns}
        - 90秒内送信数: ${kpis.messagesWithin90s}
        - 平均返信文字数: ${avgLen} 文字
        - 平均返信速度: ${avgSpeed} 秒
        - 絵文字出現率: ${emojiRatio} %`);

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);
        setShowSafetyMsg(false);

        // 3-second Safety UI Timeout
        const safetyTimer = setTimeout(() => {
            setShowSafetyMsg(true);
        }, 3000);

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

            clearTimeout(safetyTimer);
            setShowSafetyMsg(false);

            setMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
            kpis.lastBotReplyTime = Date.now();
            
            if (onUsageUpdate) onUsageUpdate();

            // L2E Web3 Onboarding Animation (+10 $VRB)
            setEarnedTokens(prev => prev + 10);
            setShowTokenAnim(true);
            setTimeout(() => setShowTokenAnim(false), 3000);

        } catch (err) {
            console.error(err);
            clearTimeout(safetyTimer);
            setShowSafetyMsg(false);
            setMessages(prev => [...prev, { role: 'assistant', content: `エラーが発生しました: ${err.message}` }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="tutor-container" style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', flexDirection: 'column', height: 'calc(100vh - 150px)', background: 'white', borderRadius: '16px', boxShadow: '0 10px 25px rgba(0,0,0,0.1)', overflow: 'hidden', position: 'relative' }}>
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
                {/* L2E Token Display */}
                <div style={{ background: 'rgba(255,255,255,0.2)', padding: '5px 12px', borderRadius: '20px', display: 'flex', alignItems: 'center', gap: '5px', fontWeight: 'bold' }}>
                    <Gift size={16} /> 
                    <span>{earnedTokens} $VRB</span>
                    {showTokenAnim && (
                        <span style={{ position: 'absolute', top: '30px', right: '30px', color: '#fbbf24', fontWeight: 'bold', animation: 'floatUp 2s forwards' }}>
                            +10 $VRB ✨
                        </span>
                    )}
                </div>
            </div>

            {/* Custom CSS for animation */}
            <style>{`
                @keyframes floatUp {
                    0% { transform: translateY(0); opacity: 1; }
                    100% { transform: translateY(-30px); opacity: 0; }
                }
            `}</style>

            <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '15px', background: '#f9f9fb' }}>
                {messages.map((msg, idx) => (
                    <div key={idx} style={{ alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start', maxWidth: '80%', display: 'flex', gap: '8px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: msg.role === 'user' ? '#9333ea' : 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', flexShrink: 0 }}>
                            {msg.role === 'user' ? <User size={18} /> : <MessageCircle size={18} />}
                        </div>
                        <div style={{ padding: '12px 16px', borderRadius: '16px', background: msg.role === 'user' ? 'white' : 'white', border: '1px solid #e2e8f0', boxShadow: '0 2px 4px rgba(0,0,0,0.02)', color: '#2d3748', lineHeight: '1.8' }}>
                            {msg.role === 'assistant' ? (
                                <div className="react-markdown">
                                    <ReactMarkdown 
                                        rehypePlugins={[rehypeRaw]}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                            ) : (
                                <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                            )}
                        </div>
                    </div>
                ))}
                {loading && !showSafetyMsg && (
                    <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                            <RefreshCw className="spinner" size={18} />
                        </div>
                        <div style={{ padding: '12px 16px', borderRadius: '16px', background: 'white', color: '#a0aec0', fontSize: '0.9rem' }}>
                            ミス・キャプランが教案（バイブル）を確認中...
                        </div>
                    </div>
                )}
                {/* 3s Safety UI */}
                {showSafetyMsg && (
                    <div style={{ alignSelf: 'flex-start', display: 'flex', gap: '8px' }}>
                        <div style={{ width: '32px', height: '32px', borderRadius: '50%', background: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                            <MessageCircle size={18} />
                        </div>
                        <div style={{ padding: '12px 16px', borderRadius: '16px', background: '#fffbeb', border: '1px solid #fde68a', color: '#92400e', fontSize: '0.95rem' }}>
                            *(Miss Kaplanが嬉しそうに考えています...)* ✨
                        </div>
                    </div>
                )}

                {/* 90s Discord CTA */}
                {showDiscordCTA && (
                    <div style={{ alignSelf: 'center', width: '90%', margin: '20px 0', padding: '15px', borderRadius: '12px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', color: 'white', textAlign: 'center', boxShadow: '0 4px 15px rgba(99, 102, 241, 0.3)' }}>
                        <h4 style={{ margin: '0 0 10px 0', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                            <MessageSquare size={20} /> 🎉 初回チュートリアルクリア！
                        </h4>
                        <p style={{ margin: '0 0 15px 0', fontSize: '0.9rem', opacity: 0.9 }}>
                            今ならDiscordコミュニティで限定ロール「初期貢献者」が付与されます！
                        </p>
                        <a href="#" style={{ display: 'inline-block', padding: '8px 24px', background: 'white', color: '#6366f1', textDecoration: 'none', borderRadius: '20px', fontWeight: 'bold', fontSize: '0.9rem' }}>
                            Discordに参加
                        </a>
                    </div>
                )}
                
                <div ref={messagesEndRef} />
            </div>

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

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("ErrorBoundary caught an error", error, errorInfo);
    this.setState({ errorInfo });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', color: 'red', background: '#fee2e2', minHeight: '100vh', zIndex: 9999, position: 'relative' }}>
          <h2>React Runtime Error!</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '14px' }}>
            {this.state.error && this.state.error.toString()}
          </pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px', color: '#7f1d1d' }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

const TutorWithErrorBoundary = (props) => (
  <ErrorBoundary>
    <Tutor {...props} />
  </ErrorBoundary>
);

export default TutorWithErrorBoundary;
