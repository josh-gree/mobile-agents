import { query } from "@anthropic-ai/claude-agent-sdk";

export const FILE_EDITING_TOOLS = ["Read", "Edit", "Write", "Glob", "Grep"];

export function buildPrompt(title, body) {
  if (!title || !body) {
    throw new Error("Title and body are required");
  }

  const systemInstructions = `You are a code editing agent. Your task is to make changes to the codebase.

IMPORTANT: You MUST use the file editing tools (Read, Edit, Write, Glob, Grep) to complete your task.
- Use Glob to find files by pattern
- Use Grep to search for code
- Use Read to read file contents
- Use Edit to modify existing files
- Use Write to create new files

Do NOT just describe what changes should be made - actually make them using the tools.`;

  return `${systemInstructions}\n\n# ${title}\n\n${body}`;
}

export async function runClaude(prompt, options = {}) {
  const defaultOptions = {
    permissionMode: "bypassPermissions",
    maxTurns: 10,
    tools: FILE_EDITING_TOOLS
  };

  const result = await query({
    prompt,
    options: { ...defaultOptions, ...options }
  });

  return result;
}

export async function* streamMessages(result) {
  for await (const message of result) {
    yield message;
  }
}
