import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { asksForCarePlace, coordsForQuestion } from "./deviceLocation";

/** The device is only asked when the answer needs it, and never twice. */
describe("deviceLocation", () => {
  let getCurrentPosition: any;

  beforeEach(() => {
    sessionStorage.clear();
    getCurrentPosition = vi.fn();
    vi.stubGlobal("navigator", { geolocation: { getCurrentPosition } });
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("recognises a question about where to get care", () => {
    expect(asksForCarePlace("which hospital is nearest to me")).toBe(true);
    expect(asksForCarePlace("ni irihe vuriro rinyegereye")).toBe(true);
    expect(asksForCarePlace("pharmacie hafi ya Kigali")).toBe(true);
    expect(asksForCarePlace("I have had a fever and a headache for three days")).toBe(false);
  });

  it("does not ask for the device location for a symptom", async () => {
    const coords = await coordsForQuestion("my leg hurts when I walk");

    expect(coords).toBeUndefined();
    expect(getCurrentPosition).not.toHaveBeenCalled();
  });

  it("sends the position the device gave", async () => {
    getCurrentPosition.mockImplementation(
      (success: (position: any) => void) =>
        success({ coords: { latitude: -1.9530, longitude: 29.8750 } })
    );

    const coords = await coordsForQuestion("hospital near me");

    expect(coords).toEqual({ latitude: -1.953, longitude: 29.875 });
    expect(getCurrentPosition).toHaveBeenCalledTimes(1);

    // The next place question is answered from the cache: a patient who asks
    // again a minute later is still standing where they were.
    await expect(coordsForQuestion("and a pharmacy near me")).resolves.toEqual({
      latitude: -1.953,
      longitude: 29.875,
    });
    expect(getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it("asks once when the patient refuses, and then leaves the choice alone", async () => {
    getCurrentPosition.mockImplementation(
      (_success: unknown, error: () => void) => error()
    );

    await expect(coordsForQuestion("nearest hospital")).resolves.toBeUndefined();
    await expect(coordsForQuestion("nearest hospital")).resolves.toBeUndefined();

    expect(getCurrentPosition).toHaveBeenCalledTimes(1);
  });

  it("still sends the message when the device never answers", async () => {
    getCurrentPosition.mockImplementation(() => undefined);
    vi.useFakeTimers();

    const asked = coordsForQuestion("nearest hospital");
    vi.advanceTimersByTime(6000);

    await expect(asked).resolves.toBeUndefined();
    vi.useRealTimers();
  });
});
