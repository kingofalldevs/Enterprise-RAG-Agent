import { deleteChunksByFilePath } from "@/app/db";
import { unlink } from "node:fs/promises";
import path from "path";

export async function DELETE(request: Request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get("filename") || searchParams.get("fileurl");

  if (!filename) {
    return new Response("Filename not provided", { status: 400 });
  }

  // Remove leading slash or path parts if any
  const cleanFilename = path.basename(filename);

  try {
    const filePath = path.join(process.cwd(), "public", "uploads", cleanFilename);
    await unlink(filePath);
  } catch (err) {
    console.error("Failed to delete file from disk:", err);
  }

  await deleteChunksByFilePath({ filePath: cleanFilename });

  return Response.json({ success: true });
}
