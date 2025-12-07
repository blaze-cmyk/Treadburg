export interface Source {
    title: string;
    url: string;
}

export interface Message {
    id: string;
    role: 'user' | 'model' | 'assistant'; // handle both model/assistant
    content: string;
    isThinking?: boolean;
    searchSteps?: string[];
    sources?: Source[];
    attachments?: any[]; // Keep your existing attachment type
}

export interface SearchState {
    query: string;
    messages: Message[];
    isLoading: boolean;
}
