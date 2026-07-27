import { readdir } from "node:fs/promises";
import path from "path";

export async function GET() {
  const uploadDir = path.join(process.cwd(), "public", "uploads");
  const files = await readdir(uploadDir);
  const blobs = files.map((filename) => ({
    pathname: `${filename}`,
    url: `/uploads/${filename}`,
  }));
  return Response.json(blobs);
}
