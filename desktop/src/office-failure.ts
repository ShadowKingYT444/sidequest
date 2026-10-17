export type OfficeFailureKind = 'graphics' | 'bindings' | 'assets' | 'scene';
export interface OfficeFailure {kind:OfficeFailureKind; title:string; message:string}

/** Attribute failures to the operation that failed; never infer absent files from a renderer error. */
export function describeOfficeFailure(error:unknown, phase:'bindings'|'assets'|'scene'='scene'):OfficeFailure {
  if(phase==='bindings')return {kind:'bindings',title:'Office layout unavailable',message:'The office layout could not load. Retry or run setup again.'};
  if(phase==='assets')return {kind:'assets',title:'Office files could not load',message:'An office file could not load. Retry or run setup again.'};
  const message=error instanceof Error?error.message:'';
  if(/webgl|(?:graphics|rendering) context|gpu.*(?:blocked|blocklisted|unavailable)|context.*(?:creation|lost)/i.test(message)){
    return {kind:'graphics',title:'3D graphics unavailable',message:'WebGL2 could not start. Your office files may still be installed.'};
  }
  return {kind:'scene',title:'The office could not open',message:'Rendering failed. Retry or restart the app.'};
}
