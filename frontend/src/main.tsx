import React from "react";
import ReactDOM from "react-dom/client";
import './index.css'
import App from './App.tsx'
import { loadConfig } from "./config/loadConfig.ts";
import type { RuntimeConfig } from "./config/loadConfig.ts";

declare global {
  interface Window {
    RUNTIME_CONFIG: RuntimeConfig;
  }
}

loadConfig().then((config: RuntimeConfig) => {
  window.RUNTIME_CONFIG = config;

  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
});