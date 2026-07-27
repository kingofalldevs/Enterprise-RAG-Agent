import { drizzle } from "drizzle-orm/better-sqlite3";
import Database from "better-sqlite3";
import { desc, eq, inArray } from "drizzle-orm";
import { chat, chunk } from "@/schema";

let sqlite: Database.Database | null = null;
let db: ReturnType<typeof drizzle> | null = null;

function getDb() {
  if (!db) {
    sqlite = new Database("sqlite.db");
    db = drizzle(sqlite);
  }
  return db;
}

export async function createMessage({
  id,
  messages,
  author,
}: {
  id: string;
  messages: any;
  author: string;
}) {
  const selectedChats = await getDb().select().from(chat).where(eq(chat.id, id));

  if (selectedChats.length > 0) {
    return await getDb()
      .update(chat)
      .set({
        messages: messages,
      })
      .where(eq(chat.id, id));
  }

  return await getDb().insert(chat).values({
    id,
    createdAt: new Date(),
    messages: messages,
    author,
  });
}

export async function getChatsByUser({ email }: { email: string }) {
  return await getDb()
    .select()
    .from(chat)
    .where(eq(chat.author, email))
    .orderBy(desc(chat.createdAt));
}

export async function getChatById({ id }: { id: string }) {
  const [selectedChat] = await getDb().select().from(chat).where(eq(chat.id, id));
  return selectedChat;
}

export async function insertChunks({ chunks }: { chunks: any[] }) {
  return await getDb().insert(chunk).values(chunks);
}

export async function getChunksByFilePaths({
  filePaths,
}: {
  filePaths: Array<string>;
}) {
  return await getDb()
    .select()
    .from(chunk)
    .where(inArray(chunk.filePath, filePaths));
}

export async function deleteChunksByFilePath({
  filePath,
}: {
  filePath: string;
}) {
  return await getDb().delete(chunk).where(eq(chunk.filePath, filePath));
}
