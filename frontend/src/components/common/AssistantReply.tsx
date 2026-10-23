import type { ReactNode } from "react";
import { parseReplyBlocks, splitInlineSegments } from "../../utils/replyText";

function withCitations(text: string, keyPrefix: string): ReactNode[] {
  return splitInlineSegments(text).map((segment, index) =>
    segment.kind === "citation" ? (
      <sup key={`${keyPrefix}-${index}`} className="reply-citation">
        [{segment.value}]
      </sup>
    ) : (
      segment.value
    )
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
 */
export function AssistantReply({ content }: { content: string }) {
  const blocks = parseReplyBlocks(content);
  if (!blocks.length) return null;

  return (
    <>
      {blocks.map((block, index) => {
        const key = `b${index}`;
        if (block.kind === "label") {
          return (
            <div key={key} className="reply-section-label">
              {withCitations(block.text, key)}
            </div>
          );
        }
        if (block.kind === "list") {
          const items = block.items.map((item, itemIndex) => (
            <li key={`i${itemIndex}`} className="reply-list-item">
              {withCitations(item, `${key}-${itemIndex}`)}
            </li>
          ));
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
            {withCitations(block.text, key)}
          </p>
        );
      })}
    </>
  );
}
