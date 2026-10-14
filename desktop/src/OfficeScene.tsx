import React, {
  Component,
  Suspense,
  useEffect,
  useRef,
  useMemo,
  type ErrorInfo,
  type MouseEvent,
  type ReactNode,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Html, OrbitControls, useGLTF } from "@react-three/drei";
import { Box3, DirectionalLight, DoubleSide, MathUtils, Mesh, Vector3 as ThreeVector3 } from "three";
import type { GLTFLoader, OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { validateOfficeResourceUrl } from "./office-bindings";
import type { OfficeBindings, OfficeStationBinding, Vector3 } from "./office-bindings";

export interface OfficeSceneProps {
  bindings: OfficeBindings;
  selectedStationId: string | null;
  onSelectStation: (id: string) => void;
  onSelectBoard?: () => void;
  childrenForStation?: (id: string) => ReactNode;
  reducedMotion: boolean;
  active: boolean;
  onError?: (error: Error) => void;
}

interface OfficeModelProps {
  url: OfficeBindings["modelUrl"];
}

function OfficeModel({ url }: OfficeModelProps) {
  const gltf = useGLTF(url, false, true, configureOfficeAssetLoader);
  const light=useRef<DirectionalLight>(null);
  const bounds=useMemo(()=>new Box3().setFromObject(gltf.scene),[gltf.scene]);
  const center=bounds.getCenter(new ThreeVector3());
  const radius=Math.max(1,bounds.getSize(new ThreeVector3()).length()/2);
  useEffect(()=>{
    gltf.scene.traverse(object=>{if(object instanceof Mesh){object.castShadow=true;object.receiveShadow=true;}});
    if(light.current){light.current.target.position.copy(center);light.current.target.updateMatrixWorld();}
  },[gltf.scene,bounds]);
  // Keep the imported scene intact: bindings add interaction surfaces around it.
  return <><primitive object={gltf.scene} dispose={null}/><directionalLight ref={light} position={[center.x+radius*.6,center.y+radius*1.4,center.z+radius*.8]} intensity={0.9} castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-radius} shadow-camera-right={radius} shadow-camera-top={radius} shadow-camera-bottom={-radius} shadow-camera-near={.1} shadow-camera-far={radius*5} shadow-normalBias={.02}/></>;
}

function configureOfficeAssetLoader(loader: GLTFLoader) {
  loader.manager.setURLModifier((resourceUrl) => validateOfficeResourceUrl(resourceUrl, window.location.href));
}

interface ErrorBoundaryProps {
  children: ReactNode;
  onError?: (error: Error) => void;
}

interface ErrorBoundaryState {
  failed: boolean;
}

class LoaderErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { failed: false };

  static getDerivedStateFromError(): ErrorBoundaryState {
    return { failed: true };
  }

  componentDidCatch(error: Error, _info: ErrorInfo) {
    this.props.onError?.(error);
  }

  render() {
    return this.state.failed ? null : this.props.children;
  }
}

interface StationMonitorProps {
  station: OfficeStationBinding;
  selected: boolean;
  onSelectStation: (id: string) => void;
  childrenForStation?: (id: string) => ReactNode;
}

const HTML_SCREEN_PIXELS = { width: 640, height: 360 } as const;

function StationMonitor({
  station,
  selected,
  onSelectStation,
  childrenForStation,
}: StationMonitorProps) {
  const { gl } = useThree();
  const handlePointerEnter = (event: { stopPropagation: () => void }) => {
    event.stopPropagation();
    gl.domElement.style.cursor = "pointer";
  };
  const handlePointerLeave = (event: { stopPropagation: () => void }) => {
    event.stopPropagation();
    gl.domElement.style.cursor = "default";
  };

  const previewClick = (event: MouseEvent<HTMLButtonElement>) => {
    event.stopPropagation();
    onSelectStation(station.id);
  };

  return (
    <group position={station.anchor} rotation={station.rotation}>
      <mesh
        position={[0, 0, 0.002]}
        onClick={(event) => {
          event.stopPropagation();
          onSelectStation(station.id);
        }}
        onPointerOver={handlePointerEnter}
        onPointerOut={handlePointerLeave}
      >
        <planeGeometry args={station.screenSize} />
        <meshBasicMaterial
          transparent
          opacity={0}
          depthWrite={false}
          side={DoubleSide}
        />
      </mesh>
      <group
        position={[0, 0, 0.004]}
        scale={[
          station.screenSize[0] / HTML_SCREEN_PIXELS.width,
          station.screenSize[1] / HTML_SCREEN_PIXELS.height,
          1,
        ]}
      >
        <Html transform center distanceFactor={400} zIndexRange={[1, 1]} occlude style={{ pointerEvents: "auto" }}>
          <div
            style={{
              width: `${HTML_SCREEN_PIXELS.width}px`,
              height: `${HTML_SCREEN_PIXELS.height}px`,
              boxSizing: "border-box",
              overflow: "hidden",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              pointerEvents: "auto",
            }}
          >
            {selected ? (
              childrenForStation?.(station.id) ?? null
            ) : (
              <button
                type="button"
                aria-label={`Open ${station.label}`}
                onClick={previewClick}
                style={{
                  border: "1px solid rgba(255,255,255,.24)",
                  borderRadius: 5,
                  padding: "10px 15px",
                  color: "#eef2f5",
                  background: "rgba(19,26,34,.82)",
                  font: "500 24px/1.25 system-ui, sans-serif",
                  cursor: "pointer",
                }}
              >
                {station.label}
              </button>
            )}
          </div>
        </Html>
      </group>
    </group>
  );
}

interface CameraRigProps {
  bindings: OfficeBindings;
  selectedStationId: string | null;
  reducedMotion: boolean;
  active: boolean;
  controlsRef: React.RefObject<OrbitControlsImpl | null>;
}

interface CameraTransition {
  fromPosition: ThreeVector3;
  fromTarget: ThreeVector3;
  toPosition: ThreeVector3;
  toTarget: ThreeVector3;
  elapsed: number;
}

function asThreeVector(value: Vector3) {
  return new ThreeVector3(value[0], value[1], value[2]);
}

function CameraRig({
  bindings,
  selectedStationId,
  reducedMotion,
  active,
  controlsRef,
}: CameraRigProps) {
  const { camera, invalidate } = useThree();
  const transition = useRef<CameraTransition | null>(null);
  const selectedStation = bindings.stations.find((item) => item.id === selectedStationId);
  const pose = selectedStation?.focus ?? bindings.overview;

  useEffect(() => {
    if (!active) return;
    const controls = controlsRef.current;
    const toPosition = asThreeVector(pose.position);
    const toTarget = asThreeVector(pose.target);

    if (reducedMotion) {
      camera.position.copy(toPosition);
      camera.lookAt(toTarget);
      if (controls) {
        controls.target.copy(toTarget);
        controls.update();
      }
      transition.current = null;
      invalidate();
      return;
    }

    const currentTarget = controls?.target.clone() ?? new ThreeVector3();
    transition.current = {
      fromPosition: camera.position.clone(),
      fromTarget: currentTarget,
      toPosition,
      toTarget,
      elapsed: 0,
    };
    invalidate();
  }, [active, camera, controlsRef, invalidate, pose, reducedMotion]);

  useFrame((_, delta) => {
    const current = transition.current;
    if (!active || !current) return;

    current.elapsed = Math.min(current.elapsed + delta, 0.55);
    const amount = MathUtils.smoothstep(current.elapsed / 0.55, 0, 1);
    camera.position.lerpVectors(current.fromPosition, current.toPosition, amount);
    const controls = controlsRef.current;
    if (controls) {
      controls.target.lerpVectors(current.fromTarget, current.toTarget, amount);
      controls.update();
    } else {
      camera.lookAt(current.fromTarget.clone().lerp(current.toTarget, amount));
    }

    if (current.elapsed < 0.55) invalidate();
    else transition.current = null;
  });

  return null;
}

/** Render the supplied office model and bind station interaction to mapped monitors. */
export function OfficeScene({
  bindings,
  selectedStationId,
  onSelectStation,
  onSelectBoard,
  childrenForStation,
  reducedMotion,
  active,
  onError,
}: OfficeSceneProps) {
  const controlsRef = useRef<OrbitControlsImpl | null>(null);

  return (
    <Canvas
      frameloop={active ? "demand" : "never"}
      dpr={[1, 1.5]}
      camera={{ position: bindings.overview.position, fov: 40, near: 0.05, far: 1000 }}
      gl={{ antialias: true, alpha: false }}
      shadows="soft"
    >
      <color attach="background" args={["#111820"]} />
      <ambientLight intensity={0.72} />
      <LoaderErrorBoundary onError={onError}>
        <Suspense fallback={null}>
          <OfficeModel url={bindings.modelUrl} />
        </Suspense>
      </LoaderErrorBoundary>
      {bindings.stations.map((station) => (
        <StationMonitor
          key={station.id}
          station={station}
          selected={selectedStationId === station.id}
          onSelectStation={onSelectStation}
          childrenForStation={childrenForStation}
        />
      ))}
      {bindings.board&&onSelectBoard&&<group position={bindings.board.anchor} rotation={bindings.board.rotation}><mesh onClick={event=>{event.stopPropagation();onSelectBoard();}}><planeGeometry args={bindings.board.size}/><meshBasicMaterial transparent opacity={0} depthWrite={false} side={DoubleSide}/></mesh></group>}
      <OrbitControls
        ref={controlsRef}
        makeDefault
        enabled={active && !selectedStationId}
        enableDamping={false}
        minDistance={0.25}
        maxDistance={100}
      />
      <CameraRig
        bindings={bindings}
        selectedStationId={selectedStationId}
        reducedMotion={reducedMotion}
        active={active}
        controlsRef={controlsRef}
      />
    </Canvas>
  );
}

export default OfficeScene;
