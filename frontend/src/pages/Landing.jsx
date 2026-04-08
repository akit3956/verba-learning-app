import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, Check, Star, Zap, MessageCircle, ArrowRight, User, Shield } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const PayPalButton = ({ amount, plan, onSuccess }) => {
  const containerRef = React.useRef(null);

  React.useEffect(() => {
    if (window.paypal && containerRef.current) {
      containerRef.current.innerHTML = ''; // Clear previous button
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
            onSuccess(plan);
          });
        }
      }).render(containerRef.current);
    }
  }, [amount, plan, onSuccess]);

  return <div ref={containerRef} className="w-full mt-4" />;
};

const Landing = () => {
  const navigate = useNavigate();

  const handlePaymentSuccess = (plan) => {
    navigate(`/auth?payment=success&plan=${plan}`);
  };

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 overflow-x-hidden">
      {/* Background Orbs */}
      <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[500px] h-[500px] bg-indigo-600/20 blur-[120px] rounded-full"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[500px] h-[500px] bg-blue-600/20 blur-[120px] rounded-full"></div>
      </div>

      {/* Navigation */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <span className="text-white font-bold text-xl">V</span>
          </div>
          <span className="text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">
            Verba
          </span>
        </div>
        <div className="flex items-center gap-6">
          <Link to="/auth" className="text-sm font-medium hover:text-white transition-colors">Log In</Link>
          <Link 
            to="/auth" 
            className="px-5 py-2.5 bg-white text-slate-900 rounded-full text-sm font-bold hover:bg-slate-200 transition-all shadow-lg hover:shadow-white/10"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-20 pb-32 px-6 max-w-7xl mx-auto flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 bg-indigo-500/10 border border-indigo-500/20 rounded-full mb-8">
          <Sparkles size={14} className="text-indigo-400" />
          <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">Next Gen JLPT Learning</span>
        </div>
        
        <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight tracking-tight text-white">
          <span className="text-3xl md:text-4xl block mb-4 text-indigo-400">🇯🇵 Japanese Teacher x Web3 x AI</span>
          Next Gen Language App: <br />
          <span className="bg-gradient-to-r from-indigo-400 via-blue-400 to-emerald-400 bg-clip-text text-transparent italic">
            'Learn to Earn'
          </span>
        </h1>
        
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          The ultimate JLPT prep platform using advanced AI tutors. Start earning VRB tokens today while you learn from professional lesson plans.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center gap-4">
          <Link 
            to="/auth" 
            className="group px-8 py-4 bg-gradient-to-r from-indigo-500 to-blue-600 text-white rounded-2xl font-bold text-lg hover:shadow-[0_0_40px_rgba(79,70,229,0.4)] transition-all flex items-center gap-2"
          >
            Start Learning for Free
            <ArrowRight size={20} className="group-hover:translate-x-1 transition-transform" />
          </Link>
          <div className="flex -space-x-3 items-center">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="w-10 h-10 rounded-full border-2 border-[#0f172a] bg-slate-800 overflow-hidden">
                <img src={`https://i.pravatar.cc/100?u=user${i}`} alt="user" />
              </div>
            ))}
            <span className="ml-4 text-sm text-slate-500 font-medium">+10k learners</span>
          </div>
        </div>

        {/* Aki Avatar Welcome */}
        <div className="mt-20 relative group">
          <div className="absolute inset-0 bg-indigo-500/20 blur-3xl rounded-full scale-150 group-hover:scale-175 transition-transform duration-700"></div>
          <div className="relative glass p-6 rounded-[2rem] border border-white/10 shadow-2xl flex flex-col md:flex-row items-center gap-8 max-w-3xl overflow-hidden">
            <div className="w-32 h-32 md:w-48 md:h-48 rounded-2xl overflow-hidden bg-slate-800 flex-shrink-0 shadow-lg border border-white/5">
              <img 
                src="/assets/aki_avatar.png" 
                alt="Aki" 
                className="w-full h-full object-cover transform hover:scale-105 transition-transform duration-500" 
                onError={(e) => { e.target.src = 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aki'; }}
              />
            </div>
            <div className="text-left">
              <div className="bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded inline-block mb-3">Welcome from Founder</div>
              <h3 className="text-2xl font-bold text-white mb-2 italic">"Hajimemashite! I'm Aki."</h3>
              <p className="text-slate-400 line-clamp-3">
                I built Verba to be the AI teacher I always wanted when I was a professional Japanese instructor. I'm here to help you hit N1 success.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Founder's Story Section */}
      <section className="py-32 px-6 relative">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-sm font-black uppercase tracking-widest text-indigo-500 mb-4">Founder's Story</h2>
            <h3 className="text-4xl font-bold text-white mb-4">Why I Built Verba</h3>
            <p className="text-slate-500 font-medium">From a Former Pro Japanese Teacher</p>
          </div>
          
          <div className="glass p-12 rounded-[3rem] border border-white/10 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-2 h-full bg-gradient-to-b from-indigo-500 to-blue-600"></div>
            <div className="relative z-10">
              <span className="text-6xl font-serif text-indigo-500/20 absolute -top-4 -left-4">"</span>
              <p className="text-2xl md:text-3xl text-white font-medium leading-relaxed mb-12 relative">
                Learning to code was incredibly hard because I didn't have a teacher beside me. That struggle made me realize something: <span className="text-indigo-400">millions of you are trying to learn Japanese right now, struggling alone.</span>
              </p>
              <p className="text-xl text-slate-400 leading-relaxed italic mb-8">
                So, I took my years of professional Japanese lesson plans and built the AI Tutor I wished I had. With Miss Kaplan, you are never studying alone.
              </p>
              <div className="flex items-center gap-4 mt-8 pt-8 border-t border-white/5">
                <div className="w-12 h-12 rounded-full bg-slate-800 border border-white/10 overflow-hidden">
                   <img src="/assets/aki_avatar.png" alt="Aki Signature" className="w-full h-full object-cover" />
                </div>
                <div>
                  <div className="text-white font-bold text-lg">Aki</div>
                  <div className="text-slate-500 text-sm">Founder of Verba</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Tutor Feature (Miss Kaplan) */}
      <section className="py-32 px-6 bg-slate-900/50">
        <div className="max-w-7xl mx-auto grid md:grid-rows-1 md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="w-12 h-12 bg-indigo-500/20 rounded-2xl flex items-center justify-center mb-6">
              <MessageCircle className="text-indigo-400" />
            </div>
            <h2 className="text-4xl font-bold text-white mb-6">Meet Miss Kaplan: Your 24/7 AI Sensei</h2>
            <p className="text-xl text-slate-400 mb-8 leading-relaxed">
              Experience personalized tutoring that adapts to your level. Miss Kaplan uses professional Japanese curriculum and real-time context to guide your journey.
            </p>
            <ul className="space-y-4">
              {[
                "24/7 Individual Guidance",
                "Context-Aware Corrections",
                "Personalized Lesson Plans",
                "Instant Grammatical Explanations"
              ].map(f => (
                <li key={f} className="flex items-center gap-3 text-white font-medium">
                  <div className="w-5 h-5 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Check size={12} className="text-emerald-400" />
                  </div>
                  {f}
                </li>
              ))}
            </ul>
          </div>
          <div className="relative group">
             <div className="absolute inset-0 bg-indigo-500/20 blur-[100px] rounded-full scale-75 group-hover:scale-100 transition-duration-700"></div>
             <div className="relative rounded-[2.5rem] border border-white/10 overflow-hidden shadow-2xl glass p-2 backdrop-blur-3xl aspect-[4/5] md:aspect-auto h-[500px]">
                <img 
                  src="/assets/miss_kaplan.webp" 
                  alt="Miss Kaplan AI Tutor" 
                  className="w-full h-full object-cover rounded-[2rem]"
                  onError={(e) => { e.target.src = 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1000&auto=format&fit=crop'; }}
                />
                <div className="absolute bottom-6 left-6 right-6 glass border-white/10 rounded-2xl p-4 flex items-center gap-4">
                   <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
                   <div className="text-sm font-bold text-white">Miss Kaplan is online & ready to help</div>
                </div>
             </div>
          </div>
        </div>
      </section>

      {/* Pricing Table */}
      <section className="py-32 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-white mb-4">Transparent Pricing for Everyone</h2>
            <p className="text-slate-400">Choose the plan that fits your learning pace.</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Standard Plan */}
            <div className="glass p-8 rounded-[2.5rem] border border-white/10 flex flex-col hover:border-white/20 transition-all">
              <div className="mb-8">
                <div className="text-emerald-400 bg-emerald-400/10 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Standard</div>
                <h4 className="text-2xl font-bold text-white">Free</h4>
                <p className="text-slate-500 text-sm mt-1">Perfect for casual learners</p>
              </div>
              <ul className="space-y-4 mb-20 flex-1">
                <li className="flex gap-3 text-sm text-slate-300">
                  <Check size={18} className="text-emerald-400 shrink-0" />
                  10 High-Quality Quizzes / day
                </li>
                <li className="flex gap-3 text-sm text-slate-300">
                  <Check size={18} className="text-emerald-400 shrink-0" />
                  AI Tutor (Miss Kaplan): 3 questions / day
                </li>
                <li className="flex gap-3 text-sm text-slate-300">
                  <Check size={18} className="text-emerald-400 shrink-0" />
                  Earn basic VRB tokens
                </li>
              </ul>
              <Link to="/auth" className="w-full py-4 text-center bg-white/5 border border-white/10 rounded-2xl text-white font-bold hover:bg-white/10 transition-colors">Start for Free</Link>
            </div>

            {/* Pro Plan */}
            <div className="glass p-8 rounded-[2.5rem] border border-white/10 flex flex-col hover:border-white/20 transition-all relative">
              <div className="mb-8">
                <div className="text-blue-400 bg-blue-400/10 inline-block px-3 py-1 rounded-full text-xs font-bold uppercase mb-4 tracking-tighter">Pro</div>
                <div className="flex items-baseline gap-1">
                  <span className="text-4xl font-bold text-white">$12.99</span>
                  <span className="text-slate-500 font-medium text-sm">/ Month</span>
                </div>
                <p className="text-slate-500 text-sm mt-1">Accelerate your fluency</p>
              </div>
              <ul className="space-y-4 mb-20 flex-1">
                <li className="flex gap-3 text-sm text-slate-300">
                  <Check size={18} className="text-blue-400 shrink-0" />
                  Unlimited Quizzes
                </li>
                <li className="flex gap-3 text-sm text-slate-300">
                  <Check size={18} className="text-blue-400 shrink-0" />
                  Unlimited AI Tutor Chat (24/7)
                </li>
                <li className="flex gap-3 text-sm text-slate-300">
                   <Zap size={18} className="text-yellow-400 shrink-0" />
                  1.5x VRB Token Boost
                </li>
              </ul>
               <PayPalButton 
                 amount="12.99" 
                 plan="pro" 
                 onSuccess={handlePaymentSuccess} 
               />
             </div>

            {/* Founder's Pass */}
            <div className="relative group lg:-translate-y-4">
              <div className="absolute inset-0 bg-indigo-500/10 blur-xl rounded-[2.5rem]"></div>
              <div className="relative bg-gradient-to-br from-indigo-600 to-blue-700 p-[2px] rounded-[2.5rem] shadow-2xl shadow-indigo-500/20">
                <div className="bg-[#0f172a] rounded-[2.4rem] p-8 h-full flex flex-col">
                  <div className="absolute top-6 right-6 flex flex-col items-end gap-2">
                     <span className="bg-indigo-500 text-white text-[10px] font-black uppercase tracking-widest px-3 py-1 rounded-full animate-pulse shadow-lg shadow-indigo-500/30">Best Value</span>
                     <span className="bg-red-500/20 text-red-400 text-[9px] font-bold uppercase tracking-tight px-2 py-0.5 rounded border border-red-500/30">Spots filling up fast! ⚡</span>
                  </div>
                  <div className="mb-8">
                    <div className="flex items-center gap-2 mb-4">
                       <img src="/assets/vrb_coin.png" alt="VRB Coin" className="w-8 h-8 drop-shadow-lg" />
                       <span className="text-indigo-400 text-xs font-black uppercase tracking-tighter">Founder's Pass</span>
                    </div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-extrabold text-white">$109.99</span>
                      <span className="text-slate-500 font-medium text-sm">/ Year</span>
                    </div>
                    <p className="text-indigo-400/80 text-sm mt-1 font-semibold uppercase tracking-tighter">Become a legacy backer</p>
                  </div>
                  <ul className="space-y-4 mb-20 flex-1">
                    <li className="flex gap-3 text-sm text-indigo-100">
                      <Shield size={18} className="text-indigo-400 shrink-0" />
                      1 Year of Full Pro Access
                    </li>
                    <li className="flex gap-3 text-sm text-indigo-100">
                      <Star size={18} className="text-indigo-400 shrink-0 fill-indigo-400/20" />
                      10,000 VRB Instant Airdrop!
                    </li>
                    <li className="flex gap-3 text-sm text-indigo-100">
                      <User size={18} className="text-indigo-400 shrink-0" />
                      Founder's Club Discord VIP
                    </li>
                  </ul>
                   <PayPalButton 
                     amount="109.99" 
                     plan="founder" 
                     onSuccess={handlePaymentSuccess} 
                   />
                 </div>
               </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 px-6 border-t border-white/5 bg-slate-900/50">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2 grayscale brightness-200 opacity-50">
             <div className="w-8 h-8 bg-slate-400 rounded-lg flex items-center justify-center">
                <span className="text-slate-900 font-bold text-sm">V</span>
             </div>
             <span className="text-xl font-bold">Verba</span>
          </div>
          <div className="flex gap-8 text-slate-500 text-sm font-medium">
             <a href="#" className="hover:text-white transition-colors">Twitter</a>
             <a href="#" className="hover:text-white transition-colors">Discord</a>
             <Link to="/inquiry" className="hover:text-white transition-colors">Contact</Link>
             <a href="#" className="hover:text-white transition-colors">Privacy</a>
          </div>
          <p className="text-slate-600 text-xs tracking-widest">© 2026 VERBA TECHNOLOGIES. ALL RIGHTS RESERVED.</p>
        </div>
      </footer>

      {/* CSS Utility for Glassmorphism */}
      <style dangerouslySetInnerHTML={{ __html: `
        .glass {
          background: rgba(255, 255, 255, 0.03);
          backdrop-filter: blur(12px);
          -webkit-backdrop-filter: blur(12px);
        }
      `}} />
    </div>
  );
};

export default Landing;
