import React from "react";
import { StyleSheet, Text, View } from "react-native";
import { parseReplyBlocks, splitInlineSegments } from "../utils/replyText";

const DEFAULT_BODY_COLOR = "#1e293b";
const DEFAULT_LABEL_COLOR = "#334155";
const DEFAULT_CITATION_COLOR = "#0369a1";

/**
 * Renders an assistant `reply` blob (blank-line separated sections, short
 * section labels, `-` bullets, inline `[n]` citations) inside a chat bubble.
 *
 * The parsing/normalization rules live in `src/utils/replyText.ts`, which is
 * kept byte-identical with the web copy so a patient reads the same structure on
 * both platforms; only the emitted nodes differ (`<Text>` spans instead of DOM).
 * Plain-text-safe: nodes are built from strings only.
 */
export function AssistantReply({
  content,
  bodyColor = DEFAULT_BODY_COLOR,
  labelColor = DEFAULT_LABEL_COLOR,
  citationColor = DEFAULT_CITATION_COLOR,
}: {
  content: string;
  bodyColor?: string;
  labelColor?: string;
  citationColor?: string;
}) {
  const blocks = parseReplyBlocks(content);
  if (!blocks.length) return null;

  const inline = (text: string) =>
    splitInlineSegments(text).map((segment, index) =>
      segment.kind === "citation" ? (
        <Text
          key={`c${index}`}
          style={[styles.citation, { color: citationColor }]}
        >
          {`[${segment.value}]`}
        </Text>
      ) : (
        segment.value
      )
    );

  return (
    <View style={styles.root}>
      {blocks.map((block, index) => {
        if (block.kind === "label") {
          return (
            <Text key={`l${index}`} style={[styles.label, { color: labelColor }]}>
              {inline(block.text)}
            </Text>
          );
        }

        if (block.kind === "list") {
          return (
            <View key={`u${index}`} style={styles.list}>
              {block.items.map((item, itemIndex) => (
                <View key={`i${itemIndex}`} style={styles.listRow}>
                  <Text style={[styles.marker, { color: bodyColor }]}>
                    {block.ordered ? `${itemIndex + 1}.` : "•"}
                  </Text>
                  <Text style={[styles.item, { color: bodyColor }]}>
                    {inline(item)}
                  </Text>
                </View>
              ))}
            </View>
          );
        }

        return (
          <Text key={`p${index}`} style={[styles.paragraph, { color: bodyColor }]}>
            {inline(block.text)}
          </Text>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  root: { gap: 8 },
  paragraph: { fontSize: 15, lineHeight: 22 },
  label: { fontSize: 13.5, lineHeight: 20, fontWeight: "700", letterSpacing: 0.2 },
  list: { gap: 4 },
  listRow: { flexDirection: "row", alignItems: "flex-start" },
  marker: { width: 18, fontSize: 15, lineHeight: 22 },
  item: { flex: 1, fontSize: 15, lineHeight: 22 },
  citation: { fontSize: 11, lineHeight: 16, fontWeight: "700" },
});
