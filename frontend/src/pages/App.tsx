import React, { useState } from 'react';
import { FileUpload } from '../components/FileUpload';
import { AnalysisResult } from '../components/AnalysisResult';
import type { AnalyzeResponse } from '../types/context';

export const App: React.FC = () => {
  const [result, setResult] = useState<AnalyzeResponse | null>(null);

  return (
    <div className="min-h-screen flex flex-col">
      <header className="p-6 bg-brand text-white shadow">
        <h1 className="text-2xl font-semibold">Nexa Analyzer</h1>
        <p className="text-sm text-white">Subí tus briefs / RFPs para extraer contexto</p>
      </header>
      <main className="flex-1 p-6 max-w-4xl w-full mx-auto">
  <FileUpload onAnalyzed={setResult} />
        <div className="mt-8">
          <AnalysisResult result={result} />
        </div>
      </main>
      <footer className="p-4 text-center text-xs text-gray-500">MVP UI • {new Date().getFullYear()}</footer>
    </div>
  );
};
