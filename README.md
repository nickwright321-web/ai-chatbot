# ALChatBot
This is a live chat client demostrating the use of:
- React/Vite front end
- A backend that handles live chat conversations between an AI bot and a customer, 
with a handoff to a live agent if needed.
- The backend has a plugin architecture, allowing the use of different AI models
and cc systems such as Genesys, Zoom and Infinity

```mermaid
flowchart LR

    subgraph FE [Frontend]
        UI[React/Vite Chat Client]
    end

    subgraph API [API Gateway]
        APIGW[API Gateway (REST + WebSocket)]
    end