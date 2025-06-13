import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  env: {
    NEXT_PUBLIC_API_URL: 'http://3.71.10.131:8000',
    NEXT_PUBLIC_DEBUG_API: 'true',
    NEXT_PUBLIC_API_TIMEOUT: '10000',
  },
};

export default nextConfig;
