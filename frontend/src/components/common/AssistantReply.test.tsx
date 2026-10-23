import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import "../../i18n";
import { AssistantReply } from "./AssistantReply";
import { replyToPlainText, type ReplySource } from "../../utils/replyText";

const REPLY = [
  "Here is what the findings suggest.",
  "",
  "What this could mean:",
  "- **Viral gastroenteritis** [1]",
  "- Food intolerance",
  "",
  "What you can do now:",
  "- Sip oral rehydration solution",
  "- Rest for 48 hours",
].join("\n");

function renderReply(content: string, sources?: readonly ReplySource[]) {
  return render(
    <div className="chatgpt-msg-content chatgpt-msg-content--rich">
      <AssistantReply content={content} sources={sources} />
    </div>
  );
}

describe("<AssistantReply />", () => {
  it("renders each bullet as a list item under its own section label", () => {
    const { container } = renderReply(REPLY);
    expect(container.querySelectorAll(".reply-section-label")).toHaveLength(2);
    expect(container.querySelectorAll(".reply-list")).toHaveLength(2);
    expect(screen.getAllByRole("listitem")).toHaveLength(4);
    expect(container.querySelector(".reply-section-label")?.textContent).toBe(
      "What this could mean:"
    );
  });

  it("never leaks markdown punctuation into what the patient reads", () => {
    const { container } = renderReply(REPLY);
    expect(container.textContent).not.toContain("**");
    expect(container.textContent).toContain("Viral gastroenteritis");
  });

  it("keeps inline citations visible as distinct citation nodes", () => {
    const { container } = renderReply(REPLY);
    const citations = container.querySelectorAll(".reply-citation");
    expect(citations).toHaveLength(1);
    expect(citations[0].textContent).toBe("[1]");
    expect(citations[0].tagName.toLowerCase()).toBe("sup");
  });

  it("renders an ordered list for numbered questions", () => {
    const { container } = renderReply(
      "To help me understand better:\n1. How long?\n2. Any fever?"
    );
    const list = container.querySelector("ol.reply-list--ordered");
    expect(list?.querySelectorAll("li")).toHaveLength(2);
  });

  it("preserves single line breaks inside one paragraph", () => {
    const { container } = renderReply(
      "Shortness of breath when walking\nimproved after two days of rest"
    );
    const paragraph = container.querySelector(".reply-paragraph");
    expect(paragraph?.textContent).toBe(
      "Shortness of breath when walking\nimproved after two days of rest"
    );
  });

  it("styles a bare Kinyarwanda section label as a label", () => {
    const { container } = renderReply("Ibyo wagera\n- Imiti yanywewe\n- Kuruhuka");
    expect(container.querySelector(".reply-section-label")?.textContent).toBe("Ibyo wagera");
    expect(container.querySelectorAll(".reply-list-item")).toHaveLength(2);
  });

  it("renders a plain short reply as one paragraph", () => {
    const { container } = renderReply("Seek in-person care today.");
    expect(container.querySelectorAll(".reply-paragraph")).toHaveLength(1);
    expect(container.querySelectorAll(".reply-section-label")).toHaveLength(0);
  });

  it("renders nothing for an empty reply", () => {
    const { container } = renderReply("   ");
    expect(container.querySelector(".reply-paragraph")).toBeNull();
  });
});

const WHO_URL = "https://www.who.int/health-topics/tuberculosis";

/** The shape the backend now sends: 1:1 with the reply's `[n]` numbering. */
const SOURCES: ReplySource[] = [
  { index: 1, name: "World Health Organization", title: "Tuberculosis", url: WHO_URL },
  { index: 2, name: "MoH Rwanda", title: "Integrated Guidelines", url: "" },
];

describe("<AssistantReply /> citations as links", () => {
  it("turns a [n] marker into a real link to the page it was retrieved from", () => {
    const { container } = renderReply("Cough lasting two weeks [1].", SOURCES);
    const link = container.querySelector<HTMLAnchorElement>("a.reply-citation-link");
    expect(link).not.toBeNull();
    expect(link?.getAttribute("href")).toBe(WHO_URL);
    expect(link?.getAttribute("target")).toBe("_blank");
    expect(link?.getAttribute("rel")).toBe("noopener noreferrer");
    // The marker itself stays the same tiny superscript inside the link.
    const sup = link?.querySelector("sup.reply-citation");
    expect(sup?.textContent).toBe("[1]");
  });

  it("leaves an out-of-range marker as inert text, never a guessed link", () => {
    const { container } = renderReply("See also [7] for details.", SOURCES);
    expect(container.querySelector("a.reply-citation-link")).toBeNull();
    const citation = container.querySelector(".reply-citation");
    expect(citation?.tagName.toLowerCase()).toBe("sup");
    expect(citation?.textContent).toBe("[7]");
  });

  it("leaves a marker whose source has no URL as inert text", () => {
    const { container } = renderReply("National guidance [2] applies.", SOURCES);
    expect(container.querySelector("a.reply-citation-link")).toBeNull();
    expect(container.querySelector(".reply-citation")?.textContent).toBe("[2]");
  });

  it("resolves by the explicit index when the sources array arrives reordered", () => {
    const reordered: ReplySource[] = [
      { index: 2, name: "MoH Rwanda", title: "Guidelines", url: "https://moh.gov.rw/guidelines" },
      { index: 1, name: "World Health Organization", title: "Tuberculosis", url: WHO_URL },
    ];
    const { container } = renderReply("Cough [1] and fever [2].", reordered);
    const links = container.querySelectorAll<HTMLAnchorElement>("a.reply-citation-link");
    expect(links).toHaveLength(2);
    expect(links[0].getAttribute("href")).toBe(WHO_URL);
    expect(links[1].getAttribute("href")).toBe("https://moh.gov.rw/guidelines");
  });

  it("renders no reference strip without sources", () => {
    const { container } = renderReply("Cough [1].");
    expect(container.querySelector(".reply-references")).toBeNull();
  });

  it("renders no reference strip when no source has a usable URL", () => {
    const { container } = renderReply("Cough [1].", [
      { index: 1, name: "MoH Rwanda", title: "Guidelines", url: "" },
      { index: 2, name: "Unknown" },
    ]);
    expect(container.querySelector(".reply-references")).toBeNull();
  });

  it("lists one deduped, labelled row per distinct URL under the reply", () => {
    const { container } = renderReply(
      "Cough [1], fever [2], and a third marker [3] on the same WHO page.",
      [
        SOURCES[0],
        { index: 2, name: "PubMed", title: "Tuberculosis", url: `${WHO_URL}#footnote` },
        { index: 3, name: "Duplicate with slash", title: "", url: `${WHO_URL}/` },
        { index: 4, name: "MoH Rwanda", title: "Guidelines", url: "" },
      ]
    );

    expect(container.querySelector(".reply-references-title")?.textContent).toBe("Sources");
    const rows = container.querySelectorAll(".reply-reference-item");
    expect(rows).toHaveLength(1);

    const anchor = rows[0].querySelector<HTMLAnchorElement>("a.reply-reference-link");
    expect(anchor?.getAttribute("href")).toBe(WHO_URL);
    expect(anchor?.getAttribute("target")).toBe("_blank");
    expect(anchor?.getAttribute("rel")).toBe("noopener noreferrer");
    expect(rows[0].querySelector(".reply-reference-marker")?.textContent).toBe("[1]");
    expect(rows[0].querySelector(".reply-reference-domain")?.textContent).toBe("who.int");
    expect(rows[0].querySelector(".reply-reference-name")?.textContent).toBe("Tuberculosis");
  });

  it("keeps a second distinct source as its own row", () => {
    const { container } = renderReply("Cough [1], fever [2].", [
      SOURCES[0],
      { index: 2, name: "PubMed", title: "Malaria", url: "https://pubmed.ncbi.nlm.nih.gov/malaria" },
    ]);
    const rows = container.querySelectorAll(".reply-reference-item");
    expect(rows).toHaveLength(2);
    expect(rows[1].querySelector(".reply-reference-marker")?.textContent).toBe("[2]");
    expect(rows[1].querySelector(".reply-reference-domain")?.textContent).toBe(
      "pubmed.ncbi.nlm.nih.gov"
    );
  });

  it("keeps what the pages hand to text-to-speech free of links and markers", () => {
    // The pages speak replyToPlainText(content), never this DOM, so the strip's
    // URLs and domains can no more be read aloud than the [n] markers can.
    const content = "Cough [1]. Read more at [WHO guidance](https://www.who.int/x).";
    renderReply(content, SOURCES);
    const spoken = replyToPlainText(content);
    expect(spoken).not.toContain("http");
    expect(spoken).not.toContain("who.int");
    expect(spoken).not.toContain("[1]");
    expect(spoken).not.toMatch(/citation/i);
    expect(spoken).toContain("Cough");
    expect(spoken).toContain("WHO guidance");
  });
});
