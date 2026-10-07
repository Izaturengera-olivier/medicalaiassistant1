import { useTranslation } from "react-i18next";
import { useVoiceInput } from "../../hooks/useVoiceInput";

interface Props {
  onTranscript: (text: string) => void;
  onError?: (message: string) => void;
  disabled?: boolean;
}

export function MicButton({ onTranscript, onError, disabled }: Props) {
  const { t, i18n } = useTranslation();
  const lang = (i18n.language || "en").startsWith("rw") ? "rw-RW" : "en-US";

  const { supported, listening, toggle } = useVoiceInput({
    lang,
    onTranscript,
    onError: (code) =>
      onError?.(
        code === "not-allowed"
          ? t("chat.voicePermissionDenied")
          : t("chat.voiceInputUnavailable"),
      ),
  });

  if (!supported) return null;

  const label = listening ? t("chat.voiceInputListening") : t("chat.voiceInput");

  return (
    <button
      type="button"
      className={listening ? "chatgpt-mic is-listening" : "chatgpt-mic"}
      onClick={toggle}
      aria-label={label}
      title={label}
      disabled={disabled}
    >
      <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3z" />
        <path d="M19 10v2a7 7 0 0 1-14 0v-2M12 19v3" />
      </svg>
    </button>
  );
}
