import React, { useState, useEffect } from 'react';
import { 
  Key, 
  Database, 
  ShieldAlert, 
  Copy, 
  Check, 
  Eye, 
  EyeOff, 
  User, 
  Server, 
  ExternalLink,
  Lock,
  Cpu
} from 'lucide-react';
import { fetchConfig } from '../services/api';

export default function Profile() {
  const [config, setConfig] = useState(null);
  const [loading, setLoading] = useState(true);
  const [copiedKey, setCopiedKey] = useState(null);
  const [showAnon, setShowAnon] = useState(false);
  const [showService, setShowService] = useState(false);
  const [showDbUrl, setShowDbUrl] = useState(false);

  // Fallback defaults matching provided Supabase details
  const fallbackConfig = {
    supabase_url: 'https://wvbuqgfghbeyiifpgqxh.supabase.co',
    supabase_anon_key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2YnVxZ2ZnaGJleWlpZnBncXhoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODM2OTI0OTAsImV4cCI6MjA5OTI2ODQ5MH0.cTqashxyzZag1tbix5S8pKevUVgzkwzHPbShEzYDdtE',
    supabase_service_role_key: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind2YnVxZ2ZnaGJleWlpZnBncXhoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MzY5MjQ5MCwiZXhwIjoyMDk5MjY4NDkwfQ.pmGw47tqKf3YZk04CyB42sSWMYnJ7EsI1ysrr3GhROA',
    database_url: 'postgresql://postgres:ragaviragavisupabse@db.wvbuqgfghbeyiifpgqxh.supabase.co:5432/postgres',
    project_ref: 'wvbuqgfghbeyiifpgqxh',
    environment: 'development'
  };

  useEffect(() => {
    const load = async () => {
      try {
        const data = await fetchConfig();
        setConfig(data);
      } catch (err) {
        console.warn('Config fetch failed, using profile fallbacks', err);
        setConfig(fallbackConfig);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const handleCopy = (text, keyName) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(keyName);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  const activeConfig = config || fallbackConfig;

  // Mask database password in view
  const maskedDatabaseUrl = activeConfig.database_url 
    ? activeConfig.database_url.replace(/:([^:@]+)@/, ':•••••••••@') 
    : '';

  return (
    <div className="space-y-6 max-w-5xl pb-10">
      
      {/* ── Profile Hero Header ─────────────────────────────────────────── */}
      <div className="relative overflow-hidden bg-gradient-to-br from-[#1b2336] to-[#121724] border border-[#242F41] rounded-3xl p-6 sm:p-8 shadow-2xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="absolute -top-12 -left-12 w-48 h-48 rounded-full bg-blue-500/10 blur-3xl" />
        <div className="absolute -bottom-12 -right-12 w-48 h-48 rounded-full bg-indigo-500/10 blur-3xl" />

        <div className="flex flex-col sm:flex-row items-center gap-5 relative">
          {/* Avatar frame */}
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-blue-500 to-indigo-500 flex items-center justify-center font-black text-white text-3xl shadow-lg shadow-blue-500/20 border border-blue-400/20">
            RM
          </div>
          <div className="text-center sm:text-left">
            <div className="flex items-center justify-center sm:justify-start gap-2">
              <h2 className="text-2xl font-black text-white tracking-tight">Ragavimurugesh</h2>
              <span className="bg-blue-500/10 border border-blue-500/20 text-blue-400 text-[10px] font-bold tracking-widest px-2.5 py-0.5 rounded-full uppercase">
                Admin
              </span>
            </div>
            <p className="text-slate-400 text-sm mt-1 flex items-center justify-center sm:justify-start gap-1.5">
              <Cpu size={13} className="text-slate-500" />
              MLOps & Cloud Infrastructure Specialist
            </p>
            <p className="text-[11px] text-slate-500 mt-0.5">
              Active Project: <span className="font-mono text-slate-400">{activeConfig.project_ref}</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 relative shrink-0">
          <div className="bg-[#161B26] border border-[#242F41] rounded-2xl px-5 py-3 text-center min-w-[130px]">
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Environment</p>
            <p className="text-sm font-bold text-blue-400 capitalize mt-0.5">{activeConfig.environment}</p>
          </div>
          <div className="bg-[#161B26] border border-[#242F41] rounded-2xl px-5 py-3 text-center min-w-[130px]">
            <p className="text-[9px] font-bold text-slate-500 uppercase tracking-widest">Platform</p>
            <p className="text-sm font-bold text-emerald-400 mt-0.5">Supabase v2</p>
          </div>
        </div>
      </div>

      {/* ── Credentials Grid ───────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Supabase Connection Credentials */}
        <div className="lg:col-span-2 bg-[#161B26]/70 backdrop-blur border border-[#242F41] rounded-3xl p-6 space-y-5 shadow-xl">
          <div className="flex items-center gap-2 pb-2 border-b border-[#242F41]">
            <Database className="text-blue-400" size={18} />
            <h3 className="text-base font-bold text-white">Supabase Connection Credentials</h3>
          </div>

          {/* Supabase URL */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                <Server size={12} className="text-slate-500" />
                Supabase URL (Endpoint)
              </span>
              <button 
                onClick={() => handleCopy(activeConfig.supabase_url, 'url')}
                className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded transition-all"
              >
                {copiedKey === 'url' ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                {copiedKey === 'url' ? 'Copied' : 'Copy'}
              </button>
            </div>
            <div className="w-full bg-[#0a0e17] border border-[#242F41] rounded-xl px-4 py-2.5 text-xs font-mono text-slate-300 flex items-center justify-between overflow-hidden">
              <span className="truncate mr-3">{activeConfig.supabase_url}</span>
              <a 
                href={activeConfig.supabase_url} 
                target="_blank" 
                rel="noreferrer" 
                className="text-slate-500 hover:text-blue-400 shrink-0"
              >
                <ExternalLink size={13} />
              </a>
            </div>
          </div>

          {/* Anon Public API Key */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                <Key size={12} className="text-slate-500" />
                Anon Public Key (anon public)
              </span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setShowAnon(!showAnon)}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded"
                >
                  {showAnon ? <EyeOff size={10} /> : <Eye size={10} />}
                  {showAnon ? 'Hide' : 'Reveal'}
                </button>
                <button 
                  onClick={() => handleCopy(activeConfig.supabase_anon_key, 'anon')}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded transition-all"
                >
                  {copiedKey === 'anon' ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                  {copiedKey === 'anon' ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="w-full bg-[#0a0e17] border border-[#242F41] rounded-xl px-4 py-2.5 text-xs font-mono text-slate-300 flex items-center justify-between">
              <span className="truncate mr-3">
                {showAnon ? activeConfig.supabase_anon_key : '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'}
              </span>
            </div>
          </div>

          {/* Service Role API Key */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                <Lock size={12} className="text-amber-500" />
                Service Role API Key (service_role)
              </span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setShowService(!showService)}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded"
                >
                  {showService ? <EyeOff size={10} /> : <Eye size={10} />}
                  {showService ? 'Reveal' : 'Reveal'}
                </button>
                <button 
                  onClick={() => handleCopy(activeConfig.supabase_service_role_key, 'service')}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded transition-all"
                >
                  {copiedKey === 'service' ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                  {copiedKey === 'service' ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="w-full bg-[#0a0e17] border border-[#242F41] rounded-xl px-4 py-2.5 text-xs font-mono text-slate-300 flex items-center justify-between">
              <span className="truncate mr-3 text-slate-400">
                {showService ? activeConfig.supabase_service_role_key : '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'}
              </span>
            </div>
          </div>

          {/* Postgres Database URL */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-slate-400 flex items-center gap-1.5">
                <Database size={12} className="text-slate-500" />
                Direct PostgreSQL Database URL
              </span>
              <div className="flex items-center gap-2">
                <button 
                  onClick={() => setShowDbUrl(!showDbUrl)}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded"
                >
                  {showDbUrl ? <EyeOff size={10} /> : <Eye size={10} />}
                  {showDbUrl ? 'Hide' : 'Reveal'}
                </button>
                <button 
                  onClick={() => handleCopy(activeConfig.database_url, 'dburl')}
                  className="text-[10px] text-slate-400 hover:text-white flex items-center gap-1 bg-[#242F41]/50 px-2 py-0.5 rounded transition-all"
                >
                  {copiedKey === 'dburl' ? <Check size={10} className="text-emerald-400" /> : <Copy size={10} />}
                  {copiedKey === 'dburl' ? 'Copied' : 'Copy'}
                </button>
              </div>
            </div>
            <div className="w-full bg-[#0a0e17] border border-[#242F41] rounded-xl px-4 py-2.5 text-xs font-mono text-slate-300 flex items-center justify-between">
              <span className="truncate mr-3">
                {showDbUrl ? activeConfig.database_url : maskedDatabaseUrl}
              </span>
            </div>
          </div>

        </div>

        {/* Security & Configuration Recommendations */}
        <div className="bg-[#161B26]/70 backdrop-blur border border-[#242F41] rounded-3xl p-6 space-y-5 shadow-xl">
          <div className="flex items-center gap-2 pb-2 border-b border-[#242F41]">
            <ShieldAlert className="text-amber-500" size={18} />
            <h3 className="text-base font-bold text-white">MLOps Recommendations</h3>
          </div>

          <div className="space-y-4 text-xs text-slate-300">
            
            <div className="bg-[#ea580c]/5 border border-orange-500/10 p-3 rounded-2xl space-y-1">
              <h4 className="font-bold text-amber-400 flex items-center gap-1">
                ⚠️ service_role Key Exposure
              </h4>
              <p className="text-slate-400 leading-relaxed">
                The <span className="font-mono text-slate-300">service_role</span> key bypasses all Row Level Security (RLS) policies. **Never** expose this key in your client React code or client side API calls. Keep it strictly loaded inside your backend environment.
              </p>
            </div>

            <div className="bg-blue-500/5 border border-blue-500/10 p-3 rounded-2xl space-y-1">
              <h4 className="font-bold text-blue-400">
                ⚡ Connection Pooler vs Direct
              </h4>
              <p className="text-slate-400 leading-relaxed">
                Use the Supabase Session Pooler (port <span className="font-mono text-slate-300">5432</span>) rather than direct URL connection to handle highly parallel query traffic from ML processes without hitting pool exhaustion.
              </p>
            </div>

            <div className="bg-emerald-500/5 border border-emerald-500/10 p-3 rounded-2xl space-y-1">
              <h4 className="font-bold text-emerald-400">
                🔒 Row Level Security (RLS)
              </h4>
              <p className="text-slate-400 leading-relaxed">
                Implement RLS policies on the <span className="font-mono text-slate-300">products</span> and <span className="font-mono text-slate-300">inventory</span> tables to restrict anonymous user writes, allowing updates only via vetted database triggers.
              </p>
            </div>

            <div className="bg-slate-500/5 border border-slate-500/10 p-3 rounded-2xl space-y-1">
              <h4 className="font-bold text-slate-400">
                🔄 Key Rotation Recommendation
              </h4>
              <p className="text-slate-400 leading-relaxed">
                Since project keys are exposed in this administrative profile view, it is recommended to rotate anon keys every 90 days inside the Supabase API credentials dashboard.
              </p>
            </div>

          </div>
        </div>

      </div>

    </div>
  );
}
