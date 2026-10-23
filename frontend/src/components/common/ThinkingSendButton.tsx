/**
 * Composer send control. The arrow is replaced by a spinning ring while the AI
 * works, so the wait is visible where the user is already looking.
 */
export function ThinkingSendButton({
  sending,
  disabled,
  onClick,
  label,
  thinkingLabel,
}: {
  sending: boolean;
  disabled: boolean;
  onClick: () => void;
  label: string;
  thinkingLabel: string;
}) {
  const text = sending ? thinkingLabel : label;
  return (
    <button
      type="button"
      className={`chatgpt-send${sending ? " is-thinking" : ""}`}
      onClick={onClick}
      disabled={disabled}
      aria-label={text}
      title={text}
    >
      {sending ? (
        <svg
          className="send-ring"
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="8" opacity="0.28" />
          <path d="M12 4a8 8 0 0 1 8 8" />
        </svg>
      ) : (
        <svg
          viewBox="0 0 24 24"
          width="16"
          height="16"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M12 19V5" />
          <path d="m5 12 7-7 7 7" />
        </svg>
      )}
    </button>
  );
}
