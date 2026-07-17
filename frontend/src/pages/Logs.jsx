import React from 'react';

export default function Logs() {
  const logs = [
    { time: '2026-07-10 16:45:12', level: 'INFO', component: 'FastAPI Main', msg: 'Uvicorn server running on http://127.0.0.1:8000' },
    { time: '2026-07-10 16:56:02', level: 'INFO', component: 'SQL ORM', msg: 'Resilient connection pooling initialized with pool_pre_ping=True' },
    { time: '2026-07-10 16:56:03', level: 'INFO', component: 'DB Health', msg: 'Database handshake validation successful (Suppabase Postgres Connected)' },
    { time: '2026-07-10 17:00:25', level: 'INFO', component: 'ML Pipeline', msg: 'Calling mock data generation: 3762 daily transactional rows created.' },
    { time: '2026-07-10 17:00:27', level: 'INFO', component: 'SQL Ingestion', msg: 'Starting multi-stage database commit for products and transactions...' },
    { time: '2026-07-10 17:00:29', level: 'INFO', component: 'SQL Ingestion', msg: 'Ingestion completed successfully. 5 product profiles registered, 3762 transactions records logged.' },
  ];

  return (
    <div className="bg-brand-card p-6 rounded-2xl border border-brand-border space-y-4">
      <h3 className="text-xl font-bold text-white">System Ingestion & Pipeline Logs</h3>
      <p className="text-slate-400 text-sm">Review pipeline trigger traces and server telemetry logs.</p>
      
      <div className="bg-brand-dark p-4 rounded-xl border border-brand-border font-mono text-xs overflow-x-auto space-y-2.5 max-h-[350px]">
        {logs.map((log, idx) => (
          <div key={idx} className="flex gap-4 text-slate-300 hover:bg-slate-800/20 py-1 px-1.5 rounded transition-all">
            <span className="text-slate-500">{log.time}</span>
            <span className="text-brand-accent font-bold">[{log.level}]</span>
            <span className="text-indigo-400 font-semibold">{log.component}:</span>
            <span className="text-slate-200">{log.msg}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
