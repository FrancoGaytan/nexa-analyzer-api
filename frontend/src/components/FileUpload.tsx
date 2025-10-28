import React, { useCallback, useRef, useState } from 'react';
import type { AnalyzeResponse } from '../pages/App';

const SUPPORTED_EXT = ['txt', 'text', 'pdf', 'docx'];

interface Props {
  onAnalyzed: (data: AnalyzeResponse | null) => void;
}

interface LocalFile {
  id: string;
  file: File;
  error?: string;
}

export const FileUpload: React.FC<Props> = ({ onAnalyzed }) => {
  const [clientName, setClientName] = useState('');
  const [files, setFiles] = useState<LocalFile[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const validateFile = (file: File): string | undefined => {
    const ext = file.name.split('.').pop()?.toLowerCase();
    if (!ext || !SUPPORTED_EXT.includes(ext)) {
      return `Formato no soportado: .${ext || '???'}`;
    }
    return undefined;
  };

  const onSelect = useCallback((evt: React.ChangeEvent<HTMLInputElement>) => {
    const list = evt.target.files;
    if (!list) return;
    const newOnes: LocalFile[] = [];
    const existingNames = new Set(files.map(f => f.file.name));
    Array.from(list).forEach(file => {
      if (existingNames.has(file.name)) return; // evitar duplicados por nombre
      const error = validateFile(file);
      newOnes.push({ id: crypto.randomUUID(), file, error });
    });
    setFiles(prev => [...prev, ...newOnes]);
    if (inputRef.current) inputRef.current.value = '';
  }, [files]);

  const removeFile = (id: string) => setFiles(prev => prev.filter(f => f.id !== id));

  const canSubmit = clientName.trim().length > 0 && files.length > 0 && files.every(f => !f.error) && !submitting;

  const handleSubmit = async () => {
    if (!canSubmit) return;
    setSubmitting(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('client_name', clientName.trim());
      files.forEach(f => form.append('files', f.file));
      const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const resp = await fetch(`${base}/context/analyze`, {
        method: 'POST',
        body: form,
      });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const data: AnalyzeResponse = await resp.json();
      onAnalyzed(data);
    } catch (e) {
      const msg = e instanceof Error ? e.message : 'Error al enviar';
      setError(msg);
      onAnalyzed(null);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Subir documentos</h2>
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1" htmlFor="client_name">Cliente</label>
          <input
            id="client_name"
            type="text"
            value={clientName}
            onChange={e => setClientName(e.target.value)}
            className="w-full rounded border-gray-300 focus:ring-brand focus:border-brand"
            placeholder="ACME Corp"
            autoComplete="off"
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Archivos (.txt, .pdf, .docx)</label>
          <input
            ref={inputRef}
            type="file"
            multiple
            onChange={onSelect}
            className="block w-full text-sm text-gray-600"
            accept={SUPPORTED_EXT.map(e => '.' + e).join(',')}
          />
          <p className="text-xs text-gray-500 mt-1">Se ignoran duplicados por nombre</p>
        </div>
        {files.length > 0 && (
          <ul className="divide-y rounded border border-gray-200 bg-gray-50 text-sm">
            {files.map(f => (
              <li key={f.id} className="flex items-center justify-between px-3 py-2">
                <span className={f.error ? 'text-red-600' : ''}>{f.file.name}{f.error && ` — ${f.error}`}</span>
                <button
                  onClick={() => removeFile(f.id)}
                  className="text-xs text-gray-500 hover:text-gray-800"
                  type="button"
                >Quitar</button>
              </li>
            ))}
          </ul>
        )}
        <div className="flex items-center gap-3">
          <button
            disabled={!canSubmit}
            onClick={handleSubmit}
            className="inline-flex items-center rounded bg-brand px-4 py-2 text-white disabled:opacity-50 disabled:cursor-not-allowed hover:bg-brand-dark transition"
            type="button"
          >{submitting ? 'Enviando...' : 'Analizar'}</button>
          {error && <span className="text-sm text-red-600">{error}</span>}
        </div>
      </div>
    </div>
  );
};
