import React, { useState, useEffect } from 'react';
import { fetchInventory } from '../services/api';

export default function Ledger() {
  const [inventory, setInventory] = useState([]);

  useEffect(() => {
    const load = async () => {
      const data = await fetchInventory();
      setInventory(data);
    };
    load();
  }, []);

  return (
    <div className="bg-brand-card p-6 rounded-2xl border border-brand-border space-y-4">
      <h3 className="text-xl font-bold text-white">Inventory Ledger</h3>
      <p className="text-slate-400 text-sm">Real-time breakdown of warehouse item capacities and reorder parameters.</p>
      
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse text-sm">
          <thead>
            <tr className="border-b border-brand-border text-slate-400 font-semibold">
              <th className="py-3 px-4">SKU</th>
              <th className="py-3 px-4">Product Name</th>
              <th className="py-3 px-4">Category</th>
              <th className="py-3 px-4">Stock on Hand</th>
              <th className="py-3 px-4">Allocated</th>
              <th className="py-3 px-4">Reserved</th>
              <th className="py-3 px-4">Unit Price</th>
              <th className="py-3 px-4">Reorder Level</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-brand-border/40">
            {inventory.map((item) => (
              <tr key={item.sku} className="text-slate-300 hover:bg-brand-border/20 transition-colors">
                <td className="py-3.5 px-4 font-mono font-semibold text-brand-accent">{item.sku}</td>
                <td className="py-3.5 px-4 font-medium text-white">{item.name}</td>
                <td className="py-3.5 px-4">{item.category}</td>
                <td className="py-3.5 px-4 font-bold text-slate-100">{item.stock_on_hand}</td>
                <td className="py-3.5 px-4">{item.allocated_stock}</td>
                <td className="py-3.5 px-4">{item.reserved_stock}</td>
                <td className="py-3.5 px-4 font-semibold">${item.unit_price}</td>
                <td className="py-3.5 px-4 text-brand-warning">{item.reorder_level}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
