import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { AssistantReply } from "./AssistantReply";

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

function renderReply(content: string) {
  return render(
    <div className="chatgpt-msg-content chatgpt-msg-content--rich">
      <AssistantReply content={content} />
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
