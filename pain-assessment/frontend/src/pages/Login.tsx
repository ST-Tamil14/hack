import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Lock, Mail, ShieldCheck, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { AuthUser } from '../types';

interface LoginProps {
  onLoginSuccess: (user: AuthUser) => void;
}

export const Login: React.FC<LoginProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('dr.jenkins@hospital.org');
  const [password, setPassword] = useState('clinicalpassword123');
  const [selectedRole, setSelectedRole] = useState<'clinician' | 'researcher' | 'admin'>('clinician');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await api.login(email, password);
      res.user.role = selectedRole;
      onLoginSuccess(res.user);
      navigate('/');
    } catch {
      setError('Invalid clinical credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl border border-slate-200 shadow-xl overflow-hidden">
        {/* Header Banner */}
        <div className="bg-gradient-to-r from-cyan-600 via-teal-600 to-emerald-600 p-6 text-white text-center relative">
          <div className="w-14 h-14 bg-white/10 backdrop-blur-md rounded-2xl mx-auto flex items-center justify-center mb-3 shadow-inner">
            <Activity className="w-8 h-8 text-white stroke-[2.5]" />
          </div>
          <h1 className="text-xl font-extrabold tracking-tight">PainSense AI System</h1>
          <p className="text-xs text-teal-100 mt-1">Clinical Multimodal Pain & Physiological Portal</p>
        </div>

        {/* Form Container */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-rose-50 border border-rose-200 text-rose-700 text-xs p-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Role Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1.5">Select Role</label>
            <div className="grid grid-cols-3 gap-2">
              {(['clinician', 'researcher', 'admin'] as const).map((role) => (
                <button
                  type="button"
                  key={role}
                  onClick={() => setSelectedRole(role)}
                  className={`py-2 text-xs font-semibold rounded-lg capitalize border transition-all ${
                    selectedRole === role
                      ? 'bg-cyan-50 border-cyan-600 text-cyan-700 shadow-2xs'
                      : 'bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100'
                  }`}
                >
                  {role}
                </button>
              ))}
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Clinical Email</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="name@hospital.org"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-xs border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-cyan-600 hover:bg-cyan-700 text-white text-xs font-bold py-3 rounded-xl transition-all flex items-center justify-center space-x-2 shadow-sm cursor-pointer"
          >
            <span>{loading ? 'Authenticating...' : 'Sign In to Clinical Dashboard'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>

          {/* Safety Footnote */}
          <div className="pt-2 flex items-center justify-center space-x-1.5 text-[11px] text-slate-400 text-center">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span>HIPAA-Compliant Encrypted Portal Access</span>
          </div>
        </form>
      </div>
    </div>
  );
};
