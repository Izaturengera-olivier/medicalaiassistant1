import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test, vi } from "vitest";
import { HomePage } from "./pages/HomePage";
import { AssessmentPage } from "./pages/patient/AssessmentPage";
import "./i18n";

test("renders landing heading and safety disclaimer", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <HomePage />
    </MemoryRouter>
  );

  expect(
    screen.getByRole("heading", { name: /clinical decision support/i })
  ).toBeInTheDocument();

  expect(
    screen.getAllByText(
      /does not diagnose conditions or independently prescribe medication/i
    ).length
  ).toBeGreaterThan(0);
});

test("shows a microphone button on the symptom assessment page", () => {
  class MockSpeechRecognition {
    lang = "en-US";
    continuous = false;
    interimResults = true;
    onresult: ((event: unknown) => void) | null = null;
    onerror: ((event: unknown) => void) | null = null;
    onend: (() => void) | null = null;
    start = vi.fn();
    stop = vi.fn();
  }

  Object.defineProperty(window, "SpeechRecognition", {
    value: MockSpeechRecognition,
    configurable: true,
  });

  render(
    <MemoryRouter initialEntries={["/assessment"]}>
      <AssessmentPage />
    </MemoryRouter>
  );

  expect(screen.getByRole("button", { name: /voice input|microphone/i })).toBeInTheDocument();
});
