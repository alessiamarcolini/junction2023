import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import { SocketContext } from "./hooks/useSocket.ts";
import { io } from "socket.io-client";

const socket = io("http://localhost:5000");

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <SocketContext.Provider value={{ io: socket }}>
      <App />
    </SocketContext.Provider>
  </React.StrictMode>,
);
