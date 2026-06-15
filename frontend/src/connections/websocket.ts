
import type { ReceivedMessage } from "../types/Messages";
const CHAT_WSOCK_URL = "wss://1m1ntm6aoi.execute-api.eu-west-2.amazonaws.com/prod";

export interface WebSocketHandlers {
  onOpen?: () => void;
  onClose?: () => void;
  onMessage?: (message: ReceivedMessage) => void;
  onError?: (error: Event) => void;
}

export function createWebSocket({
  onOpen,
  onClose,
  onMessage,
  onError
}: WebSocketHandlers): WebSocket {
  const ws = new WebSocket(CHAT_WSOCK_URL);

  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onerror = (err) => onError?.(err);

  ws.onmessage = (event: MessageEvent) => {
    try {
      const data: ReceivedMessage = JSON.parse(event.data);
      onMessage?.(data ?? data);
    } catch {
      onMessage?.(event.data);
    }
  };

  return ws;
}
