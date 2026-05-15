import { createContext, useContext, useEffect, useReducer, useRef, type ReactNode } from 'react';
import type { AppState, Lang, TripData, Message, Tweaks, StepIndex } from '../types';
import { i18n } from './i18n';

const LS_LANG = 'tp.lang';
const LS_TWEAKS = 'tp.tweaks';
const LS_MESSAGES = 'tp.messages';
const LS_LAST_TRIP = 'tp.lastTrip';
const LS_VERSION = 1;

function loadLS<T>(key: string, fallback: T): T {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    return JSON.parse(raw) as T;
  } catch { return fallback; }
}

function saveLS(key: string, value: unknown) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* ignore */ }
}

const defaultTweaks: Tweaks = { theme: 'warm', density: 'regular', showModels: true };

function initState(): AppState {
  const lang = (loadLS<string>(LS_LANG, 'zh') as Lang) || 'zh';
  const tweaks: Tweaks = { ...defaultTweaks, ...loadLS<Partial<Tweaks>>(LS_TWEAKS, {}) };
  // Chat history and last trip are intentionally NOT restored on load —
  // each page load starts a fresh session.
  return {
    lang,
    messages: [],
    generating: false,
    step: 0,
    currentTrip: null,
    hasResult: false,
    tweaks,
    lastQuery: '',
    parsedDestination: '',
    parsedDays: 0,
  };
}

type Action =
  | { type: 'SET_LANG'; lang: Lang }
  | { type: 'SET_TWEAKS'; tweaks: Partial<Tweaks> }
  | { type: 'ADD_MESSAGE'; message: Message }
  | { type: 'SET_GENERATING'; generating: boolean }
  | { type: 'SET_STEP'; step: StepIndex }
  | { type: 'SET_TRIP'; trip: TripData }
  | { type: 'SET_LAST_QUERY'; query: string }
  | { type: 'SET_PARSED'; destination: string; days: number }
  | { type: 'CLEAR_RESULT' }
  | { type: 'CLEAR_HISTORY' };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_LANG':
      return { ...state, lang: action.lang };
    case 'SET_TWEAKS':
      return { ...state, tweaks: { ...state.tweaks, ...action.tweaks } };
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.message] };
    case 'SET_GENERATING':
      return { ...state, generating: action.generating };
    case 'SET_STEP':
      return { ...state, step: action.step };
    case 'SET_TRIP':
      return { ...state, currentTrip: action.trip, hasResult: true };
    case 'SET_LAST_QUERY':
      return { ...state, lastQuery: action.query };
    case 'SET_PARSED':
      return { ...state, parsedDestination: action.destination, parsedDays: action.days };
    case 'CLEAR_RESULT':
      return { ...state, hasResult: false };
    case 'CLEAR_HISTORY':
      return { ...state, messages: [], currentTrip: null, hasResult: false, lastQuery: '', parsedDestination: '', parsedDays: 0 };
    default:
      return state;
  }
}

interface AppContextValue {
  state: AppState;
  dispatch: React.Dispatch<Action>;
  t: (key: keyof typeof i18n.zh) => string;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, undefined, initState);

  // Sync theme/density to html
  useEffect(() => {
    document.documentElement.dataset.theme = state.tweaks.theme === 'warm' ? '' : state.tweaks.theme;
    document.documentElement.dataset.density = state.tweaks.density;
  }, [state.tweaks.theme, state.tweaks.density]);

  // Persist preferences only (lang + tweaks); messages and trip reset each session
  const prev = useRef(state);
  useEffect(() => {
    if (prev.current.lang !== state.lang) saveLS(LS_LANG, state.lang);
    if (prev.current.tweaks !== state.tweaks) saveLS(LS_TWEAKS, state.tweaks);
    prev.current = state;
  }, [state]);

  const dict = i18n[state.lang];
  const t = (key: keyof typeof i18n.zh): string => {
    const val = (dict as Record<string, unknown>)[key];
    if (typeof val === 'string') return val;
    return key;
  };

  return <AppContext.Provider value={{ state, dispatch, t }}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useApp must be used within AppProvider');
  return ctx;
}

export { LS_VERSION };
