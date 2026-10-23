import { describe, expect, it } from "vitest";
import {
  normalizeReplyText,
  parseReplyBlocks,
  replyToPlainText,
  splitInlineSegments,
} from "./replyText";

// Shapes modelled on backend/ai/services/ai_service.py::_mock_conversation,
// which already joins sections with "\n\n" and emits "[n]" citation lines.
const MOCK_REPLY = [
  "Warning signs you mentioned need prompt medical review: chest pain.",
  "",
  "Thanks — I've noted: chest pain, fever.",
  "",
  "From trusted sources:",
  "[1] Acute coronary syndrome — WHO: Chest pain needs same-day assessment.",
  "[2] Malaria — MoH Rwanda: Fever with chest pain warrants testing.",
  "",
  "To help me understand better:",
  "1. Did it start during exercise?",
  "2. Do you have high blood pressure?",
  "",
  "Seek in-person care today.",
].join("\n");

const CHATGPT_STYLE_REPLY = [
  "Based on what you've described, there are a few likely explanations.",
  "",
  "**What this could mean:**",
  "- **Viral infection** — most common cause [1]",
  "- Allergic rhinitis [2]",
  "",
  "### Red flags",
  "- `difficulty breathing`",
  "- confusion",
  "",
  "Ibyo wagera: karibu gufata umuti w'itsinda.",
  "",
  "---",
  "",
  "Read more at [WHO guidance](https://www.who.int/conditions).",
].join("\n");

describe("normalizeReplyText", () => {
  it("strips leaked bold, heading, code and rule markers", () => {
    const text = normalizeReplyText(CHATGPT_STYLE_REPLY);
    expect(text).not.toMatch(/\*\*/);
    expect(text).not.toContain("###");
    expect(text).not.toContain("`");
    expect(text).not.toContain("---");
    expect(text).toContain("What this could mean:");
    expect(text).toContain("Red flags");
    expect(text).toContain("difficulty breathing");
  });

  it("keeps bracketed citations but unwraps markdown links", () => {
    const text = normalizeReplyText("[Read the WHO note](https://www.who.int/x) for details [1].");
    expect(text).toBe("Read the WHO note for details [1].");
  });

  it("preserves snake_case field names instead of eating underscores", () => {
    const text = normalizeReplyText(
      "Compare possible_conditions, warning_signs and recommended_next_step."
    );
    expect(text).toBe("Compare possible_conditions, warning_signs and recommended_next_step.");
  });

  it("removes unmatched bold leftovers and collapses spacing", () => {
    expect(normalizeReplyText("Half** open bold here")).toBe("Half open bold here");
    expect(normalizeReplyText("trailing   spaces \nnext line")).toBe("trailing spaces\nnext line");
  });

  it("is empty-safe", () => {
    expect(normalizeReplyText("")).toBe("");
    expect(normalizeReplyText(null)).toBe("");
    expect(normalizeReplyText(undefined)).toBe("");
  });
});

describe("parseReplyBlocks", () => {
  it("classifies section labels, bullets and citation lines from the mock reply", () => {
    const blocks = parseReplyBlocks(MOCK_REPLY);
    expect(blocks.map((b) => b.kind)).toEqual([
      "paragraph",
      "paragraph",
      "label",
      "list",
      "label",
      "list",
      "paragraph",
    ]);

    const sources = blocks[3];
    expect(sources.kind === "list" && sources.ordered).toBe(false);
    expect(sources.kind === "list" && sources.items).toHaveLength(2);

    const questions = blocks[5];
    expect(questions.kind === "list" && questions.ordered).toBe(true);
    expect(questions.kind === "list" && questions.items[0]).toBe("Did it start during exercise?");
  });

  it("never shows markdown punctuation in parsed blocks", () => {
    const blocks = parseReplyBlocks(CHATGPT_STYLE_REPLY);
    const flat = JSON.stringify(blocks);
    expect(flat).not.toMatch(/\\*\\*/);
    expect(flat).not.toContain("###");
    expect(flat).not.toContain("```");
    expect(flat).not.toContain("---");

    const labels = blocks.filter((b) => b.kind === "label").map((b) => (b as { text: string }).text);
    expect(labels).toEqual(["What this could mean:", "Red flags"]);
  });

  it("treats a bare Kinyarwanda label heading a list as a label", () => {
    const blocks = parseReplyBlocks("Ibyo wagera\n- Gufata amazi\n- Kuruhuka");
    expect(blocks[0].kind).toBe("label");
    expect(blocks[1].kind).toBe("list");
  });

  it("keeps a bare short line heading prose as a paragraph, not a heading", () => {
    const blocks = parseReplyBlocks("Ibyo wagera\nKaribu gufata umuti w'itsinda.");
    expect(blocks.map((b) => b.kind)).toEqual(["paragraph"]);
  });

  it("recognises a label that sits alone above a blank-line separated list", () => {
    const blocks = parseReplyBlocks("Red flags\n\n- Chest pain\n- Confusion");
    expect(blocks[0].kind).toBe("label");
    expect(blocks[1].kind === "list" && blocks[1].items).toEqual(["Chest pain", "Confusion"]);
  });

  it("keeps a lone sentence ending in a period as a paragraph", () => {
    const blocks = parseReplyBlocks("Call your doctor.");
    expect(blocks).toEqual([{ kind: "paragraph", text: "Call your doctor." }]);
  });

  it("preserves single line breaks inside one paragraph", () => {
    const blocks = parseReplyBlocks(
      "The fever started three days ago\nand it spikes every evening\n\nRest and fluids."
    );
    expect(blocks).toHaveLength(2);
    expect(blocks[0]).toEqual({
      kind: "paragraph",
      text: "The fever started three days ago\nand it spikes every evening",
    });
    expect(blocks[1]).toEqual({ kind: "paragraph", text: "Rest and fluids." });
  });

  it("handles bullet markers - * and • alike", () => {
    for (const marker of ["-", "*", "•", "·", "+"]) {
      const blocks = parseReplyBlocks(`Do this:\n${marker} one\n${marker} two`);
      const list = blocks[1] as { kind: string; items?: string[] };
      expect({ marker, kind: list.kind, items: list.items }).toEqual({
        marker,
        kind: "list",
        items: ["one", "two"],
      });
    }
  });

  it("does not merge two asterisk bullets into one italic span", () => {
    expect(normalizeReplyText("* one\n* two")).toBe("* one\n* two");
    expect(normalizeReplyText("*rapid breathing* settled")).toBe("rapid breathing settled");
  });

  it("returns no blocks for empty input", () => {
    expect(parseReplyBlocks("")).toEqual([]);
    expect(parseReplyBlocks("   \n\n  ")).toEqual([]);
  });
});

describe("splitInlineSegments", () => {
  it("isolates citation markers", () => {
    expect(splitInlineSegments("Fever [1] and cough [12] today")).toEqual([
      { kind: "text", value: "Fever " },
      { kind: "citation", value: "1" },
      { kind: "text", value: " and cough " },
      { kind: "citation", value: "12" },
      { kind: "text", value: " today" },
    ]);
  });

  it("leaves plain text untouched", () => {
    expect(splitInlineSegments("No citations here")).toEqual([
      { kind: "text", value: "No citations here" },
    ]);
  });
});

describe("replyToPlainText", () => {
  it("is what TTS receives: no markup, no bullets, no citations", () => {
    const spoken = replyToPlainText(CHATGPT_STYLE_REPLY);
    expect(spoken).not.toContain("*");
    expect(spoken).not.toContain("#");
    expect(spoken).not.toContain("`");
    expect(spoken).not.toContain("[1]");
    expect(spoken).not.toContain("[2]");
    expect(spoken).not.toContain("•");
    expect(spoken).not.toContain("(");
    expect(spoken).toContain("Viral infection — most common cause");
    expect(spoken).toContain("Read more at WHO guidance.");
  });

  it("drops a heading colon so it is not read as punctuation", () => {
    const spoken = replyToPlainText("What you can do now:\n- Rest");
    expect(spoken).toBe("What you can do now\nRest");
  });

  it("keeps every spoken idea from the mock reply", () => {
    const spoken = replyToPlainText(MOCK_REPLY);
    expect(spoken).toContain("chest pain, fever");
    expect(spoken).toContain("Acute coronary syndrome");
    expect(spoken).toContain("Did it start during exercise?");
    expect(spoken).toContain("Seek in-person care today.");
    expect(spoken).not.toMatch(/\[\d/);
  });

  it("still speaks an error string with no structure", () => {
    expect(replyToPlainText("The assessment failed.")).toBe("The assessment failed.");
  });
});
