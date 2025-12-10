import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  async rewrites() {
    return [
      {
        source: "/api/chat/:path*",
        destination: "http://127.0.0.1:8080/api/chat/:path*",
      },
      {
        source: "/api/ingest/:path*",
        destination: "http://127.0.0.1:8080/api/ingest/:path*",
      },
    ];
  },
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
};

export default nextConfig;
