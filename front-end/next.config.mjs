import createNextIntlPlugin from "next-intl/plugin";

const withNextIntl = createNextIntlPlugin("./lib/request.ts");

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  webpack: (config) => {
    // Silence the harmless `node-fetch` resolution warnings emitted by webpack's
    // filesystem cache when snapshotting build deps of Next's bundled `next/font/google`
    // loader. The cache falls back gracefully; only the noisy warnings need quieting.
    config.infrastructureLogging = { level: "error" };
    return config;
  },
};

export default withNextIntl(nextConfig);
