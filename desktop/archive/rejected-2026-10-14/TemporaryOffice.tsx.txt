import {Canvas} from '@react-three/fiber';
import {Html,OrbitControls,RoundedBox} from '@react-three/drei';
import {useRef,type ReactNode} from 'react';
import type {OrbitControls as Controls} from 'three-stdlib';
import {CameraRig,MonitorProjection,StationMonitor} from './OfficeScene';
import type {OfficeBindings} from './office-bindings';
import {UsageTankScene} from './UsageTank';

const desks=[[-2.5,1.55],[0,1.55],[2.5,1.55],[-2.5,-1.15],[0,-1.15],[2.5,-1.15]] as const;
export const temporaryBindings:OfficeBindings={modelUrl:'/office/office.glb',overview:{position:[8,7.4,10],target:[0,.7,0]},stations:desks.map(([x,z],i)=>({id:i===0?'repository':`computer-${i+1}`,label:i===0?'Repository computer':`Computer ${String(i+1).padStart(2,'0')}`,anchor:[x,1.35,z-.17],rotation:[0,0,0],screenSize:[.86,.48],focus:{position:[x,1.55,z+1.3],target:[x,1.35,z-.17]}}))};
function Box({position,size,color,roughness=.8}:{position:[number,number,number];size:[number,number,number];color:string;roughness?:number}){return <mesh position={position} castShadow receiveShadow><boxGeometry args={size}/><meshStandardMaterial color={color} roughness={roughness}/></mesh>;}
function Plant({position}:{position:[number,number,number]}){return <group position={position}><mesh position={[0,.2,0]} castShadow><cylinderGeometry args={[.23,.18,.4,16]}/><meshStandardMaterial color="#b27652"/></mesh><mesh position={[0,.75,0]} castShadow><sphereGeometry args={[.32,12,8]}/><meshStandardMaterial color="#4f7157" roughness={1}/></mesh><mesh position={[.19,.63,.07]} castShadow><sphereGeometry args={[.25,12,8]}/><meshStandardMaterial color="#6d8a60" roughness={1}/></mesh><mesh position={[-.14,.57,-.06]} castShadow><sphereGeometry args={[.25,12,8]}/><meshStandardMaterial color="#3d624c" roughness={1}/></mesh><Box position={[0,.45,0]} size={[.035,.55,.035]} color="#5c4a32"/></group>;}
function Desk({x,z,index}:{x:number;z:number;index:number}){return <group position={[x,0,z]}>
  <RoundedBox args={[1.85,.12,.95]} radius={.045} smoothness={2} position={[0,.87,0]} castShadow receiveShadow><meshStandardMaterial color={index%2?'#c9af88':'#d5bd99'} roughness={.75}/></RoundedBox>
  {[-.78,.78].flatMap(lx=>[-.34,.34].map(lz=><Box key={`${lx}:${lz}`} position={[lx,.42,lz]} size={[.055,.82,.055]} color="#39413b"/>))}
  <Box position={[0,1.35,-.22]} size={[.98,.6,.065]} color="#222c2a"/>
  <Box position={[0,1.05,-.23]} size={[.065,.23,.07]} color="#28312d"/>
  <RoundedBox args={[.37,.035,.23]} radius={.015} position={[0,.965,-.19]}><meshStandardMaterial color="#303a34"/></RoundedBox>
  <Box position={[0,.953,.23]} size={[.62,.035,.19]} color="#444e46"/>
  <RoundedBox args={[.52,.095,.5]} radius={.06} position={[0,.52,.77]} castShadow><meshStandardMaterial color={index%2?'#668078':'#818969'} roughness={1}/></RoundedBox>
  <RoundedBox args={[.5,.55,.09]} radius={.06} position={[0,.83,.99]} castShadow><meshStandardMaterial color={index%2?'#668078':'#818969'} roughness={1}/></RoundedBox>
  <Box position={[0,.27,.8]} size={[.065,.48,.065]} color="#313c35"/><Box position={[0,.06,.8]} size={[.46,.055,.46]} color="#313c35"/>
  <mesh position={[.66,.988,-.13]} castShadow><cylinderGeometry args={[.085,.075,.18,16]}/><meshStandardMaterial color="#b78558"/></mesh>
  <Box position={[-.68,.965,.2]} size={[.25,.035,.3]} color="#e6d9bd"/>
</group>;}
export default function TemporaryOffice({selectedStationId,onSelectStation,onSelectBoard,childrenForStation,onMonitorContainer,workElement,reducedMotion,active}:{selectedStationId:string|null;onSelectStation:(id:string)=>void;onSelectBoard:()=>void;childrenForStation:(id:string)=>ReactNode;onMonitorContainer?:(id:string,node:HTMLDivElement|null)=>void;workElement?:React.RefObject<HTMLDivElement|null>;reducedMotion:boolean;active:boolean}){
 const controls=useRef<Controls|null>(null);
 return <Canvas className="temporary-office-canvas" role="group" aria-label="Temporary interactive office" shadows="soft" frameloop={active?'demand':'never'} dpr={[1,1.5]} camera={{position:temporaryBindings.overview.position,fov:38,near:.1,far:60}} gl={{antialias:true}}>
  <color attach="background" args={['#182321']}/><ambientLight intensity={.65}/><hemisphereLight args={['#e4ede2','#6b5741',1.35]}/><directionalLight position={[-3,8,4]} intensity={2.6} color="#fff0d3" castShadow shadow-mapSize={[2048,2048]} shadow-camera-left={-7} shadow-camera-right={7} shadow-camera-top={7} shadow-camera-bottom={-7} shadow-normalBias={.025}/>
  <Box position={[0,-.12,0]} size={[8.9,.24,7.6]} color="#8d7657"/>
  {Array.from({length:29},(_,i)=><Box key={i} position={[-4.34+i*.31,.012,0]} size={[.302,.025,7.45]} color={i%3===0?'#ae9572':i%3===1?'#b89f7c':'#b39a77'}/>)}
  <Box position={[0,1.5,-3.7]} size={[8.9,3,.14]} color="#c8c8b6"/><Box position={[-4.4,1.5,0]} size={[.14,3,7.6]} color="#babfad"/>
  <Box position={[0,.045,.1]} size={[2.1,.04,6.3]} color="#5b7167"/>
  <Box position={[-4.31,1.75,.5]} size={[.07,1.8,3.5]} color="#e0dfd0"/><Box position={[-4.26,1.75,.5]} size={[.035,1.62,3.32]} color="#809c9b"/>
  {[-.58,1.55].map(z=><Box key={z} position={[-4.2,1.75,z]} size={[.08,1.74,.05]} color="#ebe9dc"/>)}<Box position={[-4.2,1.75,.5]} size={[.08,.06,3.4]} color="#ebe9dc"/>
  {desks.map(([x,z],i)=><Desk key={i} x={x} z={z} index={i}/>)}
  {temporaryBindings.stations.map(station=><StationMonitor key={station.id} station={station} selected={station.id===selectedStationId} onSelectStation={onSelectStation} childrenForStation={childrenForStation} onMonitorContainer={onMonitorContainer}/>)}
  <group position={[-2.35,1.83,-3.57]} onClick={event=>{event.stopPropagation();onSelectBoard();}}><Box position={[0,0,0]} size={[2.25,1.25,.09]} color="#3f5149"/>{[-.7,0,.7].map((x,i)=><Box key={x} position={[x,.05,.065]} size={[.53,.7,.018]} color={['#d3b788','#bac5b2','#ded6be'][i]}/>)}<Html position={[0,.5,.08]} center transform distanceFactor={2.5}><button className="office-board-button" onClick={onSelectBoard}>Jobs board</button></Html></group>
  <Box position={[2.8,.5,-3.1]} size={[2.2,.95,.6]} color="#788577"/><Box position={[2.8,1,-3.1]} size={[2.25,.08,.63]} color="#dfd0af"/>{[2.24,2.8,3.36].map(x=><Box key={x} position={[x,.6,-2.79]} size={[.49,.6,.024]} color="#697767"/>)}
  <Plant position={[-3.65,0,-2.95]}/><Plant position={[3.8,0,3]}/>
  <group position={[3.8,.83,-2.6]}><UsageTankScene/></group>
  <OrbitControls ref={controls} makeDefault enableDamping={false} enabled={active&&selectedStationId===null} minDistance={selectedStationId ? 0.2 : 5} maxDistance={19} maxPolarAngle={Math.PI*.48} target={temporaryBindings.overview.target}/>
  <CameraRig bindings={temporaryBindings} selectedStationId={selectedStationId} reducedMotion={reducedMotion} active={active} controlsRef={controls}/>
  <MonitorProjection station={temporaryBindings.stations.find(item=>item.id===selectedStationId)} element={workElement} active={active}/>
 </Canvas>;
}
