import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { expect, test } from "vitest";
import App from "./App";
import "./i18n";

test("renders landing disclaimer", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>
  );
  expect(
    screen.getByRole("heading", { name: /clinical decision support/i })
  ).toBeInTheDocument();
});
