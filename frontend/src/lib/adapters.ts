import type {
  TripData,
  WeatherDay,
  Attraction,
  ItineraryDay,
  WeatherRaw,
  ForecastDayRaw,
  AttractionRaw,
  ItineraryRaw,
  DayPlanRaw,
} from '../types';

/* Static city metadata */
const LOCAL_NAMES: Record<string, string> = {
  tokyo: '東京', kyoto: '京都', osaka: '大阪', hiroshima: '広島', nara: '奈良',
  paris: 'Paris', lyon: 'Lyon', nice: 'Nice',
  'new york': 'New York', nyc: 'New York', 'new york city': 'New York',
  london: 'London', rome: 'Roma', milan: 'Milano', florence: 'Firenze',
  barcelona: 'Barcelona', madrid: 'Madrid',
  beijing: '北京', shanghai: '上海', guangzhou: '广州', chengdu: '成都',
  'hong kong': '香港', taipei: '台北',
};
const ACCENT_COLORS: Record<string, string> = {
  tokyo: '#B85530', kyoto: '#8B3D1F', osaka: '#B85530',
  paris: '#A8456F', lyon: '#A8456F',
  'new york': '#1B4F8E', nyc: '#1B4F8E',
  rome: '#9B4225', milan: '#9B4225',
  london: '#2C5645',
};
const COUNTRY_NAMES: Record<string, string> = {
  tokyo: 'Japan', kyoto: 'Japan', osaka: 'Japan',
  paris: 'France', lyon: 'France',
  'new york': 'United States', nyc: 'United States',
  rome: 'Italy', milan: 'Italy',
  london: 'United Kingdom',
  beijing: 'China', shanghai: 'China',
};

const WEATHER_ICONS: Record<string, string> = {
  clear: '☀️', sunny: '☀️', fair: '🌤',
  partly: '⛅', cloudy: '☁️', overcast: '🌥',
  rain: '🌧', drizzle: '🌦', shower: '🌦',
  thunder: '⛈', storm: '🌩',
  snow: '❄️', fog: '🌫', mist: '🌫',
  wind: '💨',
};

const DAY_NAMES_ZH = ['日', '一', '二', '三', '四', '五', '六'];
const DAY_NAMES_EN = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const DAY_NAMES_JA = ['日', '月', '火', '水', '木', '金', '土'];

function weatherIcon(cond: string, code?: number): string {
  if (code != null) {
    if (code === 0) return '☀️';
    if (code <= 2) return '⛅';
    if (code <= 3) return '☁️';
    if (code <= 48) return '🌫';
    if (code <= 55) return '🌦';
    if (code <= 67) return '🌧';
    if (code <= 77) return '❄️';
    if (code <= 82) return '🌧';
    if (code <= 86) return '❄️';
    return '⛈';
  }
  const lower = (cond ?? '').toLowerCase();
  for (const [key, icon] of Object.entries(WEATHER_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return '🌤';
}

function formatDate(dateStr: string, lang = 'zh'): { date: string; day: string } {
  try {
    const d = new Date(dateStr);
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    const dow = d.getDay();
    let day: string;
    if (lang === 'en') day = DAY_NAMES_EN[dow];
    else if (lang === 'ja') day = `${DAY_NAMES_JA[dow]}曜`;
    else day = `周${DAY_NAMES_ZH[dow]}`;
    return { date: `${mm}/${dd}`, day };
  } catch {
    return { date: dateStr ?? '', day: '' };
  }
}

function verdictFromWeather(weather: WeatherRaw | null, lang = 'zh'): string {
  if (!weather) {
    if (lang === 'en') return '★ Good to go';
    if (lang === 'ja') return '★ 旅行に最適';
    return '★ 适宜出行';
  }
  const summary = (weather.summary ?? '').toLowerCase();
  const hasBad = /rain|storm|typhoon|thunder|snow|bad|poor|warning|雨|暴|雪|不适/.test(summary);
  if (hasBad) {
    if (lang === 'en') return '⚠ Check forecast';
    if (lang === 'ja') return '⚠ 予報を確認';
    return '⚠ 建议关注天气';
  }
  if (lang === 'en') return '★ Good to go';
  if (lang === 'ja') return '★ 旅行に最適';
  return '★ 适宜出行';
}

export function adaptWeather(raw: WeatherRaw | null, days: number, lang = 'zh'): WeatherDay[] {
  if (!raw) return [];
  const forecast: ForecastDayRaw[] = raw.forecast ?? [];
  return forecast.slice(0, days).map((f) => {
    const { date, day } = formatDate(f.date ?? '', lang);
    return {
      date,
      day,
      cond: f.weather ?? '',
      icon: weatherIcon(f.weather ?? '', f.weather_code),
      hi: Math.round((f.temperature_max ?? 20) * 10) / 10,
      lo: Math.round((f.temperature_min ?? 14) * 10) / 10,
    };
  });
}

export function adaptAttractions(raw: AttractionRaw[] | null): Attraction[] {
  if (!raw || !Array.isArray(raw)) return [];
  return raw.slice(0, 4).map((a, i) => ({
    name: a.name ?? `Attraction ${i + 1}`,
    name_cn: a.name_cn ?? a.name ?? '',
    name_jp: a.name_jp,
    desc: a.description ?? a.content ?? '',
    rating: String(a.rating ?? '4.5'),
    tags: Array.isArray(a.tags) ? a.tags : [],
    color: undefined,
  }));
}

export function adaptItinerary(raw: ItineraryRaw | null, days: number, startDate: string, lang = 'zh'): ItineraryDay[] {
  if (!raw) return [];

  // prefer structured daily_plans
  if (raw.daily_plans && Array.isArray(raw.daily_plans)) {
    return raw.daily_plans.slice(0, days).map((dp: DayPlanRaw, i: number) => {
      const dayNum = dp.day ?? i + 1;
      const dateStr = offsetDate(startDate, i);
      const { date, day } = formatDate(dateStr, lang);
      const items = (dp.activities ?? []).map((act) => ({
        time: act.time ?? `${9 + i * 2}:00`,
        icon: guessIcon(act.activity ?? ''),
        place: act.activity ?? '',
        note: act.description ?? dp.weather_note ?? '',
      }));
      return {
        day: dayNum,
        date: `${date} ${day}`,
        title: dp.title ?? dp.weather_note ?? `Day ${dayNum}`,
        items,
      };
    });
  }

  // fallback: itinerary_text → split by day markers
  if (raw.itinerary_text) {
    const text = raw.itinerary_text;
    const lines = text.split('\n').filter((l) => l.trim());
    const result: ItineraryDay[] = [];
    let cur: ItineraryDay | null = null;
    for (const line of lines) {
      const dayMatch = line.match(/^[#*\s]*[Dd]ay\s*(\d+)[:\s]*(.*)/);
      if (dayMatch) {
        if (cur) result.push(cur);
        const dayNum = parseInt(dayMatch[1]);
        const dateStr = offsetDate(startDate, dayNum - 1);
        const { date, day } = formatDate(dateStr, lang);
        cur = { day: dayNum, date: `${date} ${day}`, title: dayMatch[2]?.trim() || `Day ${dayNum}`, items: [] };
      } else if (cur && line.trim()) {
        const timeMatch = line.match(/^(\d{1,2}:\d{2})\s*[-–]\s*(.+)/);
        if (timeMatch) {
          cur.items.push({ time: timeMatch[1], icon: guessIcon(timeMatch[2]), place: timeMatch[2].trim(), note: '' });
        } else {
          cur.items.push({ time: '', icon: '📍', place: line.trim(), note: '' });
        }
      }
    }
    if (cur) result.push(cur);
    return result.slice(0, days);
  }

  return [];
}

function offsetDate(startDate: string, offsetDays: number): string {
  try {
    const d = new Date(startDate);
    d.setDate(d.getDate() + offsetDays);
    return d.toISOString().slice(0, 10);
  } catch { return startDate; }
}

function guessIcon(text: string): string {
  const t = (text ?? '').toLowerCase();
  if (/temple|shrine|神社|寺|稲荷/.test(t)) return '⛩';
  if (/museum|博物|美术馆/.test(t)) return '🏛';
  if (/park|公园|garden|花园/.test(t)) return '🌳';
  if (/market|市场|tsukiji|築地/.test(t)) return '🐟';
  if (/food|eat|餐|料理|ramen|sushi|pizza|pasta|美食|グルメ/.test(t)) return '🍜';
  if (/coffee|cafe|카페|茶|matcha|抹茶/.test(t)) return '☕';
  if (/tower|塔|eiffel|展望/.test(t)) return '🗼';
  if (/art|gallery|展|artwork/.test(t)) return '🎨';
  if (/shop|buy|购物|ショッピング/.test(t)) return '🛍';
  if (/bar|cocktail|wine|beer|酒|居酒屋/.test(t)) return '🥂';
  if (/beach|海|ocean/.test(t)) return '🌊';
  if (/hotel|check/.test(t)) return '🏨';
  return '📍';
}

export function buildTripData(params: {
  destination: string;
  language: string;
  days: number;
  preferences: string[];
  weatherRaw: WeatherRaw | null;
  attractionsRaw: AttractionRaw[] | null;
  itineraryRaw: ItineraryRaw | null;
}): TripData {
  const { destination, language, days, preferences, weatherRaw, attractionsRaw, itineraryRaw } = params;
  const key = destination.toLowerCase();
  const today = new Date().toISOString().slice(0, 10);

  return {
    destination,
    destination_local: LOCAL_NAMES[key] ?? destination,
    country: COUNTRY_NAMES[key] ?? '',
    days,
    start_date: today,
    preferences,
    verdict: verdictFromWeather(weatherRaw, language),
    accent: ACCENT_COLORS[key] ?? '#B85530',
    weather: adaptWeather(weatherRaw, days, language),
    attractions: adaptAttractions(attractionsRaw),
    itinerary: adaptItinerary(itineraryRaw, days, today, language),
  };
}
