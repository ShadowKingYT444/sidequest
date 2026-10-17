export type OfficeFailureKind = 'graphics' | 'bindings' | 'assets' | 'scene';
export interface OfficeFailure {kind:OfficeFailureKind; title:string; message:string}

/** Attribute failures to the operation that failed; never infer absent files from a renderer error. */
export function describeOfficeFailure(error:unknown, phase:'bindings'|'assets'|'scene'='scene'):OfficeFailure {
  if(phase==='bindings')return {kind:'bindings',title:'Office layout unavailable',message:'The office layout could not be loaded or validated. Retry, or run setup again if the problem continues.'};
  if(phase==='assets')return {kind:'assets',title:'Office files could not load',message:'An office model or image could not be loaded. Retry, or run setup again if the problem continues.'};
  const message=error instanceof Error?error.message:'';
  if(/webgl|(?:graphics|rendering) context|gpu.*(?:blocked|blocklisted|unavailable)|context.*(?:creation|lost)/i.test(message)){
    return {kind:'graphics',title:'3D graphics unavailable',message:'This device could not start WebGL2, which the office needs. This does not mean your office files are missing.'};
  }
  return {kind:'scene',title:'The office could not open',message:'The office encountered a rendering error. Retry the office or restart the app.'};
}
