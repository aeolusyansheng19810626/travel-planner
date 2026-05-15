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
  // Japan
  tokyo: '東京', kyoto: '京都', osaka: '大阪', hiroshima: '広島', nara: '奈良',
  sapporo: '札幌', yokohama: '横浜', nagoya: '名古屋', kobe: '神戸',
  fukuoka: '福岡', sendai: '仙台', kanazawa: '金沢', nagasaki: '長崎',
  okinawa: '沖縄', naha: '那覇', nikko: '日光', hakone: '箱根',
  kamakura: '鎌倉', matsumoto: '松本', beppu: '別府',
  // France
  paris: 'Paris', lyon: 'Lyon', nice: 'Nice', marseille: 'Marseille',
  // USA
  'new york': 'New York', nyc: 'New York', 'new york city': 'New York',
  'los angeles': 'Los Angeles', la: 'Los Angeles',
  chicago: 'Chicago', 'san francisco': 'San Francisco', seattle: 'Seattle',
  // Europe
  london: 'London', rome: 'Roma', milan: 'Milano', florence: 'Firenze',
  venice: 'Venezia', barcelona: 'Barcelona', madrid: 'Madrid',
  amsterdam: 'Amsterdam', vienna: 'Wien', prague: 'Praha',
  lisbon: 'Lisboa', zurich: 'Zürich',
  // China
  beijing: '北京', shanghai: '上海', guangzhou: '广州', chengdu: '成都',
  'hong kong': '香港', taipei: '台北', xian: '西安', hangzhou: '杭州',
  nanjing: '南京', wuhan: '武汉', shenzhen: '深圳', qingdao: '青岛',
  // Asia
  seoul: '서울', busan: '부산',
  singapore: 'Singapore', bangkok: 'Bangkok', 'kuala lumpur': 'KL',
  dubai: 'دبي', istanbul: 'İstanbul',
};
const ACCENT_COLORS: Record<string, string> = {
  // Japan
  tokyo: '#B85530', kyoto: '#8B3D1F', osaka: '#B85530',
  sapporo: '#2B5BA8', yokohama: '#2C5645', nagoya: '#8B3D1F',
  fukuoka: '#9B4225', naha: '#2B7A6A', okinawa: '#2B7A6A',
  // France
  paris: '#A8456F', lyon: '#A8456F',
  // USA
  'new york': '#1B4F8E', nyc: '#1B4F8E',
  'los angeles': '#B85530', chicago: '#1B4F8E',
  // Europe
  rome: '#9B4225', milan: '#9B4225', florence: '#9B4225',
  barcelona: '#A8456F', madrid: '#A8456F',
  london: '#2C5645', amsterdam: '#2B5BA8',
  // China
  beijing: '#8B3D1F', shanghai: '#B85530',
  // Asia
  seoul: '#2C5645', dubai: '#C9A664',
};
const COUNTRY_NAMES: Record<string, string> = {
  // Japan
  tokyo: 'Japan', kyoto: 'Japan', osaka: 'Japan', sapporo: 'Japan',
  yokohama: 'Japan', nagoya: 'Japan', kobe: 'Japan', fukuoka: 'Japan',
  sendai: 'Japan', kanazawa: 'Japan', naha: 'Japan', okinawa: 'Japan',
  hiroshima: 'Japan', nara: 'Japan', hakone: 'Japan', kamakura: 'Japan',
  // France
  paris: 'France', lyon: 'France', nice: 'France', marseille: 'France',
  // USA
  'new york': 'United States', nyc: 'United States',
  'los angeles': 'United States', chicago: 'United States',
  'san francisco': 'United States', seattle: 'United States',
  // Europe
  rome: 'Italy', milan: 'Italy', florence: 'Italy', venice: 'Italy',
  london: 'United Kingdom',
  barcelona: 'Spain', madrid: 'Spain',
  amsterdam: 'Netherlands', vienna: 'Austria', prague: 'Czech Republic',
  lisbon: 'Portugal', zurich: 'Switzerland',
  // China
  beijing: 'China', shanghai: 'China', guangzhou: 'China', chengdu: 'China',
  'hong kong': 'Hong Kong', taipei: 'Taiwan', xian: 'China', hangzhou: 'China',
  // Asia
  seoul: 'South Korea', busan: 'South Korea',
  singapore: 'Singapore', bangkok: 'Thailand',
  dubai: 'UAE', istanbul: 'Turkey',
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

  // fallback: itinerary_text → multi-language day/slot parser
  if (raw.itinerary_text) {
    return parseItineraryText(raw.itinerary_text, days, startDate, lang);
  }

  return [];
}

// Chinese ordinal number words → Arabic
const ZH_NUMS: Record<string, number> = {
  '一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10,
  '十一':11,'十二':12,'十三':13,'十四':14,
};

function zhWordToNum(s: string): number | null {
  // handles "第三天" → 3, "第10天" → 10
  const arabic = s.match(/\d+/);
  if (arabic) return parseInt(arabic[0]);
  for (const [w, n] of Object.entries(ZH_NUMS)) {
    if (s.includes(w)) return n;
  }
  return null;
}

// Named time slots → approximate 24h time strings
const SLOT_TIMES: Record<string, string> = {
  // Chinese
  '上午': '09:00', '早上': '08:30', '早晨': '08:30',
  '午餐': '12:00', '中午': '12:00', '午饭': '12:00',
  '下午': '14:00', '傍晚': '17:00',
  '晚上': '18:30', '晚餐': '18:30', '夜晚': '20:00',
  // Japanese
  '午前': '09:00', '朝': '08:30',
  '昼食': '12:00', '昼': '12:00',
  '午後': '14:00',
  '夜': '18:30', '夕食': '18:30', '夕方': '17:00',
  // English
  'morning': '09:00', 'breakfast': '08:30',
  'lunch': '12:00', 'noon': '12:00', 'midday': '12:00',
  'afternoon': '14:00',
  'evening': '18:30', 'dinner': '18:30', 'night': '20:00',
};

function parseSlotTime(label: string): string {
  // Strip leading bullet/dash/star characters before matching
  const cleaned = label.replace(/^[\s*\-•·]+/, '').trim();
  const lower = cleaned.toLowerCase();
  for (const [key, time] of Object.entries(SLOT_TIMES)) {
    if (lower.startsWith(key.toLowerCase()) || lower === key.toLowerCase()) return time;
  }
  return '';
}

function isDayHeader(line: string): { dayNum: number; title: string } | null {
  // English: "Day 1:", "Day 1 —", "**Day 1**", "### Day 1"
  const enMatch = line.match(/^[#*\s]*[Dd]ay\s*(\d+)[:\s\-—]*(.*)/);
  if (enMatch) return { dayNum: parseInt(enMatch[1]), title: enMatch[2].trim() };

  // Chinese: "第一天：", "第1天：", "第 1 天", "**第二天**"
  // Allow optional spaces around the number (e.g. "第 1 天")
  const zhMatch = line.match(/^[#*\s]*第\s*([一二三四五六七八九十\d]+)\s*天[：:：\s\-—]*(.*)/);
  if (zhMatch) {
    const n = zhWordToNum(zhMatch[1]);
    if (n) return { dayNum: n, title: zhMatch[2].trim() };
  }

  // Japanese: "1日目", "第1日"
  const jaMatch = line.match(/^[#*\s]*(?:第)?(\d+)日目?[：:：\s\-—]*(.*)/);
  if (jaMatch) return { dayNum: parseInt(jaMatch[1]), title: jaMatch[2].trim() };

  return null;
}

function isTimeSlotLine(line: string): { time: string; rest: string } | null {
  // Strip leading bullets "* ", "- ", "• " before any matching
  const stripped = line.replace(/^[\s*\-•·]+/, '');

  // Numeric time: "08:30 — 浅草寺", "08:30 - ..."
  const numeric = stripped.match(/^(\d{1,2}:\d{2})\s*[-–—]\s*(.*)/);
  if (numeric) return { time: numeric[1], rest: numeric[2].trim() };

  // Named slot: "上午：活动", "Lunch: ...", "午前："
  const namedSlot = stripped.match(/^([^\d：:：]{1,8})[：:：]\s*(.*)/);
  if (namedSlot) {
    const t = parseSlotTime(namedSlot[1]);
    if (t) return { time: t, rest: namedSlot[2].trim() };
  }

  // Bold slot: "**上午**：", "**Morning**:"
  const boldSlot = stripped.match(/^\*\*([^*]+)\*\*[：:：\s]\s*(.*)/);
  if (boldSlot) {
    const t = parseSlotTime(boldSlot[1]);
    if (t) return { time: t, rest: boldSlot[2].trim() };
  }

  return null;
}

function parseItineraryText(text: string, days: number, startDate: string, lang: string): ItineraryDay[] {
  const lines = text.split('\n');
  const result: ItineraryDay[] = [];
  let cur: ItineraryDay | null = null;

  for (const rawLine of lines) {
    const line = rawLine.replace(/\*\*/g, '').trim();
    if (!line) continue;

    const dayHeader = isDayHeader(rawLine.trim());
    if (dayHeader) {
      if (cur) result.push(cur);
      const dateStr = offsetDate(startDate, dayHeader.dayNum - 1);
      const { date, day } = formatDate(dateStr, lang);
      cur = {
        day: dayHeader.dayNum,
        date: `${date} ${day}`,
        title: dayHeader.title || `Day ${dayHeader.dayNum}`,
        items: [],
      };
      continue;
    }

    if (!cur) continue;

    const slot = isTimeSlotLine(rawLine.trim());
    if (slot && slot.rest) {
      // Split "place · note" or "place，note"
      const splitMatch = slot.rest.match(/^(.+?)[，,·•]\s*(.+)$/);
      const place = splitMatch ? splitMatch[1].trim() : slot.rest;
      const note = splitMatch ? splitMatch[2].trim() : '';
      cur.items.push({ time: slot.time, icon: guessIcon(place), place, note });
      continue;
    }

    // Plain content lines within a day — treat as items if non-trivial
    if (line.length > 2 && !line.startsWith('#')) {
      const splitMatch = line.match(/^(.+?)[，,·•]\s*(.+)$/);
      const place = splitMatch ? splitMatch[1].trim() : line;
      const note = splitMatch ? splitMatch[2].trim() : '';
      // Only add if not already a title-like line (usually the first line after a day header)
      if (cur.items.length > 0 || cur.title) {
        cur.items.push({ time: '', icon: guessIcon(place), place, note });
      } else {
        cur.title = cur.title || line;
      }
    }
  }

  if (cur) result.push(cur);

  // Fill missing day entries up to `days`
  const found = new Set(result.map((d) => d.day));
  for (let i = 1; i <= days; i++) {
    if (!found.has(i)) {
      const dateStr = offsetDate(startDate, i - 1);
      const { date, day } = formatDate(dateStr, lang);
      result.push({ day: i, date: `${date} ${day}`, title: `Day ${i}`, items: [] });
    }
  }

  return result
    .sort((a, b) => a.day - b.day)
    .slice(0, days)
    .filter((d) => d.items.length > 0);
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
  destinationLocal?: string;
  country?: string;
  language: string;
  days: number;
  preferences: string[];
  weatherRaw: WeatherRaw | null;
  attractionsRaw: AttractionRaw[] | null;
  itineraryRaw: ItineraryRaw | null;
}): TripData {
  const { destination, destinationLocal, country, language, days, preferences, weatherRaw, attractionsRaw, itineraryRaw } = params;
  const key = destination.toLowerCase();
  const today = new Date().toISOString().slice(0, 10);

  // LLM-returned values take priority; static dict is the fallback
  const resolvedLocal = (destinationLocal && destinationLocal !== destination)
    ? destinationLocal
    : (LOCAL_NAMES[key] ?? destination);
  const resolvedCountry = (country && country.length > 0)
    ? country
    : (COUNTRY_NAMES[key] ?? '');

  return {
    destination,
    destination_local: resolvedLocal,
    country: resolvedCountry,
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
