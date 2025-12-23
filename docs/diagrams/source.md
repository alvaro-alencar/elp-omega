# ELP-Ω Diagram Source Code

## 1. Arquitetura Geral (architecture.png)
```mermaid
graph TD
    A[Client Request] --> B{Zeckendorf Mask?}
    B -- Invalid --> C[SHADOW Reality]
    B -- Valid --> D{Timestamp Fresh?}
    D -- Stale --> E[MIRROR Reality]
    D -- Fresh --> F{HMAC Seal Match?}
    F -- No --> G{Fail Count > Max?}
    G -- Yes --> C
    G -- No --> E
    F -- Yes --> H{Nonce Used?}
    H -- Yes --> C
    H -- No --> I[PRIME Reality]