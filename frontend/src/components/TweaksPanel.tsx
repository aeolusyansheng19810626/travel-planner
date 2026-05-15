import { useState } from 'react';
import { Settings } from 'lucide-react';
import { useApp } from '../lib/context';
import type { Theme, Density } from '../types';

export default function TweaksPanel() {
  const { state, dispatch, t } = useApp();
  const { tweaks } = state;
  const [open, setOpen] = useState(false);

  const setTheme = (theme: Theme) => dispatch({ type: 'SET_TWEAKS', tweaks: { theme } });
  const setDensity = (density: Density) => dispatch({ type: 'SET_TWEAKS', tweaks: { density } });
  const toggleModels = () => dispatch({ type: 'SET_TWEAKS', tweaks: { showModels: !tweaks.showModels } });

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      zIndex: 100,
    }}>
      {open && (
        <div style={{
          position: 'absolute',
          bottom: '44px',
          right: 0,
          background: 'var(--paper)',
          border: '1px solid var(--rule)',
          borderRadius: '12px',
          padding: '16px 18px',
          minWidth: '220px',
          boxShadow: 'var(--shadow-lg)',
          display: 'flex',
          flexDirection: 'column',
          gap: '14px',
        }}>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '10px', letterSpacing: '0.16em', textTransform: 'uppercase', color: 'var(--ink-3)' }}>
            {t('tweaks_title')}
          </div>

          {/* Theme */}
          <TweakRow label={t('tweaks_theme')}>
            <RadioGroup
              options={[
                { value: 'warm', label: t('tweaks_theme_warm') },
                { value: 'forest', label: t('tweaks_theme_forest') },
                { value: 'ink', label: t('tweaks_theme_ink') },
              ]}
              value={tweaks.theme}
              onChange={(v) => setTheme(v as Theme)}
            />
          </TweakRow>

          {/* Density */}
          <TweakRow label={t('tweaks_density')}>
            <RadioGroup
              options={[
                { value: 'compact', label: t('tweaks_density_compact') },
                { value: 'regular', label: t('tweaks_density_regular') },
                { value: 'comfy', label: t('tweaks_density_comfy') },
              ]}
              value={tweaks.density}
              onChange={(v) => setDensity(v as Density)}
            />
          </TweakRow>

          {/* Show models toggle */}
          <TweakRow label={t('tweaks_show_models')}>
            <button
              onClick={toggleModels}
              style={{
                width: '36px',
                height: '20px',
                borderRadius: '99px',
                background: tweaks.showModels ? 'var(--forest)' : 'var(--rule-2)',
                border: 'none',
                cursor: 'pointer',
                position: 'relative',
                transition: 'background .15s',
                flexShrink: 0,
              }}
            >
              <span style={{
                position: 'absolute',
                top: '2px',
                left: tweaks.showModels ? '18px' : '2px',
                width: '16px',
                height: '16px',
                borderRadius: '99px',
                background: 'var(--paper)',
                transition: 'left .15s',
                boxShadow: '0 1px 2px rgba(0,0,0,.15)',
              }} />
            </button>
          </TweakRow>
        </div>
      )}

      {/* Toggle button */}
      <button
        onClick={() => setOpen((o) => !o)}
        style={{
          width: '40px',
          height: '40px',
          borderRadius: '99px',
          background: open ? 'var(--forest)' : 'var(--paper)',
          color: open ? 'var(--paper)' : 'var(--ink-3)',
          border: '1px solid var(--rule)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          boxShadow: 'var(--shadow-md)',
          transition: 'all .15s',
        }}
      >
        <Settings size={16} />
      </button>
    </div>
  );
}

function TweakRow({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px' }}>
      <span style={{ fontSize: '12px', color: 'var(--ink-2)', flexShrink: 0 }}>{label}</span>
      {children}
    </div>
  );
}

function RadioGroup({
  options,
  value,
  onChange,
}: {
  options: { value: string; label: string }[];
  value: string;
  onChange: (v: string) => void;
}) {
  return (
    <div style={{
      display: 'flex',
      gap: '2px',
      background: 'var(--bg-sunken)',
      padding: '3px',
      borderRadius: '6px',
      border: '1px solid var(--rule)',
    }}>
      {options.map((opt) => (
        <button
          key={opt.value}
          onClick={() => onChange(opt.value)}
          style={{
            padding: '4px 8px',
            fontSize: '11px',
            background: value === opt.value ? 'var(--paper)' : 'transparent',
            border: 'none',
            borderRadius: '4px',
            color: value === opt.value ? 'var(--ink)' : 'var(--ink-3)',
            cursor: 'pointer',
            fontWeight: value === opt.value ? 500 : 400,
            boxShadow: value === opt.value ? 'var(--shadow-sm)' : 'none',
            transition: 'all .12s',
          }}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
