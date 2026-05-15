import { useEffect, useState, useCallback } from 'react';
import { RefreshCw, ChevronDown } from 'lucide-react';
import { useApp } from '../lib/context';
import { fetchAgents, checkHealth } from '../lib/api';
import type { AgentsData, Lang } from '../types';
import { i18n } from '../lib/i18n';

const AGENT_GRADIENTS: Record<string, string> = {
  weather_agent: 'linear-gradient(135deg, #7BA4BE, #4F7591)',
  attraction_agent: 'linear-gradient(135deg, #B85530, #8B3D1F)',
  itinerary_agent: 'linear-gradient(135deg, #2C5645, #1F3F33)',
};
const AGENT_INITIALS: Record<string, string> = {
  weather_agent: 'W',
  attraction_agent: 'A',
  itinerary_agent: 'I',
};

export default function LeftRail() {
  const { state, dispatch, t } = useApp();
  const { lang } = state;

  const [online, setOnline] = useState(false);
  const [agents, setAgents] = useState<AgentsData | null>(null);
  const [openAgents, setOpenAgents] = useState<Record<string, boolean>>({});
  const [refreshing, setRefreshing] = useState(false);

  const refresh = useCallback(async () => {
    setRefreshing(true);
    const [health, agentsData] = await Promise.all([checkHealth(), fetchAgents()]);
    setOnline(health);
    setAgents(agentsData);
    setRefreshing(false);
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  const setLang = (l: Lang) => dispatch({ type: 'SET_LANG', lang: l });
  const toggleAgent = (key: string) =>
    setOpenAgents((prev) => ({ ...prev, [key]: !prev[key] }));

  const handleExample = (query: string) => {
    if (state.generating) return;
    dispatch({
      type: 'ADD_MESSAGE',
      message: { id: Date.now().toString(), who: 'user', kind: 'text', text: query, time: '刚刚' },
    });
    // actual query dispatch handled by ChatColumn via a custom event
    window.dispatchEvent(new CustomEvent('tp:query', { detail: { query } }));
  };

  const examples = [...i18n[lang].examples] as string[];

  return (
    <aside style={{
      background: 'var(--paper)',
      borderRight: '1px solid var(--rule)',
      overflowY: 'auto',
      padding: '20px 18px 28px',
      display: 'flex',
      flexDirection: 'column',
      gap: '22px',
    }}>
      {/* Language switcher */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <RailLabel>{t('lang_label')}</RailLabel>
        <div style={{
          display: 'flex',
          gap: '4px',
          background: 'var(--bg-sunken)',
          padding: '4px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--rule)',
        }}>
          {(['zh', 'en', 'ja'] as Lang[]).map((l, i) => (
            <button
              key={l}
              onClick={() => setLang(l)}
              style={{
                flex: 1,
                padding: '7px 0',
                fontSize: '12px',
                background: lang === l ? 'var(--paper)' : 'transparent',
                border: 0,
                borderRadius: '4px',
                color: lang === l ? 'var(--ink)' : 'var(--ink-3)',
                fontWeight: 500,
                transition: 'all .15s',
                boxShadow: lang === l ? 'var(--shadow-sm)' : 'none',
                cursor: 'pointer',
              }}
            >
              {(['中文', 'English', '日本語'] as const)[i]}
            </button>
          ))}
        </div>
      </section>

      {/* System status */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <RailLabel>{t('status_label')}</RailLabel>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '12px 14px',
          background: 'var(--card)',
          border: '1px solid var(--rule)',
          borderRadius: 'var(--radius)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ position: 'relative', width: '8px', height: '8px', flexShrink: 0 }}>
              <span style={{
                display: 'block',
                width: '8px',
                height: '8px',
                borderRadius: '99px',
                background: online ? '#3F9A6E' : 'var(--ink-4)',
              }} />
              {online && (
                <span style={{
                  position: 'absolute',
                  inset: '-4px',
                  borderRadius: '99px',
                  border: '1px solid #3F9A6E',
                  opacity: 0.35,
                  animation: 'pulse 2.4s ease-in-out infinite',
                }} />
              )}
            </span>
            <div>
              <div style={{ fontSize: '12px', fontWeight: 500, color: 'var(--ink-2)' }}>
                {online ? t('status_online') : t('status_offline')}
              </div>
              <div style={{ fontSize: '11px', color: 'var(--ink-3)', fontFamily: 'var(--font-mono)' }}>
                {agents ? `${agents.count} AGENTS · ${t('version')}` : t('version')}
              </div>
            </div>
          </div>
          <button
            onClick={refresh}
            style={{
              background: 'transparent',
              border: 0,
              padding: '6px',
              color: 'var(--ink-3)',
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              cursor: 'pointer',
              transition: 'all .15s',
              transform: refreshing ? 'rotate(45deg)' : 'none',
            }}
            title={t('refresh')}
          >
            <RefreshCw size={14} />
          </button>
        </div>
      </section>

      {/* Discovered agents */}
      {online && agents && (
        <section style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <RailLabel>{t('agents_label')}</RailLabel>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {Object.entries(agents.agents).map(([key, agent]) => {
              const isOpen = openAgents[key] ?? false;
              const gradient = AGENT_GRADIENTS[key] ?? 'linear-gradient(135deg, #9A9C92, #6B6E64)';
              const initial = AGENT_INITIALS[key] ?? agent.name?.[0]?.toUpperCase() ?? 'A';
              const skills = agent.skills ?? [];
              return (
                <div key={key} style={{
                  background: 'var(--card)',
                  border: '1px solid var(--rule)',
                  borderRadius: 'var(--radius)',
                  overflow: 'hidden',
                  transition: 'border-color .15s',
                }}>
                  <div
                    onClick={() => toggleAgent(key)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '10px',
                      padding: '11px 12px',
                      cursor: 'pointer',
                      userSelect: 'none',
                    }}
                  >
                    <span style={{
                      width: '28px',
                      height: '28px',
                      borderRadius: '7px',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '13px',
                      fontWeight: 600,
                      flexShrink: 0,
                      color: 'white',
                      background: gradient,
                    }}>
                      {initial}
                    </span>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: '13px', fontWeight: 500, color: 'var(--ink)' }}>
                        {agent.name ?? key}
                      </div>
                      <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--ink-3)', marginTop: '2px' }}>
                        {skills.length} SKILLS · {t('online_label')}
                      </div>
                    </div>
                    <ChevronDown
                      size={14}
                      color="var(--ink-4)"
                      style={{ transition: 'transform .2s', transform: isOpen ? 'rotate(180deg)' : 'none' }}
                    />
                  </div>
                  {isOpen && (
                    <div style={{
                      padding: '0 12px 12px',
                      borderTop: '1px dashed var(--rule)',
                      marginTop: 0,
                      paddingTop: '12px',
                    }}>
                      <dl style={{ margin: 0 }}>
                        <AgentRow label={t('desc_label')}>
                          <span style={{ fontSize: '11px', color: 'var(--ink-2)' }}>
                            {agent.description ?? '—'}
                          </span>
                        </AgentRow>
                        <AgentRow label={t('endpoint_label')}>
                          <code style={{
                            fontFamily: 'var(--font-mono)',
                            fontSize: '10px',
                            background: 'var(--bg-sunken)',
                            padding: '2px 6px',
                            borderRadius: '4px',
                            color: 'var(--forest)',
                          }}>
                            {agent.url ?? agent.endpoint ?? '—'}
                          </code>
                        </AgentRow>
                        {skills.length > 0 && (
                          <AgentRow label={t('skills_label')}>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                              {skills.map((s) => (
                                <span key={s.name} style={{
                                  display: 'inline-block',
                                  fontFamily: 'var(--font-mono)',
                                  fontSize: '10px',
                                  background: 'var(--bg-sunken)',
                                  color: 'var(--ink-2)',
                                  padding: '2px 7px',
                                  borderRadius: '4px',
                                  border: '1px solid var(--rule)',
                                }}>
                                  {s.name}
                                </span>
                              ))}
                            </div>
                          </AgentRow>
                        )}
                      </dl>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </section>
      )}

      {/* Example queries */}
      <section style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <RailLabel>{t('examples_label')}</RailLabel>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          {examples.map((ex, i) => (
            <ExampleButton key={i} index={i + 1} onClick={() => handleExample(ex)} disabled={state.generating}>
              {ex}
            </ExampleButton>
          ))}
        </div>
      </section>

      {/* Clear history */}
      <div style={{ marginTop: 'auto', paddingTop: '8px' }}>
        <button
          onClick={() => dispatch({ type: 'CLEAR_HISTORY' })}
          style={{
            width: '100%',
            textAlign: 'left',
            background: 'transparent',
            border: '1px solid var(--rule)',
            borderRadius: '6px',
            padding: '8px 12px',
            fontSize: '11px',
            color: 'var(--ink-4)',
            fontFamily: 'var(--font-mono)',
            letterSpacing: '0.08em',
            cursor: 'pointer',
            transition: 'all .15s',
          }}
          onMouseEnter={(e) => { e.currentTarget.style.color = 'var(--terra)'; e.currentTarget.style.borderColor = 'var(--terra-soft)'; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = 'var(--ink-4)'; e.currentTarget.style.borderColor = 'var(--rule)'; }}
        >
          {t('clear_history')}
        </button>
      </div>
    </aside>
  );
}

function RailLabel({ children }: { children: React.ReactNode }) {
  return (
    <div style={{
      fontFamily: 'var(--font-mono)',
      fontSize: '10px',
      letterSpacing: '0.16em',
      textTransform: 'uppercase',
      color: 'var(--ink-3)',
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
    }}>
      {children}
      <span style={{ flex: 1, height: '1px', background: 'var(--rule)' }} />
    </div>
  );
}

function AgentRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '56px 1fr', gap: '8px', padding: '4px 0', fontSize: '11px' }}>
      <dt style={{
        fontFamily: 'var(--font-mono)',
        fontSize: '10px',
        letterSpacing: '0.08em',
        textTransform: 'uppercase',
        color: 'var(--ink-3)',
        margin: '2px 0 0',
      }}>
        {label}
      </dt>
      <dd style={{ margin: 0 }}>{children}</dd>
    </div>
  );
}

function ExampleButton({
  index,
  children,
  onClick,
  disabled,
}: {
  index: number;
  children: string;
  onClick: () => void;
  disabled: boolean;
}) {
  const [hovered, setHovered] = useState(false);
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        textAlign: 'left',
        background: hovered ? 'var(--card)' : 'transparent',
        border: `1px solid ${hovered ? 'var(--forest)' : 'var(--rule)'}`,
        borderRadius: '8px',
        padding: '10px 12px',
        fontSize: '12.5px',
        color: hovered ? 'var(--forest)' : 'var(--ink-2)',
        display: 'flex',
        gap: '9px',
        alignItems: 'flex-start',
        transition: 'all .15s',
        transform: hovered ? 'translateX(2px)' : 'none',
        cursor: disabled ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        width: '100%',
        fontFamily: 'inherit',
      }}
    >
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--ink-4)', marginTop: '2px', flexShrink: 0 }}>
        {String(index).padStart(2, '0')}
      </span>
      {children}
    </button>
  );
}
