# ALChatBot
This is a live chat client demostrating the use of:
- React/Vite front end
- A backend that handles live chat conversations between an AI bot and a customer, 
with a handoff to a live agent if needed.
- The backend has a plugin architecture, allowing the use of different AI models
and cc systems such as Genesys, Zoom and Infinity

While it is fully deployable, it is intended for demo purposes and is not production ready. In a real situation, must CC platforms have alternative live chat platforms that would be more appropriate.

```mermaid
flowchart LR

    subgraph FE [Frontend]
        UI[React/Vite Chat Client]
    end

    subgraph API [API Gateway]
        APIGW[API Websocket Gateway]
    end

    subgraph BE [Backend - AWS Lambda]
        Processor[Lambda: Chat Processor]
        Router[Lambda: Message Router]
        AIHandler[Lambda: AI Plugin - Bedrock]
        GenesysHandler[Lambda: Genesys Plugin]
        ZoomHandler[Lambda: Zoom Plugin]
        InfinityHandler[Lambda: Infinity Plugin]
        SNOWHandler[Lambda: ServiceNow Plugin]
    end

    subgraph DB [Data Layer]
        ConnTable[(DynamoDB Connections)]
        ChatTable[(DynamoDB Chat History)]
    end

    subgraph EXT [External Systems]
        Bedrock[Amazon Bedrock]
        Genesys[Genesys Cloud]
        Zoom[Zoom Contact Center]
        Infinity[Infinity Contact Center]
        SNOW[ServiceNow]
    end

    UI --> APIGW
    APIGW --> Processor

    Processor -> AIHandler


    AIHandler --> Bedrock
    GenesysHandler --> Genesys
    ZoomHandler --> Zoom
    InfinityHandler --> Infinity
    SNOWHandler --> SNOW

    Router --> ConnTable
    Router --> ChatTable
    AIHandler --> ChatTable
