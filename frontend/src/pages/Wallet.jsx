import API_BASE_URL from "../api_config";
import React, { useState, useEffect } from 'react';
import { Wallet as WalletIcon, History, Send, ArrowRight, User, TrendingUp, TrendingDown, Sparkles } from 'lucide-react';

function Wallet() {
    const [userId, setUserId] = useState(null);
    const [balance, setBalance] = useState(null);
    const [transactions, setTransactions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [transferData, setTransferData] = useState({ receiver: '', amount: '' });
    const [message, setMessage] = useState('');

    const fetchData = async () => {
        setLoading(true);
        try {
            const token = localStorage.getItem('token');
            const meRes = await fetch(API_BASE_URL + '/auth/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });

            if (!meRes.ok) throw new Error('Failed to fetch user');

            const userData = await meRes.json();
            setUserId(userData.id);
            setBalance({ balance: userData.vrb_balance, username: userData.username });

            const txRes = await fetch(`${API_BASE_URL}/api/wallet/transactions/${userData.id}`);
            const txData = await txRes.json();
            setTransactions(txData);
        } catch (err) {
            console.error("Wallet fetch error:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleTransfer = async (e) => {
        e.preventDefault();
        setMessage('');

        if (!transferData.receiver || !transferData.amount || !userId) return;

        try {
            const res = await fetch(API_BASE_URL + '/api/wallet/transfer', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sender_id: userId,
                    receiver_id: transferData.receiver,
                    amount: parseInt(transferData.amount),
                    description: "User Transfer"
                })
            });

            const data = await res.json();

            if (res.ok) {
                setMessage('Transferred successfully!');
                setTransferData({ receiver: '', amount: '' });
                fetchData(); // Refresh UI
            } else {
                setMessage(`Error: ${data.detail || 'Transfer failed'}`);
            }
        } catch (err) {
            setMessage('Network error');
        }
    };

    if (loading && !balance) return <div className="glass-panel">Loading Wallet...</div>;

    return (
        <div className="glass-panel">
            <h1 className="flex items-center gap-2 text-2xl font-bold mb-6">
                <WalletIcon className="text-purple-600" /> Verba Wallet
            </h1>

            {/* Balance Card */}
            <div style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                padding: '2rem',
                borderRadius: '16px',
                marginBottom: '2rem',
                textAlign: 'center',
                boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                position: 'relative',
                overflow: 'hidden'
            }}>
                <Sparkles className="absolute top-4 right-4 text-yellow-300 opacity-50" size={32} />
                <div style={{ fontSize: '1.2rem', opacity: 0.9 }}>Your Balance</div>
                <div style={{ fontSize: '3.5rem', fontWeight: 'bold', margin: '10px 0', lineHeight: 1 }}>
                    {balance ? balance.balance : 0} <span style={{ fontSize: '1.5rem' }}>VRB</span>
                </div>

                <div style={{ fontSize: '0.9rem', opacity: 0.8 }}>User: {balance ? balance.username : 'Guest'}</div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Transfer Section */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-700">
                        <Send size={20} /> Send Tokens
                    </h2>
                    <form onSubmit={handleTransfer} className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-500 mb-1">Receiver ID</label>
                            <div className="flex items-center border rounded px-3 py-2 bg-gray-50 focus-within:bg-white focus-within:ring-2 ring-indigo-100 transition-all">
                                <User size={16} className="text-gray-400 mr-2" />
                                <input
                                    type="text"
                                    placeholder="e.g. user_2"
                                    className="bg-transparent outline-none w-full text-gray-700"
                                    value={transferData.receiver}
                                    onChange={(e) => setTransferData({ ...transferData, receiver: e.target.value })}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-500 mb-1">Amount (VRB)</label>
                            <input
                                type="number"
                                min="1"
                                placeholder="0"
                                className="w-full border rounded px-3 py-2 bg-gray-50 focus:bg-white focus:ring-2 ring-indigo-100 outline-none transition-all text-gray-700"
                                value={transferData.amount}
                                onChange={(e) => setTransferData({ ...transferData, amount: e.target.value })}
                            />
                        </div>

                        {message && (
                            <div className={`text-sm p-2 rounded ${message.includes('Error') ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                {message}
                            </div>
                        )}

                        <button type="submit" className="w-full bg-indigo-600 text-white py-2 rounded hover:bg-indigo-700 transition flex items-center justify-center gap-2 font-medium shadow-md hover:shadow-lg transform hover:-translate-y-0.5">
                            Send Tokens <ArrowRight size={16} />
                        </button>
                    </form>
                </div>

                {/* History Section */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 text-gray-700">
                        <History size={20} /> Recent Activity
                    </h2>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }} className="pr-1 custom-scrollbar">
                        {transactions.length === 0 ? (
                            <div className="text-gray-400 text-center py-8 bg-gray-50 rounded border border-dashed border-gray-200">No transactions yet</div>
                        ) : (
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <tbody>
                                    {transactions.map(tx => {
                                        const isCredit = ['reward', 'transfer_in'].includes(tx.type);
                                        return (
                                            <tr key={tx.id} className="border-b last:border-0 border-gray-50 hover:bg-gray-50 transition-colors">
                                                <td className="py-3 pl-2">
                                                    <div className={`p-2 rounded-full ${isCredit ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'} w-8 h-8 flex items-center justify-center`}>
                                                        {isCredit ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
                                                    </div>
                                                </td>
                                                <td className="py-3 px-2">
                                                    <div className="font-medium text-gray-800 text-sm capitalize">{tx.type.replace('_', ' ')}</div>
                                                    <div className="text-xs text-gray-500">
                                                        {new Date(tx.timestamp).toLocaleDateString()}
                                                    </div>
                                                </td>
                                                <td className="py-3 px-2 text-sm text-gray-600 truncate max-w-[120px]" title={tx.description}>
                                                    {tx.description}
                                                </td>
                                                <td className={`py-3 pr-2 text-right font-bold text-sm ${isCredit ? 'text-green-600' : 'text-red-600'}`}>
                                                    {isCredit ? '+' : '-'}{tx.amount}
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Wallet;
