interface Props {
  name: string;
  name_cn: string;
  tags: string[];
  color?: string;
}

export default function AttrThumb({ name, name_cn, tags, color }: Props) {
  const tagsLower = (tags || []).join(' ').toLowerCase();
  const all = `${name} ${name_cn} ${tagsLower}`.toLowerCase();
  let kind = 'generic';
  if (/temple|寺|神社|shrine|jingū|jingu|inari/.test(all)) kind = 'shrine';
  else if (/bamboo|竹|岚山|arashiyama/.test(all)) kind = 'bamboo';
  else if (/market|市场|tsukiji|食|food|海鲜/.test(all)) kind = 'market';
  else if (/tower|塔|铁塔|eiffel|地标/.test(all)) kind = 'tower';
  else if (/museum|博物馆|louvre|orsay|met|moma|vatican|艺术|art|印象派/.test(all)) kind = 'museum';
  else if (/park|公园|central|中央/.test(all)) kind = 'park';
  else if (/colosseo|斗兽场|古迹|pantheon|万神殿|forum|罗马/.test(all)) kind = 'ruins';
  else if (/fountain|喷泉|trevi/.test(all)) kind = 'fountain';
  else if (/shopping|购物|soho|store|times/.test(all)) kind = 'city';
  else if (/teamlab|沉浸|数字|planets/.test(all)) kind = 'immersive';
  else if (/montmartre|蒙马特|gion|祇园|古街/.test(all)) kind = 'alley';

  const stroke = color || '#1F3F33';

  switch (kind) {
    case 'shrine': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#F1E0CB"/>
        <path d="M0 70 Q20 50 36 60 T84 56 L84 84 L0 84 Z" fill="#5A7959" opacity=".55"/>
        <rect x="22" y="32" width="40" height="4" fill={stroke}/>
        <rect x="20" y="28" width="44" height="4" fill={stroke}/>
        <rect x="28" y="36" width="3" height="34" fill={stroke}/>
        <rect x="53" y="36" width="3" height="34" fill={stroke}/>
        <rect x="40" y="40" width="4" height="30" fill={stroke}/>
      </svg>
    );
    case 'bamboo': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#E5EEDB"/>
        {[8,22,36,50,64,76].map((x, i) => (
          <g key={i}>
            <rect x={x} y="-4" width="4" height="92" fill="#6B8A4F" opacity={0.6 + (i%2)*0.2}/>
            <rect x={x-1} y={16+i*8} width="6" height="2" fill="#3F5A28"/>
            <rect x={x-1} y={40+i*4} width="6" height="2" fill="#3F5A28"/>
          </g>
        ))}
      </svg>
    );
    case 'market': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#F0E4C1"/>
        <path d="M0 30 L84 30 L78 38 L6 38 Z" fill={stroke}/>
        <path d="M0 38 L84 38 L78 46 L6 46 Z" fill="#9C2722"/>
        <path d="M30 58 Q42 50 60 58 Q42 66 30 58 Z" fill="#D88A6A"/>
        <circle cx="56" cy="58" r="1.5" fill="#1B201C"/>
        <path d="M28 58 L22 54 L22 62 Z" fill="#D88A6A"/>
      </svg>
    );
    case 'tower': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#E8DCC0"/>
        <path d="M42 8 L48 70 L60 80 L24 80 L36 70 Z" fill={stroke}/>
        <rect x="38" y="30" width="8" height="3" fill="#E8DCC0"/>
        <rect x="36" y="45" width="12" height="3" fill="#E8DCC0"/>
        <rect x="32" y="60" width="20" height="3" fill="#E8DCC0"/>
        <circle cx="42" cy="10" r="2" fill="#C9A664"/>
      </svg>
    );
    case 'museum': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#E6DDC8"/>
        <path d="M14 36 L42 18 L70 36 Z" fill={stroke}/>
        <rect x="14" y="36" width="56" height="4" fill={stroke}/>
        <rect x="18" y="40" width="6" height="28" fill={stroke}/>
        <rect x="30" y="40" width="6" height="28" fill={stroke}/>
        <rect x="42" y="40" width="6" height="28" fill={stroke}/>
        <rect x="54" y="40" width="6" height="28" fill={stroke}/>
        <rect x="10" y="68" width="64" height="6" fill={stroke}/>
      </svg>
    );
    case 'park': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#CEE0C2"/>
        <path d="M0 56 Q20 44 42 50 T84 50 L84 84 L0 84 Z" fill="#7AA068" opacity=".75"/>
        <circle cx="22" cy="46" r="14" fill={stroke} opacity=".85"/>
        <rect x="20" y="46" width="4" height="14" fill="#3F2E1F"/>
        <circle cx="58" cy="38" r="18" fill={stroke}/>
        <rect x="56" y="40" width="4" height="20" fill="#3F2E1F"/>
      </svg>
    );
    case 'ruins': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#EFE0C8"/>
        <path d="M0 70 L84 70 L84 84 L0 84 Z" fill="#B89668"/>
        {[10,24,38,52,66].map(x => (
          <g key={x}><rect x={x} y={28+(x%3)*4} width="6" height="42" fill={stroke}/></g>
        ))}
        <path d="M6 28 L80 32 L80 36 L6 36 Z" fill={stroke}/>
        <ellipse cx="42" cy="28" rx="40" ry="4" fill={stroke}/>
      </svg>
    );
    case 'fountain': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#DBE5E8"/>
        <path d="M10 70 Q42 60 74 70 L74 84 L10 84 Z" fill="#5C7E8C"/>
        <circle cx="42" cy="42" r="14" fill={stroke}/>
        <path d="M30 30 Q42 14 54 30 Q50 40 42 38 Q34 40 30 30 Z" fill="#9BB6BD"/>
        <circle cx="42" cy="42" r="4" fill="#E8DCC0"/>
      </svg>
    );
    case 'city': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <defs>
          <linearGradient id="cit" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#1B2A4E"/>
            <stop offset="1" stopColor={stroke}/>
          </linearGradient>
        </defs>
        <rect width="84" height="84" fill="url(#cit)"/>
        <rect x="6" y="36" width="10" height="48" fill="#0F1A30"/>
        <rect x="18" y="22" width="10" height="62" fill="#0F1A30"/>
        <rect x="30" y="40" width="8" height="44" fill="#0F1A30"/>
        <rect x="40" y="14" width="12" height="70" fill="#0F1A30"/>
        <rect x="54" y="30" width="10" height="54" fill="#0F1A30"/>
        <rect x="66" y="44" width="14" height="40" fill="#0F1A30"/>
        {[[10,46],[22,30],[44,22],[58,38],[70,52]].map(([x,y],i) => (
          <rect key={i} x={x} y={y} width="2" height="2" fill="#FFD66B"/>
        ))}
      </svg>
    );
    case 'immersive': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <defs>
          <radialGradient id="tl2" cx=".5" cy=".5">
            <stop offset="0" stopColor="#B987A8"/>
            <stop offset="1" stopColor="#3A2740"/>
          </radialGradient>
        </defs>
        <rect width="84" height="84" fill="url(#tl2)"/>
        {[8,18,28,38,48,58,68].map(y => (
          <ellipse key={y} cx="42" cy={y+10} rx={32-Math.abs(40-y)*0.3} ry="2" fill="#fff" opacity={0.08+y/200}/>
        ))}
        <circle cx="42" cy="42" r="10" fill={stroke} opacity=".75"/>
        <circle cx="22" cy="58" r="5" fill={stroke} opacity=".5"/>
      </svg>
    );
    case 'alley': return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill="#E8D9C2"/>
        <path d="M0 84 L30 30 L54 30 L84 84 Z" fill={stroke} opacity=".85"/>
        <rect x="32" y="40" width="6" height="10" fill="#F4E8D2"/>
        <rect x="46" y="42" width="6" height="10" fill="#F4E8D2"/>
        <rect x="38" y="60" width="8" height="18" fill="#F4E8D2"/>
        <circle cx="6" cy="20" r="3" fill="#F4E8D2" opacity=".7"/>
        <circle cx="78" cy="14" r="2" fill="#F4E8D2" opacity=".5"/>
      </svg>
    );
    default: return (
      <svg viewBox="0 0 84 84" style={{ width: '100%', height: '100%', display: 'block' }}>
        <rect width="84" height="84" fill={stroke} opacity=".15"/>
        <rect x="14" y="14" width="56" height="56" rx="6" fill={stroke} opacity=".7"/>
        <text x="42" y="50" textAnchor="middle" fontFamily="Instrument Serif" fontStyle="italic" fontSize="28" fill="#FBF7EE">
          {(name_cn||name||'·').slice(0,1)}
        </text>
      </svg>
    );
  }
}
