"use client";

import StaticHeader from "@/layout/StaticHeader";
import Backdrop from "@/layout/Backdrop";
import React from "react";

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {

  return (
    <div className="min-h-screen xl:flex">
      {/* Sidebar and Backdrop */}
      <Backdrop />
      {/* Main Content Area */}
      <div
        className={`flex-1 transition-all  duration-300 ease-in-out`}
      >
        {/* Header */}
        <StaticHeader />
        {/* Page Content */}
        <div className="p-4 mx-auto md:p-6">{children}</div>
      </div>
    </div>
  );
}
