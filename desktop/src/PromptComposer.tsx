import { useEffect, useId, useLayoutEffect, useRef, useState, type ClipboardEvent, type DragEvent, type FormEvent } from 'react';
import { addLocalFiles, cleanPlainText, extractLocalTransfer, insertDraftText, localDraftIssue, removeLocalAttachment, createDraftOperations, type DraftOperations, type DraftIssue, type LocalDraft } from './local-drafts';
import './PromptComposer.css';

export interface PromptComposerProps {
  draft: LocalDraft;
  onChange: (draft: LocalDraft) => void;
  canSubmit: boolean;
  onSubmit?: (draft: LocalDraft) => void;
  disabledReason?: string;
  label?: string;
  getCurrentDraft?:()=>LocalDraft;
  operations?:DraftOperations;
}

const fileAccept = '.png,.jpg,.jpeg,.gif,.webp,.pdf,.txt,.md,.markdown,.csv,.tsv,.json,.jsonl,.yaml,.yml,.toml,.xml,.log,.ts,.tsx,.js,.jsx,.mjs,.cjs,.py,.rb,.rs,.go,.java,.c,.h,.cpp,.hpp,.cs,.css,.scss,.sql,.vue,.svelte,.swift,.kt,.diff,.patch';
const fileSize = (size: number) => size < 1024 ? `${size} B` : size < 1024 * 1024 ? `${Math.ceil(size / 1024)} KiB` : `${(size / (1024 * 1024)).toFixed(1)} MiB`;

/** The parent owns the draft across Escape; this component does not upload or dispatch. */
export default function PromptComposer({ draft, onChange, canSubmit, onSubmit, getCurrentDraft, operations, disabledReason = 'This session cannot accept messages or attachments on this host.', label = 'Message this session' }: PromptComposerProps) {
  const id = useId();
  const textarea = useRef<HTMLTextAreaElement>(null);
  const picker = useRef<HTMLInputElement>(null);
  const current = useRef(draft); current.current = draft;
  const change = useRef(onChange); change.current = onChange;
  const pending = useRef(createDraftOperations());
  const store=operations??pending.current;
  const getDraft=useRef(getCurrentDraft);getDraft.current=getCurrentDraft;
  const [issues, setIssuesState] = useState<DraftIssue[]>(store.issues);
  const announce=()=>store.listeners.forEach(listener=>listener());
  const setIssues=(next:DraftIssue[])=>{store.issues=next;announce();};
  const [reading, setReading] = useState(store.reading>0);
  useEffect(()=>{const sync=()=>{setIssuesState(store.issues);setReading(store.reading>0);};store.listeners.add(sync);sync();return()=>{store.listeners.delete(sync);};},[store]);
  useLayoutEffect(()=>{if(store.selection&&textarea.current)textarea.current.setSelectionRange(...store.selection);},[store]);
  const [dragging, setDragging] = useState(false);
  const [failedPreviews, setFailedPreviews] = useState<Set<string>>(() => new Set());
  const dragDepth = useRef(0);
  const commit = (next: LocalDraft) => { current.current = next; change.current(next); };

  function attach(files: File[]) {
    if (!files.length) return;
    store.reading++;announce();
    // Serialize local reads so fast paste/drop actions cannot overwrite each other.
    const queue=store;
    queue.pending = queue.pending.then(async () => {
      const initial = getDraft.current?.()??current.current;
      const result = await addLocalFiles(initial, files);
      const additions = result.draft.attachments.slice(initial.attachments.length);
      // Text edits and removals during a bounded raster read remain intact.
      // The retained getter/queue also covers Escape followed by a new component lifetime.
      const latest = getDraft.current?.()??current.current;
      const updated = { text: latest.text, attachments: [...latest.attachments, ...additions] };
      commit(updated); setIssues(result.issues);
    }).catch(() => setIssues([{ code: 'read', message: 'Files could not be added. Try selecting them again.' }])).finally(() => {store.reading=Math.max(0,store.reading-1);announce();});
  }

  function insert(text: string) {
    if (!text) return;
    const input = textarea.current;
    const result = insertDraftText(current.current.text, text, input?.selectionStart, input?.selectionEnd);
    commit({ ...current.current, text: result.text });
    setIssues(result.issue ? [result.issue] : []);
    requestAnimationFrame(() => { input?.focus(); input?.setSelectionRange(result.caret, result.caret); });
  }

  function paste(event: ClipboardEvent<HTMLTextAreaElement>) {
    const payload = extractLocalTransfer(event.clipboardData);
    if (!payload.files.length && !payload.text) return;
    event.preventDefault(); insert(payload.text); attach(payload.files);
  }

  function drop(event: DragEvent<HTMLFormElement>) {
    const payload = extractLocalTransfer(event.dataTransfer);
    dragDepth.current = 0; setDragging(false);
    if (!payload.files.length && !payload.text) return;
    event.preventDefault(); event.stopPropagation(); insert(payload.text); attach(payload.files);
  }

  const draftProblem = localDraftIssue(draft);
  const sendReady = canSubmit && !!onSubmit && !!draft.text.trim() && !draftProblem && !reading;
  function submit(event: FormEvent) { event.preventDefault(); if (sendReady) onSubmit?.(current.current); }

  return <form className={`prompt-composer${dragging ? ' is-dragging' : ''}`} aria-label="Local prompt composer" onSubmit={submit} onDrop={drop}
    onDragEnter={event => { if (event.dataTransfer.types.includes('Files')) { event.preventDefault(); dragDepth.current++; setDragging(true); } }}
    onDragLeave={() => { dragDepth.current = Math.max(0, dragDepth.current - 1); if (!dragDepth.current) setDragging(false); }}
    onDragOver={event => { if (event.dataTransfer.types.includes('Files') || event.dataTransfer.types.includes('text/plain')) event.preventDefault(); }}>
    {!!draft.attachments.length && <ul className="prompt-attachments" aria-label="Local attachments">{draft.attachments.map(attachment => <li key={attachment.id}>
      {attachment.kind === 'image' && attachment.previewURL && !failedPreviews.has(attachment.id) ? <img src={attachment.previewURL} alt={`Preview of ${attachment.name}`} width="40" height="40" onError={() => { setFailedPreviews(previous => new Set(previous).add(attachment.id)); setIssues([{ code: 'read', message: `${attachment.name}: preview unavailable. The file is still local.`, fileName: attachment.name }]); }} /> : <span className="prompt-file-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M7 3h7l4 4v14H7zM14 3v5h4M10 12h5m-5 4h5" /></svg></span>}
      <span className="prompt-attachment-copy"><span>{attachment.name}</span><small>{fileSize(attachment.size)}</small></span>
      <button type="button" aria-label={`Remove ${attachment.name}`} onClick={() => commit(removeLocalAttachment(current.current, attachment.id))}><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="m6 6 8 8M14 6l-8 8" /></svg></button>
    </li>)}</ul>}
    <div className="prompt-compose-row">
      <button className="prompt-attach" type="button" onClick={() => picker.current?.click()} aria-label="Attach files" title="Attach files"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><path d="m8 13 7-7a3 3 0 0 1 4 4L9 20a5 5 0 0 1-7-7l10-10M5 16l10-10" /></svg></button>
      <label className="sr-only" htmlFor={`${id}-prompt`}>{label}</label>
      <textarea id={`${id}-prompt`} ref={textarea} value={draft.text} maxLength={2000} rows={1} placeholder="Write a local draft…" onPaste={paste}
        onSelect={event=>{store.selection=[event.currentTarget.selectionStart,event.currentTarget.selectionEnd];}} onChange={event => { commit({ ...current.current, text: cleanPlainText(event.target.value).slice(0, 2000) }); setIssues([]); }}
        onKeyDown={event => { if (event.key === 'Enter' && (event.ctrlKey || event.metaKey) && !event.nativeEvent.isComposing) { event.preventDefault(); if (sendReady) onSubmit?.(current.current); } }} />
      <button className="prompt-send" type="submit" disabled={!sendReady} aria-label="Send message" title={!canSubmit?'Sending unavailable':'Send message (Ctrl+Enter)'}><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6" /></svg></button>
    </div>
    <input ref={picker} className="sr-only" type="file" multiple accept={fileAccept} aria-label="Select local files" tabIndex={-1} onChange={event => { attach(Array.from(event.target.files ?? [])); event.target.value = ''; }} />
    <div className="prompt-compose-meta"><details><summary>Local draft{!canSubmit?' · sending unavailable':''}{draft.attachments.length ? ` · ${draft.attachments.length} files` : ''}</summary><p>Text, images and files stay on this device. Up to 10 files; 10 MiB each, 25 MiB total. PNG, JPEG, GIF, WebP, PDF and plain text/code files only. No SVG or executable files. Prompts: 2,000 characters.</p>{(!canSubmit || !onSubmit) && <p>{disabledReason}</p>}</details><span aria-live="polite">{reading ? 'Reading local files…' : `${draft.text.length}/2,000`}</span></div>
    {(issues.length > 0 || draftProblem) && <div className="prompt-compose-errors" role="alert"><ul>{[...issues, ...(draftProblem ? [draftProblem] : [])].map((problem, index) => <li key={`${problem.code}-${index}`}>{problem.message}</li>)}</ul><button type="button" aria-label="Dismiss attachment errors" onClick={() => setIssues([])}>Dismiss</button></div>}
    {dragging && <div className="prompt-drop-hint" aria-hidden="true">Drop files to keep them in this draft</div>}
  </form>;
}
