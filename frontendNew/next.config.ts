import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    NEXT_PUBLIC_API_URL: 'http://3.65.227.81:8000',
    NEXT_PUBLIC_DEBUG_API: 'true',
    NEXT_PUBLIC_API_TIMEOUT: '10000',
  },
};

export default nextConfig;
