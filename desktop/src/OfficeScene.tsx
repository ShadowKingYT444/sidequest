import React, {
  Component,
  memo,
  Suspense,
  useEffect,
  useLayoutEffect,
  useRef,
  useMemo,
  type ErrorInfo,
  type ReactNode,
} from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import { ACESFilmicToneMapping, Box3, CanvasTexture, DirectionalLight, DoubleSide, Euler, LinearFilter, MathUtils, Mesh, SRGBColorSpace, Vector3 as ThreeVector3, type Object3D } from "three";
import OriginalActors, { type OriginalActorState } from "./OriginalActors";
import type { GLTFLoader, OrbitControls as OrbitControlsImpl } from "three-stdlib";
import { validateOfficeResourceUrl } from "./office-bindings";
import type { OfficeBindings, OfficeStationBinding, Vector3 } from "./office-bindings";
import type {OfficeNotification} from './notifications';
import {isSoftwareRenderer} from './graphics';

export interface OfficeSceneProps {
  bindings: OfficeBindings;
  selectedStationId: string | null;
  onSelectStation: (id: string) => void;
  onSelectBoard?: () => void;
  onSelectWorkstation?: (id: string) => void;
  onSelectActor?: (id: string, sceneId?: string) => void;
  contextualCard?: {stationId:string;kind:'actor'|'workstation';sceneId?:string|null;element:React.RefObject<HTMLDivElement|null>};
  boardSelected?: boolean;
  workElement?:React.RefObject<HTMLDivElement|null>;
  reducedMotion: boolean;
  active: boolean;
  onError?: (error: Error) => void;
  onActorState?: (state: OriginalActorState) => void;
  stationBadges?: ReadonlyMap<string,OfficeNotification>;
  onNotification?: (notification:OfficeNotification)=>void;
}

interface OfficeModelProps {
  url: OfficeBindings["modelUrl"];
  onSelectWorkstation?: (id: string) => void;
}

function OfficeModel({ url, onSelectWorkstation }: OfficeModelProps) {
  const gltf = useGLTF(url, false, false, configureOfficeAssetLoader);
  const {gl,invalidate}=useThree();
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
    gltf.scene.traverse(object=>{if(object instanceof Mesh){const materials=Array.isArray(object.material)?object.material:[object.material];object.castShadow=!materials.some(material=>material.name==='Architectural clear glass');object.receiveShadow=true;}});
    if(light.current){light.current.target.position.set(0,1,-2);light.current.target.updateMatrixWorld();}
    gl.shadowMap.needsUpdate=true;invalidate();
  },[gltf.scene,bounds,gl,invalidate]);
  // Keep the imported scene intact: bindings add interaction surfaces around it.
  return <><primitive object={gltf.scene} dispose={null}/>{onSelectWorkstation&&pickBounds.map(pick=><mesh key={pick.id} matrixAutoUpdate={false} matrix={pick.object.matrixWorld.clone()} userData={{workstationPicker:pick.id}} onClick={event=>{
    const specific=event.intersections.some(hit=>{let node:Object3D|null=hit.object;while(node){if(node.userData.monitorStation||node.userData.actorReferenceStation)return true;node=node.parent;}return false;});
    if(specific)return;event.stopPropagation();onSelectWorkstation(pick.id);
  }}><boxGeometry args={pick.size}/><meshBasicMaterial transparent opacity={0} depthWrite={false}/></mesh>)}<directionalLight ref={light} position={[-24,10,14]} color="#ffe1b5" intensity={2.2} castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-radius} shadow-camera-right={radius} shadow-camera-top={radius} shadow-camera-bottom={-radius} shadow-camera-near={.1} shadow-camera-far={radius*5} shadow-normalBias={.006}/></>;
}

function configureOfficeAssetLoader(loader: GLTFLoader) {
  loader.manager.setURLModifier((resourceUrl) => validateOfficeResourceUrl(resourceUrl, window.location.href));
}

export function clearOfficeModelCache() { useGLTF.clear('/office/office.glb'); }

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

function monitorPose(station:OfficeStationBinding,aspect:number){
  const target=asThreeVector(station.focus.target);
  const direction=asThreeVector(station.focus.position).sub(target);
  // Fit the supplied screen in both dimensions, retaining its authored viewing side.
  const tangent=Math.tan(MathUtils.degToRad(35)/2);
  const distance=Math.max(direction.length(),1.12*Math.max(station.screenSize[1]/(2*tangent),station.screenSize[0]/(2*tangent*Math.max(.1,aspect))));
  return {position:target.clone().add(direction.normalize().multiplyScalar(distance)),target};
}

// Keep the selected application UI in its original React root. The world scene
// supplies only projection math; secondary HTML roots never own a full editor.
export function MonitorProjection({station,element,active}:{station?:OfficeStationBinding;element?:React.RefObject<HTMLDivElement|null>;active:boolean}){
  const {camera,size,invalidate}=useThree();
  useEffect(()=>{invalidate();},[station,element,active,invalidate]);
  useFrame(()=>{
    const node=element?.current;if(!node||!station||!active)return;
    const ready=camera.position.distanceTo(monitorPose(station,size.width/size.height).position)<.015;
    const corners=[[-1,-1],[1,-1],[-1,1],[1,1]].map(([x,y])=>new ThreeVector3(x*station.screenSize[0]/2,y*station.screenSize[1]/2,.01).applyEuler(new Euler(...station.rotation)).add(asThreeVector(station.anchor)).project(camera));
    const xs=corners.map(point=>(point.x+1)*size.width/2),ys=corners.map(point=>(1-point.y)*size.height/2);
    const left=Math.min(...xs),top=Math.min(...ys),width=Math.max(...xs)-left,height=Math.max(...ys)-top;
    node.style.transform=`translate(${left}px,${top}px) scale(${width/640},${height/360})`;
    node.style.visibility=ready&&width>0&&height>0?'visible':'hidden';
  });
  return null;
}

function ContextCardProjection({card,bindings}:{card?:OfficeSceneProps['contextualCard'];bindings:OfficeBindings}){
  const {camera,size,scene}=useThree();
  useLayoutEffect(()=>{
    if(!card?.element.current)return;
    const host=card.element.current;
    let watched:HTMLElement|null=null;
    const resize=new ResizeObserver(()=>position());
    const position=()=>{
      const node=host.matches('.object-modal')?host:host.querySelector<HTMLElement>('.provider-picker,.station-launcher');
      if(!node)return;
      if(watched!==node){resize.disconnect();resize.observe(node);watched=node;}
      const station=bindings.stations.find(item=>item.id===card.stationId);
      if(!station)return;
      const point=asThreeVector(station.anchor);
      let object=card.kind==='workstation'?scene.getObjectByName(`Desk_${card.stationId}__PickBounds.001`):card.sceneId?scene.getObjectByName(card.sceneId):undefined;
      if(!object&&card.kind==='actor')scene.traverse(candidate=>{if(!object&&candidate.userData.actorReferenceStation===card.stationId)object=candidate.children[0];});
      if(object){object.getWorldPosition(point);if(card.kind==='actor')point.y+=1.1;}
      point.project(camera);
      const width=node.offsetWidth,height=node.offsetHeight;
      const left=size.width<600?(size.width-width)/2:Math.max(12,Math.min(size.width-width-12,(point.x+1)*size.width/2+24));
      const top=size.width<600?Math.max(12,size.height-height-12):Math.max(12,Math.min(size.height-height-12,(1-point.y)*size.height/2-height*.3));
      node.style.left=`${left}px`;node.style.top=`${top}px`;
    };
    const mutation=new MutationObserver(position);mutation.observe(host,{childList:true,subtree:true});
    position();
    return()=>{mutation.disconnect();resize.disconnect();};
  },[card,camera,scene,size.width,size.height,bindings]);
  return null;
}

export function CameraRig({
  bindings,
  selectedStationId,
  reducedMotion,
  active,
  controlsRef,
}: CameraRigProps) {
  const { camera, invalidate, size, gl } = useThree();
  const softwareRendering = useMemo(() => isSoftwareRenderer(gl.getContext()), [gl]);
  const instantMotion = reducedMotion || softwareRendering;
  const transition = useRef<CameraTransition | null>(null);
  const previousStation=useRef<string|null>(null),initialized=useRef(false);
  const returningToOffice=useRef(false);
  const officePose=useRef({position:asThreeVector(bindings.overview.position),target:asThreeVector(bindings.overview.target)});
  const selectedStation = bindings.stations.find((item) => item.id === selectedStationId);
  const pose=useMemo(()=>selectedStation?monitorPose(selectedStation,size.width/size.height):null,[selectedStation,size.width,size.height]);
  useEffect(()=>{
    const controls=controlsRef.current;const publish=()=>{gl.domElement.dataset.cameraPosition=JSON.stringify(camera.position.toArray());gl.domElement.dataset.cameraTarget=JSON.stringify((controls?.target??officePose.current.target).toArray());};
    controls?.addEventListener('change',publish);publish();return()=>controls?.removeEventListener('change',publish);
  },[camera,controlsRef,gl]);

  useEffect(() => {
    if (!active) return;
    gl.domElement.dataset.cameraMotion = softwareRendering ? 'instant-software' : reducedMotion ? 'instant-reduced-motion' : 'animated';
    const controls = controlsRef.current;
    if(selectedStation&&!previousStation.current&&initialized.current&&!returningToOffice.current){officePose.current={position:camera.position.clone(),target:controls?.target.clone()??asThreeVector(bindings.overview.target)};}
    if(!selectedStation&&!previousStation.current&&initialized.current)return;
    returningToOffice.current=!selectedStation&&!!previousStation.current;
    const toPosition=(pose??officePose.current).position.clone();
    const toTarget=(pose??officePose.current).target.clone();
    previousStation.current=selectedStation?.id??null;initialized.current=true;

    if (instantMotion) {
      camera.position.copy(toPosition);
      camera.lookAt(toTarget);
      if (controls) {
        controls.target.copy(toTarget);
        controls.update();
      }
      transition.current = null;
      returningToOffice.current=false;
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
  }, [active, camera, controlsRef, invalidate, pose, instantMotion, reducedMotion, softwareRendering, gl, selectedStation, bindings.overview.target]);

  useFrame((_, delta) => {
    const current = transition.current;
    if (!active) return;
    if(current){

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
    else {transition.current = null;returningToOffice.current=false;}
    }
    gl.domElement.dataset.renderFrameCount=String(Number(gl.domElement.dataset.renderFrameCount??0)+1);
    gl.domElement.dataset.cameraPosition=JSON.stringify(camera.position.toArray());
    gl.domElement.dataset.cameraTarget=JSON.stringify((controlsRef.current?.target??officePose.current.target).toArray());
  });

  return null;
}

/** Render the supplied office model and bind station interaction to mapped monitors. */
function ContextControls({controlsRef,enabled,world}:{controlsRef:React.RefObject<OrbitControlsImpl|null>;enabled:boolean;world:ReactNode}) {
  const gl=useThree(state=>state.gl);
  useLayoutEffect(()=>{
    // Lock interaction without invalidating the static scene. Reapply after
    // a world commit so the controls primitive cannot override a card's lock.
    if(controlsRef.current)controlsRef.current.enabled=enabled;
    gl.domElement.dataset.officeControlsEnabled=String(enabled);
  },[controlsRef,enabled,world,gl]);
  return null;
}

function StaticShadows() {
  const {gl,invalidate}=useThree();
  useLayoutEffect(()=>{
    const previous=gl.shadowMap.autoUpdate;
    // Original room, lights and sampled actors are static. Camera/UI updates
    // must not redraw their six-million-vertex shadow map every frame.
    gl.shadowMap.autoUpdate=false;
    const refresh=()=>{gl.shadowMap.needsUpdate=true;invalidate();};
    refresh();gl.domElement.addEventListener('webglcontextrestored',refresh);
    return()=>{gl.shadowMap.autoUpdate=previous;gl.domElement.removeEventListener('webglcontextrestored',refresh);};
  },[gl,invalidate]);
  return null;
}

function SceneMetrics() {
  const {gl}=useThree();
  useLayoutEffect(()=>{
    if (!import.meta.env.DEV) return;
    const render=gl.render, shadowRender=gl.shadowMap.render;
    gl.render=function(...args){const start=performance.now();try{return render.apply(this,args);}finally{performance.measure('sidequest:render',{start,end:performance.now()});}};
    gl.shadowMap.render=function(...args){
      const update=this.enabled&&(this.autoUpdate||this.needsUpdate),start=performance.now();
      try{return shadowRender.apply(this,args);}finally{
        if(update){gl.domElement.dataset.shadowPasses=String(Number(gl.domElement.dataset.shadowPasses??0)+1);performance.measure('sidequest:shadow-render',{start,end:performance.now()});}
      }
    };
    return()=>{gl.render=render;gl.shadowMap.render=shadowRender;};
  },[gl]);
  return null;
}

export function OfficeScene({
  bindings,
  selectedStationId,
  onSelectStation,
  onSelectBoard,
  onSelectWorkstation,
  onSelectActor,
  contextualCard,
  boardSelected=false,
  workElement,
  reducedMotion,
  active,
  onError,
  onActorState,
  stationBadges,
  onNotification,
}: OfficeSceneProps) {
  const controlsRef = useRef<OrbitControlsImpl | null>(null);
  const viewBindings=useMemo(()=>({...bindings,overview:{target:[1,-.3,-3.8] as Vector3,position:[11.5,8.5,12] as Vector3}}),[bindings]);

  // HTML cards and control locks do not alter any world pixels. Keep this
  // subtree stable until geometry, camera, visibility or recorded badges change.
  const world=useMemo(()=><>
      <StaticShadows/>
      <SceneMetrics/>
      <color attach="background" args={["#d8e1e7"]} />
      <ambientLight intensity={0.25} />
      <hemisphereLight args={['#cfe3fa','#8a6342',1.25]}/>
      <LoaderErrorBoundary onError={onError}>
        <Suspense fallback={null}>
          <OfficeModel url={bindings.modelUrl} onSelectWorkstation={onSelectWorkstation} />
        </Suspense>
      </LoaderErrorBoundary>
      <OriginalActors active={active} onState={onActorState} onSelectActor={onSelectActor} stationBadges={stationBadges} onNotification={onNotification}/>
      {bindings.stations.map((station) => (
        <StationMonitor
          key={station.id}
          station={station}
          selected={selectedStationId === station.id}
          onSelectStation={onSelectStation}
        />
      ))}
      {bindings.board&&onSelectBoard&&<group position={bindings.board.anchor} rotation={bindings.board.rotation}><mesh onClick={event=>{event.stopPropagation();onSelectBoard();}}><planeGeometry args={bindings.board.size}/><meshBasicMaterial transparent opacity={boardSelected?.12:0} color="#699eff" depthWrite={false} side={DoubleSide}/></mesh></group>}
      <OrbitControls
        ref={controlsRef}
        makeDefault
        enabled={false}
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
    </>,[bindings,viewBindings,selectedStationId,boardSelected,workElement,reducedMotion,active,onError,onActorState,stationBadges,onNotification,onSelectStation,onSelectBoard,onSelectWorkstation,onSelectActor]);

  return (
    <Canvas className="office-canvas"
      frameloop={active ? "demand" : "never"}
      dpr={[1, 1.5]}
      camera={{ position: viewBindings.overview.position, fov: 35, near: 0.05, far: 1000 }}
      gl={{ antialias: true, alpha: false, toneMapping:ACESFilmicToneMapping, toneMappingExposure:1.2 }}
      shadows="percentage"
    >
      {world}
      <ContextControls controlsRef={controlsRef} enabled={active && !selectedStationId && !contextualCard && !boardSelected} world={world}/>
      <ContextCardProjection card={contextualCard} bindings={bindings}/>
    </Canvas>
  );
}

// Local editor/draft state must not invalidate the independent demand-rendered scene.
export default memo(OfficeScene);
