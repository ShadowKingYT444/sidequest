import type { ProviderDiscovery, RuntimeCapabilities, RuntimeProject, RuntimeSnapshot } from './types';

export type ProviderId = 'codex' | 'claude' | 'cursor' | 'grok' | 'opencode' | 'antigravity';
export interface ProviderChoice { id: ProviderId; name: string; mark: string; image?: string }
export const PROVIDERS: readonly ProviderChoice[] = [
  { id: 'codex', name: 'Codex', mark: '>_', image: '/office/caps/textures/portable_CODEX_cap_RGBA.png' },
  { id: 'claude', name: 'Claude', mark: 'Cl', image: '/office/caps/textures/portable_CLAUDE_CODE_cap_RGBA.png' },
  { id: 'cursor', name: 'Cursor', mark: 'Cu' },
  { id: 'grok', name: 'Grok', mark: 'G', image: '/office/caps/textures/portable_XAI_GROK_cap_RGBA.png' },
  { id: 'opencode', name: 'OpenCode', mark: 'Oc', image: '/office/caps/textures/portable_HARNESS_OPENCODE_cap_RGBA.png' },
  { id: 'antigravity', name: 'Antigravity', mark: 'A' },
];

export interface ProviderReadinessInput {
  discovery: ProviderDiscovery | null;
  capabilities: RuntimeCapabilities | null;
  snapshot: RuntimeSnapshot | null;
  project?: RuntimeProject;
  failed?: boolean;
}
export interface ProviderReadiness {
  available: boolean;
  installed: boolean;
  status: 'checking' | 'not_detected' | 'unsupported' | 'unavailable' | 'permission_needed' | 'ready';
  label: string;
  reason: string;
}

const result = (status: ProviderReadiness['status'], label: string, reason: string, installed = false): ProviderReadiness =>
  ({ available: status === 'ready', installed, status, label, reason });
const allowed = (project: RuntimeProject | undefined, action: string) => Array.isArray(project?.policy?.allowed_actions) && project.policy.allowed_actions.includes(action);

/** Metadata reads alone never establish a provider connection or dispatch authority. */
export function providerReadiness(id: ProviderId, input: ProviderReadinessInput): ProviderReadiness {
  const { discovery, capabilities: caps, snapshot, project } = input;
  if (input.failed) return result('unavailable', 'Unavailable', 'Local setup could not be verified.');
  if (!discovery || !caps || !snapshot) return result('checking', 'Checking', 'Waiting for local setup metadata.');
  if (discovery.v !== 1 || caps.v !== 1 || snapshot.v !== 1 || !Array.isArray(discovery.providers) || !Number.isSafeInteger(snapshot.revision) || snapshot.revision < 0) {
    return result('unavailable', 'Unavailable', 'Local setup metadata could not be verified.');
  }
  const matches = discovery.providers.filter(item => item.id === id);
  const cli = matches.length === 1 ? matches[0] : undefined;
  const installed = cli?.installed === true && typeof cli.binaryPath === 'string' && cli.binaryPath.startsWith('/') && cli.binaryPath.length <= 4096 && !/[\u0000-\u001f\u007f]/.test(cli.binaryPath);
  if (!installed) return result('not_detected', 'Not detected', 'No verified local executable was found.');
  if (id !== 'codex') return result('unsupported', 'No adapter', 'Executable found. Sidequest has no supported dispatch adapter for this provider.', true);
  if (snapshot.stopped !== false) return result('unavailable', 'Unavailable', 'Task dispatch is stopped.', true);
  if (caps.codex?.host_enabled !== true) return result('unavailable', 'Unavailable', 'Codex execution is disabled by host settings.', true);
  if (caps.codex.catalog_verified !== true || caps.worker_model?.verified !== true ||
      typeof caps.worker_model.id !== 'string' || !caps.worker_model.id.trim() ||
      typeof caps.worker_model.effort !== 'string' || !caps.worker_model.effort.trim()) {
    return result('unavailable', 'Unavailable', 'The configured model and effort are not freshly verified.', true);
  }
  if (caps.codex.usd_cost_enforced !== true) return result('unavailable', 'Unavailable', 'This host cannot enforce the required USD limit.', true);
  // The runtime exposes true features only after host consent and fresh execution verification.
  if (caps.codex.state !== 'available' || caps.features?.coding !== true || caps.features.codex_session !== true) {
    return result('unavailable', 'Unavailable', 'The runtime has not verified execution readiness and host consent.', true);
  }
  if (!project || project.status !== 'active' || !snapshot.projects?.some(item => item.id === project.id)) return result('unavailable', 'Unavailable', 'Choose an active registered repository.', true);
  if (!allowed(project, 'read_repo') || !allowed(project, 'run_checks')) return result('unavailable', 'Unavailable', 'The repository does not permit scoped coding tasks.', true);
  if (!allowed(project, 'propose_patch')) return result('permission_needed', 'Permission needed', 'Allow candidate proposals explicitly for this repository.', true);
  return result('ready', 'Ready', 'Verified runtime readiness. Submitting and launching remain separate explicit actions.', true);
}
