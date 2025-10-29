import React from 'react';
import type { AnalyzeResponse, ClientContext } from '../types/context';

interface Props {
  result: AnalyzeResponse | null;
}

export const AnalysisResult: React.FC<Props> = ({ result }) => {
  if (!result) {
    return <div className="text-sm text-gray-500">No hay resultado aún.</div>;
  }
  const s: ClientContext = result.summary;
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-lg font-semibold mb-4">Resultado</h2>
      <div className="grid gap-2 text-sm md:grid-cols-2">
        <div><span className="font-medium">ID:</span> {result.analysis_id}</div>
        <div><span className="font-medium">Estado:</span> {result.status}</div>
        {s.client_name && <div><span className="font-medium">Cliente:</span> {s.client_name}</div>}
        {s.industry && <div><span className="font-medium">Industria:</span> {s.industry}</div>}
        {s.location && <div><span className="font-medium">Ubicación:</span> {s.location}</div>}
        {typeof s.engagement_age === 'number' && s.engagement_age > 0 && <div><span className="font-medium">Antigüedad (años):</span> {s.engagement_age}</div>}
      </div>
      {s.business_overview && (
        <section className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Overview</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{s.business_overview}</p>
        </section>
      )}
      {s.objectives?.length > 0 && (
        <section className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Objetivos</h3>
          <ul className="list-disc ml-5 space-y-1 text-sm">
            {s.objectives.map((o, i) => <li key={i}>{o}</li>)}
          </ul>
        </section>
      )}
      {s.company_info && (
        <section className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Info de la compañía</h3>
          <p className="text-sm text-gray-700 whitespace-pre-line">{s.company_info}</p>
        </section>
      )}
      {s.additional_context_questions?.length > 0 && (
        <section className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Preguntas adicionales</h3>
          <ul className="list-disc ml-5 space-y-1 text-sm">
            {s.additional_context_questions.map((q, i) => <li key={i}>{q}</li>)}
          </ul>
        </section>
      )}
      {s.potential_future_opportunities?.length > 0 && (
        <section className="mt-4">
          <h3 className="text-sm font-semibold mb-1">Oportunidades futuras</h3>
          <ul className="list-disc ml-5 space-y-1 text-sm">
            {s.potential_future_opportunities.map((op, i) => <li key={i}>{op}</li>)}
          </ul>
        </section>
      )}
      <details className="mt-6">
        <summary className="cursor-pointer text-xs text-gray-500">Ver JSON completo</summary>
        <pre className="mt-2 max-h-80 overflow-auto text-xs bg-gray-900 text-green-200 p-4 rounded">{JSON.stringify(result, null, 2)}</pre>
      </details>
    </div>
  );
};
