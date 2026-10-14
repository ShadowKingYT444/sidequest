import { useEffect, useId, useRef, useState } from 'react';
import type { OfficeNotification } from './notifications';
import './NotificationTray.css';

export interface NotificationTrayProps {
  items: readonly OfficeNotification[];
  onSelect: (item: OfficeNotification) => void;
  loading?: boolean;
  error?: string | null;
  disabled?: boolean;
}

export function NotificationIcon({ kind }: { kind: OfficeNotification['kind'] }) {
  return <svg viewBox="0 0 20 20" width="18" height="18" aria-hidden="true" fill="none"><circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />{kind === 'completed'
    ? <path d="m6 10 2.7 2.7 5.5-5.5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    : <><path d="M10 5.5v5" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" /><circle cx="10" cy="14" r="1" fill="currentColor" /></>}</svg>;
}

export default function NotificationTray({ items, onSelect, loading = false, error, disabled = false }: NotificationTrayProps) {
  const [open, setOpen] = useState(false);
  const button = useRef<HTMLButtonElement>(null), root = useRef<HTMLDivElement>(null);
  const panelId = useId();
  const attention = items.filter(item => item.kind === 'attention').length;
  useEffect(() => {
    if (!open) return;
    const dismiss = (event: PointerEvent) => { if (!root.current?.contains(event.target as Node)) setOpen(false); };
    const escape = (event: KeyboardEvent) => { if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); setOpen(false); button.current?.focus(); } };
    document.addEventListener('pointerdown', dismiss); document.addEventListener('keydown', escape, true);
    return () => { document.removeEventListener('pointerdown', dismiss); document.removeEventListener('keydown', escape, true); };
  }, [open]);
  useEffect(() => { if (disabled) setOpen(false); }, [disabled]);
  return <div className="notification-control" ref={root}>
    <button ref={button} type="button" className="notification-toggle" aria-expanded={open} aria-controls={panelId} disabled={disabled}
      onClick={() => setOpen(value => !value)} aria-label={`Notifications${items.length ? `, ${items.length} recorded${attention ? `, ${attention} need attention` : ''}` : ''}`}>
      <svg viewBox="0 0 20 20" width="15" height="15" fill="none" aria-hidden="true"><path d="M5 7.5a5 5 0 0 1 10 0c0 5 1.5 5.5 1.5 5.5h-13S5 12.5 5 7.5Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" /><path d="M8 16h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" /></svg>
      <span>Notifications</span>{items.length > 0 && <span className="notification-count" aria-hidden="true" data-attention={attention > 0}>{items.length}</span>}
    </button>
    {open && <section id={panelId} className="notification-tray" aria-label="Notifications">
      <header><h2>Notifications</h2><button type="button" aria-label="Close notifications" onClick={() => { setOpen(false); button.current?.focus(); }}>×</button></header>
      {items.some(item => item.fixture) && <p className="notification-fixture">Test fixture</p>}
      {error && <div role="alert" className="notification-empty">Notifications unavailable<details><summary>Details</summary><p>{error.slice(0, 1000)}</p></details></div>}
      {loading && <p className="notification-empty" role="status">Refreshing…</p>}
      {!items.length && !loading && !error && <p className="notification-empty">No completed tasks or alerts yet.</p>}
      {!!items.length && <ul>{items.map(item => <li key={item.id} data-notification-kind={item.kind} data-notification-job={item.jobId}>
        <button type="button" className="notification-row" onClick={() => { setOpen(false); onSelect(item); }}>
          <span className="notification-state-icon"><NotificationIcon kind={item.kind} /></span>
          <span className="notification-copy"><strong>{item.title}</strong><span>{item.label}{item.fixture ? ' · Test fixture' : ''}{item.stationId ? ` · Computer ${Number(item.stationId.slice(-3))}` : ''}</span></span>
          <span className="notification-open" aria-hidden="true">→</span>
        </button>
        {item.detail && <details className="notification-detail"><summary>Details</summary><p>{item.detail.slice(0, 2000)}</p></details>}
      </li>)}</ul>}
    </section>}
  </div>;
}
