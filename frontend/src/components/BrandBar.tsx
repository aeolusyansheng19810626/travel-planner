import { useApp } from '../lib/context';

export default function BrandBar() {
  const { t } = useApp();
  return (
    <header style={{
      height: '56px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 24px',
      background: 'var(--paper)',
      borderBottom: '1px solid var(--rule)',
      position: 'relative',
      zIndex: 10,
      whiteSpace: 'nowrap',
      flexShrink: 0,
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: '14px', minWidth: 0 }}>
        <span style={{
          fontFamily: 'var(--font-display)',
          fontStyle: 'italic',
          fontSize: '24px',
          letterSpacing: '-0.01em',
          color: 'var(--forest)',
          lineHeight: 1,
        }}>
          <em>Travel</em>·<em>Planner</em>
        </span>
        <span style={{
          fontSize: '11px',
          letterSpacing: '0.18em',
          textTransform: 'uppercase',
          color: 'var(--ink-3)',
          borderLeft: '1px solid var(--rule-2)',
          paddingLeft: '14px',
        }} className="brand-sub-hide">
          {t('brand_sub')}
        </span>
      </div>
      <div style={{ display: 'flex', gap: '16px', alignItems: 'center', fontSize: '12px', color: 'var(--ink-3)' }}>
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
          <b style={{ color: 'var(--ink-2)', fontWeight: 500 }}>aeolusyansheng</b>
          <span style={{ color: 'var(--ink-4)' }}>/</span>
          travel-planner
        </span>
        <span style={{
          padding: '3px 8px',
          border: '1px solid var(--rule)',
          borderRadius: '99px',
          fontSize: '10px',
          letterSpacing: '0.12em',
          color: 'var(--ink-3)',
          fontFamily: 'var(--font-mono)',
        }}>
          PRIVATE
        </span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{
            width: '6px',
            height: '6px',
            borderRadius: '99px',
            background: '#3F9A6E',
            boxShadow: '0 0 0 3px rgba(63,154,110,.18)',
            display: 'inline-block',
          }} />
          {t('running')}
        </span>
      </div>
    </header>
  );
}
