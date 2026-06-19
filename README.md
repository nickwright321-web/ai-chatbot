# ALChatBot
This is a live chat client demostrating the use of:
- React/Vite front end
- A backend that handles live chat conversations between an AI bot and a customer, 
with a handoff to a live agent if needed.
- The backend has a plugin architecture, allowing the use of different AI models
and cc systems such as Genesys, Zoom and Infinity

```mermaid
flowchart LR
    subgraph FE[Frontend]
        UI[React/Vite Chat Client]
    end

    subgraph API[API Layer]
        APIGW[API Gateway<br/>(REST + WebSocket)]
    end

    subgraph BE[Backend - AWS Lambda]
        Router[Lambda: Message Router]
        AIHandler[Lambda: AI Plugin<br/>(Bedrock)]
        GenesysHandler[Lambda: Genesys Plugin]
        ZoomHandler[Lambda: Zoom Plugin]
        InfinityHandler[Lambda: Infinity Plugin]
        SNOWHandler[Lambda: ServiceNow Plugin]
    end

    subgraph DB[Data Layer]
        ConnTable[(DynamoDB<br/>Connections Table)]
        ChatTable[(DynamoDB<br/>Chat History)]
    end

    subgraph EXT[External Systems]
        Bedrock[Amazon Bedrock<br/>AI Model]
        Genesys[Genesys Cloud<br/>Live Agent]
        Zoom[Zoom Contact Center]
        Infinity[Infinity CC]
        SNOW[ServiceNow<br/>Ticketing]
    end

    %% Frontend to API
    UI --> APIGW

    %% API to backend router
    APIGW --> Router

    %% Router to plugins
    Router --> AIHandler
    Router --> GenesysHandler
    Router --> ZoomHandler
    Router --> InfinityHandler
    Router --> SNOWHandler

    %% AI plugin to Bedrock
    AIHandler --> Bedrock

    %% CC plugins to external CC systems
    GenesysHandler --> Genesys
    ZoomHandler --> Zoom
    InfinityHandler --> Infinity

    %% ServiceNow plugin
    SNOWHandler --> SNOW

    %% Database interactions
    Router --> ConnTable
    Router --> ChatTable
    AIHandler --> ChatTable
