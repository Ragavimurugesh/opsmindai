import React, { useState } from 'react';

export default function Settings() {
  const [darkMode, setDarkMode] = useState(true);
  const [notifications, setNotifications] = useState(true);

  return (
    <div className="bg-brand-card p-6 rounded-2xl border border-brand-border space-y-6">
      <h3 className="text-xl font-bold text-white mb-2">Application Settings</h3>
      <p className="text-slate-400 text-sm mb-4">
        Customize the look and feel of OpsMind AI. These controls are placeholders for future persistence.
      </p>
      <div className="grid gap-4 max-w-md">
        <label className="flex items-center justify-between">
          <span className="text-slate-200">Dark Mode</span>
          <input
            type="checkbox"
            checked={darkMode}
            onChange={() => setDarkMode(!darkMode)}
            className="toggle-checkbox"
          />
        </label>
        <label className="flex items-center justify-between">
          <span className="text-slate-200">Enable Notifications</span>
          <input
            type="checkbox"
            checked={notifications}
            onChange={() => setNotifications(!notifications)}
            className="toggle-checkbox"
          />
        </label>
        <button
          className="mt-4 px-4 py-2 bg-brand-accent text-white rounded-lg hover:bg-brand-accent/90 transition-colors"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
}
