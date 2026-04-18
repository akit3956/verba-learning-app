import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sparkles, Check, Star, Zap, Shield, AlertCircle, MessageCircle } from 'lucide-react';
import API_BASE_URL from "../api_config";

const PayPalButton = ({ amount, planId, onApprove, onError }) => {
    const containerRef = React.useRef(null);
  
    React.useEffect(() => {
      if (containerRef.current) {
          containerRef.current.innerHTML = '';
      }

      if (window.paypal && containerRef.current) {
        window.paypal.Buttons({
          style: {
            shape: 'pill',
            color: 'gold',
            layout: 'vertical',
            label: planId ? 'subscribe' : 'pay',
          },
          // Conditional logic: if planId is provided, create a subscription. Otherwise, create an order.
          createSubscription: planId ? (data, actions) => {
            return actions.subscription.create({
              plan_id: planId
            });
          } : undefined,
          createOrder: !planId ? (data, actions) => {
            return actions.order.create({
              purchase_units: [{
                amount: { value: amount }
              }]
            });
          } : undefined,
          onApprove: (data, actions) => {
            if (planId) {
              // For subscriptions, onApprove returns data.subscriptionID
              console.log("Subscription ID:", data.subscriptionID);
              onApprove({ id: data.subscriptionID, isSubscription: true });
            } else {
              // For orders, we still need to capture
              return actions.order.capture().then((details) => {
                onApprove({ ...details, isSubscription: false });
              });
            }
          },
          onError: (err) => {
             console.error("PayPal Error:", err);
             if (onError) onError(err);
          }
        }).render(containerRef.current);
      }
    }, [amount, planId, onApprove, onError]);
  
    return <div ref={containerRef} className="w-full mt-4" style={{ minHeight: '150px' }} />;
  };

const Upgrade = () => {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [agreedToTerms, setAgreedToTerms] = useState(false);
    const [successMessage, setSuccessMessage] = useState(null);

    const handleUpgradePlan = async (details, planType) => {
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
                    paypal_subscription_id: details.isSubscription ? details.id : null,
                    plan_type: planType
                })
            });

            if (!res.ok) throw new Error(`Failed to upgrade to ${planType} on the server.`);
            
            setSuccessMessage(`Successfully upgraded to ${planType.toUpperCase()}! Welcome to the club.`);
            
            setTimeout(() => {
                navigate('/');
                window.location.reload();
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
            <div className="max-w-6xl mx-auto">
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
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        
                        {/* Token Purchase Section */}
                        <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-200 flex flex-col hover:shadow-md transition-shadow">
                            <div className="mb-6">
                                <div className="text-emerald-600 bg-emerald-50 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Token Pack</div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-3xl font-bold text-slate-800">$5.00</span>
                                </div>
                                <p className="text-slate-500 text-sm mt-1">One-time purchase</p>
                            </div>
                            
                            <ul className="space-y-3 mb-6 flex-1 text-sm">
                                <li className="flex gap-2 text-slate-600">
                                    <Star size={14} className="text-emerald-600 shrink-0 mt-0.5" />
                                    500 VRB Tokens
                                </li>
                                <li className="flex gap-2 text-slate-600">
                                    <Check size={14} className="text-slate-600 shrink-0 mt-0.5" />
                                    Access to all AI Quizzes
                                </li>
                            </ul>
                            
                            <div className="mb-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input 
                                        type="checkbox" 
                                        className="rounded border-slate-300"
                                        checked={agreedToTerms}
                                        onChange={() => setAgreedToTerms(!agreedToTerms)}
                                    />
                                    <span className="text-[10px] text-slate-500">Agree to Terms</span>
                                </label>
                            </div>

                            {agreedToTerms ? (
                                <PayPalButton 
                                    amount="5.00" 
                                    onApprove={(details) => handlePurchaseVRB(details, 5.00, 500)} 
                                    onError={(err) => setError("PayPal transaction failed.")}
                                />
                            ) : (
                                <button className="w-full py-3 bg-slate-50 border border-slate-200 rounded-xl text-slate-400 font-bold text-sm cursor-not-allowed">
                                    PayPal
                                </button>
                            )}
                        </div>

                        {/* Pro Upgrade Section */}
                        <div className="bg-gradient-to-b from-indigo-50 to-white p-6 rounded-3xl shadow-md border border-indigo-100 flex flex-col hover:shadow-lg transition-shadow">
                            <div className="mb-6">
                                <div className="text-indigo-600 bg-indigo-100 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Verba Pro</div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-3xl font-bold text-indigo-900">$12.99</span>
                                    <span className="text-slate-500 font-medium text-xs">/ Mo</span>
                                </div>
                                <p className="text-indigo-600/80 text-xs mt-1 font-medium">Monthly Subscription</p>
                            </div>
                            
                            <ul className="space-y-3 mb-6 flex-1 text-sm">
                                <li className="flex gap-2 text-slate-700">
                                    <Zap size={14} className="text-indigo-600 shrink-0 mt-0.5" />
                                    Unlimited AI Quizzes
                                </li>
                                <li className="flex gap-2 text-slate-700">
                                    <Check size={14} className="text-indigo-600 shrink-0 mt-0.5" />
                                    24/7 AI Tutor Chat
                                </li>
                            </ul>
                            
                            <div className="mb-4">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input 
                                        type="checkbox" 
                                        className="rounded border-indigo-300"
                                        checked={agreedToTerms}
                                        onChange={() => setAgreedToTerms(!agreedToTerms)}
                                    />
                                    <span className="text-[10px] text-slate-500">Agree to Terms</span>
                                </label>
                            </div>
                            {agreedToTerms ? (
                                <PayPalButton 
                                    amount="12.99" 
                                    planId="P-8SY96959DW884681XNHRQM2I" 
                                    onApprove={(details) => handleUpgradePlan(details, 'pro')} 
                                    onError={(err) => setError("PayPal transaction failed.")}
                                />
                            ) : (
                                <button className="w-full py-3 bg-indigo-50 border border-indigo-100 rounded-xl text-indigo-300 font-bold text-sm cursor-not-allowed">
                                    PayPal
                                </button>
                            )}
                        </div>

                        {/* Founder's Club Section */}
                        <div className="bg-[#0f172a] p-6 rounded-3xl shadow-xl border border-indigo-500/30 flex flex-col hover:shadow-indigo-500/20 transition-all relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-20 h-20 bg-indigo-500/10 rounded-full blur-xl"></div>
                            <div className="mb-6 relative z-10">
                                <div className="text-indigo-400 bg-indigo-500/10 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Founder's Pass</div>
                                <div className="flex items-baseline gap-1">
                                    <span className="text-3xl font-bold text-white">$109.99</span>
                                    <span className="text-slate-500 font-medium text-xs">/ Yr</span>
                                </div>
                                <p className="text-indigo-400/80 text-xs mt-1 font-medium">Yearly Membership</p>
                            </div>
                            
                            <ul className="space-y-3 mb-6 flex-1 text-sm relative z-10">
                                <li className="flex gap-2 text-indigo-100">
                                    <Shield size={14} className="text-indigo-400 shrink-0 mt-0.5" />
                                    1 Year Pro + 10k VRB
                                </li>
                                <li className="flex gap-2 text-indigo-100">
                                    <Star size={14} className="text-indigo-400 shrink-0 mt-0.5" />
                                    VIP Discord Access
                                </li>
                            </ul>
                            
                            <div className="mb-4 relative z-10">
                                <label className="flex items-center gap-2 cursor-pointer">
                                    <input 
                                        type="checkbox" 
                                        className="rounded border-indigo-500/50"
                                        checked={agreedToTerms}
                                        onChange={() => setAgreedToTerms(!agreedToTerms)}
                                    />
                                    <span className="text-[10px] text-indigo-300/60">Agree to Terms</span>
                                </label>
                            </div>
                            {agreedToTerms ? (
                                <PayPalButton 
                                    amount="109.99" 
                                    planId="P-8TN50650638884621NHRQPAI" 
                                    onApprove={(details) => handleUpgradePlan(details, 'founder')} 
                                    onError={(err) => setError("PayPal transaction failed.")}
                                />
                            ) : (
                                <button className="w-full py-3 bg-indigo-500/10 border border-indigo-500/20 rounded-xl text-indigo-400/50 font-bold text-sm cursor-not-allowed">
                                    PayPal
                                </button>
                            )}
                        </div>

                    </div>
                )}
            </div>
        </div>
    );
};

export default Upgrade;
