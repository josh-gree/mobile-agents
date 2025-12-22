import { describe, it, expect, vi, beforeEach } from "vitest";
import { buildPrompt, runClaude, FILE_EDITING_TOOLS } from "../src/claude-runner.mjs";
import { query } from "@anthropic-ai/claude-agent-sdk";

vi.mock("@anthropic-ai/claude-agent-sdk", () => ({
  query: vi.fn()
}));

describe("buildPrompt", () => {
  it("includes system instructions and title/body", () => {
    const result = buildPrompt("My Title", "Some body text");
    expect(result).toContain("# My Title");
    expect(result).toContain("Some body text");
    expect(result).toContain("You are a code editing agent");
    expect(result).toContain("MUST use the file editing tools");
  });

  it("handles multiline body", () => {
    const body = "Line 1\nLine 2\nLine 3";
    const result = buildPrompt("Title", body);
    expect(result).toContain("# Title");
    expect(result).toContain("Line 1\nLine 2\nLine 3");
  });

  it("throws when title is missing", () => {
    expect(() => buildPrompt("", "body")).toThrow("Title and body are required");
    expect(() => buildPrompt(null, "body")).toThrow("Title and body are required");
    expect(() => buildPrompt(undefined, "body")).toThrow("Title and body are required");
  });

  it("throws when body is missing", () => {
    expect(() => buildPrompt("title", "")).toThrow("Title and body are required");
    expect(() => buildPrompt("title", null)).toThrow("Title and body are required");
    expect(() => buildPrompt("title", undefined)).toThrow("Title and body are required");
  });
});

describe("runClaude", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("calls query with prompt and default options including tools", async () => {
    const mockResult = (async function* () {
      yield { type: "message", content: "Hello" };
    })();
    query.mockReturnValue(mockResult);

    await runClaude("Test prompt");

    expect(query).toHaveBeenCalledWith({
      prompt: "Test prompt",
      options: {
        permissionMode: "bypassPermissions",
        maxTurns: 10,
        tools: FILE_EDITING_TOOLS
      }
    });
  });

  it("merges custom options with defaults", async () => {
    const mockResult = (async function* () {
      yield { type: "message", content: "Hello" };
    })();
    query.mockReturnValue(mockResult);

    await runClaude("Test prompt", { maxTurns: 5 });

    expect(query).toHaveBeenCalledWith({
      prompt: "Test prompt",
      options: {
        permissionMode: "bypassPermissions",
        maxTurns: 5,
        tools: FILE_EDITING_TOOLS
      }
    });
  });

  it("returns the result from query", async () => {
    const mockResult = (async function* () {
      yield { type: "message", content: "Hello" };
    })();
    query.mockReturnValue(mockResult);

    const result = await runClaude("Test prompt");
    const messages = [];
    for await (const msg of result) {
      messages.push(msg);
    }

    expect(messages).toEqual([{ type: "message", content: "Hello" }]);
  });
});
