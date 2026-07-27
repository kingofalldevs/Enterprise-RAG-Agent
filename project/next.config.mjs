/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {},
  serverExternalPackages: ["pdf-parse", "better-sqlite3"],
};

export default nextConfig;
