import { useApp } from '../lib/context';
import type { TripData, WeatherDay, Attraction, ItineraryDay } from '../types';
import AttrThumb from './AttrThumb';

export default function ResultPanel() {
  const { state, t } = useApp();
  const { hasResult, currentTrip, generating, lastQuery } = state;

  return (
    <div style={{
      background: 'var(--bg)',
      overflowY: 'auto',
      position: 'relative',
    }}>
      {(!hasResult || !currentTrip) ? (
        <EmptyDetail generating={generating} t={t} />
      ) : (
        <TripDetail trip={currentTrip} t={t} lastQuery={lastQuery} />
      )}
    </div>
  );
}

type TFunc = (k: keyof typeof import('../lib/i18n').i18n.zh) => string;

function EmptyDetail({ generating, t }: { generating: boolean; t: TFunc }) {
  return (
    <div style={{
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '60px 32px',
      textAlign: 'center',
      color: 'var(--ink-3)',
    }}>
      {generating ? (
        <div style={{ width: '100%', maxWidth: '320px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {[80, 60, 90].map((w, i) => (
            <div key={i} className="shimmer" style={{ height: '16px', width: `${w}%`, margin: '0 auto' }} />
          ))}
        </div>
      ) : (
        <>
          <div style={{
            fontFamily: 'var(--font-display)',
            fontStyle: 'italic',
            fontSize: '96px',
            color: 'var(--rule-2)',
            lineHeight: 1,
            marginBottom: '18px',
          }}>~</div>
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '28px',
            color: 'var(--ink-2)',
            margin: '0 0 12px',
            fontWeight: 400,
          }}>
            {t('empty_title')}
          </h2>
          <p style={{ fontSize: '13px', maxWidth: '320px', lineHeight: 1.5, margin: 0 }}>
            {t('empty_desc')}
          </p>
        </>
      )}
    </div>
  );
}

function TripDetail({ trip, t, lastQuery }: { trip: TripData; t: TFunc; lastQuery: string }) {
  const {
    destination, destination_local, country, days,
    start_date, preferences, verdict, accent,
    weather, attractions, itinerary,
  } = trip;

  const itinStops = itinerary.reduce((sum, d) => sum + d.items.length, 0);
  const itineraryNote = `${days} ${t('stat_days_unit')} · ${itinStops} 站`;
  const attractionsNote = `${attractions.length} 处精选`;

  // Hash-based itinerary number
  const hashNum = String(destination.charCodeAt(0) * 97 % 9999).padStart(4, '0');
  const endDate = offsetDateStr(start_date, days - 1);
  const [smm, sdd] = formatYMD(start_date);
  const [emm, edd] = formatYMD(endDate);
  const dateRange = `${smm}-${sdd} – ${emm}/${edd}`;

  return (
    <div style={{ paddingBottom: '40px' }}>
      {/* Hero */}
      <div style={{
        background: 'var(--forest)',
        color: 'var(--paper)',
        padding: `var(--d-hero-pad-y, 24px) 26px`,
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* radial gradient overlay */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: `
            radial-gradient(circle at 90% 20%, color-mix(in oklab, ${accent} 30%, transparent), transparent 40%),
            radial-gradient(circle at 10% 100%, color-mix(in oklab, ${accent} 24%, transparent), transparent 50%)
          `,
          pointerEvents: 'none',
        }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Eyebrow */}
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '10px',
            letterSpacing: '0.24em',
            textTransform: 'uppercase',
            color: 'var(--gold)',
            marginBottom: '8px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
          }}>
            {country.toUpperCase()} · ITINERARY № {hashNum}
            <span style={{ flex: 1, height: '1px', background: 'rgba(201,166,100,.4)' }} />
            {dateRange}
          </div>

          {/* Title */}
          <h1 style={{
            fontFamily: 'var(--font-display)',
            fontSize: 'clamp(52px, 5vw, 72px)',
            lineHeight: 0.95,
            margin: '0 0 4px',
            letterSpacing: '-0.02em',
            fontWeight: 400,
          }}>
            {destination}
            {destination_local && destination_local !== destination && (
              <em style={{
                fontStyle: 'italic',
                fontSize: '38px',
                opacity: 0.6,
                marginLeft: '8px',
              }}>
                {destination_local}
              </em>
            )}
          </h1>

          {/* Subtitle */}
          {preferences.length > 0 && (
            <p style={{
              fontSize: '13px',
              color: 'rgba(246,241,231,.7)',
              margin: '8px 0 22px',
              maxWidth: '360px',
            }}>
              {preferences.join(' · ')} — {days} 天 {destination_local} 之行
            </p>
          )}

          {/* Stats */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '14px',
            paddingTop: '16px',
            borderTop: '1px solid rgba(246,241,231,.14)',
          }}>
            <Stat label={t('stat_destination')} value={destination} />
            <Stat label={t('stat_days')} value={String(days)} unit={t('stat_days_unit')} />
            <Stat label={t('stat_attractions')} value={String(attractions.length)} unit={t('stat_attractions_unit')} />
            <Stat label={t('stat_verdict')} value={verdict} isVerdict />
          </div>
        </div>
      </div>

      {/* Section I: Weather */}
      {weather.length > 0 && (
        <section style={{ padding: `var(--d-section-pad, 22px) 26px 6px` }}>
          <SectionHead num="I." title={t('section_weather')} note={t('section_weather_note')} />
          <WeatherCard destination={destination} country={country} verdict={verdict} weather={weather} />
        </section>
      )}

      {/* Section II: Attractions */}
      {attractions.length > 0 && (
        <section style={{ padding: `var(--d-section-pad, 22px) 26px 6px` }}>
          <SectionHead num="II." title={t('section_attractions')} note={attractionsNote} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--d-attr-row-gap, 12px)' }}>
            {attractions.map((a, i) => (
              <AttractionCard key={i} attr={a} index={i} total={attractions.length} />
            ))}
          </div>
        </section>
      )}

      {/* Section III: Itinerary */}
      <section style={{ padding: `var(--d-section-pad, 22px) 26px 6px` }}>
        <SectionHead num="III." title={t('section_itinerary')} note={itinerary.length > 0 ? itineraryNote : undefined} />
        {itinerary.length > 0
          ? <ItineraryTimeline itinerary={itinerary} />
          : <ItineraryEmpty lastQuery={lastQuery} />
        }
      </section>

      {/* Footer */}
      <div style={{
        textAlign: 'center',
        padding: '24px 32px 0',
        color: 'var(--ink-4)',
        fontFamily: 'var(--font-mono)',
        fontSize: '10px',
        letterSpacing: '0.16em',
        textTransform: 'uppercase',
      }}>
        · {t('detail_footer')} ·
      </div>
    </div>
  );
}

function Stat({ label, value, unit, isVerdict }: {
  label: string; value: string; unit?: string; isVerdict?: boolean;
}) {
  return (
    <div>
      <div style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '9px',
        letterSpacing: '0.18em',
        textTransform: 'uppercase',
        color: 'rgba(246,241,231,.55)',
        marginBottom: '4px',
      }}>
        {label}
      </div>
      <div style={{
        fontFamily: 'var(--font-display)',
        fontSize: isVerdict ? '16px' : '22px',
        color: 'var(--paper)',
        lineHeight: 1,
        fontWeight: 400,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
      }}>
        {value}
        {unit && <small style={{ fontSize: '11px', fontFamily: 'var(--font-body)', color: 'rgba(246,241,231,.6)', marginLeft: '4px' }}>{unit}</small>}
      </div>
    </div>
  );
}

function SectionHead({ num, title, note }: { num: string; title: string; note?: string }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'baseline',
      gap: '12px',
      marginBottom: '16px',
    }}>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.16em', color: 'var(--ink-3)' }}>
        {num}
      </span>
      <h3 style={{
        fontFamily: 'var(--font-display)',
        fontSize: '24px',
        color: 'var(--ink)',
        margin: 0,
        letterSpacing: '-0.01em',
        fontWeight: 400,
      }}>
        {title}
      </h3>
      <span style={{ flex: 1, height: '1px', background: 'var(--rule)' }} />
      {note && (
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--ink-3)', letterSpacing: '0.08em' }}>
          {note}
        </span>
      )}
    </div>
  );
}

function WeatherCard({ destination, country, verdict, weather }: {
  destination: string; country: string; verdict: string; weather: WeatherDay[];
}) {
  return (
    <div style={{
      background: 'var(--paper)',
      border: '1px solid var(--rule)',
      borderRadius: 'var(--radius-lg)',
      padding: '18px 20px',
      display: 'flex',
      gap: '20px',
      alignItems: 'stretch',
      boxShadow: 'var(--shadow-sm)',
    }}>
      {/* Left: place */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        paddingRight: '18px',
        borderRight: '1px solid var(--rule)',
        minWidth: '110px',
      }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '9px', letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
          FORECAST
        </span>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '24px', color: 'var(--ink)', lineHeight: 1.1, marginTop: '4px' }}>
          {destination}
        </span>
        {country && (
          <span style={{ fontSize: '11px', color: 'var(--ink-3)', marginTop: '2px' }}>{country}</span>
        )}
        <div style={{ marginTop: 'auto', paddingTop: '12px', fontSize: '11px', color: 'var(--forest)', display: 'flex', alignItems: 'center', gap: '5px' }}>
          ● {verdict.replace(/^[★⚠]\s*/, '')}
        </div>
      </div>
      {/* Right: days */}
      <div style={{ display: 'flex', gap: '10px', flex: 1 }}>
        {weather.map((day, i) => (
          <WeatherDay key={i} day={day} />
        ))}
      </div>
    </div>
  );
}

function WeatherDay({ day }: { day: WeatherDay }) {
  return (
    <div style={{
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      gap: '4px',
      padding: '4px 0',
      textAlign: 'center',
      position: 'relative',
    }}>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--ink-3)', letterSpacing: '0.04em' }}>
        {day.date}
      </span>
      <span style={{ fontSize: '11px', color: 'var(--ink-2)', fontWeight: 500 }}>{day.day}</span>
      <span style={{ fontSize: '26px', margin: '2px 0', filter: 'grayscale(0.25)' }}>{day.icon}</span>
      <span style={{ fontFamily: 'var(--font-display)', fontSize: '18px', color: 'var(--ink)', lineHeight: 1 }}>
        {day.hi}°
        <small style={{ fontSize: '11px', color: 'var(--ink-3)', fontFamily: 'var(--font-body)' }}>
          /{day.lo}°
        </small>
      </span>
      <span style={{ fontSize: '10px', color: 'var(--ink-3)' }}>{day.cond}</span>
    </div>
  );
}

function AttractionCard({ attr, index, total }: { attr: Attraction; index: number; total: number }) {
  return (
    <div
      style={{
        background: 'var(--paper)',
        border: '1px solid var(--rule)',
        borderRadius: 'var(--radius-lg)',
        padding: '14px 16px',
        display: 'grid',
        gridTemplateColumns: '72px 1fr auto',
        gap: '14px',
        alignItems: 'center',
        transition: 'all .15s',
        cursor: 'default',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.borderColor = 'var(--rule-2)';
        e.currentTarget.style.boxShadow = 'var(--shadow-sm)';
        e.currentTarget.style.transform = 'translateY(-1px)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.borderColor = 'var(--rule)';
        e.currentTarget.style.boxShadow = 'none';
        e.currentTarget.style.transform = 'none';
      }}
    >
      {/* Thumb */}
      <div style={{
        width: '72px',
        height: '72px',
        borderRadius: '10px',
        background: 'var(--sand)',
        overflow: 'hidden',
        flexShrink: 0,
      }}>
        <AttrThumb name={attr.name} name_cn={attr.name_cn} tags={attr.tags} color={attr.color} />
      </div>

      {/* Body */}
      <div style={{ minWidth: 0 }}>
        <h4 style={{
          fontFamily: 'var(--font-display)',
          fontSize: '20px',
          color: 'var(--ink)',
          margin: '0 0 2px',
          lineHeight: 1.1,
          letterSpacing: '-0.005em',
          fontWeight: 400,
        }}>
          {attr.name_cn || attr.name}
        </h4>
        {(attr.name_jp || (attr.name_cn && attr.name !== attr.name_cn)) && (
          <div style={{ fontSize: '11px', color: 'var(--ink-3)', letterSpacing: '0.08em', marginBottom: '6px' }}>
            {attr.name_jp || attr.name}
          </div>
        )}
        <p style={{
          fontSize: '12.5px',
          color: 'var(--ink-2)',
          lineHeight: 1.5,
          margin: 0,
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        } as React.CSSProperties}>
          {attr.desc}
        </p>
        {attr.tags.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px', marginTop: '6px' }}>
            {attr.tags.slice(0, 4).map((tag) => (
              <span key={tag} style={{
                fontSize: '10px',
                padding: '2px 7px',
                borderRadius: '99px',
                background: 'var(--bg-sunken)',
                color: 'var(--ink-2)',
                border: '1px solid var(--rule)',
              }}>
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Meta */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '4px',
        textAlign: 'right',
        fontSize: '10px',
        fontFamily: 'var(--font-mono)',
        color: 'var(--ink-3)',
        letterSpacing: '0.04em',
        flexShrink: 0,
      }}>
        <span style={{ fontFamily: 'var(--font-display)', fontSize: '20px', color: 'var(--forest)', lineHeight: 1 }}>
          {attr.rating}
        </span>
        <span>{String(index + 1).padStart(2, '0')} / {String(total).padStart(2, '0')}</span>
      </div>
    </div>
  );
}

function ItineraryTimeline({ itinerary }: { itinerary: ItineraryDay[] }) {
  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      position: 'relative',
      paddingLeft: '18px',
    }}>
      {/* Vertical line */}
      <div style={{
        position: 'absolute',
        left: '5px',
        top: '8px',
        bottom: '8px',
        width: '1px',
        background: 'var(--rule-2)',
      }} />
      {itinerary.map((day, i) => (
        <ItinDay key={i} day={day} />
      ))}
    </div>
  );
}

function ItinDay({ day }: { day: ItineraryDay }) {
  return (
    <div style={{ position: 'relative', padding: '10px 0 18px' }}>
      {/* Timeline dot */}
      <div style={{
        position: 'absolute',
        left: '-18px',
        top: '16px',
        width: '11px',
        height: '11px',
        borderRadius: '99px',
        background: 'var(--paper)',
        border: '2px solid var(--forest)',
      }} />

      {/* Day header */}
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '12px', marginBottom: '10px' }}>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontStyle: 'italic',
          fontSize: '28px',
          color: 'var(--forest)',
          lineHeight: 1,
        }}>
          Day {day.day}
        </span>
        <span style={{ fontSize: '13px', fontWeight: 500, color: 'var(--ink)', letterSpacing: '0.01em', flex: 1, minWidth: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
          {day.title}
        </span>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--ink-3)', marginLeft: 'auto', flexShrink: 0 }}>
          {day.date}
        </span>
      </div>

      {/* Items */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '12px 14px',
        background: 'var(--paper)',
        border: '1px solid var(--rule)',
        borderRadius: '12px',
      }}>
        {day.items.map((item, i) => (
          <div key={i} style={{
            display: 'grid',
            gridTemplateColumns: '56px 1fr auto',
            gap: '12px',
            alignItems: 'center',
            padding: '6px 0',
            borderTop: i > 0 ? '1px dashed var(--rule)' : 'none',
            paddingTop: i > 0 ? '10px' : '6px',
            marginTop: i > 0 ? '2px' : '0',
          }}>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '11px',
              color: 'var(--terra)',
              letterSpacing: '0.02em',
            }}>
              {item.time}
            </span>
            <div>
              <div style={{ fontSize: '13px', color: 'var(--ink)', fontWeight: 500 }}>{item.place}</div>
              {item.note && <div style={{ fontSize: '11px', color: 'var(--ink-3)', marginTop: '1px' }}>{item.note}</div>}
            </div>
            <div style={{
              width: '26px',
              height: '26px',
              borderRadius: '6px',
              background: 'var(--bg-sunken)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '14px',
              flexShrink: 0,
            }}>
              {item.icon}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ItineraryEmpty({ lastQuery }: { lastQuery: string }) {
  const retry = () => {
    if (lastQuery) window.dispatchEvent(new CustomEvent('tp:send', { detail: { query: lastQuery } }));
  };
  return (
    <div style={{
      background: 'var(--paper)',
      border: '1px dashed var(--rule-2)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px 20px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: '12px',
      textAlign: 'center',
    }}>
      <span style={{ fontSize: '28px', opacity: 0.4 }}>🗓</span>
      <div style={{ fontSize: '13px', color: 'var(--ink-3)', lineHeight: 1.5 }}>
        行程数据未能获取，可能是首次请求时模型响应超时。
      </div>
      {lastQuery && (
        <button
          onClick={retry}
          style={{
            marginTop: '4px',
            padding: '8px 20px',
            background: 'var(--forest)',
            color: 'var(--paper)',
            border: 'none',
            borderRadius: '8px',
            fontSize: '13px',
            cursor: 'pointer',
            transition: 'background .15s',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.background = 'var(--forest-2)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.background = 'var(--forest)'; }}
        >
          重新生成行程
        </button>
      )}
    </div>
  );
}

/* Date utilities */
function offsetDateStr(start: string, offset: number): string {
  try {
    const d = new Date(start);
    d.setDate(d.getDate() + offset);
    return d.toISOString().slice(0, 10);
  } catch { return start; }
}
function formatYMD(date: string): [string, string] {
  try {
    const d = new Date(date);
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const dd = String(d.getDate()).padStart(2, '0');
    return [mm, dd];
  } catch { return ['', '']; }
}
