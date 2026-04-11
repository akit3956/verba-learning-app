import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Check, Star, Zap, Shield, AlertCircle, MessageCircle } from 'lucide-react';
import API_BASE_URL from "../api_config";

const PayPalButton = ({ amount, onApprove, onError }) => {
    const containerRef = React.useRef(null);
  
    React.useEffect(() => {
      // Clean up previous button to prevent duplicates
      if (containerRef.current) {
          containerRef.current.innerHTML = '';
      }

      if (window.paypal && containerRef.current) {
        window.paypal.Buttons({
          style: {
            shape: 'rect',
            color: 'gold',
            layout: 'vertical',
            label: 'pay',
          },
          createOrder: (data, actions) => {
            return actions.order.create({
              purchase_units: [{
                amount: { value: amount }
              }]
            });
          },
          onApprove: (data, actions) => {
            return actions.order.capture().then((details) => {
              onApprove(details);
            });
          },
          onError: (err) => {
             console.error("PayPal Error:", err);
             if (onError) onError(err);
          }
        }).render(containerRef.current);
      }
    }, [amount, onApprove, onError]);
  
    return <div ref={containerRef} className="w-full mt-4" style={{ minHeight: '150px' }} />;
  };

const Upgrade = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleUpgradePro = async (details) => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/wallet/upgrade-plan`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    paypal_order_id: details.id,
                    plan_type: 'pro'
                })
            });

            if (!res.ok) throw new Error("Failed to upgrade plan on the server.");
            
            setSuccessMessage("Successfully upgraded to Pro! Welcome to unlimited learning.");
            
            // Reload page or force auth refresh in a real app. For now we prompt re-login or just navigate.
            setTimeout(() => {
                navigate('/');
                window.location.reload(); // Refresh to ensure NavBar gets the new userPlan
            }, 3000);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    const handlePurchaseVRB = async (details, amountUSD, vrbTokens) => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${API_BASE_URL}/api/wallet/purchase-tokens`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    paypal_order_id: details.id,
                    amount_usd: amountUSD,
                    tokens_granted: vrbTokens
                })
            });

            if (!res.ok) throw new Error("Failed to grant VRB tokens on the server.");
            
            setSuccessMessage(`Successfully purchased ${vrbTokens} VRB!`);
            
            setTimeout(() => {
                navigate('/wallet');
            }, 2000);
        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-10 px-6">
            <div className="max-w-4xl mx-auto">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-slate-800 mb-4 flex items-center justify-center gap-2">
                        <Sparkles className="text-indigo-500" /> Account Upgrade
                    </h2>
                    <p className="text-slate-600">Upgrade your plan to unlock more features, or buy VRB tokens to use directly in the app.</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-8 flex items-center gap-2 border border-red-200">
                        <AlertCircle size={20} />
                        <span>{error}</span>
                    </div>
                )}

                {successMessage && (
                    <div className="bg-emerald-50 text-emerald-600 p-4 rounded-lg mb-8 flex items-center gap-2 border border-emerald-200">
                        <Sparkles size={20} />
                        <span>{successMessage}</span>
                    </div>
                )}

                {loading ? (
                    <div className="text-center py-20">
                        <div className="text-xl text-indigo-600 font-bold animate-pulse">Processing your transaction...</div>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                        
                        {/* Token Purchase Section */}
                        <div className="bg-white p-8 rounded-3xl shadow-sm border border-slate-200 flex flex-col hover:shadow-md transition-shadow">
                            <div className="mb-6">
                                <div className="text-emerald-600 bg-emerald-50 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Token Pack</div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-4xl font-bold text-slate-800">$5.00</span>
                                </div>
                                <p className="text-slate-500 text-sm mt-1">One-time purchase</p>
                            </div>
                            
                            <ul className="space-y-4 mb-8 flex-1">
                                <li className="flex gap-3 text-sm text-slate-600 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-emerald-100 flex items-center justify-center shrink-0">
                                        <Star size={12} className="text-emerald-600" />
                                    </div>
                                    Get 500 VRB Tokens Instantly
                                </li>
                                <li className="flex gap-3 text-sm text-slate-600 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                                        <Check size={12} className="text-slate-600" />
                                    </div>
                                    Use for quizzes and AI Tutor rounds
                                </li>
                                <li className="flex gap-3 text-sm text-slate-600 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                                        <Check size={12} className="text-slate-600" />
                                    </div>
                                    Never expires
                                </li>
                            </ul>
                            
                            <PayPalButton 
                                amount="5.00" 
                                onApprove={(details) => handlePurchaseVRB(details, 5.00, 500)} 
                                onError={(err) => setError("PayPal transaction failed. Please try again.")}
                            />
                        </div>

                        {/* Pro Upgrade Section */}
                        <div className="bg-gradient-to-b from-indigo-50 to-white p-8 rounded-3xl shadow-md border border-indigo-100 flex flex-col hover:shadow-lg transition-shadow relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-2xl"></div>
                            
                            <div className="mb-6 relative z-10">
                                <div className="text-indigo-600 bg-indigo-100 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter shadow-sm">Verba Pro</div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-4xl font-bold text-indigo-900">$12.99</span>
                                    <span className="text-slate-500 font-medium text-sm">/ Month</span>
                                </div>
                                <p className="text-indigo-600/80 text-sm mt-1 font-medium">1-Month Unlimited Pass</p>
                            </div>
                            
                            <ul className="space-y-4 mb-8 flex-1 relative z-10">
                                <li className="flex gap-3 text-sm text-slate-700 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                                        <Zap size={12} className="text-indigo-600" />
                                    </div>
                                    Unlimited JLPT Quizzes
                                </li>
                                <li className="flex gap-3 text-sm text-slate-700 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                                        <MessageCircle size={12} className="text-indigo-600" />
                                    </div>
                                    Unlimited AI Tutor Chat (24/7)
                                </li>
                                <li className="flex gap-3 text-sm text-slate-700 font-medium">
                                    <div className="w-5 h-5 rounded-full bg-indigo-100 flex items-center justify-center shrink-0">
                                        <Shield size={12} className="text-indigo-600" />
                                    </div>
                                    Priority email support
                                </li>
                            </ul>
                            
                            <div className="relative z-10">
                                <PayPalButton 
                                    amount="12.99" 
                                    onApprove={(details) => handleUpgradePro(details)} 
                                    onError={(err) => setError("PayPal transaction failed. Please try again.")}
                                />
                            </div>
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
};

export default Upgrade;
