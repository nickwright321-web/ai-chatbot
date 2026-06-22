import type { ReceivedMessage } from "../types/Messages";

export interface WebSocketHandlers {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: ReceivedMessage) => void;
  onError?: (error: Event) => void;
}

let ws: WebSocket | null = null;
let handlers: WebSocketHandlers | null = null;

export function createWebSocket(newHandlers: WebSocketHandlers): WebSocket {
  const CHAT_WSOCK_URL = window.RUNTIME_CONFIG.websocketUrl;
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