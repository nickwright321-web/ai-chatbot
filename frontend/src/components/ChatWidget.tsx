import React, { useState, useEffect, useRef } from "react";
import { createWebSocket } from "../connections/websocket";
import type { DisplayMessage, ReceivedMessage }from "../types/Messages" 

export default function ChatWidget() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);

  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    //runs on mounting and creates a websocket connection to the backend

    const ws = createWebSocket({
      onOpen: () => setConnected(true),
      onClose: () => setConnected(false),
      onMessage: (event:ReceivedMessage) => {
        const agentName = event.agentName ? event.agentName : "Agent";
        const message = event.message ? event.message : "";
        setMessages((prev) => [
          ...prev,
          { from: agentName, text: String(message) }
        ]);
      },
      onError: (err) => {
        console.warn("WebSocket warning:", err);
      }

    });

    wsRef.current = ws;

  ws.onclose = (e) => {
    console.log("CLOSE CODE:", e.code, e.reason);
  };


    return () => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.close();
  }
};
  }, []);

  const sendMessage = () => {
    if (!input.trim() || !wsRef.current) return;

    wsRef.current.send(
      JSON.stringify({ action: "sendMessage", message: input })
    );

    setMessages((prev) => [
      ...prev,
      { from: "user", text: input }
    ]);

    setInput("");
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>AI Chat</div>

      <div style={styles.messages}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={m.from === "user" ? styles.userMsg : styles.aiMsg}
          >
            {m.text}
          </div>
        ))}
      </div>

      <div style={styles.inputRow}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={connected ? "Type a message..." : "Connecting..."}
        />
        <button
          style={styles.button}
          onClick={sendMessage}
          disabled={!connected}
        >
          Send
        </button>
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    width: 320,
    height: 420,
    position: "fixed",
    bottom: 20,
    right: 20,
    background: "#fff",
    borderRadius: 10,
    boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
    display: "flex",
    flexDirection: "column",
    overflow: "hidden",
    fontFamily: "sans-serif"
  },
  header: {
    background: "#0078ff",
    color: "#fff",
    padding: 12,
    fontWeight: "bold",
    textAlign: "center"
  },
  messages: {
    flex: 1,
    padding: 10,
    overflowY: "auto"
  },
  userMsg: {
    background: "#daf1ff",
    padding: 8,
    borderRadius: 6,
    marginBottom: 6,
    alignSelf: "flex-end",
    maxWidth: "80%"
  },
  aiMsg: {
    background: "#eee",
    padding: 8,
    borderRadius: 6,
    marginBottom: 6,
    alignSelf: "flex-start",
    maxWidth: "80%"
  },
  inputRow: {
    display: "flex",
    padding: 10,
    borderTop: "1px solid #ddd"
  },
  input: {
    flex: 1,
    padding: 8,
    borderRadius: 6,
    border: "1px solid #ccc"
  },
  button: {
    marginLeft: 8,
    padding: "8px 12px",
    background: "#0078ff",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer"
  }
};
