import React, { useState, useEffect } from 'react';
import { User, Mail, Calendar, Shield, AlertTriangle } from 'lucide-react';
import API_BASE_URL from '../api_config';

const Dashboard = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchUser = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Failed to load account info.');
            const data = await res.json();
            setUser(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUser();
    }, []);

    const handleWithdraw = async () => {
        if (!window.confirm('本当に退会しますか？この操作は取り消せず、学習履歴もすべて失われます。')) {
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/auth/me`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (res.ok) {
                alert('退会処理が完了しました。ご利用ありがとうございました。');
                localStorage.removeItem('token');
                window.location.href = '/';
            } else {
                const err = await res.json();
                alert(`退会に失敗しました: ${err.detail || '不明なエラー'}`);
            }
        } catch (err) {
            alert('ネットワークエラーが発生しました');
        }
    };

    if (loading) return <div style={styles.container}>Loading account info...</div>;
    if (error) return <div style={styles.container}>{error}</div>;

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <div style={styles.titleWrapper}>
                    <User size={26} className="text-purple-600" />
                    <h1 style={styles.title}>My Account</h1>
                </div>
            </div>

            <div style={styles.infoCard}>
                <div style={styles.infoRow}>
                    <div style={styles.infoLabel}><User size={16} /> Username</div>
                    <div style={styles.infoValue}>{user?.username || 'N/A'}</div>
                </div>
                <div style={styles.infoRow}>
                    <div style={styles.infoLabel}><Mail size={16} /> Email</div>
                    <div style={styles.infoValue}>{user?.email || 'N/A'}</div>
                </div>
                <div style={styles.infoRow}>
                    <div style={styles.infoLabel}><Shield size={16} /> Plan</div>
                    <div style={styles.infoValue}>
                        <span style={styles.badge}>{(user?.plan_type || 'standard').toUpperCase()}</span>
                    </div>
                </div>
                <div style={styles.infoRow}>
                    <div style={styles.infoLabel}><Calendar size={16} /> Member Since</div>
                    <div style={styles.infoValue}>
                        {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                    </div>
                </div>
            </div>

            <div style={styles.dangerCard}>
                <h2 style={styles.dangerTitle}>
                    <AlertTriangle size={18} /> Danger Zone
                </h2>
                <p style={styles.dangerText}>
                    アカウントを削除し、Verbaから退会します。学習履歴はすべて失われ、復元することはできません。
                </p>
                <button onClick={handleWithdraw} style={styles.dangerBtn}>
                    アカウントを削除して退会する
                </button>
            </div>
        </div>
    );
};

const styles = {
    container: { maxWidth: '700px', margin: '0 auto', padding: '20px', fontFamily: 'Inter, sans-serif' },
    header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' },
    titleWrapper: { display: 'flex', alignItems: 'center', gap: '12px' },
    title: { fontSize: '26px', fontWeight: 'bold', color: '#1a202c', margin: 0 },
    infoCard: { background: 'white', borderRadius: '12px', boxShadow: '0 4px 6px rgba(0,0,0,0.05)', border: '1px solid #edf2f7', padding: '8px 24px', marginBottom: '24px' },
    infoRow: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px 0', borderBottom: '1px solid #edf2f7' },
    infoLabel: { display: 'flex', alignItems: 'center', gap: '8px', color: '#718096', fontSize: '14px', fontWeight: '500' },
    infoValue: { color: '#2d3748', fontSize: '14px', fontWeight: '600' },
    badge: { background: '#ebf4ff', color: '#3182ce', padding: '4px 12px', borderRadius: '9999px', fontSize: '12px', fontWeight: 'bold' },
    dangerCard: { background: '#fff5f5', padding: '24px', borderRadius: '12px', border: '1px solid #fed7d7' },
    dangerTitle: { display: 'flex', alignItems: 'center', gap: '8px', fontSize: '16px', fontWeight: '600', color: '#c53030', marginBottom: '8px' },
    dangerText: { fontSize: '13px', color: '#c53030', marginBottom: '16px', lineHeight: 1.6 },
    dangerBtn: { background: '#e53e3e', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', fontWeight: 'bold', cursor: 'pointer', fontSize: '14px' }
};

export default Dashboard;
