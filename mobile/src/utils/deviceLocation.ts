/** The device's position, for the one kind of question it improves: "where do
 * I get care".
 *
 * The backend ranks the facilities it answers with by real distance only when the
 * request carries coordinates; without them it asks which sector the patient is
 * in. So the phone is asked once per session, and never when the message does not
 * need it: a patient describing symptoms gets a medical answer, not a permission
 * dialog. Refused, unavailable or too slow, the message is sent without
 * coordinates rather than made to wait.
 */

import * as Location from "expo-location";

export type DeviceCoords = { latitude: number; longitude: number };

// Ten minutes: a patient who asks again shortly after is still standing where
// they were, and a cold GPS fix costs seconds each time it is taken.
const CACHE_MS = 10 * 60 * 1000;

// The permission dialog and the satellite search are the patient's to answer and
// the phone's to finish, not the message's to wait on.
const ANSWER_WAIT_MS = 8000;

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

let remembered: { coords?: DeviceCoords; until: number } = { until: 0 };
let inFlight: Promise<DeviceCoords | undefined> | undefined;

async function fixedPosition(): Promise<DeviceCoords | undefined> {
  const permission = await Location.requestForegroundPermissionsAsync();
  if (!permission.granted) return undefined;
  // A recent fix first: it is approximate, and approximate is enough to put the
  // right hospital at the top of a list.
  const known = await Location.getLastKnownPositionAsync({ maxAge: 5 * 60 * 1000 });
  const position =
    known ?? (await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced }));
  return {
    latitude: position.coords.latitude,
    longitude: position.coords.longitude,
  };
}

export async function coordsForQuestion(
  text: string
): Promise<DeviceCoords | undefined> {
  if (!asksForCarePlace(text)) return undefined;
  if (remembered.until > Date.now()) return remembered.coords;

  if (!inFlight) {
    inFlight = fixedPosition().then(
      (coords) => {
        // Both outcomes are remembered, so a patient who declined is not asked
        // again for every message. The cost is that a question sent while the
        // phone is still searching goes without a distance; the next one does not.
        remembered = { coords, until: Date.now() + CACHE_MS };
        inFlight = undefined;
        return coords;
      },
      () => {
        remembered = { until: Date.now() + CACHE_MS };
        inFlight = undefined;
        return undefined;
      }
    );
  }
  const pending = inFlight;

  return new Promise((resolve) => {
    const timer = setTimeout(() => resolve(undefined), ANSWER_WAIT_MS);
    void pending.then((coords) => {
      clearTimeout(timer);
      resolve(coords);
    });
  });
}
