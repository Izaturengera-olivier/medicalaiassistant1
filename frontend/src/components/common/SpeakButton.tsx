import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { detectLanguage, speak, stopSpeaking, ttsSupported } from "../../utils/voice";

export function SpeakButton({ text }: { text: string }) {
  const { t } = useTranslation();
  const [speaking, setSpeaking] = useState(false);

  useEffect(() => {
    return () => {
      if (speaking) stopSpeaking();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (!ttsSupported()) return null;

  const toggle = () => {
    if (speaking) {
      stopSpeaking();
      setSpeaking(false);
      return;
    }
    speak(text, detectLanguage(text), () => setSpeaking(false));
    setSpeaking(true);
  };

  return (
    <button
      type="button"
      className={speaking ? "speak-btn is-speaking" : "speak-btn"}
      onClick={toggle}
      aria-label={speaking ? t("chat.stopListening") : t("chat.listen")}
      title={speaking ? t("chat.stopListening") : t("chat.listen")}
    >
      {speaking ? (
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <rect x="6" y="5" width="4" height="14" rx="1" />
          <rect x="14" y="5" width="4" height="14" rx="1" />
        </svg>
      ) : (
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M11 5 6 9H2v6h4l5 4z" />
          <path d="M15.5 8.5a5 5 0 0 1 0 7" />
          <path d="M19 5a9 9 0 0 1 0 14" />
        </svg>
      )}
    </button>
  );
}
