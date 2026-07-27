import { getChatsByUser } from "@/app/db";

export async function GET() {
  let session = { user: { email: 'local@example.com' } };

  const chats = await getChatsByUser({ email: session.user.email! });
  return Response.json(chats);
}
