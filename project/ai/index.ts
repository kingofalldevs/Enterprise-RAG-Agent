import { createOpenAI } from "@ai-sdk/openai";

const localPythonAgent = createOpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: "dummy-key",
});

export const customModel = localPythonAgent("nexus-agent");
