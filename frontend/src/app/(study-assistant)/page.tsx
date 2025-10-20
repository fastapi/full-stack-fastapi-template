// src/app/landing/page.tsx
import React from "react";

export default function LandingPage() {
  return (
    <div className="text-center space-y-6">
      <h2 className="text-3xl font-bold">Welcome to Study Assistant</h2>
      <p>Upload documents, generate exams, and start practicing!</p>
      <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
        Upload Docs & Generate Exam
      </button>
    </div>
  );
}
