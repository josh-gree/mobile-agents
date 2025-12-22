#!/usr/bin/env node

import { buildPrompt, runClaude } from "../../src/claude-runner.mjs";

const issueTitle = process.env.ISSUE_TITLE;
const issueBody = process.env.ISSUE_BODY;
const apiKey = process.env.ANTHROPIC_API_KEY;

if (!apiKey) {
  console.error("Error: ANTHROPIC_API_KEY environment variable is required");
  process.exit(1);
}

if (!issueTitle || !issueBody) {
  console.error("Error: ISSUE_TITLE and ISSUE_BODY environment variables are required");
  process.exit(1);
}

try {
  const prompt = buildPrompt(issueTitle, issueBody);
  const result = await runClaude(prompt);

  for await (const message of result) {
    console.log(JSON.stringify(message));
  }

  process.exit(0);
} catch (error) {
  console.error("Error running Claude:", error.message);
  process.exit(1);
}
