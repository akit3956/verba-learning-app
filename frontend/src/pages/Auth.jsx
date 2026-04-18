import API_BASE_URL from "../api_config";
import React, { useState, useEffect } from 'react';
import { LogIn, UserPlus, Lock, User, AlertCircle, Sparkles, Mail } from 'lucide-react';

const Auth = ({ onLogin }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [isForgotPassword, setIsForgotPassword] = useState(false);
    const [email, setEmail] = useState('');
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [successMsg, setSuccessMsg] = useState('');
    const [loading, setLoading] = useState(false);
    const [planType, setPlanType] = useState('standard');
    const [isPaymentVerified, setIsPaymentVerified] = useState(false);
    const [subscriptionId, setSubscriptionId] = useState('');

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const plan = params.get('plan');
        const payment = params.get('payment');

        if (plan) {
            setPlanType(plan);
            if (plan !== 'standard') {
                setIsLogin(false); // Force Sign Up for paid plans
            }
        }

        if (payment === 'success') {
            setIsPaymentVerified(true);
            const subId = params.get('subscription_id');
            if (subId) setSubscriptionId(subId);
        }
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccessMsg('');

        if (isForgotPassword) {
            if (!email) {
                setError('Please enter your email address');
                return;
            }
        } else if (isLogin) {
            if (!email || !password) {
                setError('Please fill in all fields');
                return;
            }
        } else {
            if (!email || !username || !password) {
                setError('Please fill in all fields');
                return;
            }
        }

        setLoading(true);

        const endpoint = isLogin ? '/auth/login' : '/auth/register';

        try {
            if (isForgotPassword) {
                const response = await fetch(`${API_BASE_URL}/auth/forgot-password`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email })
                });
                
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || 'Failed to send reset request.');
                }
                setSuccessMsg(data.message || 'Password reset link generated.');
                return;
            }

            let body, headers;
            // OAuth2PasswordRequestForm expects x-www-form-urlencoded
            if (isLogin) {
                body = new URLSearchParams({
                    username: email, // Map email input to the required 'username' field format
                    password: password,
                });
                headers = {
                    'Content-Type': 'application/x-www-form-urlencoded',
                };
            } else {
                body = JSON.stringify({ 
                    email, 
                    username, 
                    password, 
                    plan_type: planType,
                    is_founder: planType === 'founder',
                    paypal_subscription_id: subscriptionId
                });
                headers = { 'Content-Type': 'application/json' };
            }

            const response = await fetch(`${API_BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: headers,
                body: body,
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.detail || 'Authentication failed. Please try again.');
            }

            const data = await response.json();
            localStorage.setItem('token', data.access_token);
            onLogin(data.access_token);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                {isPaymentVerified && !isLogin && (
                    <div style={styles.founderBanner}>
                        <Sparkles size={20} color="#2f855a" />
                        <span>
                            {planType === 'founder' 
                                ? "Thank you for funding Verba! Create your account to activate Founder's status."
                                : `Payment Verified! Create your account to activate your ${planType.toUpperCase()} status.`}
                        </span>
                    </div>
                )}

                <div style={styles.header}>
                    <h2 style={styles.title}>
                        {isForgotPassword ? 'Reset Password' : (isLogin ? 'Welcome Back' : 'Create Account')}
                    </h2>
                    <p style={styles.subtitle}>
                        {isForgotPassword 
                            ? 'Enter your email to receive a password reset link'
                            : (isLogin
                                ? 'Sign in to continue your JLPT learning journey'
                                : 'Sign up to start learning and earning VRB Tokens')}
                    </p>
                </div>

                {error && (
                    <div style={styles.error}>
                        <AlertCircle size={18} />
                        <span>{error}</span>
                    </div>
                )}
                
                {successMsg && (
                    <div style={{...styles.error, background: '#f0fff4', color: '#2f855a', borderColor: '#c6f6d5'}}>
                        <Sparkles size={18} />
                        <span>{successMsg}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} style={styles.form}>
                    {(!isLogin && !isForgotPassword) && (
                        <div style={styles.inputGroup}>
                            <div style={styles.inputIconWrapper}>
                                <User size={18} style={styles.inputIcon} />
                            </div>
                            <input
                                type="text"
                                placeholder="Display Name / Username"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                style={styles.input}
                            />
                        </div>
                    )}

                    <div style={styles.inputGroup}>
                        <div style={styles.inputIconWrapper}>
                            <Mail size={18} style={styles.inputIcon} />
                        </div>
                        <input
                            type="email"
                            placeholder="Email Address"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            style={styles.input}
                        />
                    </div>

                    {!isForgotPassword && (
                        <div style={styles.inputGroup}>
                            <div style={styles.inputIconWrapper}>
                                <Lock size={18} style={styles.inputIcon} />
                            </div>
                            <input
                                type="password"
                                placeholder="Password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                style={styles.input}
                            />
                        </div>
                    )}
                    
                    {isLogin && !isForgotPassword && (
                        <div style={{ textAlign: 'right', marginTop: '-8px' }}>
                            <button 
                                type="button" 
                                onClick={() => { setIsForgotPassword(true); setError(''); setSuccessMsg(''); }}
                                style={{ background: 'none', border: 'none', color: '#3182ce', fontSize: '13px', cursor: 'pointer', padding: 0 }}
                            >
                                Forgot Password?
                            </button>
                        </div>
                    )}

                    <button
                        type="submit"
                        style={{ ...styles.button, opacity: loading ? 0.7 : 1 }}
                        disabled={loading}
                    >
                        {loading ? (
                            <span className="loading-dots" style={{ margin: 0, height: '24px' }}>
                                <span className="dot" style={{ width: '8px', height: '8px', background: 'white' }}></span>
                                <span className="dot" style={{ width: '8px', height: '8px', background: 'white' }}></span>
                                <span className="dot" style={{ width: '8px', height: '8px', background: 'white' }}></span>
                            </span>
                        ) : isForgotPassword ? (
                            <><Mail size={18} /> Send Reset Link</>
                        ) : isLogin ? (
                            <><LogIn size={18} /> Sign In</>
                        ) : (
                            <><UserPlus size={18} /> Sign Up</>
                        )}
                    </button>
                </form>

                <div style={styles.footer}>
                    {isForgotPassword ? (
                        <p style={styles.switchText}>
                            Remember your password?{' '}
                            <button
                                onClick={() => { setIsForgotPassword(false); setIsLogin(true); setError(''); setSuccessMsg(''); }}
                                style={styles.switchButton}
                            >
                                Back to sign in
                            </button>
                        </p>
                    ) : (
                        <p style={styles.switchText}>
                            {isLogin ? "Don't have an account? " : "Already have an account? "}
                            <button
                                onClick={() => { setIsLogin(!isLogin); setError(''); setSuccessMsg(''); }}
                                style={styles.switchButton}
                            >
                                {isLogin ? 'Sign up' : 'Sign in'}
                            </button>
                        </p>
                    )}
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        width: '100%',
        maxWidth: '400px',
        margin: '0 auto',
    },
    card: {
        background: '#ffffff',
        borderRadius: '16px',
        boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        padding: '32px',
        border: '1px solid rgba(0,0,0,0.05)',
    },
    founderBanner: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        backgroundColor: '#fffff0',
        color: '#975a16',
        padding: '16px',
        borderRadius: '8px',
        border: '1px solid #fefcbf',
        marginBottom: '24px',
        fontSize: '14px',
        fontWeight: '500',
        lineHeight: '1.4',
    },
    header: {
        textAlign: 'center',
        marginBottom: '24px',
    },
    title: {
        fontSize: '24px',
        fontWeight: '700',
        color: '#1a202c',
        marginBottom: '8px',
    },
    subtitle: {
        fontSize: '14px',
        color: '#718096',
        lineHeight: '1.5',
    },
    form: {
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
    },
    inputGroup: {
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
    },
    inputIconWrapper: {
        position: 'absolute',
        left: '12px',
        color: '#a0aec0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    inputIcon: {
        color: '#a0aec0',
    },
    input: {
        width: '100%',
        padding: '12px 12px 12px 40px',
        borderRadius: '8px',
        border: '1px solid #e2e8f0',
        fontSize: '15px',
        outline: 'none',
        transition: 'border-color 0.2s, box-shadow 0.2s',
        boxSizing: 'border-box',
        backgroundColor: '#f8fafc',
    },
    button: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        background: '#3182ce',
        color: 'white',
        border: 'none',
        borderRadius: '8px',
        padding: '12px',
        fontSize: '16px',
        fontWeight: '600',
        cursor: 'pointer',
        transition: 'background 0.2s',
        marginTop: '8px',
    },
    error: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        background: '#fff5f5',
        color: '#e53e3e',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
        fontSize: '14px',
        border: '1px solid #fed7d7',
    },
    footer: {
        marginTop: '24px',
        textAlign: 'center',
    },
    switchText: {
        fontSize: '14px',
        color: '#4a5568',
    },
    switchButton: {
        background: 'none',
        border: 'none',
        color: '#3182ce',
        fontWeight: '600',
        cursor: 'pointer',
        padding: 0,
        fontSize: '14px',
    }
};

export default Auth;
