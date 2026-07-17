# OpsMind AI - Phase 4 Verification Checklist & UI Validation

This document outlines the detailed verification tests to execute after implementing the frontend views and Recharts dashboard components.

---

## 💻 1. Component Compiling & Launching
Verify that the React + Vite frontend starts correctly:
```bash
cd frontend
npm run dev
```
- [ ] **Launch Verification**: The development server launches without errors, exposing a local URL (e.g. `http://localhost:5173`).
- [ ] **Console Inspection**: Open the browser Developer Tools Console (`F12`) and confirm there are zero warnings, syntax exceptions, or import errors.

---

## 📡 2. Responsive Layout & API Connection Checking
Navigate to `http://localhost:5173` in your browser:
- [ ] **Collapsible Sidebar**: Clicking the toggle button collapses and expands the sidebar smoothly with animations.
- [ ] **Navigation Switches**: Clicking sidebar tabs (`Dashboard`, `Inventory Ledger`, `Forecast Models`, `System Logs`) switches routes and displays corresponding headers and components instantly without reloading the page.
- [ ] **Live Health Indicator**: The top header displays the "Supabase Database" badge:
  - If the FastAPI backend is running and connected, it displays a green `CONNECTED` tag.
  - If the backend is stopped or disconnected, it fails gracefully to a red `OFFLINE` tag without interrupting client state or crashing the UI.

---

## 📊 3. Dashboard KPI & Recharts Graph Verification
On the **Dashboard** view:
- [ ] **KPI scorecards**: 4 scorecard cards are rendered at the top, displaying `SKUs Monitored` (5), `Out of Stock` (0), `Reorder Indicators` (2), and `Model Accuracy` (94.8%).
- [ ] **Line/Area Chart Composite**: The Recharts composed chart renders correctly:
  - Historical sales are mapped with a solid green curve.
  - Forecast predictions are mapped with a dashed blue curve.
  - Confidence intervals are visualized as a translucent blue shaded area around the forecast predictions.
- [ ] **Cursor Tooltip Interaction**: Hovering cursor points over the chart area reveals the custom detailed tooltip showing:
  - Date
  - Exact quantities (historical or forecast depending on data type)
  - Confidence range bounds (e.g. `[72 - 88]`)
  - Predictive model engine name (e.g. `Prophet` or `XGBoost`)

---

## 🎛️ 4. Interactive State Update Controls
Verify that state changes trigger database/data updates successfully:
- [ ] **Product SKU Selector**: Change the SKU dropdown from `SKU-001` to `SKU-002` or others:
  - Confirm the chart recalculates data and transitions lines.
  - Confirm the KPI card for `Model Accuracy` updates to the respective SKU accuracy (e.g. `96.2%` for `SKU-002`).
  - Confirm the right-hand product profile card updates its specifications (Name, Unit Price, Reorder Level, and Availability).
- [ ] **Time Horizon Span**: Click different Day Horizon buttons (`7 Days`, `30 Days`, `90 Days`):
  - Confirm the x-axis timeline scales to show the selected quantity of future days.
  - Confirm the loading spinner overlay appears briefly during re-fetching and disappears once plotting is complete.
- [ ] **Raw Data Ingestion Button**: Click the `Run Raw Data Ingestion` button:
  - Confirm the button changes to `Running Ingestion Pipeline...` and disables.
  - Upon completion, confirm the green success banner appears summarizing loaded metadata.
