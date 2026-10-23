/**
 * Plain-text AI reply formatting rules.
 *
 * This module is deliberately dependency-free and React-free. It holds the
 * *rules* only (normalization, block parsing, speech text, and the `[n]` ->
 * source lookup) so the web (`frontend/src/components/common/AssistantReply.tsx`)
 * and the mobile (`mobile/src/components/AssistantReply.tsx`) renderers can each
 * build their own platform nodes from the exact same structure.
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

/**
 * One retrieved evidence item, as sent by the backend alongside a reply.
 *
 * The array is 1:1 with the reply's evidence numbering — `[n]` is `sources[n-1]`
 * — and every entry carries an explicit `index` so a reordered array can still
 * be resolved. URLs may repeat and may be empty, so nothing here may assume a
 * marker is linkable.
 */
export interface ReplySource {
  index?: number;
  name?: string;
  title?: string;
  url?: string;
}

/** One row of the reference strip shown under a reply. */
export interface ReplySourceLink {
  /** The href exactly as retrieved, only trimmed — never rewritten. */
  url: string;
  /** Scheme-less host shown first, e.g. "who.int". */
  domain: string;
  /** The source's own words: title, then name, then the domain again. */
  label: string;
  /** The `[n]` of the lowest marker that points at this URL. */
  marker: number;
}

/** `[1]`, `[12]` — the inline citation shape the prompt asks for. */
const CITATION_RE = /\[\d{1,2}\]/g;

/** A bullet line: `- item` / `* item` / `+ item` / `• item` / `· item`. */
const BULLET_RE = /^[-*+•·]\s+(.*)$/;
/** An ordered line: `1. item` / `2) item` (the mock reply already uses these). */
const NUMBERED_RE = /^\d{1,2}[.)]\s+(.*)$/;

/** How terse a label line may be before we stop trusting it as a heading. */
const MAX_LABEL_CHARS = 72;
const MAX_LABEL_WORDS_COLON = 12;
const MAX_LABEL_WORDS_BARE = 6;

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
    .filter((line) => !/^\s*([-*_])[ \t]*(?:\1[ \t]*){2,}$/.test(line)) // horizontal rules: ---, *** ___, - - -
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

/** Trimmed string-or-nothing, for fields the backend may send as null/undefined. */
function trimmed(value: string | null | undefined): string {
  return typeof value === "string" ? value.trim() : "";
}

/** `[1]` -> 1; anything that is not a positive integer is not a real marker. */
function markerNumber(value: string | number | null | undefined): number {
  const parsed = typeof value === "number" ? value : Number.parseInt(String(value ?? ""), 10);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 0;
}

/**
 * The source a `[n]` marker points at: strictly `sources[n-1]`, except when that
 * entry's own `index` disagrees with `n` (an array that came back reordered), in
 * which case the entry stamped with that index wins. Returns `null` when nothing
 * matches — out-of-range markers, `[0]`, an empty array — so the caller falls
 * back to plain, unlinked text instead of guessing at a source.
 */
export function sourceForMarker(
  sources: readonly ReplySource[] | null | undefined,
  marker: string | number | null | undefined
): ReplySource | null {
  if (!sources || !sources.length) return null;
  const wanted = markerNumber(marker);
  if (!wanted) return null;

  const positional = sources[wanted - 1];
  if (positional && (positional.index === undefined || positional.index === wanted)) {
    return positional;
  }
  return sources.find((source) => source && source.index === wanted) ?? null;
}

/**
 * Display host for a source URL ("www.who.int" -> "who.int"). Parsed by hand,
 * not with `new URL()`: React Native's runtime does not reliably provide it,
 * and this module is shared with mobile.
 */
export function sourceDomain(url: string | null | undefined): string {
  const href = trimmed(url);
  if (!href) return "";
  const host = /^[a-zA-Z][a-zA-Z0-9+.-]*:\/\/(?:[^/?#@]*@)?([^/?#:]+)/.exec(href)?.[1] ?? href.split(/[/?#]/)[0];
  return String(host).toLowerCase().replace(/^www\./, "");
}

/** Two spellings of the same target: ignoring fragment, trailing slash, case. */
function sourceUrlKey(url: string): string {
  return url.split("#")[0].replace(/\/+$/, "").toLowerCase();
}

/** Which markers the reply actually cites: "see [2] then [1]" returns [2, 1]. */
export function citedMarkers(raw: string | null | undefined): number[] {
  const text = normalizeReplyText(raw);
  const found: number[] = [];
  const pattern = /\[(\d{1,3})\]/g;
  let match = pattern.exec(text);
  while (match) {
    const marker = Number(match[1]);
    if (marker > 0 && !found.includes(marker)) found.push(marker);
    match = pattern.exec(text);
  }
  return found;
}

/**
 * The reference strip: every *distinct usable* URL, in citation order. Retrieval
 * can return the same page for two markers, and an entry without a URL cannot be
 * opened, so it appears nowhere — which is why this can be empty even when the
 * response carries sources.
 *
 * Pass the reply's `citedMarkers` and only the pages the answer actually points
 * at are listed; everything else the search returned stays out of the patient's
 * view.
 */
export function sourceLinksForDisplay(
  sources: readonly ReplySource[] | null | undefined,
  cited?: readonly number[] | null
): ReplySourceLink[] {
  if (!sources || !sources.length) return [];

  const byUrl = new Map<string, { link: ReplySourceLink; markers: number[] }>();
  sources.forEach((source, position) => {
    const url = trimmed(source?.url);
    if (!url) return;

    const marker = markerNumber(source?.index) || position + 1;
    const key = sourceUrlKey(url);
    const group = byUrl.get(key);
    if (group) {
      // Several markers can share a page: keep the lowest number for that row.
      group.markers.push(marker);
      if (marker < group.link.marker) group.link.marker = marker;
      return;
    }

    const domain = sourceDomain(url);
    byUrl.set(key, {
      markers: [marker],
      link: {
        url,
        domain,
        label: trimmed(source?.title) || trimmed(source?.name) || domain,
        marker,
      },
    });
  });

  const groups = [...byUrl.values()];
  if (!cited) return groups.map((group) => group.link);

  const wanted = new Set(cited);
  return groups
    .filter((group) => group.markers.some((marker) => wanted.has(marker)))
    .map((group) => {
      // Show the number the reader actually sees next to the sentence.
      const shown = group.markers
        .filter((marker) => wanted.has(marker))
        .sort((a, b) => a - b)[0];
      return shown === undefined ? group.link : { ...group.link, marker: shown };
    });
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
 * "What this could mean:", "Red flags", "What you can do now", "Ibyo wagera".
 *
 * A colon-terminated line is always treated as a label — that is the shape the
 * prompt asks for. A label *without* a colon is only trusted when the very next
 * content is a list: word count alone cannot separate the heading "Red flags"
 * from the first half of a hard-wrapped sentence such as "Shortness of breath
 * when walking / improved after rest", and mislabelling prose would restyle a
 * patient's sentence as a heading. A bare line heading prose therefore stays a
 * paragraph, which is the safe direction (nothing is lost, only emphasised).
 */
function isSectionLabel(line: string, headsList: boolean): boolean {
  const text = line.trim();
  if (!text || text.length > MAX_LABEL_CHARS) return false;
  if (matchListLine(text)) return false;
  if (/[.!?…]$/.test(text)) return false;

  const words = text.split(/\s+/);
  if (/:\s*$/.test(text)) return words.length <= MAX_LABEL_WORDS_COLON;
  return headsList && words.length <= MAX_LABEL_WORDS_BARE;
}

/** Turn a reply into ordered display blocks. */
export function parseReplyBlocks(raw: string | null | undefined): ReplyBlock[] {
  const normalized = normalizeReplyText(raw);
  if (!normalized) return [];

  const groups = normalized
    .split(/\n{2,}/)
    .map((group) => group.split("\n").map((line) => line.trim()).filter(Boolean))
    .filter((lines) => lines.length > 0);

  const blocks: ReplyBlock[] = [];

  groups.forEach((lines, groupIndex) => {
    const nextGroup = groups[groupIndex + 1];
    // Does the content this line introduces read as a list? Look at the next
    // line, or — for a label alone in its own block — the next block's first.
    const headsList = lines.length > 1
      ? Boolean(matchListLine(lines[1]))
      : Boolean(nextGroup && matchListLine(nextGroup[0]));

    let index = 0;
    if (isSectionLabel(lines[0], headsList)) {
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
  });

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
