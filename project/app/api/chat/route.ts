import { customModel } from "@/ai";
import { createMessage, getChunksByFilePaths } from "@/app/db";
import { streamText } from "ai";

export async function POST(request: Request) {
  const { id, messages, selectedFilePathnames } = await request.json();

  const session = { user: { email: 'local@example.com' } };

  let messagesToSend = [...messages];

  if (selectedFilePathnames && selectedFilePathnames.length > 0) {
    const chunks = await getChunksByFilePaths({ filePaths: selectedFilePathnames });
    if (chunks && chunks.length > 0) {
      const fileContext = chunks.map((c) => c.content).join("\n\n---\n\n");
      messagesToSend.push({
        role: "system",
        content: `Selected Document Context (${selectedFilePathnames.join(", ")}):\n${fileContext}`,
      });
    }
  }

  const result = streamText({
    model: customModel,
    system:
      "you are a friendly assistant! keep your responses concise and helpful.",
    messages: messagesToSend,
    onFinish: async ({ text }) => {
      await createMessage({
        id,
        messages: [...messages, { role: "assistant", content: text }],
        author: session.user?.email!,
      });
    },
  });

  return result.toDataStreamResponse({});
}
