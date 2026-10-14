import { Component, Suspense, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { useThree } from "@react-three/fiber";
import { useGLTF } from "@react-three/drei";
import { AnimationMixer, Bone, Group, Matrix4, Mesh, MeshStandardMaterial, Skeleton, SkinnedMesh, TextureLoader, Vector3, type AnimationClip, type Material, type Object3D } from "three";
import { clone as cloneSkeleton } from "three/examples/jsm/utils/SkeletonUtils.js";
import type { GLTF, GLTFLoader, GLTFParser } from "three-stdlib";
import { validateOfficeResourceUrl } from "./office-bindings";
import AgentBadge from './AgentBadge';
import type {OfficeNotification} from './notifications';

const ACTORS_URL = "/office/actors.json";
const PROFILES_URL = "/office/caps/attachment-profiles.json";
const MAX_MANIFEST_BYTES = 256 * 1024;
const STATIC_POSE_SECONDS = 0.5;
type MatrixRows = [number[], number[], number[], number[]];
type PoseClip = "Idle" | "Typing" | "Point" | "Walk";

interface HumanAsset {
  assetId: string;
  url: string;
  variant: string;
  capReady: boolean;
}

interface HeadAccessory {
  fitBaseUrl: string;
  identityCapUrl: string;
  variant: string;
}

export interface OriginalActorInstance {
  sceneId: string;
  stationId: string;
  assetUrl: string;
  worldMatrixGltfRows: MatrixRows;
  clip: PoseClip;
  headAccessory: HeadAccessory | null;
  runtimeConnected: false;
}

export interface OriginalActorsManifest {
  instances: OriginalActorInstance[];
  humanVariantCount: number;
}

export interface OriginalActorState {
  status: "loading" | "ready" | "error";
  stagedActorCount: number;
  loadedActorCount: number;
  runtimeConnected: false;
}

export interface OriginalActorsProps {
  active: boolean;
  onState?: (state: OriginalActorState) => void;
  onError?: (error: Error) => void;
  onSelectActor?: (stationId: string, sceneId?: string) => void;
  stationBadges?: ReadonlyMap<string,OfficeNotification>;
  onNotification?: (notification:OfficeNotification)=>void;
}

function record(value: unknown, field: string): Record<string, unknown> {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new Error(`${field} must be an object.`);
  return value as Record<string, unknown>;
}

function items(value: unknown, field: string, maximum: number): unknown[] {
  if (!Array.isArray(value) || value.length === 0 || value.length > maximum) throw new Error(`${field} exceeds the bounded actor manifest.`);
  return value;
}

function identifier(value: unknown, field: string): string {
  if (typeof value !== "string" || !/^[A-Za-z0-9_]{1,96}$/.test(value)) throw new Error(`${field} is invalid.`);
  return value;
}

function assetUrl(value: unknown, kind: "actors" | "caps", field: string): string {
  if (typeof value !== "string" || !new RegExp(`^/office/${kind}/SQ_${kind === "actors" ? "HUMAN" : "CAP"}_[A-Z0-9_]+\\.glb$`).test(value)) {
    throw new Error(`${field} must identify an original local ${kind} GLB.`);
  }
  return value;
}

function matrixRows(value: unknown, field: string): MatrixRows {
  if (!Array.isArray(value) || value.length !== 4 || value.some(row => !Array.isArray(row) || row.length !== 4)) {
    throw new Error(`${field} must be a 4 by 4 matrix.`);
  }
  const rows = value.map(row => (row as unknown[]).map(component => {
    if (typeof component !== "number" || !Number.isFinite(component) || Math.abs(component) > 1000) throw new Error(`${field} contains an invalid transform.`);
    return component;
  })) as MatrixRows;
  if (rows[3].some((n, i) => Math.abs(n - (i === 3 ? 1 : 0)) > 1e-6) || Math.abs(matrixFromRows(rows).determinant()) < 1e-8) {
    throw new Error(`${field} must be a non-singular affine transform.`);
  }
  return rows;
}

/** Source matrices are rows; Matrix4.fromArray would transpose their meaning. */
export function matrixFromRows(rows: MatrixRows): Matrix4 {
  return new Matrix4().set(
    ...rows[0] as [number, number, number, number],
    ...rows[1] as [number, number, number, number],
    ...rows[2] as [number, number, number, number],
    ...rows[3] as [number, number, number, number],
  );
}

/** Copy only the fields needed to display the supplied staged artwork. */
export function parseOriginalActorsManifest(value: unknown): OriginalActorsManifest {
  const source = record(value, "actors");
  if (source.schema !== "sidequest-original-actors-v1" || source.units !== "metres" || source.attachmentProfilesUrl !== PROFILES_URL) {
    throw new Error("Original actor manifest version, units or attachment path is invalid.");
  }
  const humans = new Map<string, HumanAsset>();
  const variants = new Set<string>();
  for (const entry of items(source.workers, "actors.workers", 12)) {
    const human = record(entry, "human");
    const assetId = identifier(human.assetId, "human.assetId");
    const match = /^SQ_HUMAN_(\d{2}_[A-Z_]+?)(__CAP_READY)?$/.exec(assetId);
    const url = assetUrl(human.url, "actors", "human.url");
    if (!match || human.jointCount !== 17 || human.capReady !== !!match[2] || url !== `/office/actors/${assetId}.glb` || humans.has(url)) {
      throw new Error("Original human identity or skin declaration is invalid.");
    }
    const declaredClips = items(human.clips, "human.clips", 4).map(entry => {
      const clip = record(entry, "clip");
      if (typeof clip.durationSeconds !== "number" || !Number.isFinite(clip.durationSeconds) || clip.durationSeconds <= 0 || clip.durationSeconds > 60) {
        throw new Error("Original human clip duration is invalid.");
      }
      return clip.name;
    });
    if ([...declaredClips].sort().join(",") !== "Idle,Point,Typing,Walk") throw new Error("Original human clips are incomplete.");
    const variant = match[1].toLowerCase();
    variants.add(variant);
    humans.set(url, { assetId, url, variant, capReady: human.capReady as boolean });
  }
  const caps = new Map<string, string>();
  for (const entry of items(source.caps, "actors.caps", 24)) {
    const cap = record(entry, "cap");
    const id = identifier(cap.assetId, "cap.assetId");
    const url = assetUrl(cap.url, "caps", "cap.url");
    if (cap.jointCount !== 1 || url !== `/office/caps/${id}.glb` || caps.has(id)) throw new Error("Original cap identity or skin declaration is invalid.");
    caps.set(id, url);
  }
  const textures = new Set(items(source.identityTextures, "actors.identityTextures", 24).map(entry => {
    const texture = record(entry, "identity texture");
    if (typeof texture.url !== "string" || !/^\/office\/caps\/textures\/(?:portable_)?[A-Z0-9_]+_cap_RGBA\.png$/.test(texture.url)) {
      throw new Error("Original identity texture must be local.");
    }
    return texture.url;
  }));
  const sceneIds = new Set<string>();
  const instances = items(source.stagedReferenceInstances, "actors.stagedReferenceInstances", 64).map((entry): OriginalActorInstance => {
    const instance = record(entry, "staged actor");
    const sceneId = identifier(instance.sceneId, "staged actor.sceneId");
    const stationId = identifier(instance.stationId, "staged actor.stationId");
    const url = assetUrl(instance.assetUrl, "actors", "staged actor.assetUrl");
    const human = humans.get(url);
    if (!human || sceneIds.has(sceneId) || !/^parent_0(?:0[1-9]|1[0-9]|2[0-4])$/.test(stationId) || instance.runtimeConnected !== false) {
      throw new Error("Staged actor identity must be unique, local and disconnected.");
    }
    sceneIds.add(sceneId);
    // The world-layout hint calls the retained original Walk clip "Walking".
    const clip = instance.clipHint === "Walking" ? "Walk" : instance.clipHint;
    if (clip !== "Idle" && clip !== "Typing" && clip !== "Point" && clip !== "Walk") throw new Error("Staged actor pose does not name an original clip.");
    let headAccessory: HeadAccessory | null = null;
    if (instance.headAccessory !== null) {
      const accessory = record(instance.headAccessory, "head accessory");
      const fitId = `SQ_CAP_BASE_${human.variant.toUpperCase()}`;
      const identityId = identifier(accessory.identity_asset_id, "head accessory.identity_asset_id");
      const identityCapUrl = caps.get(identityId);
      if (accessory.fit_base_asset_id !== fitId || accessory.fitBaseUrl !== caps.get(fitId) || !identityCapUrl ||
          identityId.startsWith("SQ_CAP_BASE_") || accessory.attachmentProfilesUrl !== PROFILES_URL ||
          !textures.has(accessory.identityTextureUrl as string) || accessory.alpha_mode !== "MASK" || accessory.alpha_cutoff !== 0.5 ||
          (human.variant === "04_slate_beanie" && (!human.capReady || accessory.slate_original_beanie_omitted !== true))) {
        throw new Error("Staged cap must use its original variant fit, identity and cap-ready companion.");
      }
      const expectedTexture = `/office/caps/textures/${identityId.slice("SQ_CAP_".length)}_cap_RGBA.png`;
      if (accessory.identityTextureUrl !== expectedTexture) throw new Error("Staged cap identity texture does not match its original identity.");
      headAccessory = { fitBaseUrl: accessory.fitBaseUrl as string, identityCapUrl, variant: human.variant };
    }
    return { sceneId, stationId, assetUrl: url, worldMatrixGltfRows: matrixRows(instance.worldMatrixGltfRows, "staged actor matrix"), clip, headAccessory, runtimeConnected: false };
  });
  return { instances, humanVariantCount: variants.size };
}

/** Convert the supplied Blender head-rest basis to glTF once, then invert it. */
export function parseOriginalHeadRestInverses(value: unknown): Map<string, Matrix4> {
  const source = record(value, "attachment profiles");
  const profiles = items(source.profiles, "attachment profiles.profiles", 12);
  const matrices = record(source.head_rest_matrices, "attachment profiles.head_rest_matrices");
  const inverseByVariant = new Map<string, Matrix4>();
  const blenderToGltf = new Matrix4().makeRotationX(-Math.PI / 2);
  for (const entry of profiles) {
    const profile = record(entry, "attachment profile");
    const variant = identifier(profile.variant, "attachment profile.variant");
    const attachment = record(profile.attachment, "attachment profile.attachment");
    if (inverseByVariant.has(variant) || profile.read_only_original_library !== true || attachment.vertex_group !== "head" || attachment.weight !== 1) {
      throw new Error("Original cap attachment profile is invalid.");
    }
    const originalRest = matrixFromRows(matrixRows(matrices[variant], "original head-rest matrix"));
    inverseByVariant.set(variant, blenderToGltf.clone().multiply(originalRest).invert());
  }
  return inverseByVariant;
}

function localEmbeddedImages(parser: GLTFParser) {
  // ImageBitmapLoader fetches blob images through connect-src. TextureLoader
  // uses the existing img-src blob permission, retaining CSP and original bytes.
  parser.textureLoader = new TextureLoader(parser.options.manager)
    .setCrossOrigin(parser.options.crossOrigin);
  return { name: "SIDEQUEST_LOCAL_ORIGINAL_IMAGES", beforeRoot: async () => undefined };
}

export function configureOriginalActorLoader(loader: GLTFLoader) {
  loader.manager.setURLModifier(url => validateOfficeResourceUrl(url, window.location.href));
  loader.register(localEmbeddedImages);
}

interface ActorAssembly {
  object: Group;
  sample: () => void;
  dispose: () => void;
}

function identityReceiver(scene: Object3D): Material {
  let material: Material | undefined;
  scene.traverse(node => {
    if (node instanceof Mesh && node.userData.normalized_uv_receiver === true) {
      if (material || Array.isArray(node.material) || !(node.material instanceof MeshStandardMaterial) || !node.material.map) throw new Error("Original cap identity receiver or image is missing or ambiguous.");
      material = node.material;
    }
  });
  if (!material) throw new Error("Original cap identity receiver is missing.");
  return material;
}

/** Build an independent static actor; all geometry and identity materials stay cached and unchanged. */
export function assembleOriginalActor(
  instance: OriginalActorInstance,
  human: Pick<GLTF, "scene" | "animations">,
  headRestInverse?: Matrix4,
  fitCap?: Pick<GLTF, "scene">,
  identityCap?: Pick<GLTF, "scene">,
): ActorAssembly {
  const actor = cloneSkeleton(human.scene) as Group;
  const skeletons = new Set<Skeleton>();
  let head: Bone | undefined;
  let primarySkeleton: Skeleton | undefined;
  actor.traverse(node => {
    if (node instanceof Bone && node.name === "head") {
      if (head) throw new Error("Original actor has an ambiguous head joint.");
      head = node;
    }
    if (node instanceof SkinnedMesh) {
      if (node.skeleton.bones.length !== 17) throw new Error("Original actor must retain its 17-joint skin.");
      // Slate has many original component meshes, all using this same skin.
      if (!primarySkeleton) primarySkeleton = node.skeleton;
      else if (node.skeleton !== primarySkeleton && node.skeleton.bones.every((bone, i) => bone === primarySkeleton!.bones[i])) {
        node.skeleton.dispose();
        node.skeleton = primarySkeleton;
      }
      skeletons.add(node.skeleton);
      node.castShadow = true;
      node.receiveShadow = true;
    }
  });
  if (!head || !primarySkeleton) throw new Error("Original actor skin or head joint is missing.");
  if (instance.headAccessory) {
    if (!headRestInverse || !fitCap || !identityCap) throw new Error("Original actor cap resources are incomplete.");
    const cap = cloneSkeleton(fitCap.scene);
    const receiver = identityReceiver(identityCap.scene);
    const sharedHead = new Skeleton([head], [headRestInverse.clone()]);
    skeletons.add(sharedHead);
    let capMeshes = 0, receivers = 0;
    cap.traverse(node => {
      if (!(node instanceof SkinnedMesh)) return;
      capMeshes++;
      node.skeleton.dispose();
      // Cap vertices are already in the original rest-character coordinates.
      // The shared head and source inverse carry its pose; no second actor scale.
      node.bind(sharedHead, new Matrix4());
      node.castShadow = true;
      node.receiveShadow = true;
      if (node.userData.normalized_uv_receiver === true) { node.material = receiver; receivers++; }
    });
    if (capMeshes !== 5 || receivers !== 1) throw new Error("Original fit cap meshes or receiver are incomplete.");
    // Remove the cap's now-unused duplicate head to keep a single actor head.
    const capHead = cap.getObjectByName("head");
    capHead?.removeFromParent();
    actor.add(cap);
  }
  const clip: AnimationClip | undefined = human.animations.find(clip => clip.name === instance.clip);
  if (!clip) throw new Error("Original staged pose clip is missing.");
  const mixer = new AnimationMixer(actor);
  const sample = () => {
    const action = mixer.clipAction(clip).reset().play();
    mixer.setTime(Math.min(STATIC_POSE_SECONDS, clip.duration));
    action.paused = true;
    actor.updateMatrixWorld(true);
  };
  sample();
  const object = new Group();
  object.name = instance.sceneId;
  object.userData = { artworkOnly: true, runtimeConnected: false, stationReferenceId: instance.stationId, sampledClip: instance.clip, sampledSeconds: Math.min(STATIC_POSE_SECONDS, clip.duration) };
  // Keep the native actor pivot intact; apply the supplied world matrix once.
  object.matrixAutoUpdate = false;
  object.matrix.copy(matrixFromRows(instance.worldMatrixGltfRows));
  object.add(actor);
  object.updateMatrixWorld(true);
  return { object, sample, dispose: () => { mixer.stopAllAction(); mixer.uncacheRoot(actor); skeletons.forEach(skeleton => skeleton.dispose()); } };
}

interface StaticActorProps {
  instance: OriginalActorInstance;
  headRestInverse?: Matrix4;
  onLoaded: (id: string) => void;
  badge?:OfficeNotification;
  onNotification?: (notification:OfficeNotification)=>void;
}

function ActorPrimitive({ instance, headRestInverse, onLoaded, human, fit, identity, badge, onNotification }: StaticActorProps & {
  human: Pick<GLTF, "scene" | "animations">; fit?: Pick<GLTF, "scene">; identity?: Pick<GLTF, "scene">;
}) {
  const assembly = useMemo(() => assembleOriginalActor(instance, human, headRestInverse, fit, identity), [instance, human, headRestInverse, fit, identity]);
  const badgePosition=useMemo(()=>{const point=new Vector3();assembly.object.getObjectByName('head')!.getWorldPosition(point);point.y+=.4;return point.toArray() as [number,number,number];},[assembly]);
  const invalidate = useThree(state => state.invalidate);
  useLayoutEffect(() => {
    // React's development remount also resamples after cleanup restored bind poses.
    assembly.sample(); invalidate(); onLoaded(instance.sceneId);
    return assembly.dispose;
  }, [assembly, instance.sceneId, onLoaded, invalidate]);
  return <><primitive object={assembly.object} dispose={null} />{badge&&<AgentBadge kind={badge.kind} label={`${badge.fixture?'Test fixture · ':''}${badge.label}: ${badge.title} · recorded status at ${instance.stationId}`} position={badgePosition} onClick={()=>onNotification?.(badge)}/>}</>;
}

function CappedActor(props: StaticActorProps & { human: Pick<GLTF, "scene" | "animations"> }) {
  const accessory = props.instance.headAccessory!;
  const fit = useGLTF(accessory.fitBaseUrl, false, false, configureOriginalActorLoader);
  const identity = useGLTF(accessory.identityCapUrl, false, false, configureOriginalActorLoader);
  return <ActorPrimitive {...props} fit={fit} identity={identity} />;
}

function StaticActor(props: StaticActorProps) {
  // Cache each original GLB by its own URL across all 26 staged instances.
  // No original file requires either external compression decoder.
  const human = useGLTF(props.instance.assetUrl, false, false, configureOriginalActorLoader);
  return props.instance.headAccessory ? <CappedActor {...props} human={human} /> : <ActorPrimitive {...props} human={human} />;
}

class ActorBoundary extends Component<{ children: ReactNode; onError: (error: Error) => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error) { this.props.onError(error); }
  render() { return this.state.failed ? null : this.props.children; }
}

async function localJson(url: string, signal: AbortSignal): Promise<unknown> {
  const response = await fetch(url, { credentials: "same-origin", cache: "no-store", signal, redirect: "error" });
  if (!response.ok) throw new Error(`Unable to load original actor metadata (${response.status}).`);
  const declaredSize = response.headers.get("content-length");
  if (declaredSize && Number(declaredSize) > MAX_MANIFEST_BYTES) throw new Error("Original actor metadata is too large.");
  const reader = response.body?.getReader();
  if (!reader) throw new Error("Original actor metadata body is unavailable.");
  const chunks: Uint8Array[] = [];
  let length = 0;
  for (;;) {
    const chunk = await reader.read();
    if (chunk.done) break;
    length += chunk.value.byteLength;
    if (length > MAX_MANIFEST_BYTES) { await reader.cancel(); throw new Error("Original actor metadata is too large."); }
    chunks.push(chunk.value);
  }
  const bytes = new Uint8Array(length);
  let offset = 0;
  chunks.forEach(chunk => { bytes.set(chunk, offset); offset += chunk.byteLength; });
  return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes));
}

/** Static original artwork only. Status and refresh never invoke an agent or animate a typing loop. */
export default function OriginalActors({ active, onState, onError, onSelectActor, stationBadges, onNotification }: OriginalActorsProps) {
  const gl = useThree(state => state.gl);
  const [resources, setResources] = useState<{ manifest: OriginalActorsManifest; inverses: Map<string, Matrix4> } | null>(null);
  const [loaded, setLoaded] = useState<Set<string>>(() => new Set());
  const [error, setError] = useState<Error | null>(null);
  const callbacks = useRef({ onState, onError });
  callbacks.current = { onState, onError };
  const invalidate = useThree(state => state.invalidate);
  const handlers = useMemo(() => ({
    loaded: (id: string) => setLoaded(previous => previous.has(id) ? previous : new Set([...previous, id])),
    error: (failure: Error) => setError(failure),
  }), []);
  useEffect(() => {
    if (!active || resources || error) return;
    const controller = new AbortController();
    Promise.all([localJson(ACTORS_URL, controller.signal), localJson(PROFILES_URL, controller.signal)])
      .then(([actors, profiles]) => {
        const manifest = parseOriginalActorsManifest(actors);
        const inverses = parseOriginalHeadRestInverses(profiles);
        if (manifest.instances.some(instance => instance.headAccessory && !inverses.has(instance.headAccessory.variant))) throw new Error("Original cap head-rest profile is missing.");
        if (!controller.signal.aborted) setResources({ manifest, inverses });
      }).catch(failure => { if (!controller.signal.aborted) setError(failure instanceof Error ? failure : new Error(String(failure))); });
    return () => controller.abort();
  }, [active, resources, error]);
  useEffect(() => {
    callbacks.current.onState?.({ status: error ? "error" : resources && loaded.size === resources.manifest.instances.length ? "ready" : "loading", stagedActorCount: resources?.manifest.instances.length ?? 0, loadedActorCount: loaded.size, runtimeConnected: false });
    if (error) callbacks.current.onError?.(error);
  }, [resources, loaded, error]);
  useEffect(() => { if (active) invalidate(); }, [active, resources, loaded, invalidate]);
  useEffect(()=>{
    // Only the explicitly named primary workstation figure displays recorded status.
    // Decorative children sharing that station never imply another worker association.
    const badges=resources?.manifest.instances.filter(instance=>instance.sceneId===`worker_${instance.stationId}`&&loaded.has(instance.sceneId)&&stationBadges?.has(instance.stationId)).map(instance=>({sceneId:instance.sceneId,stationId:instance.stationId,kind:stationBadges!.get(instance.stationId)!.kind,jobId:stationBadges!.get(instance.stationId)!.jobId}))??[];
    gl.domElement.dataset.agentBadges=JSON.stringify(badges);if(active)invalidate();
  },[active,resources,loaded,stationBadges,gl,invalidate]);
  if (!resources || error) return null;
  return <group name="original-staged-artwork" visible={active} userData={{ artworkOnly: true, runtimeConnected: false }}>
    <ActorBoundary onError={handlers.error}>
      <Suspense fallback={null}>
        {resources.manifest.instances.map(instance => <group key={instance.sceneId} userData={{actorReferenceStation:instance.stationId}} onClick={event=>{event.stopPropagation();onSelectActor?.(instance.stationId,instance.sceneId);}} onPointerOver={event=>{event.stopPropagation();gl.domElement.style.cursor='pointer';}} onPointerOut={()=>{gl.domElement.style.cursor='default';}}><StaticActor instance={instance} headRestInverse={instance.headAccessory ? resources.inverses.get(instance.headAccessory.variant) : undefined} onLoaded={handlers.loaded} badge={instance.sceneId===`worker_${instance.stationId}`?stationBadges?.get(instance.stationId):undefined} onNotification={onNotification}/></group>)}
      </Suspense>
    </ActorBoundary>
  </group>;
}
