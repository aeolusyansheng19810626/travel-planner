export type Lang = 'zh' | 'en' | 'ja';
export type Theme = 'warm' | 'forest' | 'ink';
export type Density = 'compact' | 'regular' | 'comfy';
export type StepIndex = 0 | 1 | 2 | 3 | 4 | 5;

export interface WeatherDay {
  date: string;
  day: string;
  cond: string;
  icon: string;
  hi: number;
  lo: number;
}

export interface Attraction {
  name: string;
  name_cn: string;
  name_jp?: string;
  desc: string;
  rating: string;
  tags: string[];
  color?: string;
}

export interface ItineraryItem {
  time: string;
  icon: string;
  place: string;
  note: string;
}

export interface ItineraryDay {
  day: number;
  date: string;
  title: string;
  items: ItineraryItem[];
}

export interface TripData {
  destination: string;
  destination_local: string;
  country: string;
  days: number;
  start_date: string;
  preferences: string[];
  verdict: string;
  accent: string;
  weather: WeatherDay[];
  attractions: Attraction[];
  itinerary: ItineraryDay[];
}

export interface AgentSkill {
  name: string;
  description?: string;
}

export interface AgentInfo {
  name: string;
  description?: string;
  url?: string;
  endpoint?: string;
  skills?: AgentSkill[];
}

export interface AgentsData {
  count: number;
  agents: Record<string, AgentInfo>;
}

export type MessageKind = 'text' | 'thinking' | 'result' | 'error';

export interface Message {
  id: string;
  who: 'user' | 'bot';
  kind: MessageKind;
  text: string;
  time: string;
  tripData?: TripData;
  modelsUsed?: Record<string, string>;
  stepError?: string;
}

export interface Tweaks {
  theme: Theme;
  density: Density;
  showModels: boolean;
}

export interface AppState {
  lang: Lang;
  messages: Message[];
  generating: boolean;
  step: StepIndex;
  currentTrip: TripData | null;
  hasResult: boolean;
  tweaks: Tweaks;
  lastQuery: string;
  parsedDestination: string;
  parsedDays: number;
}

/* SSE event payloads */
export interface SseParsedPayload {
  language: string;
  destination: string;
  days: number;
  preferences: string[];
}
export interface SseWeatherPayload {
  weather_info?: WeatherRaw;
  model?: string;
  error?: string;
  stage?: string;
}
export interface SseAttractionsPayload {
  attractions?: AttractionRaw[];
  model?: string;
  error?: string;
  stage?: string;
}
export interface SseItineraryPayload {
  itinerary?: ItineraryRaw;
  model?: string;
  error?: string;
  stage?: string;
}
export interface SseDonePayload {
  full_result?: Record<string, unknown>;
  models_used?: Record<string, string>;
}
export interface SseFatalPayload { error: string; }

/* Raw API shapes (before adaptation) */
export interface WeatherRaw {
  city?: string;
  country?: string;
  summary?: string;
  forecast?: ForecastDayRaw[];
  [key: string]: unknown;
}
export interface ForecastDayRaw {
  date?: string;
  weather?: string;
  weather_code?: number;
  temperature_max?: number;
  temperature_min?: number;
  [key: string]: unknown;
}
export interface AttractionRaw {
  name?: string;
  name_cn?: string;
  name_jp?: string;
  description?: string;
  content?: string;
  rating?: number | string;
  tags?: string[];
  [key: string]: unknown;
}
export interface ItineraryRaw {
  daily_plans?: DayPlanRaw[];
  itinerary_text?: string;
  model_used?: string;
  [key: string]: unknown;
}
export interface DayPlanRaw {
  day?: number;
  date?: string;
  title?: string;
  weather_note?: string;
  activities?: ActivityRaw[];
  [key: string]: unknown;
}
export interface ActivityRaw {
  time?: string;
  activity?: string;
  description?: string;
  [key: string]: unknown;
}
