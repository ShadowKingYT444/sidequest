import { Html } from "@react-three/drei";
import { DoubleSide } from "three";
import "./UsageTank.css";

export interface UsageReading {
  usedFraction: number | null;
  status: "live" | "stale" | "unknown" | "demo";
  observedAt?: string | null;
  resetAt?: string | null;
  windowLabel?: string;
}

type ReadingStatus = UsageReading["status"];

interface UsageTankProps {
  reading?: UsageReading;
  title?: string;
}

interface TankReadingView {
  status: ReadingStatus;
  fraction: number | null;
  percent: number | null;
  observedLabel: string | null;
  resetLabel: string | null;
  windowLabel: string | null;
}

const UNKNOWN_READING: UsageReading = {
  usedFraction: null,
  status: "unknown",
};

function formatTimestamp(value?: string | null): string | null {
  if (!value) return null;
  const timestamp = new Date(value);
  if (!Number.isFinite(timestamp.getTime())) return null;

  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(timestamp);
}

function getReadingView(reading?: UsageReading): TankReadingView {
  const source = reading ?? UNKNOWN_READING;
  const rawFraction = source.usedFraction;
  const hasFiniteFraction =
    typeof rawFraction === "number" && Number.isFinite(rawFraction);
  const hasKnownValue = source.status !== "unknown" && hasFiniteFraction;
  const fraction = hasKnownValue
    ? Math.max(0, Math.min(1, rawFraction as number))
    : null;
  const status = fraction === null ? "unknown" : source.status;

  return {
    status,
    fraction,
    percent: fraction === null ? null : Math.round(fraction * 100),
    observedLabel: status === "stale" ? formatTimestamp(source.observedAt) : null,
    resetLabel: fraction === null ? null : formatTimestamp(source.resetAt),
    windowLabel: fraction === null ? null : source.windowLabel?.trim() || null,
  };
}

function statusLabel(status: ReadingStatus): string {
  switch (status) {
    case "live":
      return "LIVE";
    case "stale":
      return "STALE";
    case "demo":
      return "DEMO DATA";
    default:
      return "UNKNOWN";
  }
}

function statusClass(status: ReadingStatus): string {
  return `usage-tank-status usage-tank-status--${status}`;
}

export function UsageTank({
  reading,
  title = "Usage tank",
}: UsageTankProps) {
  const view = getReadingView(reading);
  const isUnknown = view.percent === null;
  const fillStyle = view.fraction === null
    ? undefined
    : { height: `${view.fraction * 100}%` };

  return (
    <section className="usage-tank-card" aria-label={title}>
      <header className="usage-tank-header">
        <div>
          <p className="usage-tank-kicker">CAPACITY</p>
          <h2 className="usage-tank-title">{title}</h2>
        </div>
        <span className={statusClass(view.status)}>{statusLabel(view.status)}</span>
      </header>

      <div className="usage-tank-content">
        <div
          className={`usage-tank-vessel${isUnknown ? " is-unknown" : ""}`}
          role={isUnknown ? "img" : "meter"}
          aria-label={isUnknown ? "Usage unknown" : `${view.percent}% used`}
          aria-valuemin={isUnknown ? undefined : 0}
          aria-valuemax={isUnknown ? undefined : 100}
          aria-valuenow={view.percent ?? undefined}
          aria-valuetext={isUnknown ? undefined : `${view.percent}% used`}
        >
          {view.fraction !== null && view.fraction > 0 && (
            <div className="usage-tank-liquid" style={fillStyle} />
          )}
          <div className="usage-tank-glass" />
          <div className="usage-tank-ticks" aria-hidden="true">
            <i />
            <i />
            <i />
            <i />
            <i />
          </div>
          {isUnknown && <span className="usage-tank-question" aria-hidden="true">?</span>}
          <span className="usage-tank-vessel-caption" aria-hidden="true">USED</span>
        </div>

        <div className="usage-tank-reading">
          {isUnknown ? (
            <>
              <p className="usage-tank-value usage-tank-value--unknown">?</p>
              <p className="usage-tank-reading-label">Usage unknown</p>
              <p className="usage-tank-subtext">No reading available</p>
            </>
          ) : (
            <>
              <p className="usage-tank-unit">PERCENT USED</p>
              <p className="usage-tank-value">
                {view.percent}<span>%</span>
              </p>
              {view.windowLabel && (
                <p className="usage-tank-window">{view.windowLabel} window</p>
              )}
              {view.status === "stale" && (
                <p className="usage-tank-subtext usage-tank-observed">
                  Observed {view.observedLabel ?? "time unavailable"}
                </p>
              )}
              {view.status === "demo" && (
                <p className="usage-tank-subtext usage-tank-demo-note">
                  Demonstration reading
                </p>
              )}
              {view.resetLabel && (
                <p className="usage-tank-reset">Resets {view.resetLabel}</p>
              )}
            </>
          )}
        </div>
      </div>

      <footer className="usage-tank-footer">
        <span className="usage-tank-footer-mark" aria-hidden="true" />
        <span>{isUnknown ? "Waiting for a known reading" : view.status === "live" ? "Current usage" : statusLabel(view.status)}</span>
        <span className="usage-tank-footer-window">{view.windowLabel ?? "—"}</span>
      </footer>
    </section>
  );
}

interface UsageTankSceneProps {
  reading?: UsageReading;
}

export function UsageTankScene({ reading }: UsageTankSceneProps) {
  const view = getReadingView(reading);
  const isUnknown = view.fraction === null;
  const isHighUsage = view.fraction !== null && view.fraction >= 0.78;
  const liquidColor = isHighUsage ? "#d6aa61" : "#67a997";
  const liquidHeight = view.fraction === null ? 0 : view.fraction * 1.16;
  const liquidBottom = -0.64;
  const liquidY = liquidBottom + liquidHeight / 2;

  return (
    <group position={[0, 0.125, 0]}>
      {/* The glass column, braces and plinth stay static between data updates. */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.33, 0.33, 1.34, 40, 1, true]} />
        <meshBasicMaterial color="#b5cbbd" transparent opacity={0.16} side={DoubleSide} depthWrite={false} />
      </mesh>

      {!isUnknown && view.fraction !== null && view.fraction > 0 && (
        <mesh position={[0, liquidY, 0]}>
          <cylinderGeometry args={[0.265, 0.265, liquidHeight, 40]} />
          <meshBasicMaterial color={liquidColor} transparent opacity={0.9} />
        </mesh>
      )}

      {view.fraction !== null && view.fraction > 0 && (
        <mesh position={[0, liquidBottom + liquidHeight, 0]}>
          <cylinderGeometry args={[0.265, 0.265, 0.012, 40]} />
          <meshBasicMaterial color={liquidColor} transparent opacity={0.92} />
        </mesh>
      )}

      <mesh position={[0, 0.67, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.35, 0.026, 8, 40]} />
        <meshBasicMaterial color="#d6bc87" />
      </mesh>
      <mesh position={[0, -0.67, 0]} rotation={[Math.PI / 2, 0, 0]}>
        <torusGeometry args={[0.35, 0.026, 8, 40]} />
        <meshBasicMaterial color="#8c9a8e" />
      </mesh>
      <mesh position={[-0.34, 0, 0]}>
        <boxGeometry args={[0.035, 1.36, 0.045]} />
        <meshBasicMaterial color="#a9b4a8" />
      </mesh>
      <mesh position={[0.34, 0, 0]}>
        <boxGeometry args={[0.035, 1.36, 0.045]} />
        <meshBasicMaterial color="#a9b4a8" />
      </mesh>

      {[0.42, 0.21, 0, -0.21, -0.42].map((y) => (
        <mesh key={y} position={[-0.22, y, 0.286]}>
          <boxGeometry args={[0.11, 0.012, 0.01]} />
          <meshBasicMaterial color="#d0d3c4" transparent opacity={0.66} />
        </mesh>
      ))}

      <mesh position={[-0.19, -0.75, 0]}>
        <boxGeometry args={[0.045, 0.25, 0.08]} />
        <meshBasicMaterial color="#7e8d83" />
      </mesh>
      <mesh position={[0.19, -0.75, 0]}>
        <boxGeometry args={[0.045, 0.25, 0.08]} />
        <meshBasicMaterial color="#7e8d83" />
      </mesh>
      <mesh position={[0, -0.91, 0]}>
        <boxGeometry args={[0.52, 0.07, 0.22]} />
        <meshBasicMaterial color="#bca36d" />
      </mesh>

      <Html position={[0, 0.04, 0.34]} center distanceFactor={8} zIndexRange={[1, 1]} style={{ pointerEvents: "none" }}>
        <div
          className={`usage-tank-scene-label${isUnknown ? " is-unknown" : ""}`}
          role={isUnknown ? "img" : "meter"}
          aria-label={isUnknown ? "Usage unknown" : `${view.percent}% used`}
          aria-valuemin={isUnknown ? undefined : 0}
          aria-valuemax={isUnknown ? undefined : 100}
          aria-valuenow={view.percent ?? undefined}
          aria-valuetext={isUnknown ? undefined : `${view.percent}% used`}
        >
          <span className={statusClass(view.status)}>{statusLabel(view.status)}</span>
          {isUnknown ? (
            <strong>?</strong>
          ) : (
            <strong>{view.percent}<small>% USED</small></strong>
          )}
          {isUnknown && <span>Usage unknown</span>}
          {view.status === "stale" && (
            <span>Observed {view.observedLabel ?? "time unavailable"}</span>
          )}
          {view.status === "demo" && <span>Demo reading</span>}
          {view.resetLabel && <span>Resets {view.resetLabel}</span>}
        </div>
      </Html>
    </group>
  );
}

export default UsageTank;
