import { Message } from "ai";
import { Chat } from "@/schema";
import { getChatById } from "@/app/db";
import { notFound } from "next/navigation";
import { Chat as PreviewChat } from "@/components/chat";

export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const chatFromDb = await getChatById({ id });

  if (!chatFromDb) {
    notFound();
  }

  // type casting
  const chat: Chat = {
    ...chatFromDb,
    messages: chatFromDb.messages as Message[],
  };

  const session = { user: { email: 'local@example.com' } };

  return (
    <PreviewChat
      id={chat.id}
      initialMessages={chat.messages}
      session={session as any}
    />
  );
}
