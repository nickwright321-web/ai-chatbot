import type { ReceivedMessage } from "../types/Messages";

const CHAT_WSOCK_URL =
  "wss://r6uuq83dfk.execute-api.eu-west-2.amazonaws.com/prod?token=abc123";

// const CHAT_WSOCK_URL =
//   "wss://gyubbrgk3b.execute-api.eu-west-2.amazonaws.com/prod?token=abc123";


export interface WebSocketHandlers {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: ReceivedMessage) => void;
  onError?: (error: Event) => void;
}

// 🔥 Singleton state
let ws: WebSocket | null = null;
let handlers: WebSocketHandlers | null = null;

export function createWebSocket(newHandlers: WebSocketHandlers): WebSocket {
  handlers = newHandlers;

  // If socket already exists, just reuse it
  if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
    return ws;
  }

  ws = new WebSocket(CHAT_WSOCK_URL);

  ws.onopen = () => handlers?.onOpen?.();
  ws.onclose = () => handlers?.onClose?.();
  ws.onerror = (err) => handlers?.onError?.(err);

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data: ReceivedMessage = JSON.parse(event.data);
      handlers?.onMessage?.(data);
    } catch {
      handlers?.onMessage?.(event.data as any);
    }
  };

  return ws;
}