import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Lock, AlertCircle, CheckCircle } from 'lucide-react';
import API_BASE_URL from '../api_config';

const ResetPassword = () => {
    const { token } = useParams();
    const navigate = useNavigate();
    const [newPassword, setNewPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [status, setStatus] = useState({ type: '', message: '' });
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (newPassword !== confirmPassword) {
            setStatus({ type: 'error', message: 'Passwords do not match.' });
            return;
        }

        if (newPassword.length < 6) {
            setStatus({ type: 'error', message: 'Password must be at least 6 characters.' });
            return;
        }

        setLoading(true);
        setStatus({ type: '', message: '' });

        try {
            const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token, new_password: newPassword })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to reset password.');
            }

            setStatus({ type: 'success', message: 'Password successfully reset! You can now log in.' });
            setTimeout(() => {
                navigate('/');
            }, 3000);

        } catch (err) {
            setStatus({ type: 'error', message: err.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <div style={styles.card}>
                <div style={styles.header}>
                    <h2 style={styles.title}>Reset Password</h2>
                    <p style={styles.subtitle}>Enter your new password below.</p>
                </div>

                {status.message && (
                    <div style={{ ...styles.alert, background: status.type === 'error' ? '#fff5f5' : '#f0fff4', color: status.type === 'error' ? '#e53e3e' : '#2f855a', borderColor: status.type === 'error' ? '#fed7d7' : '#c6f6d5' }}>
                        {status.type === 'error' ? <AlertCircle size={18} /> : <CheckCircle size={18} />}
                        <span>{status.message}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} style={styles.form}>
                    <div style={styles.inputGroup}>
                        <div style={styles.inputIconWrapper}>
                            <Lock size={18} style={styles.inputIcon} />
                        </div>
                        <input
                            type="password"
                            placeholder="New Password"
                            value={newPassword}
                            onChange={(e) => setNewPassword(e.target.value)}
                            style={styles.input}
                            disabled={loading || status.type === 'success'}
                        />
                    </div>
                    
                    <div style={styles.inputGroup}>
                        <div style={styles.inputIconWrapper}>
                            <Lock size={18} style={styles.inputIcon} />
                        </div>
                        <input
                            type="password"
                            placeholder="Confirm New Password"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                            style={styles.input}
                            disabled={loading || status.type === 'success'}
                        />
                    </div>

                    <button
                        type="submit"
                        style={{ ...styles.button, opacity: (loading || status.type === 'success') ? 0.7 : 1 }}
                        disabled={loading || status.type === 'success'}
                    >
                        {loading ? 'Resetting...' : 'Reset Password'}
                    </button>
                    
                    <div style={styles.footer}>
                        <p style={styles.switchText}>
                            <button
                                type="button"
                                onClick={() => navigate('/')}
                                style={styles.switchButton}
                            >
                                Back to Sign In
                            </button>
                        </p>
                    </div>
                </form>
            </div>
        </div>
    );
};

const styles = {
    container: {
        width: '100%',
        maxWidth: '400px',
        margin: '40px auto',
    },
    card: {
        background: '#ffffff',
        borderRadius: '16px',
        boxShadow: '0 8px 30px rgba(0,0,0,0.08)',
        padding: '32px',
        border: '1px solid rgba(0,0,0,0.05)',
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
    alert: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '12px',
        borderRadius: '8px',
        marginBottom: '16px',
        fontSize: '14px',
        border: '1px solid',
    },
    footer: {
        marginTop: '16px',
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

export default ResetPassword;
