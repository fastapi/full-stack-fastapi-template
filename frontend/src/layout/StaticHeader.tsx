"use client";

import { ThemeToggleButton } from "@/components/common/ThemeToggleButton";
import Image from "next/image";
import Link from "next/link";
import React from "react";

const StaticHeader: React.FC = () => {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md dark:border-gray-800 dark:bg-gray-900/80">
<div className="flex items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
          {/* Logo */}
        <Link href="/" className="flex items-center gap-2">
          <Image
            width={32}
            height={32}
            src="/images/logo/logo.svg"
            alt="Logo"
            className="dark:hidden"
          />
          <Image
            width={32}
            height={32}
            src="/images/logo/logo-dark.svg"
            alt="Logo Dark"
            className="hidden dark:block"
          />
          <span className="text-lg font-semibold text-gray-900 dark:text-white">
            Study Assistant
          </span>
        </Link>

        {/* Right Side Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/signin"
            className="rounded-md border border-gray-300 px-3 py-1.5 text-sm font-medium text-gray-700 hover:bg-gray-100 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-800"
          >
            Log in
          </Link>
          <Link
            href="/signup"
            className="rounded-md bg-indigo-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-indigo-700 dark:bg-indigo-500 dark:hover:bg-indigo-600"
          >
            Get Started
          </Link>
          <ThemeToggleButton />
        </div>
      </div>
    </header>
  );
};

export default StaticHeader;
