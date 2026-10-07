export interface SpeechRecognitionLike {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  start: () => void;
  stop: () => void;
  onresult: ((event: unknown) => void) | null;
  onerror: ((event: unknown) => void) | null;
  onend: (() => void) | null;
}

export type SpeechRecognitionConstructor = new () => SpeechRecognitionLike;

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

export function getRecognitionConstructor(): SpeechRecognitionConstructor | undefined {
  return window.SpeechRecognition ?? window.webkitSpeechRecognition;
}

export function ttsSupported(): boolean {
  return typeof window !== "undefined" && "speechSynthesis" in window;
}

const RW_WORDS = new Set([
  "kandi", "ariko", "cyangwa", "ntabwo", "mfite", "ndumva", "ibimenyetso",
  "ikimenyetso", "umuganga", "imiti", "umuti", "murakoze", "urakoze", "njye",
  "niba", "kuko", "nyuma", "byose", "rwose", "nta", "hari", "wowe", "amezi",
  "ukwezi", "iminsi", "umunsi", "ubushyuhe", "inkorora", "umubiri", "uburibwe",
  "ikibazo", "ibibazo", "mbwira", "mperutse", "ndashaka", "nkeneye", "igihe",
  "ubu", "ejo", "none", "kubera", "gukora", "kurya", "kunywa", "guhumeka",
  "ndababara", "arababara", "umutwe", "inda", "ibicurane", "impiswi",
  "guhitwa", "kuruka", "gusesema", "amaraso", "umuvuduko", "diabeti",
  "umusonga", "malariya", "nka", "uri", "afite", "bari", "bafite", "gusa",
]);
const RW_DIGRAPHS = ["cy", "rw", "bw", "by", "jy", "mw"];

export function detectLanguage(text: string): "rw" | "en" {
  const words = text
    .toLowerCase()
    .replace(/[^a-z'’\s]/gi, " ")
    .split(/\s+/)
    .filter(Boolean);
  if (words.length === 0) return "en";

  let score = 0;
  for (const word of words) {
    if (RW_WORDS.has(word.replace(/['’]/g, ""))) score += 2;
    else if (word.length >= 4 && RW_DIGRAPHS.some((d) => word.includes(d))) score += 1;
  }
  return score >= 2 ? "rw" : "en";
}

export function speak(text: string, lang: "rw" | "en", onDone?: () => void): void {
  if (!ttsSupported()) return;
  window.speechSynthesis.cancel();

  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = lang === "rw" ? "rw-RW" : "en-US";
  if (onDone) {
    utterance.onend = onDone;
    utterance.onerror = onDone;
  }
  window.speechSynthesis.speak(utterance);
}

export function stopSpeaking(): void {
  if (ttsSupported()) window.speechSynthesis.cancel();
}
