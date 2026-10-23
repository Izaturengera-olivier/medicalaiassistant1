import React from "react";
import { Linking, Pressable, StyleSheet, Text, View } from "react-native";
import {
  citedMarkers,
  parseReplyBlocks,
  sourceDomain,
  sourceForMarker,
  sourceLinksForDisplay,
  splitInlineSegments,
} from "../utils/replyText";
import type { ReplySource } from "../utils/replyText";

const DEFAULT_BODY_COLOR = "#1e293b";
const DEFAULT_LABEL_COLOR = "#334155";
const DEFAULT_CITATION_COLOR = "#0369a1";

/**
 * Opens a retrieved source in the platform browser. `Linking.openURL` rejects on
 * a device that has no handler for the scheme, and a tapped citation must never
 * turn into a red error screen in front of a patient, so the failure is dropped.
 */
function openSource(url: string): void {
  void Linking.openURL(url).catch(() => undefined);
}

/**
 * Renders an assistant `reply` blob (blank-line separated sections, short
 * section labels, `-` bullets, inline `[n]` citations) inside a chat bubble.
 *
 * The parsing/normalization rules live in `src/utils/replyText.ts`, which is
 * kept byte-identical with the web copy so a patient reads the same structure on
 * both platforms; only the emitted nodes differ (`<Text>` spans instead of DOM).
 * Plain-text-safe: nodes are built from strings only.
 *
 * With `sources` the `[n]` markers open the page they were retrieved from and a
 * compact tappable reference strip appears under the reply.
 */
export function AssistantReply({
  content,
  sources,
  bodyColor = DEFAULT_BODY_COLOR,
  labelColor = DEFAULT_LABEL_COLOR,
  citationColor = DEFAULT_CITATION_COLOR,
  referenceLabel = "Sources",
}: {
  content: string;
  sources?: readonly ReplySource[] | null;
  bodyColor?: string;
  labelColor?: string;
  citationColor?: string;
  referenceLabel?: string;
}) {
  const blocks = parseReplyBlocks(content);
  if (!blocks.length) return null;

  const references = sourceLinksForDisplay(sources, citedMarkers(content));

  const inline = (text: string) =>
    splitInlineSegments(text).map((segment, index) => {
      if (segment.kind !== "citation") return segment.value;

      const marker = `[${segment.value}]`;
      const source = sourceForMarker(sources, segment.value);
      const url = (source?.url ?? "").trim();

      // Out-of-range marker, or a source with no URL: inert superscript, as before.
      if (!url) {
        return (
          <Text key={`c${index}`} style={[styles.citation, { color: citationColor }]}>
            {marker}
          </Text>
        );
      }

      // React Native 0.74's Text exposes no `link` / `onLinkPress` props, so a
      // nested Text with onPress + Linking is how a citation opens its page here.
      const name = (source?.title || source?.name || "").trim();
      return (
        <Text
          key={`c${index}`}
          style={[styles.citation, styles.citationLink, { color: citationColor }]}
          onPress={() => openSource(url)}
          accessibilityRole="link"
          accessibilityLabel={name ? `${marker} ${name}` : `${marker} ${sourceDomain(url)}`}
        >
          {marker}
        </Text>
      );
    });

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

      {references.length > 0 && (
        <View style={styles.references}>
          <Text style={styles.referencesTitle}>{referenceLabel}</Text>
          {references.map((reference) => (
            <Pressable
              key={`${reference.marker}-${reference.url}`}
              onPress={() => openSource(reference.url)}
              hitSlop={6}
              style={({ pressed }) => [styles.referenceRow, pressed && styles.referenceRowPressed]}
              accessibilityRole="link"
              accessibilityLabel={`[${reference.marker}] ${reference.domain} ${reference.label}`}
            >
              <Text style={[styles.referenceMarker, { color: citationColor }]}>
                {`[${reference.marker}]`}
              </Text>
              <Text
                style={[styles.referenceDomain, { color: citationColor }]}
                numberOfLines={1}
              >
                {reference.domain}
              </Text>
              {reference.label && reference.label !== reference.domain ? (
                <Text style={[styles.referenceName, { color: bodyColor }]} numberOfLines={1}>
                  {reference.label}
                </Text>
              ) : null}
            </Pressable>
          ))}
        </View>
      )}
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
  citationLink: { textDecorationLine: "underline" },
  // A footnote strip inside the bubble: one hairline rule, then quiet rows.
  references: {
    marginTop: 2,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#e2e8f0",
    gap: 6,
  },
  referencesTitle: {
    fontSize: 11,
    lineHeight: 16,
    fontWeight: "700",
    letterSpacing: 0.5,
    color: "#64748b",
  },
  referenceRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    backgroundColor: "#f8fafc",
  },
  referenceRowPressed: { opacity: 0.7 },
  referenceMarker: { fontSize: 12, lineHeight: 17, fontWeight: "700" },
  referenceDomain: { fontSize: 12.5, lineHeight: 17, fontWeight: "600" },
  referenceName: { flex: 1, fontSize: 12.5, lineHeight: 17 },
});
