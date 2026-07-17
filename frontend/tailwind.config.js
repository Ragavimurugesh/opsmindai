/**
 * tailwind.config.js
 *
 * NOTE: Tailwind CSS v4 is CSS-first. Brand tokens are now defined via @theme
 * in src/index.css. This file is kept for tooling compatibility (e.g., editor
 * IntelliSense) but is NOT the primary configuration source.
 *
 * Content paths are still respected by v4 for class scanning.
 */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          dark:      '#0B0F19',
          card:      '#161B26',
          accent:    '#3B82F6',
          success:   '#10B981',
          warning:   '#F59E0B',
          danger:    '#EF4444',
          border:    '#242F41',
          textMuted: '#94A3B8',
        },
      },
    },
  },
  plugins: [],
};
