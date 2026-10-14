import { useState } from 'react';
import { PROVIDERS, providerReadiness, type ProviderChoice, type ProviderId, type ProviderReadinessInput } from './provider-readiness';
import './ProviderTiles.css';

export interface ProviderTilesProps extends ProviderReadinessInput {
  value: string;
  onChange: (provider: ProviderId) => void;
  disabled?: boolean;
  label?: string;
}

function ProviderMark({ provider }: { provider: ProviderChoice }) {
  const [imageFailed, setImageFailed] = useState(false);
  return <span className={'provider-tile-mark provider-tile-mark--' + provider.id} aria-hidden="true">
    {provider.image && !imageFailed ? <img src={provider.image} alt="" width={28} height={28} draggable={false} onError={() => setImageFailed(true)} /> : provider.mark}
  </span>;
}

/** Six known providers; no executable is presented as a connected session. */
export default function ProviderTiles({ value, onChange, disabled = false, label = 'Agent providers', ...readiness }: ProviderTilesProps) {
  return <div className="provider-tiles" role="group" aria-label={label}>
    {PROVIDERS.map(provider => {
      const state = providerReadiness(provider.id, readiness);
      return <button type="button" key={provider.id} className="provider-tile" aria-label={provider.name + ' — ' + state.label}
        aria-pressed={state.available && value === provider.id} disabled={disabled || !state.available} data-provider={provider.id} data-readiness={state.status}
        onClick={() => { if (!disabled && state.available) onChange(provider.id); }}>
        <ProviderMark provider={provider} /><span className="provider-tile-copy"><strong>{provider.name}</strong><small>{state.label}</small></span>
      </button>;
    })}
  </div>;
}
