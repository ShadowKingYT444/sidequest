import React, {
  Component,
  Suspense,
  useEffect,
  useRef,
  useMemo,
  type ErrorInfo,
  type ReactNode,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import { Box3, CanvasTexture, DirectionalLight, DoubleSide, Euler, LinearFilter, MathUtils, Mesh, SRGBColorSpace, Vector3 as ThreeVector3, type Object3D } from "three";
import OriginalActors, { type OriginalActorState } from "./OriginalActors";
import type { GLTFLoader, OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { validateOfficeResourceUrl } from "./office-bindings";
import type { OfficeBindings, OfficeStationBinding, Vector3 } from "./office-bindings";

export interface OfficeSceneProps {
  bindings: OfficeBindings;
  selectedStationId: string | null;
  onSelectStation: (id: string) => void;
  onSelectBoard?: () => void;
  onSelectWorkstation?: (id: string) => void;
  onSelectActor?: (id: string) => void;
  workElement?:React.RefObject<HTMLDivElement|null>;
  reducedMotion: boolean;
  active: boolean;
  onError?: (error: Error) => void;
  onActorState?: (state: OriginalActorState) => void;
}

interface OfficeModelProps {
  url: OfficeBindings["modelUrl"];
  onSelectWorkstation?: (id: string) => void;
}

function OfficeModel({ url, onSelectWorkstation }: OfficeModelProps) {
  const gltf = useGLTF(url, false, false, configureOfficeAssetLoader);
  const light=useRef<DirectionalLight>(null);
  const bounds=useMemo(()=>new Box3().setFromObject(gltf.scene),[gltf.scene]);
  const center=bounds.getCenter(new ThreeVector3());
  const radius=Math.max(1,bounds.getSize(new ThreeVector3()).length()/2);
  const pickBounds=useMemo(()=>{
    const result:{id:string;object:Object3D;size:Vector3}[]=[];
    gltf.scene.updateMatrixWorld(true);
    gltf.scene.traverse(object=>{
      const data=object.userData;
      if(data.anchor_only===true&&data.proxy_shape==='box'&&/^parent_0(?:0[1-9]|1[0-9]|2[0-4])$/.test(data.scene_owner_id)&&Array.isArray(data.proxy_local_size)&&data.proxy_local_size.length===3&&data.proxy_local_size.every((n:unknown)=>typeof n==='number'&&Number.isFinite(n)&&n>0&&n<=4))result.push({id:data.scene_owner_id,object,size:data.proxy_local_size as Vector3});
    });
    return result;
  },[gltf.scene]);
  useEffect(()=>{
    gltf.scene.traverse(object=>{if(object instanceof Mesh){object.castShadow=true;object.receiveShadow=true;}});
    if(light.current){light.current.target.position.copy(center);light.current.target.updateMatrixWorld();}
  },[gltf.scene,bounds]);
  // Keep the imported scene intact: bindings add interaction surfaces around it.
  return <><primitive object={gltf.scene} dispose={null}/>{onSelectWorkstation&&pickBounds.map(pick=><mesh key={pick.id} matrixAutoUpdate={false} matrix={pick.object.matrixWorld.clone()} userData={{workstationPicker:pick.id}} onClick={event=>{
    const specific=event.intersections.some(hit=>{let node:Object3D|null=hit.object;while(node){if(node.userData.monitorStation||node.userData.actorReferenceStation)return true;node=node.parent;}return false;});
    if(specific)return;event.stopPropagation();onSelectWorkstation(pick.id);
  }}><boxGeometry args={pick.size}/><meshBasicMaterial transparent opacity={0} depthWrite={false}/></mesh>)}<directionalLight ref={light} position={[center.x+radius*.6,center.y+radius*1.4,center.z+radius*.8]} intensity={1.4} castShadow shadow-mapSize={[1024,1024]} shadow-camera-left={-radius} shadow-camera-right={radius} shadow-camera-top={radius} shadow-camera-bottom={-radius} shadow-camera-near={.1} shadow-camera-far={radius*5} shadow-normalBias={.02}/></>;
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
}

const HTML_SCREEN_PIXELS = { width: 640, height: 360 } as const;

export function StationMonitor({
  station,
  selected,
  onSelectStation,
}: StationMonitorProps) {
  const preview = useMemo(() => {
    const canvas = document.createElement('canvas');
    canvas.width = HTML_SCREEN_PIXELS.width;
    canvas.height = HTML_SCREEN_PIXELS.height;
    const context = canvas.getContext('2d');
    if (context) {
      context.fillStyle = '#15191f'; context.fillRect(0, 0, canvas.width, canvas.height);
      context.fillStyle = '#e7eaee'; context.font = '500 40px system-ui, sans-serif';
      context.textAlign = 'center'; context.fillText(station.label, 320, 166);
      context.fillStyle = '#aeb6c0'; context.font = '24px system-ui, sans-serif';
      context.fillText('Read-only files and results', 320, 218);
    }
    const texture = new CanvasTexture(canvas);
    texture.colorSpace = SRGBColorSpace;
    texture.minFilter = LinearFilter;
    return texture;
  }, [station.label]);
  useEffect(() => { preview.needsUpdate = true; return () => preview.dispose(); }, [preview]);
  const { gl } = useThree();
  const handlePointerEnter = (event: { stopPropagation: () => void }) => {
    event.stopPropagation();
    gl.domElement.style.cursor = "pointer";
  };
  const handlePointerLeave = (event: { stopPropagation: () => void }) => {
    event.stopPropagation();
    gl.domElement.style.cursor = "default";
  };

  return (
    <group position={station.anchor} rotation={station.rotation} userData={{monitorStation:station.id}}>
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
      {!selected && <mesh position={[0, 0, 0.004]} onClick={event => { event.stopPropagation(); onSelectStation(station.id); }} onPointerOver={handlePointerEnter} onPointerOut={handlePointerLeave}>
        <planeGeometry args={station.screenSize} />
        <meshBasicMaterial map={preview} side={DoubleSide} toneMapped={false} />
      </mesh>}
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

// Keep the selected application UI in its original React root. The world scene
// supplies only projection math; secondary HTML roots never own a full editor.
export function MonitorProjection({station,element,active}:{station?:OfficeStationBinding;element?:React.RefObject<HTMLDivElement|null>;active:boolean}){
  const {camera,size,invalidate}=useThree();
  useEffect(()=>{invalidate();},[station,element,active,invalidate]);
  useFrame(()=>{
    const node=element?.current;if(!node||!station||!active)return;
    const ready=camera.position.distanceTo(asThreeVector(station.focus.position))<.15;
    const corners=[[-1,-1],[1,-1],[-1,1],[1,1]].map(([x,y])=>new ThreeVector3(x*station.screenSize[0]/2,y*station.screenSize[1]/2,.01).applyEuler(new Euler(...station.rotation)).add(asThreeVector(station.anchor)).project(camera));
    const xs=corners.map(point=>(point.x+1)*size.width/2),ys=corners.map(point=>(1-point.y)*size.height/2);
    const left=Math.min(...xs),top=Math.min(...ys),width=Math.max(...xs)-left,height=Math.max(...ys)-top;
    node.style.transform=`translate(${left}px,${top}px) scale(${width/640},${height/360})`;
    node.style.visibility=ready&&width>0&&height>0?'visible':'hidden';
  });
  return null;
}

export function CameraRig({
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
  onSelectWorkstation,
  onSelectActor,
  workElement,
  reducedMotion,
  active,
  onError,
  onActorState,
}: OfficeSceneProps) {
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const viewBindings=useMemo(()=>({...bindings,overview:{target:bindings.overview.target,position:bindings.overview.position.map((n,i)=>bindings.overview.target[i]+(n-bindings.overview.target[i])*(i===1?.62:.72)) as Vector3}}),[bindings]);

  return (
    <Canvas className="office-canvas"
      frameloop={active ? "demand" : "never"}
      dpr={[1, 1.5]}
      camera={{ position: viewBindings.overview.position, fov: 40, near: 0.05, far: 1000 }}
      gl={{ antialias: true, alpha: false }}
      shadows="percentage"
    >
      <color attach="background" args={["#111820"]} />
      <ambientLight intensity={0.95} />
      <LoaderErrorBoundary onError={onError}>
        <Suspense fallback={null}>
          <OfficeModel url={bindings.modelUrl} onSelectWorkstation={onSelectWorkstation} />
        </Suspense>
      </LoaderErrorBoundary>
      <OriginalActors active={active} onState={onActorState} onSelectActor={onSelectActor} />
      {bindings.stations.map((station) => (
        <StationMonitor
          key={station.id}
          station={station}
          selected={selectedStationId === station.id}
          onSelectStation={onSelectStation}
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
        bindings={viewBindings}
        selectedStationId={selectedStationId}
        reducedMotion={reducedMotion}
        active={active}
        controlsRef={controlsRef}
      />
      <MonitorProjection station={bindings.stations.find(item=>item.id===selectedStationId)} element={workElement} active={active}/>
    </Canvas>
  );
}

export default OfficeScene;
