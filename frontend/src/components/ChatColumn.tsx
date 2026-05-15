import { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { useApp } from '../lib/context';
import { i18n } from '../lib/i18n';
import type { Message, StepIndex } from '../types';

export default function ChatColumn() {
  const { state, dispatch, t } = useApp();
  const { messages, generating, step, lang, tweaks } = state;
  const [input, setInput] = useState('');
  const streamRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // auto-scroll to bottom
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [messages, step]);

  // listen for send events (from Composer Enter key or LeftRail example buttons)
  useEffect(() => {
    const handler = (e: Event) => {
      const { query } = (e as CustomEvent<{ query: string }>).detail;
      sendQuery(query);
    };
    window.addEventListener('tp:send', handler);
    return () => window.removeEventListener('tp:send', handler);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [generating]);

  const sendQuery = (text: string) => {
    if (!text.trim() || generating) return;
    dispatch({
      type: 'ADD_MESSAGE',
      message: { id: Date.now().toString(), who: 'user', kind: 'text', text: text.trim(), time: '刚刚' },
    });
    dispatch({ type: 'SET_GENERATING', generating: true });
    dispatch({ type: 'SET_STEP', step: 1 as StepIndex });
    dispatch({ type: 'CLEAR_RESULT' });
    // Actual SSE logic runs from useQueryStream hook wired in phase 4
    // Trigger it via a custom event
    window.dispatchEvent(new CustomEvent('tp:run_query', { detail: { query: text.trim() } }));
  };

  const onSend = () => {
    if (!input.trim() || generating) return;
    sendQuery(input.trim());
    setInput('');
  };

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  // auto-grow textarea
  const onInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    const ta = e.target;
    ta.style.height = 'auto';
    ta.style.height = Math.min(ta.scrollHeight, 120) + 'px';
  };

  const steps = [...i18n[lang].steps] as string[];
  const stepHeader = t('step_header');

  return (
    <div style={{
      background: 'var(--bg)',
      borderRight: '1px solid var(--rule)',
      display: 'flex',
      flexDirection: 'column',
      overflow: 'hidden',
    }}>
      {/* Chat head */}
      <div style={{
        padding: '24px 28px 14px',
        borderBottom: '1px solid var(--rule)',
        background: 'var(--bg)',
        flexShrink: 0,
      }}>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          letterSpacing: '0.2em',
          textTransform: 'uppercase',
          color: 'var(--terra)',
          marginBottom: '6px',
        }}>
          {t('chat_eyebrow')}
        </div>
        <h1 style={{
          fontFamily: 'var(--font-display)',
          fontSize: 'clamp(30px, 3vw, 44px)',
          lineHeight: 1.08,
          color: 'var(--ink)',
          margin: '0 0 6px',
          letterSpacing: '-0.01em',
        }}>
          {t('chat_title_plain')} <em style={{ fontStyle: 'italic', color: 'var(--forest)' }}>{t('chat_title_em')}</em>{t('chat_title_suffix')}
        </h1>
        <p style={{ fontSize: '13px', color: 'var(--ink-3)', margin: 0 }}>
          {t('chat_subtitle')}
        </p>
      </div>

      {/* Chat stream */}
      <div ref={streamRef} style={{
        flex: 1,
        overflowY: 'auto',
        padding: '20px 28px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
      }}>
        {messages.length === 0 && (
          <div style={{ color: 'var(--ink-4)', fontSize: '13px', textAlign: 'center', marginTop: '40px' }}>
            —
          </div>
        )}
        {messages.map((msg) => (
          <MessageBubble key={msg.id} msg={msg} showModels={tweaks.showModels} />
        ))}
        {generating && step > 0 && step < 5 && (
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
            <div style={{
              width: '32px', height: '32px', borderRadius: '8px',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'var(--font-display)', fontStyle: 'italic', fontSize: '14px',
              background: 'var(--forest)', color: 'var(--paper)', flexShrink: 0,
            }}>A</div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div style={{
                background: 'var(--paper)',
                border: '1px solid var(--rule)',
                borderRadius: '12px',
                borderBottomLeftRadius: '4px',
                padding: '10px 14px',
              }}>
                <div style={{
                  fontFamily: 'var(--font-mono)',
                  fontSize: '11px',
                  letterSpacing: '0.12em',
                  textTransform: 'uppercase',
                  color: 'var(--ink-3)',
                  marginBottom: '8px',
                }}>
                  {stepHeader}
                </div>
                <AgentStepChecklist step={step} steps={steps} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Composer */}
      <div style={{
        borderTop: '1px solid var(--rule)',
        padding: '14px 28px 20px',
        background: 'var(--paper)',
        flexShrink: 0,
      }}>
        <div style={{
          display: 'flex',
          background: 'var(--card)',
          border: `1px solid ${generating ? 'var(--rule)' : 'var(--rule)'}`,
          borderRadius: '14px',
          padding: '4px 4px 4px 14px',
          alignItems: 'flex-end',
          gap: '8px',
          transition: 'border-color .15s, box-shadow .15s',
        }}
          className="composer-wrap"
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--forest)';
            e.currentTarget.style.boxShadow = '0 0 0 3px rgba(31,63,51,.06)';
          }}
          onBlur={(e) => {
            if (!e.currentTarget.contains(e.relatedTarget as Node)) {
              e.currentTarget.style.borderColor = 'var(--rule)';
              e.currentTarget.style.boxShadow = 'none';
            }
          }}
        >
          <textarea
            ref={textareaRef}
            value={input}
            onChange={onInput}
            onKeyDown={onKeyDown}
            disabled={generating}
            placeholder={t('composer_placeholder')}
            rows={1}
            style={{
              flex: 1,
              border: 0,
              resize: 'none',
              fontFamily: 'inherit',
              fontSize: '14px',
              color: 'var(--ink)',
              background: 'transparent',
              outline: 'none',
              padding: '10px 0',
              maxHeight: '120px',
              overflowY: 'auto',
            }}
          />
          <button
            onClick={onSend}
            disabled={!input.trim() || generating}
            style={{
              background: (!input.trim() || generating) ? 'var(--rule-2)' : 'var(--forest)',
              color: 'var(--paper)',
              border: 0,
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all .15s',
              cursor: (!input.trim() || generating) ? 'not-allowed' : 'pointer',
              flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              if (!(!input.trim() || generating)) {
                e.currentTarget.style.background = 'var(--forest-2)';
                e.currentTarget.style.transform = 'translateX(1px)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = (!input.trim() || generating) ? 'var(--rule-2)' : 'var(--forest)';
              e.currentTarget.style.transform = 'none';
            }}
          >
            <Send size={14} />
          </button>
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          marginTop: '8px',
          fontSize: '11px',
          color: 'var(--ink-4)',
        }}>
          <span>
            {t('composer_hint_left')} ·{' '}
            <kbd style={{
              fontFamily: 'var(--font-mono)',
              background: 'var(--bg-sunken)',
              padding: '1px 5px',
              borderRadius: '3px',
              fontSize: '10px',
              border: '1px solid var(--rule)',
            }}>{t('composer_hint_enter')}</kbd>
            {' · '}{t('composer_hint_shift')}
          </span>
          <span>{t('composer_powered')}</span>
        </div>
      </div>
    </div>
  );
}

function AgentStepChecklist({ step, steps }: { step: StepIndex; steps: string[] }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      {steps.map((label, i) => {
        const stepNum = (i + 1) as StepIndex;
        const state: 'done' | 'active' | 'pending' =
          step > stepNum ? 'done' : step === stepNum ? 'active' : 'pending';
        return (
          <div key={i} style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '12px',
            color: state === 'pending' ? 'var(--ink-3)' : 'var(--ink-2)',
            padding: '6px 0',
          }}>
            <span style={{
              width: '16px',
              height: '16px',
              borderRadius: '99px',
              background: state === 'done' ? 'var(--forest)' : state === 'active' ? 'var(--terra)' : 'var(--rule-2)',
              color: state === 'pending' ? 'var(--ink-3)' : 'var(--paper)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '10px',
              flexShrink: 0,
              animation: state === 'active' ? 'spin 1s linear infinite' : 'none',
            }}>
              {state === 'done' ? '✓' : state === 'pending' ? String(i + 1) : ''}
            </span>
            <span style={{ flex: 1 }}>{label}</span>
            <span style={{
              fontFamily: 'var(--font-mono)',
              fontSize: '10px',
              color: 'var(--ink-4)',
              marginLeft: 'auto',
            }}>
              {state === 'active' ? '…' : state === 'done' ? `${(0.4 + i * 0.3).toFixed(1)}s` : ''}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function MessageBubble({ msg, showModels }: { msg: Message; showModels: boolean }) {
  const isUser = msg.who === 'user';
  return (
    <div style={{
      display: 'flex',
      gap: '12px',
      alignItems: 'flex-start',
      flexDirection: isUser ? 'row-reverse' : 'row',
    }}>
      {/* Avatar */}
      <div style={{
        width: '32px',
        height: '32px',
        borderRadius: '8px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'var(--font-display)',
        fontStyle: 'italic',
        fontSize: '14px',
        background: isUser ? 'var(--terra)' : 'var(--forest)',
        color: 'var(--paper)',
        flexShrink: 0,
      }}>
        {isUser ? 'U' : 'A'}
      </div>

      {/* Message column */}
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        minWidth: 0,
        maxWidth: 'calc(100% - 44px)',
        alignItems: isUser ? 'flex-end' : 'flex-start',
      }}>
        <div style={{
          background: isUser ? 'var(--forest)' : 'var(--paper)',
          color: isUser ? '#F0EBDD' : 'var(--ink)',
          border: isUser ? 'none' : '1px solid var(--rule)',
          borderRadius: '12px',
          borderBottomRightRadius: isUser ? '4px' : '12px',
          borderBottomLeftRadius: isUser ? '12px' : '4px',
          padding: '10px 14px',
          fontSize: '13.5px',
          lineHeight: 1.5,
          wordBreak: 'break-word',
        }}>
          {msg.text}
          {msg.kind === 'result' && msg.modelsUsed && showModels && (
            <ModelChips modelsUsed={msg.modelsUsed} />
          )}
          {msg.kind === 'error' && (
            <div style={{ marginTop: '4px', fontSize: '12px', color: 'var(--terra-soft)' }}>
              {msg.stepError}
            </div>
          )}
        </div>
        <div style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          color: 'var(--ink-4)',
          marginTop: '6px',
          letterSpacing: '0.05em',
        }}>
          {msg.time}
        </div>
      </div>
    </div>
  );
}

function ModelChips({ modelsUsed }: { modelsUsed: Record<string, string> }) {
  return (
    <div style={{
      marginTop: '6px',
      paddingTop: '8px',
      borderTop: '1px dashed var(--rule)',
      display: 'flex',
      flexWrap: 'wrap',
      gap: '4px',
    }}>
      {Object.entries(modelsUsed).map(([step, model]) => (
        <span key={step} style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '10px',
          background: 'var(--bg-sunken)',
          border: '1px solid var(--rule)',
          padding: '2px 6px',
          borderRadius: '4px',
          color: 'var(--ink-2)',
        }}>
          {step} · <b style={{ color: 'var(--forest)', fontWeight: 500 }}>{model}</b>
        </span>
      ))}
    </div>
  );
}
