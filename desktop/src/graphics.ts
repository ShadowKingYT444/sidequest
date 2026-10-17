/** Software GPUs can spend seconds per office frame; retain the scene and snap camera focus. */
export function isSoftwareRenderer(context: Pick<WebGLRenderingContext, 'getExtension' | 'getParameter' | 'RENDERER'>): boolean {
  try {
    const info = context.getExtension('WEBGL_debug_renderer_info');
    const renderer: unknown = context.getParameter(info?.UNMASKED_RENDERER_WEBGL ?? context.RENDERER);
    return typeof renderer === 'string' && /swiftshader|llvmpipe|softpipe|software rasterizer|software renderer|microsoft basic render driver/i.test(renderer);
  } catch {
    return false;
  }
}
