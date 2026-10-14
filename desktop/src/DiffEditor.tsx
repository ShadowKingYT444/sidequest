import { useLayoutEffect, useRef } from 'react';
import * as monaco from 'monaco-editor/editor/editor.api';
import '../node_modules/monaco-editor/esm/vs/base/browser/ui/codicons/codicon/codicon.css';
import 'monaco-editor/languages/definitions/python/register';
import 'monaco-editor/languages/definitions/typescript/register';
import 'monaco-editor/languages/definitions/javascript/register';
import 'monaco-editor/languages/definitions/markdown/register';
import EditorWorker from 'monaco-editor/editor/editor.worker?worker';
import type { GitDiff } from './types';
self.MonacoEnvironment = { getWorker: () => new EditorWorker() };
monaco.editor.defineTheme('sidequest', {
  base: 'vs-dark', inherit: true,
  rules: [
    { token: 'comment', foreground: 'B0BCAA' },
    { token: 'keyword', foreground: '8BD4F5' },
    { token: 'string', foreground: 'E3B18D' },
    { token: 'number', foreground: 'C5D8A7' },
    { token: 'type', foreground: '8FD9C9' },
    { token: 'markup.heading', foreground: '9BCCEC' },
  ],
  colors: {
    'editor.background': '#1E2220', 'editor.foreground': '#E0DFD7',
    'editorLineNumber.foreground': '#B4BAB2',
    'editorLineNumber.activeForeground': '#EBE9E4',
    'diffEditor.insertedLineBackground': '#233329',
    'diffEditor.removedLineBackground': '#382629',
    'diffEditor.insertedTextBackground': '#2F493680',
    'diffEditor.removedTextBackground': '#51313980',
  },
});
export type EditorViews = Map<string, monaco.editor.IDiffEditorViewState>;
export default function DiffEditor({ diff, views }: { diff: GitDiff; views: EditorViews }) {
  const container = useRef<HTMLDivElement>(null);
  useLayoutEffect(() => {
    performance.mark('sidequest:editor-mount');
    const host = container.current!;
    const cached = views.get(diff.id);
    const editor = monaco.editor.createDiffEditor(host, {
      theme: 'sidequest', readOnly: true, originalEditable: false,
      automaticLayout: true, renderSideBySide: false, minimap: { enabled: false },
      scrollBeyondLastLine: false, fontSize: 13, lineHeight: 21,
      wordWrap: 'on', diffWordWrap: 'on', contextmenu: false,
      renderIndicators: true, accessibilitySupport: 'on',
      ariaLabel: 'Read-only Git diff', originalAriaLabel: 'Original committed file, read-only', modifiedAriaLabel: 'Modified committed file, read-only', links: false, unicodeHighlight: { ambiguousCharacters: false },
      stickyScroll: { enabled: false },
    });
    // Monaco 0.57 can clear sub-editor names when diff layout options change.
    // Keep the accessible names through its public editor configuration API.
    const originalEditor = editor.getOriginalEditor();
    const modifiedEditor = editor.getModifiedEditor();
    const keepName = (target: monaco.editor.ICodeEditor, label: string) => {
      if (target.getOption(monaco.editor.EditorOption.ariaLabel) !== label) target.updateOptions({ ariaLabel: label });
    };
    const originalName = originalEditor.onDidChangeConfiguration(() => keepName(originalEditor, 'Original committed file, read-only'));
    const modifiedName = modifiedEditor.onDidChangeConfiguration(() => keepName(modifiedEditor, 'Modified committed file, read-only'));
    keepName(originalEditor, 'Original committed file, read-only');
    keepName(modifiedEditor, 'Modified committed file, read-only');
    const original = monaco.editor.createModel(diff.original, diff.language);
    const modified = monaco.editor.createModel(diff.modified, diff.language);
    let restoring = true;
    const save = () => {
      host.dataset.scrollTop = String(Math.round(editor.getModifiedEditor().getScrollTop()));
      if (!restoring) { const state = editor.saveViewState(); if (state) views.set(diff.id, state); }
    };
    const scroll = editor.getModifiedEditor().onDidScrollChange(save);
    const cursor = editor.getModifiedEditor().onDidChangeCursorSelection(save);
    const update = editor.onDidUpdateDiff(() => {
      if (!restoring) return;
      if (cached) editor.restoreViewState(cached);
      restoring = false; save();
    });
    editor.setModel({ original, modified });
    if (cached) editor.restoreViewState(cached);
    return () => {
      restoring = false; save(); originalName.dispose(); modifiedName.dispose(); scroll.dispose(); cursor.dispose(); update.dispose();
      editor.setModel(null); editor.dispose(); original.dispose(); modified.dispose();
    };
  }, [diff, views]);
  return <div className="diff-editor" data-testid="diff-editor" data-file-id={diff.id} ref={container} />;
}
