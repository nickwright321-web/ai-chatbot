export interface DisplayMessage {
  from: string;
  text: string;
}

export interface ReceivedMessage {
  agentName: "ai";
  message: string;
}
