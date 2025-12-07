export interface Source {
  title: string;
  url: string;
}

export interface Message {
  id: string;
  role: 'user' | 'model';
  content: string;
  sources?: Source[];
  isThinking?: boolean;
  relatedQuestions?: string[];
  searchSteps?: string[]; 
  query?: string; // The user query that triggered this model message
  attachments?: {
    mimeType: string;
    data: string; // base64
    file: File; // Keep the original file object for previews
  }[];
}

export interface SearchState {
  query: string;
  messages: Message[];
  isLoading: boolean;
}

export type Plan = 'pro' | 'max';

// Types for new widgets
export type SeriesData = {
  name: string;
  data: number[];
  color?: string;
};

export type ChartConfig = {
  type: "line" | "bar" | "arc";
  title: string;
  labels: string[];
  series: SeriesData[];
  yAxisLabel?: string;
  valuePrefix?: string;
  valueSuffix?: string;
};

export type TableConfig = {
  headers: string[];
  rows: (string | number)[][];
  title?: string;
};
