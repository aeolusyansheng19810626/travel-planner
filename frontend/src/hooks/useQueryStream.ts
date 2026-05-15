import { useEffect } from 'react';
import { useApp } from '../lib/context';
import { buildTripData } from '../lib/adapters';
import type {
  StepIndex,
  SseParsedPayload,
  SseWeatherPayload,
  SseAttractionsPayload,
  SseItineraryPayload,
  SseDonePayload,
  SseFatalPayload,
  WeatherRaw,
  AttractionRaw,
  ItineraryRaw,
} from '../types';

export function useQueryStream() {
  const { dispatch } = useApp();

  useEffect(() => {
    const handler = async (e: Event) => {
      const { query } = (e as CustomEvent<{ query: string }>).detail;
      await runStream(query);
    };

    window.addEventListener('tp:run_query', handler);
    return () => window.removeEventListener('tp:run_query', handler);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const runStream = async (query: string) => {
    dispatch({ type: 'SET_LAST_QUERY', query });
    // accumulated data for adapting at the end
    let language = 'zh';
    let destination = '';
    let days = 3;
    let preferences: string[] = [];
    let weatherRaw: WeatherRaw | null = null;
    let attractionsRaw: AttractionRaw[] | null = null;
    let itineraryRaw: ItineraryRaw | null = null;
    let modelsUsed: Record<string, string> = {};

    try {
      const res = await fetch('/api/query/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!res.ok || !res.body) {
        throw new Error(`HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        const parts = buffer.split('\n\n');
        buffer = parts.pop() ?? '';

        for (const part of parts) {
          const lines = part.split('\n');
          let event = '';
          let dataStr = '';
          for (const line of lines) {
            if (line.startsWith('event:')) event = line.slice(6).trim();
            if (line.startsWith('data:')) dataStr = line.slice(5).trim();
          }
          if (!event || !dataStr) continue;

          try {
            const data = JSON.parse(dataStr);
            handleEvent(event, data);
          } catch { /* skip malformed */ }
        }
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      dispatch({
        type: 'ADD_MESSAGE',
        message: {
          id: Date.now().toString(),
          who: 'bot',
          kind: 'error',
          text: `抱歉，发生错误：${msg}`,
          time: '刚刚',
          stepError: msg,
        },
      });
      dispatch({ type: 'SET_GENERATING', generating: false });
      dispatch({ type: 'SET_STEP', step: 0 as StepIndex });
    }

    function handleEvent(event: string, data: unknown) {
      const d = data as Record<string, unknown>;

      if (event === 'parsed') {
        const p = d as unknown as SseParsedPayload;
        language = p.language || 'zh';
        destination = p.destination || '';
        days = p.days || 3;
        preferences = p.preferences || [];
        dispatch({ type: 'SET_STEP', step: 2 as StepIndex });
        dispatch({ type: 'SET_PARSED', destination, days });
      }

      else if (event === 'weather') {
        const p = d as SseWeatherPayload;
        if (!p.error) {
          weatherRaw = p.weather_info ?? null;
          if (p.model) modelsUsed['weather'] = p.model;
        }
        dispatch({ type: 'SET_STEP', step: 3 as StepIndex });
      }

      else if (event === 'attractions') {
        const p = d as SseAttractionsPayload;
        if (!p.error) {
          attractionsRaw = p.attractions ?? null;
          if (p.model) modelsUsed['attraction'] = p.model;
        }
        dispatch({ type: 'SET_STEP', step: 4 as StepIndex });
      }

      else if (event === 'itinerary') {
        const p = d as SseItineraryPayload;
        if (!p.error) {
          itineraryRaw = p.itinerary ?? null;
          if (p.model) modelsUsed['itinerary'] = p.model;
        }
        dispatch({ type: 'SET_STEP', step: 5 as StepIndex });
      }

      else if (event === 'done') {
        const p = d as SseDonePayload;
        if (p.models_used) modelsUsed = { ...modelsUsed, ...p.models_used };

        const tripData = buildTripData({
          destination,
          language,
          days,
          preferences,
          weatherRaw,
          attractionsRaw,
          itineraryRaw,
        });

        dispatch({ type: 'SET_TRIP', trip: tripData });

        const destLocal = tripData.destination_local || destination;
        const intro = buildIntroText(language, destLocal, days);
        dispatch({
          type: 'ADD_MESSAGE',
          message: {
            id: Date.now().toString(),
            who: 'bot',
            kind: 'result',
            text: intro,
            time: '刚刚',
            tripData,
            modelsUsed,
          },
        });
        dispatch({ type: 'SET_GENERATING', generating: false });
        dispatch({ type: 'SET_STEP', step: 0 as StepIndex });
      }

      else if (event === 'fatal') {
        const p = d as unknown as SseFatalPayload;
        dispatch({
          type: 'ADD_MESSAGE',
          message: {
            id: Date.now().toString(),
            who: 'bot',
            kind: 'error',
            text: p.error || '请求失败，请重试。',
            time: '刚刚',
          },
        });
        dispatch({ type: 'SET_GENERATING', generating: false });
        dispatch({ type: 'SET_STEP', step: 0 as StepIndex });
      }
    }
  };
}

function buildIntroText(lang: string, destLocal: string, days: number): string {
  if (lang === 'en') return `Done! Here's your custom ${days}-day itinerary for ${destLocal}.`;
  if (lang === 'ja') return `完了！${destLocal}の${days}日間旅程をご用意しました。`;
  return `完成！以下是为你定制的${destLocal} ${days} 日行程。`;
}
