
import { insertChunks } from "@/app/db";
import { getPdfContentFromUrl } from "@/utils/pdf";
import { RecursiveCharacterTextSplitter } from "@langchain/textsplitters";
import { writeFile } from "node:fs/promises";
import path from "path";

export async function POST(request: Request) {
  const { searchParams } = new URL(request.url);
  const filename = searchParams.get("filename");

  let session = { user: { email: 'local@example.com' } };
  const { user } = session;

  if (request.body === null || !filename) {
    return new Response("Request body is empty or filename missing", { status: 400 });
  }

  const uploadDir = path.join(process.cwd(), "public", "uploads");
  const filePath = path.join(uploadDir, filename);
  
  const arrayBuffer = await request.arrayBuffer();
  const buffer = Buffer.from(arrayBuffer);
  await writeFile(filePath, buffer);

  try {
    const pdfData = await require("pdf-parse")(buffer);
    const content = pdfData.text || "";
    
    const textSplitter = new RecursiveCharacterTextSplitter({
      chunkSize: 1000,
    });
    const chunkedContent = await textSplitter.createDocuments([content]);

    await insertChunks({
      chunks: chunkedContent.map((chunk, i) => ({
        id: `${user.email}/${filename}/${i}`,
        filePath: filename,
        content: chunk.pageContent,
        embedding: [],
      })),
    });
  } catch (e) {
    console.error("PDF parse error:", e);
  }

  return Response.json({ url: `/uploads/${filename}` });
}
