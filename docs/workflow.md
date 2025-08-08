# Workflow

flowchart TD
    %% Document Upload & Processing
    A[📂 User uploads document\n(PDF, DOCX, HTML, ZIP)] --> B[🔍 Extract text from document\n- Handle multiple file types\n- Keep original formatting where possible]
    B --> C[🧹 Parse and clean text\n- Remove unwanted line breaks\n- Normalize punctuation and spacing]

    %% Style & Rule Checks
    C --> D[🛠 Apply style guide rules\n- Grammar and spelling\n- Passive voice detection\n- Readability scoring]

    %% Embedding & Storage
    C --> E[🧠 Generate vector embeddings\n(using NLP models like Sentence-Transformers)]
    E --> F[💾 Store embeddings + metadata\nin ChromaDB for future searches]

    %% Query Process
    G[💬 User asks a question or requests suggestions] --> H[🔎 Retrieve relevant text chunks\n(Vector Search from ChromaDB)]
    H --> I[📦 Combine retrieved chunks\n+ matching style guide rules\ninto one context package]

    %% AI Suggestion
    I --> J[🤖 Send context to AI model\n- LLM analyzes\n- Generates suggestions and rewrites]

    %% Output & Feedback
    D --> K[📋 Feedback report\n- Lists all detected issues\n- Gives direct corrections]
    J --> K
    K --> L[🌐 Display in web interface\n- Highlight issues in text\n- Show AI suggestions alongside original content]
