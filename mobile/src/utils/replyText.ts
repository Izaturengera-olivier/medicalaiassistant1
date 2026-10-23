/**
 * Plain-text AI reply formatting rules.
 *
 * This module is deliberately dependency-free and React-free. It holds the
 * *rules* only (normalization, block parsing, speech text) so the web
 * (`frontend/src/components/common/AssistantReply.tsx`) and the mobile
 * (`mobile/src/components/AssistantReply.tsx`) renderers can each build their
 * own platform nodes from the exact same structure.
 *
 * KEEP THIS FILE BYTE-IDENTICAL WITH mobile/src/utils/replyText.ts.
 * The two apps are separate packages with no shared workspace, so the rules are
 * duplicated by copy; any divergence changes what a patient sees on one
 * platform only. The backend assistant `reply` is a single plain-text blob
 * (sections separated by blank lines, short section labels, `-` bullets,
 * inline `[n]` citations), and the LLM sometimes leaks markdown into it.
 */

export type ReplyBlock =
  | { kind: "paragraph"; text: string }
  | { kind: "label"; text: string }
  | { kind: "list"; ordered: boolean; items: string[] };

export type InlineSegment =
  | { kind: "text"; value: string }
  | { kind: "citation"; value: string };

/** `[1]`, `[12]` — the inline citation shape the prompt asks for. */
const CITATION_RE = /\[\d{1,2}\]/g;

/** A bullet line: `- item` / `* item` / `+ item` / `• item` / `· item`. */
const BULLET_RE = /^[-*+•·]\s+(.*)$/;
/** An ordered line: `1. item` / `2) item` (the mock reply already uses these). */
const NUMBERED_RE = /^\d{1,2}[.)]\s+(.*)$/;

/** How terse a label line may be before we stop trusting it as a heading. */
const MAX_LABEL_CHARS = 72;
const MAX_LABEL_WORDS_COLON = 12;
const MAX_LABEL_WORDS_BARE = 5;

function collapseInlineWhitespace(text: string): string {
  return text
    .replace(/[ \t]+\n/g, "\n")
    .replace(/[ \t]{2,}/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/**
 * Normalize a reply for display so a leaked markdown token can never appear as
 * literal punctuation. This is *not* a markdown parser: every rule removes a
 * marker and keeps the human-readable text inside it, so what is shown is still
 * plain text.
 */
export function normalizeReplyText(raw: string | null | undefined): string {
  if (!raw) return "";

  const lines = String(raw)
    .replace(/\r\n?/g, "\n")
    .replace(/[\u00a0\u200b]/g, " ")
    .split("\n")
    .filter((line) => !/^\s*(?:[-*_])\s*(?:\1\s*){2,}$/.test(line)) // horizontal rules: ---, *** ___
    .map((line) =>
      line
        .replace(/^\s{0,3}#{1,6}\s+/, "") // "### Section" -> "Section"
        .replace(/^\s{0,3}#{1,6}\s*$/, "") // bare "###"
        .replace(/^\s{0,3}>\s+/, "") // blockquote "> text"
    );

  const text = lines
    .join("\n")
    // fenced code blocks: keep the code, drop the fences
    .replace(/```[\s\S]*?```/g, (fence) => fence.replace(/```[a-zA-Z0-9+-]*\n?/g, ""))
    // inline code: `amoxicillin` -> amoxicillin
    .replace(/`([^`\n]*)`/g, "$1")
    // bold + italic, then bold, then italic. `[ \t]` (never `\s`) and the
    // no-newline character classes keep these from bridging two separate
    // `* bullet` lines into one bogus italic span. `__`/`_` require a non-word
    // left boundary so API-ish names (possible_conditions) survive untouched.
    .replace(/\*\*\*[ \t]*([^*\n]+?)[ \t]*\*\*\*/g, "$1")
    .replace(/\*\*[ \t]*([^*\n]+?)[ \t]*\*\*/g, "$1")
    .replace(/(^|[^\w])__[ \t]*([^_\n]+?)[ \t]*__(?![\w])/g, "$1$2")
    .replace(/(^|[^\w])_[ \t]*([^_\n]+?)[ \t]*_(?![\w])/g, "$1$2")
    .replace(/(^|[^\w*])\*[ \t]*([^*\n]+?)[ \t]*\*(?!\*)/g, "$1$2")
    .replace(/~~([^~\n]+)~~/g, "$1")
    // links: [WHO guidance](https://...) -> WHO guidance. Citations have no
    // trailing "(" so `[1]` is never touched here.
    .replace(/\[([^\]\n]+)\]\((?:[^()\s]|\([^()]*\))*\)/g, "$1")
    .replace(/<(https?:\/\/[^>\n]+)>/gi, "$1")
    // unmatched leftovers of a half-emitted pair
    .replace(/\*\*/g, "");

  return collapseInlineWhitespace(text);
}

/** Split already-normalized text into plain text and citation segments. */
export function splitInlineSegments(text: string): InlineSegment[] {
  const segments: InlineSegment[] = [];
  const re = new RegExp(CITATION_RE.source, "g");
  let cursor = 0;
  let match: RegExpExecArray | null;
  while ((match = re.exec(text)) !== null) {
    const before = text.slice(cursor, match.index);
    if (before) segments.push({ kind: "text", value: before });
    segments.push({ kind: "citation", value: match[0].slice(1, -1) });
    cursor = match.index + match[0].length;
  }
  const tail = text.slice(cursor);
  if (tail) segments.push({ kind: "text", value: tail });
  return segments;
}

interface ListLine {
  text: string;
  ordered: boolean;
}

/** Recognize a bullet / numbered / citation-prefixed line. */
function matchListLine(line: string): ListLine | null {
  const bullet = BULLET_RE.exec(line);
  if (bullet && bullet[1].trim()) return { text: bullet[1].trim(), ordered: false };
  const numbered = NUMBERED_RE.exec(line);
  if (numbered && numbered[1].trim()) return { text: numbered[1].trim(), ordered: true };
  // A line that *starts* with a citation is a reference entry: keep `[1]` so it
  // stays visible as a citation, but list it tidily.
  if (/^\[\d{1,2}\]\s*\S/.test(line)) return { text: line.trim(), ordered: false };
  return null;
}

/**
 * A short standalone line that titles the content under it, e.g.
 * "What this could mean:", "Red flags", "Ibyo wagera".
 *
 * Colon-terminated lines are always labels (that is the shape the prompt asks
 * for). A label without a colon is only trusted when it heads other content or
 * is very short, so an ordinary short sentence is not demoted to a heading.
 */
function isSectionLabel(line: string, headsContent: boolean): boolean {
  const text = line.trim();
  if (!text || text.length > MAX_LABEL_CHARS) return false;
  if (matchListLine(text)) return false;
  if (/[.!?…]$/.test(text)) return false;

  const words = text.split(/\s+/);
  if (/:\s*$/.test(text)) return words.length <= MAX_LABEL_WORDS_COLON;
  if (!headsContent) return false;
  return words.length <= MAX_LABEL_WORDS_BARE;
}

/** Turn a reply into ordered display blocks. */
export function parseReplyBlocks(raw: string | null | undefined): ReplyBlock[] {
  const normalized = normalizeReplyText(raw);
  if (!normalized) return [];

  const blocks: ReplyBlock[] = [];

  for (const group of normalized.split(/\n{2,}/)) {
    const lines = group
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
    if (!lines.length) continue;

    let index = 0;
    if (isSectionLabel(lines[0], lines.length > 1)) {
      blocks.push({ kind: "label", text: lines[0] });
      index = 1;
    }

    while (index < lines.length) {
      const first = matchListLine(lines[index]);
      if (first) {
        const items: string[] = [];
        while (index < lines.length) {
          const next = matchListLine(lines[index]);
          if (!next || next.ordered !== first.ordered) break;
          items.push(next.text);
          index += 1;
        }
        blocks.push({ kind: "list", ordered: first.ordered, items });
        continue;
      }

      const paragraph: string[] = [];
      while (index < lines.length && !matchListLine(lines[index])) {
        paragraph.push(lines[index]);
        index += 1;
      }
      blocks.push({ kind: "paragraph", text: paragraph.join("\n") });
    }
  }

  return blocks;
}

/** Drop citation markers and a heading colon for speech. */
function toSpeechLine(text: string): string {
  return text
    .replace(new RegExp(CITATION_RE.source, "g"), " ")
    .replace(/\s{2,}/g, " ")
    .replace(/\s+([,.;:!?])/g, "$1")
    .replace(/:\s*$/, "")
    .trim();
}

/**
 * The text handed to text-to-speech (and to any other consumer that must not
 * read formatting aloud): markdown leakage removed, list markers dropped, and
 * `[n]` citations stripped so the voice never says "bracket one".
 */
export function replyToPlainText(raw: string | null | undefined): string {
  const blocks = parseReplyBlocks(raw);
  if (!blocks.length) return toSpeechLine(normalizeReplyText(raw));

  const lines: string[] = [];
  for (const block of blocks) {
    if (block.kind === "list") {
      for (const item of block.items) {
        const spoken = toSpeechLine(item);
        if (spoken) lines.push(spoken);
      }
      continue;
    }
    const spoken = toSpeechLine(block.text);
    if (spoken) lines.push(spoken);
  }
  return lines.join("\n");
}
