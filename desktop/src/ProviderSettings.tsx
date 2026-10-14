import { useEffect, useRef, useState, type ReactNode } from 'react';
import type { ProviderDiscovery, RuntimeCapabilities } from './types';
import './ProviderSettings.css';

// Layout adapted from T3 Code d765d03cb7f980794c409c38e6ea5e25d89fde33.
// See desktop/THIRD_PARTY_NOTICES.md for its MIT license.
type ProviderId = 'codex' | 'claude' | 'cursor' | 'grok' | 'opencode' | 'antigravity';
type SettingsView = 'providers' | 'usage';
type UsageMetric = 'cost' | 'tokens' | 'limits';

interface ProviderChoice { id: ProviderId; name: string; mark: string }

export interface ProviderSettingsProps {
  discovery: ProviderDiscovery | null;
  capabilities: RuntimeCapabilities | null;
  onClose: () => void;
  onRefresh: () => void;
  busy?: boolean;
}

const PROVIDERS: ProviderChoice[] = [
  { id: 'codex', name: 'Codex', mark: '>_' },
  { id: 'claude', name: 'Claude', mark: 'Cl' },
  { id: 'cursor', name: 'Cursor', mark: 'Cu' },
  { id: 'grok', name: 'Grok', mark: 'G' },
  { id: 'opencode', name: 'OpenCode', mark: 'Oc' },
  { id: 'antigravity', name: 'Antigravity', mark: 'A' },
];

function formatObservedAt(value: string | undefined) {
  if (!value) return 'Not scanned';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? 'Scan time unavailable' : 'Checked ' + date.toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}

function Icon({ name }: { name: 'close' | 'refresh' | 'device' | 'chevron' | 'chart' }) {
  return <svg className="provider-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {name === 'close' && <path d="m6 6 12 12M6 18 18 6" />}
    {name === 'refresh' && <><path d="M20 7v5h-5" /><path d="M4 17v-5h5M6.2 6.2a8 8 0 0 1 13 2L20 12M4 12l.8 3.8a8 8 0 0 0 13 2" /></>}
    {name === 'device' && <><rect x="3" y="4" width="18" height="12" rx="2" /><path d="M8 20h8M12 16v4" /></>}
    {name === 'chevron' && <path d="m8 10 4 4 4-4" />}
    {name === 'chart' && <><path d="M4 4v16h16M8 14l4-4 4 2 4-6" /></>}
  </svg>;
}

function ProviderMark({ provider }: { provider: ProviderChoice }) {
  return <span aria-hidden="true" className={'provider-mark provider-mark--' + provider.id}>{provider.mark}</span>;
}

function SettingsSection({ title, children }: { title: ReactNode; children: ReactNode }) {
  return <section className="provider-section"><h2>{title}</h2><div className="provider-settings-group">{children}</div></section>;
}

function ReadOnlyField({ label, value, description, mono = false }: { label: string; value: string | null; description?: string; mono?: boolean }) {
  return <label className="provider-field provider-settings-row">
    <span className="provider-row-copy"><span className="provider-row-title">{label}</span>{description && <span className="provider-row-description">{description}</span>}</span>
    <input aria-readonly="true" className={'provider-field__value' + (mono ? ' is-mono' : '')} readOnly value={value || 'Not reported'} title={value || undefined} />
  </label>;
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return <div className="provider-settings-row"><span className="provider-row-title">{label}</span><span className="provider-row-status">{value}</span></div>;
}

function LimitsView({ selected }: { selected: ProviderChoice }) {
  return <section className="provider-limits" aria-label={selected.name + ' usage limits'}>
    <div className="provider-limits-heading"><ProviderMark provider={selected} /><h2>{selected.name}</h2><span>Usage unknown</span></div>
    <div className="provider-limit-windows">
      {['Session', 'Weekly'].map((label) => <div className="provider-limit-window" key={label}>
        <div className="provider-limit-label"><span>{label}</span><strong>— remaining</strong></div>
        <div className="provider-limit-track" role="img" aria-label={label + ' usage unknown'} />
        <span className="provider-limit-reset">Reset unknown</span>
      </div>)}
    </div>
    <p className="provider-empty-note">Usage and reset times have not been reported.</p>
  </section>;
}

function UsageView({ selected, metric, period }: { selected: ProviderChoice; metric: UsageMetric; period: string }) {
  const [breakdown, setBreakdown] = useState<'model' | 'time'>('model');
  if (metric === 'limits') return <LimitsView selected={selected} />;
  return <div className="provider-usage-page" aria-label={selected.name + ' usage analytics'}>
    <section className="provider-usage-summary">
      <div className="provider-usage-providers">
        <div className="provider-usage-total"><span className="provider-usage-total__figure" aria-label={metric === 'cost' ? 'Total cost unknown' : 'Processed tokens unknown'}>—</span><span>{metric === 'cost' ? 'Reported cost unavailable' : 'Processed tokens unavailable'}</span><span>Sessions unknown</span></div>
        <div className="provider-usage-provider"><div><ProviderMark provider={selected} /><span>{selected.name}</span><strong>—</strong></div><span>{metric === 'cost' ? 'Cost and token totals unknown' : 'Token and cost totals unknown'}</span></div>
      </div>
      <div className="provider-usage-chart"><h2>{metric === 'tokens' ? 'Daily processed tokens' : 'Daily cost'}</h2><div className="provider-chart-empty" role="status"><Icon name="chart" /><span>No usage data reported</span></div><span className="provider-usage-period-label">{period}</span></div>
    </section>
    <section className="provider-usage-totals" aria-labelledby="provider-totals-title">
      <h2 id="provider-totals-title">Totals</h2>
      <div>{['Processed tokens', 'Cached input', 'Uncached input', 'Output', 'Cache savings'].map((label) => <div className="provider-usage-metric" key={label}><span>{label}</span><strong aria-label={label + ' unknown'}>—</strong></div>)}</div>
    </section>
    <section className="provider-usage-breakdown" aria-labelledby="provider-breakdown-title">
      <div className="provider-usage-section-heading"><h2 id="provider-breakdown-title">Breakdown</h2><div className="provider-segmented" role="group" aria-label="Usage breakdown"><button aria-pressed={breakdown === 'model'} onClick={() => setBreakdown('model')}>Model</button><button aria-pressed={breakdown === 'time'} onClick={() => setBreakdown('time')}>Day</button></div></div>
      <div className="provider-table-wrap"><table className="provider-table"><thead><tr><th scope="col">{breakdown === 'model' ? 'Model' : 'Day'}</th><th scope="col">Cost</th><th scope="col">Share</th><th scope="col">Tokens</th></tr></thead><tbody><tr><td colSpan={4}>No {breakdown === 'model' ? 'model' : 'daily'} usage data reported</td></tr></tbody></table></div>
    </section>
  </div>;
}

export default function ProviderSettings({ discovery, capabilities, onClose, onRefresh, busy = false }: ProviderSettingsProps) {
  const [selectedId, setSelectedId] = useState<ProviderId>('codex');
  const [view, setView] = useState<SettingsView>('providers');
  const [metric, setMetric] = useState<UsageMetric>('cost');
  const [period, setPeriod] = useState('Past 7 days');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const mobilePickerButton = useRef<HTMLButtonElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const scrollElement = useRef<HTMLDivElement>(null);
  const positions = useRef<Record<SettingsView, number>>({ providers: 0, usage: 0 });
  useEffect(() => { closeButton.current?.focus(); }, []);
  const selected = PROVIDERS.find((provider) => provider.id === selectedId) ?? PROVIDERS[0];
  const detail = discovery?.providers.find((provider) => provider.id === selected.id) ?? null;
  const scanned = discovery !== null;
  const installed = detail?.installed === true;
  const statusText = !scanned ? 'Not scanned' : installed ? detail?.discoverySource==='host-setting'?'Configured by host':detail?.discoverySource==='known-install'?'Located in default install directory':'Located in PATH' : 'Not detected';
  const homeLabel = selected.id === 'codex' ? 'CODEX_HOME' : 'Host home';
  const worker = selected.id === 'codex' ? capabilities?.worker_model : null;

  function chooseProvider(id: ProviderId) {
    setSelectedId(id);
    setMobileMenuOpen(false);
    requestAnimationFrame(() => mobilePickerButton.current?.focus());
  }

  function chooseView(next: SettingsView) {
    if (next === view) return;
    positions.current[view] = scrollElement.current?.scrollTop ?? 0;
    setView(next);
    setMobileMenuOpen(false);
    requestAnimationFrame(() => { if (scrollElement.current) scrollElement.current.scrollTop = positions.current[next]; });
  }

  const picker = <div className="provider-mobile-picker">
    <button ref={mobilePickerButton} className="provider-mobile-picker__button" aria-expanded={mobileMenuOpen} aria-controls="provider-mobile-menu" onClick={() => setMobileMenuOpen((open) => !open)}><span><ProviderMark provider={selected} />{selected.name}</span><Icon name="chevron" /></button>
    <nav id="provider-mobile-menu" className="provider-mobile-menu" aria-label="Choose provider" hidden={!mobileMenuOpen}>
      {PROVIDERS.map((provider) => <button key={provider.id} onClick={() => chooseProvider(provider.id)} aria-current={selected.id === provider.id ? 'page' : undefined}><ProviderMark provider={provider} /><span>{provider.name}</span></button>)}
    </nav>
  </div>;

  return <section className="provider-settings" aria-label="Provider settings">
    <header className="provider-topbar">
      <div className="provider-breadcrumb"><span>Settings</span><span aria-hidden="true">/</span><span>{view === 'providers' ? 'Providers' : 'Usage'}</span></div>
      <div className="provider-topbar__actions"><span className="provider-device"><Icon name="device" />Local device</span><button ref={closeButton} className="provider-close" onClick={onClose} aria-label="Close provider settings"><Icon name="close" /><kbd>Esc</kbd></button></div>
    </header>
    <div className="provider-viewbar"><nav className="provider-view-tabs" aria-label="Settings view"><button aria-current={view === 'providers' ? 'page' : undefined} onClick={() => chooseView('providers')}>Providers</button><button aria-current={view === 'usage' ? 'page' : undefined} onClick={() => chooseView('usage')}>Usage</button></nav><button className="provider-refresh" onClick={onRefresh} disabled={busy} aria-busy={busy} aria-label={busy ? 'Refreshing provider discovery' : 'Refresh provider discovery'}><Icon name="refresh" /><span>{busy ? 'Checking…' : formatObservedAt(discovery?.observedAt)}</span></button></div>
    <div ref={scrollElement} className="provider-scroll">
      <div className={'provider-content provider-content--' + view}>
        {view === 'providers' ? <>
          <div className="provider-page-heading"><h1>Providers</h1><span>Read-only</span></div>
          <div className="provider-editor-group">
            <aside className="provider-sidebar"><nav className="provider-list" aria-label="Providers">{PROVIDERS.map((provider) => {
              const item = discovery?.providers.find((entry) => entry.id === provider.id);
              return <button key={provider.id} className={'provider-list__item' + (selected.id === provider.id ? ' is-selected' : '')} onClick={() => chooseProvider(provider.id)} aria-current={selected.id === provider.id ? 'page' : undefined}>
                <ProviderMark provider={provider} /><span className="provider-list__copy"><strong>{provider.name}</strong><small>{!scanned ? 'Not scanned' : item?.installed ? 'Executable found' : 'Not detected'}</small></span>
              </button>;
            })}</nav></aside>
            <div className="provider-editor">
              {picker}
              <div className="provider-editor-content" key={selected.id}>
                <SettingsSection title={<span className="provider-section-title"><ProviderMark provider={selected} /><span>{selected.name}</span></span>}>
                  <ReadOnlyField label="Display name" value={selected.name} description={statusText} />
                  <StatusRow label="Authentication" value="Unknown" /><StatusRow label="Service reachability" value="Unknown" />
                </SettingsSection>
                <SettingsSection title="Runtime">
                  <ReadOnlyField label="Runtime" value={detail?.runtime === 'local' ? 'Local process' : null} />
                  <ReadOnlyField label="Binary path" value={detail?.binaryPath ?? null} mono />
                  <ReadOnlyField label={homeLabel} value={detail?.homePath ?? null} mono />
                </SettingsSection>
                <SettingsSection title="Environment"><ReadOnlyField label="Environment" value={scanned ? 'Host process' : null} /><StatusRow label="Launch arguments" value="Not inspected" /></SettingsSection>
                <SettingsSection title="Models">{worker ? <><StatusRow label="Configured worker" value={worker.id==='none'?'Not configured':worker.id + ' · ' + worker.effort} /><StatusRow label="Model catalog" value={worker.verified ? 'Verified' : 'Not verified'} /></> : <StatusRow label="Model catalog" value="Not reported" />}</SettingsSection>
              </div>
            </div>
          </div>
          <p className="provider-readonly-note">Local discovery only. Configuration is read-only.</p>
        </> : <>
          <div className="provider-usage-toolbar"><h1>Usage</h1><div className="provider-usage-controls"><div className="provider-segmented" role="group" aria-label="Usage metric">{(['cost', 'tokens', 'limits'] as const).map((value) => <button key={value} aria-pressed={metric === value} onClick={() => setMetric(value)}>{value === 'cost' ? 'Cost' : value === 'tokens' ? 'Tokens' : 'Limits'}</button>)}</div><select aria-label="Usage period" value={period} disabled={metric === 'limits'} onChange={(event) => setPeriod(event.target.value)}><option>Past 24 hours</option><option>Past 7 days</option><option>Past 30 days</option></select></div></div>
          <div className="provider-usage-provider-picker"><label htmlFor="provider-usage-selection">Provider</label><select id="provider-usage-selection" value={selectedId} onChange={(event) => chooseProvider(event.target.value as ProviderId)}>{PROVIDERS.map((provider) => <option value={provider.id} key={provider.id}>{provider.name}</option>)}</select><span>Telemetry unavailable</span></div>
          <UsageView selected={selected} metric={metric} period={period} />
        </>}
      </div>
    </div>
  </section>;
}
