// src/main.jsx
// Owner: Developer 4 (Frontend)
// App bootstrap. Do not add business logic here.

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./styles/theme.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
