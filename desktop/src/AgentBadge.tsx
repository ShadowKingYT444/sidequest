import { useEffect, useMemo } from 'react';
import { useThree } from '@react-three/fiber';
import { CanvasTexture, SRGBColorSpace } from 'three';
import type { OfficeNotification } from './notifications';

export interface AgentBadgeProps {
  kind: OfficeNotification['kind'];
  label: string;
  position: [number, number, number];
  onClick?: () => void;
}

function badgeTexture(kind: OfficeNotification['kind']) {
  const canvas = document.createElement('canvas'); canvas.width = canvas.height = 128;
  const context = canvas.getContext('2d');
  if (!context) throw new Error('Agent status texture is unavailable.');
  context.beginPath(); context.arc(64, 64, 51, 0, Math.PI * 2);
  context.fillStyle = kind === 'completed' ? '#147d54' : '#bc3c42'; context.fill();
  context.lineWidth = 5; context.strokeStyle = '#f7faf8'; context.stroke();
  context.strokeStyle = '#ffffff'; context.fillStyle = '#ffffff'; context.lineCap = 'round'; context.lineJoin = 'round'; context.lineWidth = 10;
  if (kind === 'completed') { context.beginPath(); context.moveTo(38, 64); context.lineTo(56, 82); context.lineTo(91, 46); context.stroke(); }
  else { context.beginPath(); context.moveTo(64, 35); context.lineTo(64, 68); context.stroke(); context.beginPath(); context.arc(64, 88, 5.5, 0, Math.PI * 2); context.fill(); }
  const texture = new CanvasTexture(canvas); texture.colorSpace = SRGBColorSpace; return texture;
}

/** One demand-rendered sprite; semantics also belong in the accessible notification tray. */
export default function AgentBadge({ kind, label, position, onClick }: AgentBadgeProps) {
  const texture = useMemo(() => badgeTexture(kind), [kind]);
  const invalidate = useThree(state => state.invalidate), gl = useThree(state => state.gl);
  useEffect(() => { texture.needsUpdate = true; invalidate(); return () => texture.dispose(); }, [texture, invalidate]);
  return <sprite position={position} scale={[0.5, 0.5, 1]} name={`agent-status-${kind}`} userData={{ notificationKind: kind, accessibleLabel: label }}
    onClick={event => { if (onClick) { event.stopPropagation(); onClick(); } }}
    onPointerOver={event => { if (onClick) { event.stopPropagation(); gl.domElement.style.cursor = 'pointer'; } }}
    onPointerOut={() => { if (onClick) gl.domElement.style.cursor = 'default'; }}>
    <spriteMaterial map={texture} transparent toneMapped={false} depthWrite={false} />
  </sprite>;
}
