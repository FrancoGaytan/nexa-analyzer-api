import React from 'react';
import type { AnalyzeResponse } from '../pages/App';

interface Props {
  result: AnalyzeResponse | null;
}

export const AnalysisResult: React.FC<Props> = ({ result }) => {
  if (!result) {
    return <div className="text-sm text-gray-500">No hay resultado aún.</div>;
  }
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Resultado</h2>
      <div className="space-y-2 text-sm">
        <div><span className="font-medium">ID:</span> {result.analysis_id}</div>
        <div><span className="font-medium">Estado:</span> {result.status}</div>
      </div>
      <pre className="mt-4 max-h-96 overflow-auto text-xs bg-gray-900 text-green-200 p-4 rounded">
        {JSON.stringify(result.summary, null, 2)}
      </pre>
    </div>
  );
};
