import React from 'react';

export default function Models() {
  const models = [
    { name: 'Prophet Time-Series', type: 'Additive Regression', engine: 'Facebook Prophet', accuracy: '95.5%', status: 'Active', description: 'Excellent at extracting monthly and seasonal spikes for products like Fresh Produce and Seafood.' },
    { name: 'XGBoost Regressor', type: 'Gradient Boosting', engine: 'XGBoost Python', accuracy: '94.3%', status: 'Active', description: 'Trained on historical lag structures (lag_7, lag_30, rolling_mean_7) for highly non-linear dairy and bakery demand patterns.' },
  ];

  return (
    <div className="space-y-6">
      <div className="bg-brand-card p-6 rounded-2xl border border-brand-border">
        <h3 className="text-xl font-bold text-white mb-2">Machine Learning Engine Configurations</h3>
        <p className="text-slate-400 text-sm">Review algorithms running predictive analysis pipelines for warehouse tracking.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {models.map((model) => (
          <div key={model.name} className="bg-brand-card p-6 rounded-2xl border border-brand-border flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <span className="bg-blue-500/10 text-brand-accent text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded">
                {model.engine}
              </span>
              <h4 className="text-lg font-bold text-white mt-2">{model.name}</h4>
              <p className="text-slate-400 text-xs leading-relaxed">{model.description}</p>
            </div>
            
            <div className="border-t border-brand-border pt-4 flex justify-between items-center text-xs">
              <span className="text-slate-500">Validation R2 Accuracy:</span>
              <span className="font-semibold text-brand-success">{model.accuracy}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
