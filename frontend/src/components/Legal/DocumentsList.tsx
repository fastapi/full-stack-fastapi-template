import React from "react";

const DocumentsList: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-8 px-6">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-white mb-1">Lista de Documentos</h2>
        <span className="text-gray-400 text-sm">
          GENIUS INDUSTRIES - Documentos legales generados
        </span>
      </div>
      <div className="bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-700">
        <span className="text-white">Lista de documentos funcionando con Tailwind CSS</span>
      </div>
    </div>
  );
};

export default DocumentsList;
