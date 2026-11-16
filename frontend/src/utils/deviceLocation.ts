/** The device's position, for the one kind of question it improves: "where do
 * I get care".
 *
 * The backend answers a place question from the facility register and ranks it by
 * real distance only when the request carries coordinates; without them it asks
 * which sector the patient is in. So this asks the browser once, caches the answer
 * for the session, and sends nothing whenever permission is refused, the browser
 * takes too long, or there is no GPS at all — a delayed answer is worse than an
 * unanswered distance.
 */

export type DeviceCoords = { latitude: number; longitude: number };

const STORAGE_KEY = "clinical-cds.device-location";

// Ten minutes: a patient who asks again shortly after is still standing where
// they were, and asking the phone to fix its position costs seconds each time.
const CACHE_MS = 10 * 60 * 1000;

// The permission dialog is the patient's to answer, not the message's to wait on.
const ANSWER_WAIT_MS = 6000;

// The same trigger the backend reads a place question by. When it misses one, the
// request simply goes without coordinates and the assistant asks for the sector.
const CARE_PLACE_WORDS = [
  "hospital", "hopital", "hôpital", "ibitaro",
  "vuriro", "clinic", "clinique", "polyclinique", "pharmacy", "pharmacie", "farumasi",
  "health centre", "health center", "health post",
  "near", "nearest", "nearby", "closest", "close to",
  "hafi", "egereye", "kuruta",
];

const CLINICAL_QUERY_MARKERS = [
  "symptom", "ibimenyetso", "which symptom", "what symptom", "sign", "warning",
  "why", "how to", "how do", "what is", "cause", "treatment", "cure", "pain",
  "fever", "cough", "infection", "headache", "umuriro", "ububabare", "inkorora",
  "dose", "side effect", "mean i must", "when should i", "why should i",
];

const EXPLICIT_LOCATION_WORDS = [
  "where is", "where can", "ni hehe", "iri he", "irihe", "nearest", "closest", "hafi",
  "near me", "nearby", "closest to me", "directions", "locate", "find a",
];

export function asksForCarePlace(text: string): boolean {
  const lowered = (text || "").toLowerCase();
  const isClinical = CLINICAL_QUERY_MARKERS.some((word) => lowered.includes(word));
  const hasExplicitLoc = EXPLICIT_LOCATION_WORDS.some((word) => lowered.includes(word));
  if (isClinical && !hasExplicitLoc) {
    return false;
  }
  return CARE_PLACE_WORDS.some((word) => lowered.includes(word));
}

function readCache(): { coords?: DeviceCoords; until: number } | undefined {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (!raw) return undefined;
    const cached = JSON.parse(raw) as { coords?: DeviceCoords; until: number };
    return cached.until > Date.now() ? cached : undefined;
  } catch {
    return undefined;
  }
}

function writeCache(coords?: DeviceCoords): void {
  try {
    sessionStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({ coords, until: Date.now() + CACHE_MS })
    );
  } catch {
    // A full or blocked sessionStorage only costs a second prompt later.
  }
}

export async function coordsForQuestion(text: string): Promise<DeviceCoords | undefined> {
  if (!asksForCarePlace(text) || typeof navigator === "undefined" || !("geolocation" in navigator)) {
    return undefined;
  }
  const cached = readCache();
  // The entry itself is the memory: an entry without coordinates is a refusal
  // the patient already made, and reopening that dialog is not their problem.
  if (cached) return cached.coords;

  return new Promise((resolve) => {
    let settled = false;
    const finish = (coords: DeviceCoords | undefined) => {
      if (settled) return;
      settled = true;
      window.clearTimeout(timer);
      resolve(coords);
    };
    const timer = window.setTimeout(() => finish(undefined), ANSWER_WAIT_MS);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const coords = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        };
        writeCache(coords);
        finish(coords);
      },
      // Refused, unsupported or timed out on the device: the message is sent
      // anyway, and the refusal is remembered so the next question does not
      // reopen a dialog the patient already answered.
      () => {
        writeCache(undefined);
        finish(undefined);
      },
      { enableHighAccuracy: false, timeout: ANSWER_WAIT_MS, maximumAge: 60_000 }
    );
  });
}
