import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import {
  citedMarkers,
  parseReplyBlocks,
  sourceDomain,
  sourceForMarker,
  sourceLinksForDisplay,
  splitInlineSegments,
  type ReplySource,
} from "../../utils/replyText";

/**
 * A `[n]` marker with a retrieved URL behind it becomes a real link, ChatGPT
 * style; the tooltip and the accessible name say which page it opens instead of
 * reading out a bare bracket.
 */
function citationNode(
  marker: string,
  keyPrefix: string,
  index: number,
  sources: readonly ReplySource[] | null | undefined
): ReactNode {
  const key = `${keyPrefix}-${index}`;
  const source = sourceForMarker(sources, marker);
  const url = (source?.url ?? "").trim();

  if (!url) {
    // Out-of-range marker, or a source with no URL: inert superscript, as before.
    return (
      <sup key={key} className="reply-citation">
        [{marker}]
      </sup>
    );
  }

  const host = sourceDomain(url);
  const name = (source?.title || source?.name || "").trim();
  const hint = name ? `${name} — ${host}` : host;

  return (
    <a
      key={key}
      className="reply-citation-link"
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      title={hint}
      aria-label={`[${marker}] ${hint}`}
    >
      <sup className="reply-citation">[{marker}]</sup>
    </a>
  );
}

function withCitations(
  text: string,
  keyPrefix: string,
  sources: readonly ReplySource[] | null | undefined
): ReactNode[] {
  return splitInlineSegments(text).map((segment, index) =>
    segment.kind === "citation"
      ? citationNode(segment.value, keyPrefix, index, sources)
      : segment.value
  );
}

/**
 * Renders an assistant `reply` blob (blank-line separated sections, short
 * section labels, `-` bullets, inline `[n]` citations) as readable blocks.
 *
 * Dependency-free and plain-text-safe: every node is built from strings, never
 * from HTML. Pair with `.chatgpt-msg-content--rich` on the wrapping element so
 * the wrapper's `white-space: pre-wrap` applies per paragraph instead of around
 * the whole structured reply.
 *
 * When the response's `sources` are passed too, each `[n]` becomes a link to the
 * page it was retrieved from and a compact reference strip appears under the
 * reply. Text-to-speech is untouched by either: the pages speak
 * `replyToPlainText(content)`, which drops the markers and never sees this DOM.
 */
export function AssistantReply({
  content,
  sources,
  isTyping = false,
}: {
  content: string;
  sources?: readonly ReplySource[] | null;
  isTyping?: boolean;
}) {
  const { t } = useTranslation();
  const blocks = parseReplyBlocks(content);
  if (!blocks.length) {
    if (isTyping) {
      return (
        <p className="reply-paragraph">
          <span className="chatgpt-typing-cursor" aria-hidden="true" />
        </p>
      );
    }
    return null;
  }

  const references = sourceLinksForDisplay(sources, citedMarkers(content));

  const inline = (text: string, key: string) => withCitations(text, key, sources);

  return (
    <>
      {blocks.map((block, index) => {
        const key = `b${index}`;
        const isLast = isTyping && index === blocks.length - 1;
        const cursor = isLast ? (
          <span className="chatgpt-typing-cursor" aria-hidden="true" />
        ) : null;

        if (block.kind === "label") {
          return (
            <div key={key} className="reply-section-label">
              {inline(block.text, key)}
              {cursor}
            </div>
          );
        }
        if (block.kind === "list") {
          const items = block.items.map((item, itemIndex) => {
            const isLastItem = isLast && itemIndex === block.items.length - 1;
            return (
              <li key={`i${itemIndex}`} className="reply-list-item">
                {inline(item, `${key}-${itemIndex}`)}
                {isLastItem ? cursor : null}
              </li>
            );
          });
          const className = `reply-list${block.ordered ? " reply-list--ordered" : ""}`;
          return block.ordered ? (
            <ol key={key} className={className}>
              {items}
            </ol>
          ) : (
            <ul key={key} className={className}>
              {items}
            </ul>
          );
        }
        return (
          <p key={key} className="reply-paragraph">
            {inline(block.text, key)}
            {cursor}
          </p>
        );
      })}

      {!isTyping && references.length > 0 && (
        <div className="reply-references">
          <div className="reply-references-title">{t("chat.referencesTitle")}</div>
          <ul className="reply-reference-list">
            {references.map((reference) => (
              <li key={`${reference.marker}-${reference.url}`} className="reply-reference-item">
                <a
                  className="reply-reference-link"
                  href={reference.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  title={reference.url}
                >
                  <span className="reply-reference-marker">[{reference.marker}]</span>
                  <span className="reply-reference-domain">{reference.domain}</span>
                  {reference.label && reference.label !== reference.domain ? (
                    <span className="reply-reference-name">{reference.label}</span>
                  ) : null}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}
