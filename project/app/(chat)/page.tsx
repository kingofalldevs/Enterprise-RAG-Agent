import { Chat } from "@/components/chat";
import { generateId } from "ai";

export default async function Page() {
  const session = { user: { email: 'local@example.com' } };
  return <Chat id={generateId()} initialMessages={[]} session={session as any} />;
}
