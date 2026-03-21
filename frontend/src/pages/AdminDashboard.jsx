import React, { useState, useEffect } from 'react';
import { Users, LayoutDashboard, RefreshCcw, ShieldAlert } from 'lucide-react';
import API_BASE_URL from '../api_config';

const AdminDashboard = () => {
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchUsers = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/auth/users`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                if (response.status === 403) {
                    throw new Error("You do not have permission to view the Admin Dashboard.");
                }
                throw new Error("Failed to fetch user list.");
            }

            const data = await response.json();
            setUsers(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const [config, setConfig] = useState({
        model: '',
        openai_api_key: '',
        gemini_api_key: ''
    });
    const [configLoading, setConfigLoading] = useState(false);
    const [configSuccess, setConfigSuccess] = useState(false);

    const fetchConfig = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/config`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (response.ok) {
                const data = await response.json();
                setConfig(data);
            }
        } catch (err) {
            console.error("Failed to fetch config:", err);
        }
    };

    const handleConfigChange = (e) => {
        const { name, value } = e.target;
        setConfig(prev => ({ ...prev, [name]: value }));
    };

    const saveConfig = async (e) => {
        e.preventDefault();
        setConfigLoading(true);
        setConfigSuccess(false);
        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_BASE_URL}/config`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(config)
            });
            if (response.ok) {
                setConfigSuccess(true);
                setTimeout(() => setConfigSuccess(false), 3000);
            } else {
                alert("Failed to update configuration");
            }
        } catch (err) {
            alert("Error updating configuration: " + err.message);
        } finally {
            setConfigLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
        fetchConfig();
    }, []);

    if (error) {
        return (
            <div style={styles.errorContainer}>
                <ShieldAlert size={48} color="#e53e3e" style={{ marginBottom: 16 }} />
                <h2 style={{ color: '#e53e3e', marginBottom: 8 }}>Access Denied</h2>
                <p>{error}</p>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <div style={styles.header}>
                <div style={styles.titleWrapper}>
                    <LayoutDashboard size={28} color="#3182ce" />
                    <h1 style={styles.title}>Admin Dashboard</h1>
                </div>
                <button onClick={() => { fetchUsers(); fetchConfig(); }} style={styles.refreshBtn} disabled={loading}>
                    <RefreshCcw size={18} className={loading ? "spin" : ""} />
                    Refresh
                </button>
            </div>

            <div style={styles.grid}>
                {/* Stats Card */}
                <div style={styles.statsCard}>
                    <div style={styles.statIcon}>
                        <Users size={24} color="#2b6cb0" />
                    </div>
                    <div>
                        <h3 style={styles.statLabel}>Total Registered Accounts</h3>
                        <p style={styles.statValue}>{loading ? '...' : users.length}</p>
                    </div>
                </div>

                {/* API Config Card */}
                <div style={styles.configCard}>
                    <h2 style={{ fontSize: '18px', marginBottom: '16px', color: '#2d3748' }}>System Configuration</h2>
                    <form onSubmit={saveConfig}>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>OpenAI API Key</label>
                            <input 
                                type="password" 
                                name="openai_api_key"
                                value={config.openai_api_key}
                                onChange={handleConfigChange}
                                style={styles.input}
                                placeholder="sk-proj-..."
                            />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Gemini API Key</label>
                            <input 
                                type="password" 
                                name="gemini_api_key"
                                value={config.gemini_api_key}
                                onChange={handleConfigChange}
                                style={styles.input}
                                placeholder="AIza..."
                            />
                        </div>
                        <button type="submit" style={styles.saveBtn} disabled={configLoading}>
                            {configLoading ? 'Saving...' : 'Update Keys'}
                        </button>
                        {configSuccess && <span style={styles.successMsg}>✓ Updated Successfully</span>}
                    </form>
                </div>
            </div>

            <div style={styles.tableCard}>
                <h2 style={{ fontSize: '18px', marginBottom: '16px', color: '#2d3748' }}>User List</h2>
                {loading ? (
                    <p style={{ textAlign: 'center', color: '#718096', padding: '20px' }}>Loading users...</p>
                ) : (
                    <div style={styles.tableWrapper}>
                        <table style={styles.table}>
                            <thead>
                                <tr>
                                    <th style={styles.th}>Username</th>
                                    <th style={styles.th}>Email</th>
                                    <th style={styles.th}>VRB Balance</th>
                                    <th style={styles.th}>Joined At</th>
                                </tr>
                            </thead>
                            <tbody>
                                {users.map(user => (
                                    <tr key={user.id} style={styles.tr}>
                                        <td style={styles.td}><strong>{user.username || 'N/A'}</strong></td>
                                        <td style={styles.td}>{user.email || 'N/A'}</td>
                                        <td style={styles.td}>
                                            <span style={styles.badge}>{user.vrb_balance} VRB</span>
                                        </td>
                                        <td style={styles.td}>
                                            {user.created_at ? new Date(user.created_at).toLocaleDateString() : 'Unknown'}
                                        </td>
                                    </tr>
                                ))}
                                {users.length === 0 && (
                                    <tr>
                                        <td colSpan="4" style={{ textAlign: 'center', padding: '20px', color: '#718096' }}>No users found.</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '1000px',
        margin: '0 auto',
        padding: '20px',
        fontFamily: 'Inter, sans-serif',
    },
    errorContainer: {
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 20px',
        background: '#fff5f5',
        border: '1px solid #fed7d7',
        borderRadius: '12px',
        marginTop: '40px',
        textAlign: 'center',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '30px',
    },
    titleWrapper: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
    },
    title: {
        fontSize: '28px',
        fontWeight: 'bold',
        color: '#1a202c',
        margin: 0,
    },
    refreshBtn: {
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '8px 16px',
        background: '#edf2f7',
        border: '1px solid #e2e8f0',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '500',
        color: '#4a5568',
        transition: 'all 0.2s',
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '30px',
        marginBottom: '30px',
    },
    statsCard: {
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        background: 'white',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
        border: '1px solid #edf2f7',
    },
    configCard: {
        background: 'white',
        padding: '24px',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
        border: '1px solid #edf2f7',
    },
    formGroup: {
        marginBottom: '16px',
    },
    label: {
        display: 'block',
        fontSize: '14px',
        fontWeight: '500',
        color: '#4a5568',
        marginBottom: '6px',
    },
    input: {
        width: '100%',
        padding: '10px 12px',
        borderRadius: '6px',
        border: '1px solid #e2e8f0',
        fontSize: '14px',
        color: '#2d3748',
        boxSizing: 'border-box',
    },
    saveBtn: {
        background: '#3182ce',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        borderRadius: '8px',
        fontWeight: 'bold',
        cursor: 'pointer',
        transition: 'background 0.2s',
    },
    successMsg: {
        color: '#38a169',
        fontSize: '14px',
        marginLeft: '12px',
        fontWeight: '500',
    },
    statIcon: {
        background: '#ebf8ff',
        padding: '16px',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    statLabel: {
        margin: '0 0 4px 0',
        fontSize: '14px',
        color: '#718096',
        textTransform: 'uppercase',
        letterSpacing: '0.05em',
    },
    statValue: {
        margin: 0,
        fontSize: '32px',
        fontWeight: 'bold',
        color: '#2b6cb0',
    },
    tableCard: {
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
        padding: '24px',
        border: '1px solid #edf2f7',
    },
    tableWrapper: {
        overflowX: 'auto',
    },
    table: {
        width: '100%',
        borderCollapse: 'collapse',
        textAlign: 'left',
    },
    th: {
        padding: '12px 16px',
        borderBottom: '2px solid #edf2f7',
        color: '#4a5568',
        fontWeight: '600',
        fontSize: '14px',
    },
    tr: {
        borderBottom: '1px solid #edf2f7',
    },
    td: {
        padding: '16px',
        color: '#2d3748',
        fontSize: '14px',
    },
    badge: {
        background: '#feebc8',
        color: '#c05621',
        padding: '4px 8px',
        borderRadius: '9999px',
        fontSize: '12px',
        fontWeight: 'bold',
        display: 'inline-block',
    }
};

export default AdminDashboard;
