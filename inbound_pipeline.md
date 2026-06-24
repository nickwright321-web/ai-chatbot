```mermaid

flowchart LR
    classDef external stroke:#22c55e,stroke-width:2px;

    %% ============================
    %% FRONTEND
    %% ============================
    subgraph FE [Frontend]
        direction LR
        UI[React/Vite Chat Client]
    end

    %% ============================
    %% WEBSOCKET API
    %% ============================
    subgraph WS [WebSocket API]
        direction LR
        APIGW([API Gateway WebSocket])
        CONNECT([$connect])
        SEND([$sendMessage])
    end

    %% ============================
    %% CONNECTION HANDLER
    %% ============================
    subgraph CH [Connection Handler]
        direction LR
        ConnHandler[Lambda: Connection Handler]
        ConnTable[(DynamoDB: Connections)]
    end

    %% ============================
    %% CHAT PROCESSOR
    %% ============================
    subgraph CP [Chat Processor]
        direction LR
        ChatProcessor[Lambda: Chat Processor]
        ChatTable[(DynamoDB: Chat History)]
        AIEngine[Bedrock: AI Model]
        InboundQueue[SQS: Inbound Messages Queue]
    end

    %% ============================
    %% INTENT ROUTER
    %% ============================
    subgraph IR [Intent Router]
        direction LR
        IntentRouter[Lambda: Intent Router]
        SessionState[(DynamoDB: Session State)]
        CCQueue[SQS: Inbound CC Forward Queue]
    end

    %% ============================
    %% CONTACT CENTRE
    %% ============================
    subgraph CC [Contact Centre]
        direction LR
        CCForwarder[Lambda: Inbound CC Forwarder]
        CCSystem[External: Contact Centre]:::external
    end

    %% ============================
    %% FLOWS
    %% ============================

    %% Frontend → WebSocket
    UI --> SEND
    SEND --> APIGW

    %% WebSocket → Connection Handler
    APIGW --> CONNECT
    CONNECT --> ConnHandler
    ConnHandler --> ConnTable

    %% WebSocket → Chat Processor
    APIGW --> ChatProcessor

    %% Chat Processor internal flow
    ChatProcessor --> ChatTable
    ChatProcessor --> AIEngine
    AIEngine --> ChatProcessor
    ChatProcessor --> InboundQueue

    %% Intent Router flow
    InboundQueue --> IntentRouter
    IntentRouter --> SessionState
    IntentRouter --> CCQueue

    %% CC Forwarding
    CCQueue --> CCForwarder
    CCForwarder -.-> CCSystem
