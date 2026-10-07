import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { aiAPI } from "../services/api";
import { errorMessage } from "../hooks/useAsync";
import { ConversationSidebar } from "../components/common/ConversationSidebar";
import { MicButton } from "../components/common/MicButton";
import { SpeakButton } from "../components/common/SpeakButton";
import { detectLanguage, speak, stopSpeaking } from "../utils/voice";

interface Message {
  id: number | string;
  role: "user" | "assistant";
  content: string;
}

interface Source {
  name?: string;
  title?: string;
  url?: string;
}

interface ProfessionalReply {
  reply?: string;
  warning_signs: string[];
  possible_conditions: { name?: string; likelihood?: string; description?: string }[];
  follow_up_questions: string[];
  general_information: string;
  recommended_next_step: string;
  sources: Source[];
}

export function AIAssistantPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [caseContext, setCaseContext] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voiceDraft, setVoiceDraft] = useState(false);
  const [lastReply, setLastReply] = useState<ProfessionalReply | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [refreshSignal, setRefreshSignal] = useState(0);
  const logRef = useRef<HTMLDivElement>(null);
  const nextLocalId = useRef(-1);

  useEffect(() => {
    const node = logRef.current;
    if (!node) return;
    // jsdom does not implement element.scrollTo.
    if (typeof node.scrollTo === "function") {
      node.scrollTo({ top: node.scrollHeight });
    } else {
      node.scrollTop = node.scrollHeight;
    }
  }, [messages, sending, showDetails]);

  useEffect(() => stopSpeaking, []);

  const suggestions: string[] = [
    t("aiAssistant.suggestion1"),
    t("aiAssistant.suggestion2"),
    t("aiAssistant.suggestion3"),
  ];

  const startNewChat = () => {
    stopSpeaking();
    setActiveId(null);
    setMessages([]);
    setLastReply(null);
    setShowDetails(false);
    setError(null);
    setVoiceDraft(false);
  };

  const openConversation = async (id: number) => {
    stopSpeaking();
    setError(null);
    try {
      const res = await aiAPI.conversation(id);
      const data = res.data as {
        messages: { id: number; role: "user" | "assistant"; content: string; details?: ProfessionalReply | null }[];
      };
      setActiveId(id);
      setMessages(data.messages.map((m) => ({ id: m.id, role: m.role, content: m.content })));
      const lastAssistant = [...data.messages].reverse().find((m) => m.role === "assistant" && m.details);
      setLastReply(lastAssistant?.details ?? null);
      setShowDetails(false);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const send = async (text?: string, viaVoice = false) => {
    const content = (text ?? input).trim();
    if (!content || sending) return;

    setError(null);
    setSending(true);
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { id: nextLocalId.current--, role: "user", content }]);
    setInput("");
    setVoiceDraft(false);

    try {
      const res = await aiAPI.professionalChat({
        message: content,
        history,
        conversation_id: activeId ?? undefined,
        context: {
          role: user?.role,
          case_notes: caseContext.trim() || undefined,
        },
      });
      const data = res.data as ProfessionalReply & { conversation_id?: number };
      setLastReply(data);

      if (data.conversation_id && data.conversation_id !== activeId) {
        setActiveId(data.conversation_id);
      }
      setRefreshSignal((s) => s + 1);

      const reply = data.reply?.trim() || data.general_information || t("aiAssistant.emptyReply");
      setMessages((m) => [...m, { id: nextLocalId.current--, role: "assistant", content: reply }]);
      if (viaVoice) speak(reply, detectLanguage(reply));
    } catch (err) {
      setError(errorMessage(err));
      setMessages((m) => [
        ...m,
        { id: nextLocalId.current--, role: "assistant", content: t("aiAssistant.failed") },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chatgpt">
      <ConversationSidebar
        kind="professional"
        activeId={activeId}
        refreshSignal={refreshSignal}
        onOpen={(id) => void openConversation(id)}
        onNew={startNewChat}
        footer={
          <div className="convo-context">
            <label className="kv-label" htmlFor="case-context">{t("aiAssistant.contextTitle")}</label>
            <textarea
              id="case-context"
              className="input convo-context-input"
              rows={3}
              value={caseContext}
              placeholder={t("aiAssistant.contextPlaceholder")}
              onChange={(e) => setCaseContext(e.target.value)}
              disabled={sending}
            />
          </div>
        }
      />

      <div className="chatgpt-main">
        <div className="chatgpt-log" ref={logRef}>
          {messages.length === 0 && !sending ? (
            <div className="chatgpt-empty">
              <span className="chatgpt-empty-mark" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z" />
                </svg>
              </span>
              <h2>{t("chat.emptyTitle")}</h2>
              <p className="muted">{t("aiAssistant.greeting")}</p>
              <div className="chatgpt-suggestions">
                {suggestions.map((s, i) => (
                  <button key={i} type="button" className="chatgpt-suggestion" onClick={() => void send(s)} disabled={sending}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="chatgpt-thread">
              {messages.map((m) => (
                <div key={m.id} className={`chatgpt-msg chatgpt-msg--${m.role}`}>
                  <div className="chatgpt-msg-avatar" aria-hidden="true">
                    {m.role === "user" ? (
                      (user?.first_name?.[0] ?? "U").toUpperCase()
                    ) : (
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z" />
                      </svg>
                    )}
                  </div>
                  <div className="chatgpt-msg-body">
                    <div className="chatgpt-msg-name">{m.role === "user" ? t("aiAssistant.you") : t("aiAssistant.assistant")}</div>
                    <div className="chatgpt-msg-content">{m.content}</div>
                    {m.role === "assistant" && (
                      <div className="chatgpt-msg-actions">
                        <SpeakButton text={m.content} />
                      </div>
                    )}
                  </div>
                </div>
              ))}
              {sending && (
                <div className="chatgpt-msg chatgpt-msg--assistant">
                  <div className="chatgpt-msg-avatar" aria-hidden="true">
                    <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8">
                      <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z" />
                    </svg>
                  </div>
                  <div className="chatgpt-msg-body">
                    <div className="chatgpt-msg-name">{t("aiAssistant.assistant")}</div>
                    <div className="chatgpt-msg-content muted">{t("aiAssistant.thinking")}</div>
                  </div>
                </div>
              )}

              {lastReply && !sending && (
                <div className="chatgpt-details">
                  <button type="button" className="chatgpt-details-toggle" onClick={() => setShowDetails((v) => !v)}>
                    {showDetails ? t("chat.detailsHide") : t("chat.detailsToggle")}
                    <span aria-hidden="true">{showDetails ? "▾" : "▸"}</span>
                  </button>
                  {showDetails && (
                    <div className="chatgpt-details-body">
                      {lastReply.warning_signs?.length > 0 && (
                        <div className="error-box">
                          <strong>{t("aiAssistant.warningSigns")}</strong>
                          <ul className="list-plain" style={{ marginTop: 6 }}>
                            {lastReply.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                      {lastReply.possible_conditions?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("aiAssistant.possibleConditions")}</div>
                          <ul className="list-plain">
                            {lastReply.possible_conditions.map((c, i) => (
                              <li key={i}>
                                <strong>{c.name}</strong>
                                {c.likelihood ? ` — ${c.likelihood}` : ""}
                                {c.description ? `: ${c.description}` : ""}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {lastReply.follow_up_questions?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("aiAssistant.missingInfo")}</div>
                          <ul className="list-plain">
                            {lastReply.follow_up_questions.map((q, i) => <li key={i}>{q}</li>)}
                          </ul>
                        </div>
                      )}
                      {lastReply.recommended_next_step && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 6 }}>{t("aiAssistant.recommendedNextStep")}</div>
                          <p className="mb-0" style={{ fontSize: "0.94rem", color: "var(--ink-soft)" }}>
                            {lastReply.recommended_next_step}
                          </p>
                        </div>
                      )}
                      {lastReply.sources?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("aiAssistant.sources")}</div>
                          <ul className="list-plain">
                            {lastReply.sources.map((s, i) =>
                              s.url ? (
                                <li key={i}>
                                  <a href={s.url} target="_blank" rel="noopener noreferrer">{s.name || s.title || s.url}</a>
                                </li>
                              ) : (
                                <li key={i}>{s.name || s.title}</li>
                              )
                            )}
                          </ul>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        <div className="chatgpt-composer-wrap">
          {error && <div className="error-box chatgpt-error">{error}</div>}
          <div className="chatgpt-composer">
            <MicButton
              disabled={sending}
              onError={setError}
              onTranscript={(text) => {
                setInput(text);
                setVoiceDraft(true);
              }}
            />
            <input
              className="chatgpt-input"
              value={input}
              placeholder={t("aiAssistant.inputPlaceholder")}
              onChange={(e) => {
                setInput(e.target.value);
                setVoiceDraft(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") void send(undefined, voiceDraft);
              }}
              disabled={sending}
            />
            <button
              type="button"
              className="chatgpt-send"
              onClick={() => void send(undefined, voiceDraft)}
              disabled={sending || !input.trim()}
              aria-label={t("aiAssistant.send")}
              title={t("aiAssistant.send")}
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M12 19V5" />
                <path d="m5 12 7-7 7 7" />
              </svg>
            </button>
          </div>
          <p className="chatgpt-disclaimer">{t("common.disclaimer")}</p>
        </div>
      </div>
    </div>
  );
}
