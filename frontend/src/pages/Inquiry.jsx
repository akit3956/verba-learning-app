import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, Send, ArrowLeft, CheckCircle } from 'lucide-react';
import API_BASE_URL from '../api_config';

const Inquiry = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  });
  const [status, setStatus] = useState('idle'); // idle, loading, success, error
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setStatus('loading');
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/inquiry`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        setStatus('success');
      } else {
        const data = await response.json();
        throw new Error(data.detail || '送信に失敗しました');
      }
    } catch (err) {
      setStatus('error');
      setError(err.message);
    }
  };

  if (status === 'success') {
    return (
      <div className="min-h-screen bg-[#0f172a] text-slate-200 flex flex-col items-center justify-center p-6 text-center">
        <CheckCircle size={64} className="text-emerald-400 mb-6 animate-bounce" />
        <h1 className="text-4xl font-bold text-white mb-4">Thank You!</h1>
        <p className="text-xl text-slate-400 max-w-md mb-10">
          お問い合わせを受け付けました。運営チームが確認次第、返信させていただきます。
        </p>
        <Link 
          to="/" 
          className="px-8 py-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition-all flex items-center gap-2"
        >
          <ArrowLeft size={20} /> Back to Home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 p-6 flex flex-col items-center">
      <div className="max-w-2xl w-full pt-16">
        <Link to="/" className="inline-flex items-center gap-2 text-slate-400 hover:text-white mb-12 group transition-colors">
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          Back to Home
        </Link>

        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 bg-indigo-500/20 rounded-2xl flex items-center justify-center">
            <Mail className="text-indigo-400" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-white">Contact Us</h1>
            <p className="text-slate-400">ご質問・ご要望など、お気軽にお問い合わせください。</p>
          </div>
        </div>

        <form onSubmit={handleSubmit} className="glass p-8 rounded-[2.5rem] border border-white/10 shadow-2xl space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-400 ml-1">Name</label>
              <input
                required
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                placeholder="Your Name"
                className="w-full px-5 py-4 bg-slate-800/50 border border-white/10 rounded-2xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all text-white"
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-400 ml-1">Email</label>
              <input
                required
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your@email.com"
                className="w-full px-5 py-4 bg-slate-800/50 border border-white/10 rounded-2xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all text-white"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-400 ml-1">Subject</label>
            <input
              required
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              placeholder="What is this about?"
              className="w-full px-5 py-4 bg-slate-800/50 border border-white/10 rounded-2xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all text-white"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-400 ml-1">Message</label>
            <textarea
              required
              name="message"
              value={formData.message}
              onChange={handleChange}
              placeholder="How can we help you?"
              rows="5"
              className="w-full px-5 py-4 bg-slate-800/50 border border-white/10 rounded-2xl focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 outline-none transition-all text-white resize-none"
            ></textarea>
          </div>

          {error && <div className="p-4 bg-red-500/10 border border-red-500/20 text-red-400 rounded-xl text-sm font-medium">{error}</div>}

          <button
            type="submit"
            disabled={status === 'loading'}
            className="w-full py-4 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-600/50 text-white font-bold rounded-2xl transition-all flex items-center justify-center gap-3 shadow-lg shadow-indigo-600/20"
          >
            {status === 'loading' ? 'Sending...' : 'Send Message'}
            <Send size={18} />
          </button>
        </form>
      </div>

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

export default Inquiry;
