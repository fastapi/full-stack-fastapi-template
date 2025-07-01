import React from "react";
import { FiPlus } from "react-icons/fi";

const TemplateManager: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto py-8 px-6">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div className="flex flex-col items-start">
            <h2 className="text-3xl font-bold text-white mb-1">Gestión de Templates</h2>
            <span className="text-gray-400 text-sm">
              GENIUS INDUSTRIES - Administra plantillas de documentos legales
            </span>
          </div>
          <button className="flex items-center bg-black text-white border-none rounded-lg px-4 py-3 cursor-pointer hover:bg-gray-800 transition-colors">
            <FiPlus className="mr-2" />
            Nuevo Template
          </button>
        </div>
      </div>
      <div className="bg-slate-800 rounded-xl shadow-lg p-6 border border-slate-700">
        <span className="text-white">Component funcionando correctamente con Tailwind CSS</span>
      </div>
    </div>
  );
};

export default TemplateManager;
