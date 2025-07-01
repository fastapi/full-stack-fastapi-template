import React from "react";
import { createFileRoute } from '@tanstack/react-router';
import { FiUsers, FiTarget, FiEye, FiAward, FiStar } from "react-icons/fi";

const team = [
  { name: "Ana Torres", role: "CEO & Founder", img: "https://randomuser.me/api/portraits/women/44.jpg" },
  { name: "Carlos Gómez", role: "COO", img: "https://randomuser.me/api/portraits/men/32.jpg" },
  { name: "Lucía Pérez", role: "CTO", img: "https://randomuser.me/api/portraits/women/65.jpg" },
  { name: "Miguel Ruiz", role: "CFO", img: "https://randomuser.me/api/portraits/men/41.jpg" },
];

function AboutPage() {
  return (
    <div className="bg-black min-h-screen py-16 px-4">
      <div className="max-w-4xl mx-auto text-center ">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-6">Sobre GENIUS INDUSTRIES</h1>
        <p className="text-lg text-gray-300 mb-10">Líderes en gestión inmobiliaria y de activos en Latinoamérica. Nuestra misión es transformar la experiencia de inversión y vivienda con tecnología, transparencia y excelencia.</p>
        <div className="grid md:grid-cols-3 gap-8 mb-12">
          <div className="bg-gray-800 rounded-2xl p-6 shadow-lg ">
            <h2 className="text-xl font-bold text-white mb-2">Misión</h2>
            <p className="text-gray-400">Facilitar el acceso a soluciones inmobiliarias e inversiones seguras, generando valor sostenible para nuestros clientes y aliados.</p>
          </div>
          <div className="bg-gray-800 rounded-2xl p-6 shadow-lg ">
            <h2 className="text-xl font-bold text-white mb-2">Visión</h2>
            <p className="text-gray-400">Ser la plataforma de referencia en Latinoamérica para gestión de activos y bienes raíces, impulsando la innovación y la confianza.</p>
          </div>
          <div className="bg-gray-800 rounded-2xl p-6 shadow-lg ">
            <h2 className="text-xl font-bold text-white mb-2">Valores</h2>
            <ul className="text-gray-400 list-disc list-inside text-left">
              <li>Transparencia</li>
              <li>Innovación</li>
              <li>Excelencia</li>
              <li>Compromiso</li>
              <li>Confianza</li>
            </ul>
          </div>
        </div>
        <div className="bg-gray-800 rounded-2xl p-8 shadow-lg ">
          <h2 className="text-2xl font-bold text-white mb-4">Nuestro Equipo</h2>
          <p className="text-gray-400 mb-6">Contamos con profesionales expertos en bienes raíces, finanzas, tecnología y atención al cliente, comprometidos con tu éxito.</p>
          <div className="flex flex-wrap justify-center gap-8">
            {team.map((member) => (
              <div key={member.name} className="flex flex-col items-center">
                <div className="w-20 h-20 bg-gray-600 rounded-full mb-2" />
                <div className="text-white font-bold">{member.name}</div>
                <div className="text-gray-400 text-sm">{member.role}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute('/about')({
  component: AboutPage,
}); 
