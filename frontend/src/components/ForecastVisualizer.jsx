import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

// Custom Tooltip component styled with premium dark theme aesthetics
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const isForecast = data.forecast !== null && data.forecast !== undefined;
    const model = data.model_engine || 'N/A';
    
    return (
      <div className="bg-slate-900 border border-brand-border p-4 rounded-xl shadow-2xl backdrop-blur-md">
        <p className="text-xs font-semibold text-slate-400 mb-2">{label}</p>
        
        {data.historical !== null && data.historical !== undefined && (
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2.5 h-2.5 rounded-full bg-brand-success" />
            <span className="text-sm font-medium text-slate-300">
              Historical Sales: <strong className="text-white">{data.historical} units</strong>
            </span>
          </div>
        )}
        
        {isForecast && (
          <>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2.5 h-2.5 rounded-full bg-brand-accent" />
              <span className="text-sm font-medium text-slate-300">
                Predicted Demand: <strong className="text-white">{data.forecast} units</strong>
              </span>
            </div>
            <div className="flex items-center gap-2 mb-1">
              <div className="w-2.5 h-2.5 rounded-full bg-blue-500/20 border border-brand-accent/50" />
              <span className="text-sm font-medium text-slate-300">
                Confidence Bound: <strong className="text-slate-400">[{data.confidence_lower} - {data.confidence_upper}]</strong>
              </span>
            </div>
            <div className="mt-2 pt-2 border-t border-brand-border flex justify-between items-center gap-4 text-[10px]">
              <span className="text-slate-500 font-medium">Model Engine:</span>
              <span className="bg-blue-500/10 text-brand-accent px-2 py-0.5 rounded font-semibold">
                {model}
              </span>
            </div>
          </>
        )}
      </div>
    );
  }
  return null;
};

export default function ForecastVisualizer({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-96 flex items-center justify-center border border-dashed border-brand-border rounded-2xl bg-brand-card/20 text-brand-textMuted text-sm">
        No dataset variables loaded.
      </div>
    );
  }

  return (
    <div className="w-full h-[400px] bg-brand-card p-6 rounded-2xl border border-brand-border shadow-xl">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <CartesianGrid stroke="#242F41" strokeDasharray="3 3" vertical={false} />
          
          <XAxis 
            dataKey="date" 
            stroke="#64748B" 
            fontSize={11} 
            tickLine={false}
            dy={10}
          />
          
          <YAxis 
            stroke="#64748B" 
            fontSize={11} 
            tickLine={false}
            axisLine={false}
            dx={-5}
          />
          
          <Tooltip content={<CustomTooltip />} />
          
          <Legend 
            verticalAlign="top" 
            height={36} 
            iconType="circle"
            iconSize={8}
            wrapperStyle={{ fontSize: '12px', color: '#94A3B8' }}
          />

          {/* 1. Translucent Blue Confidence Range Area */}
          <Area
            name="Confidence Bounds (Lower/Upper)"
            dataKey={(d) => [d.confidence_lower, d.confidence_upper]}
            stroke="none"
            fill="#3B82F6"
            fillOpacity={0.12}
            connectNulls
          />

          {/* 2. Solid Green Historical Sales Curve */}
          <Line
            name="Historical Sales"
            type="monotone"
            dataKey="historical"
            stroke="#10B981"
            strokeWidth={2.5}
            dot={false}
            activeDot={{ r: 6, stroke: '#10B981', strokeWidth: 2, fill: '#0B0F19' }}
            connectNulls
          />

          {/* 3. Dashed Blue Machine Learning Forecast Curve */}
          <Line
            name="ML Predicted Demand"
            type="monotone"
            dataKey="forecast"
            stroke="#3B82F6"
            strokeWidth={2.5}
            strokeDasharray="6 4"
            dot={false}
            activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2, fill: '#0B0F19' }}
            connectNulls
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
