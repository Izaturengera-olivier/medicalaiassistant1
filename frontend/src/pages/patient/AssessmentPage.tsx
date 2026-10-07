import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { aiAPI, consultationsAPI } from "../../services/api";
import { errorMessage } from "../../hooks/useAsync";
import { Badge, urgencyLabel, urgencyTone } from "../../components/ui";
import { ConversationSidebar } from "../../components/common/ConversationSidebar";
import { MicButton } from "../../components/common/MicButton";
import { SpeakButton } from "../../components/common/SpeakButton";
import { detectLanguage, speak, stopSpeaking } from "../../utils/voice";

interface Message {
  id: number | string;
  role: "user" | "assistant";
  content: string;
}

interface PossibleCondition {
  name?: string;
  likelihood?: string;
  description?: string;
}

interface Source {
  name?: string;
  title?: string;
  url?: string;
}

interface Assessment {
  reply?: string;
  symptoms_identified: string[];
  follow_up_questions: string[];
  possible_conditions: PossibleCondition[];
  warning_signs: string[];
  urgency_level: string;
  general_information: string;
  medication_information: unknown[];
  recommended_next_step: string;
  sources: Source[];
  consultation_id?: number;
}

export function AssessmentPage() {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [voiceDraft, setVoiceDraft] = useState(false);
  const [consultationId, setConsultationId] = useState<number | null>(null);
  const [assessment, setAssessment] = useState<Assessment | null>(null);
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

  const buildSummary = (a: Assessment): string => {
    const parts: string[] = [];
    if (a.symptoms_identified?.length)
      parts.push(t("patient.assessment.summarySymptoms", { symptoms: a.symptoms_identified.join(", ") }));
    if (a.urgency_level)
      parts.push(t("patient.assessment.summaryUrgency", { urgency: urgencyLabel(a.urgency_level) }));
    if (a.recommended_next_step) parts.push(a.recommended_next_step);
    if (a.follow_up_questions?.length)
      parts.push(t("patient.assessment.summaryFollowUp", { question: a.follow_up_questions[0] }));
    return parts.join(" ") || t("patient.assessment.summaryFallback");
  };

  const startNewChat = () => {
    stopSpeaking();
    setActiveId(null);
    setMessages([]);
    setAssessment(null);
    setConsultationId(null);
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
        messages: { id: number; role: "user" | "assistant"; content: string; details?: Assessment | null }[];
      };
      setActiveId(id);
      setMessages(data.messages.map((m) => ({ id: m.id, role: m.role, content: m.content })));

      const withDetails = data.messages.filter((m) => m.role === "assistant" && m.details);
      const last = withDetails[withDetails.length - 1];
      setAssessment(last?.details ?? null);
      const cid = [...withDetails].reverse().find((m) => m.details?.consultation_id)?.details?.consultation_id;
      setConsultationId(cid ?? null);
      setShowDetails(false);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const send = async (viaVoice = false) => {
    const text = input.trim();
    if (!text || sending) return;

    setError(null);
    setSending(true);
    const history = messages.map((m) => ({ role: m.role, content: m.content }));
    setMessages((m) => [...m, { id: nextLocalId.current--, role: "user", content: text }]);
    setInput("");
    setVoiceDraft(false);

    try {
      let cid = consultationId;
      if (cid === null) {
        const created = await consultationsAPI.create({ chief_complaint: text });
        cid = created.data.id as number;
        setConsultationId(cid);
      }

      const res = await aiAPI.analyzeSymptoms({
        patient_input: text,
        consultation_id: cid,
        conversation_id: activeId ?? undefined,
        history,
      });
      const data = res.data as Assessment & { conversation_id?: number };
      setAssessment(data);

      if (data.conversation_id && data.conversation_id !== activeId) {
        setActiveId(data.conversation_id);
      }
      setRefreshSignal((s) => s + 1);

      const reply = data.reply?.trim() || buildSummary(data);
      setMessages((m) => [...m, { id: nextLocalId.current--, role: "assistant", content: reply }]);
      if (viaVoice) speak(reply, detectLanguage(reply));
    } catch (err) {
      setError(errorMessage(err));
      setMessages((m) => [
        ...m,
        { id: nextLocalId.current--, role: "assistant", content: t("patient.assessment.analysisFailed") },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="chatgpt">
      <ConversationSidebar
        kind="patient"
        activeId={activeId}
        refreshSignal={refreshSignal}
        onOpen={(id) => void openConversation(id)}
        onNew={startNewChat}
      />

      <div className="chatgpt-main">
        <div className="chatgpt-log" ref={logRef}>
          {messages.length === 0 && !sending ? (
            <div className="chatgpt-empty">
              <span className="chatgpt-empty-mark" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="30" height="30" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
                  <path d="M3 12h4l2-3 3 6 2-3h7" />
                </svg>
              </span>
              <h2>{t("chat.emptyTitle")}</h2>
              <p className="muted">{t("patient.assessment.greeting")}</p>
            </div>
          ) : (
            <div className="chatgpt-thread">
              {messages.map((m) => (
                <div key={m.id} className={`chatgpt-msg chatgpt-msg--${m.role}`}>
                  <div className="chatgpt-msg-avatar" aria-hidden="true">
                    {m.role === "user" ? (
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
                      </svg>
                    ) : (
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
                        <path d="M3 12h4l2-3 3 6 2-3h7" />
                      </svg>
                    )}
                  </div>
                  <div className="chatgpt-msg-body">
                    <div className="chatgpt-msg-name">{m.role === "user" ? t("patient.assessment.you") : t("patient.assessment.assistant")}</div>
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
                      <path d="M12 21s-7-4.35-7-10a4 4 0 0 1 7-2.65A4 4 0 0 1 19 11c0 5.65-7 10-7 10z" />
                    </svg>
                  </div>
                  <div className="chatgpt-msg-body">
                    <div className="chatgpt-msg-name">{t("patient.assessment.assistant")}</div>
                    <div className="chatgpt-msg-content muted">{t("patient.assessment.analyzing")}</div>
                  </div>
                </div>
              )}

              {assessment && !sending && (
                <div className="chatgpt-details">
                  <button type="button" className="chatgpt-details-toggle" onClick={() => setShowDetails((v) => !v)}>
                    <span>
                      {showDetails ? t("chat.detailsHide") : t("chat.detailsToggle")}
                      {" "}
                      <Badge tone={urgencyTone(assessment.urgency_level)}>{urgencyLabel(assessment.urgency_level)}</Badge>
                    </span>
                    <span aria-hidden="true">{showDetails ? "▾" : "▸"}</span>
                  </button>
                  {showDetails && (
                    <div className="chatgpt-details-body">
                      {assessment.warning_signs?.length > 0 && (
                        <div className="error-box">
                          <strong>{t("patient.assessment.warningSigns")}</strong>
                          <ul className="list-plain" style={{ marginTop: 6 }}>
                            {assessment.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                      {assessment.possible_conditions?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.assessment.possibleConditions")}</div>
                          <ul className="list-plain">
                            {assessment.possible_conditions.map((c, i) => (
                              <li key={i}>
                                <strong>{c.name}</strong>
                                {c.likelihood ? ` — ${c.likelihood}` : ""}
                                {c.description ? `: ${c.description}` : ""}
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {assessment.follow_up_questions?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.assessment.followUpQuestions")}</div>
                          <ul className="list-plain">
                            {assessment.follow_up_questions.map((q, i) => <li key={i}>{q}</li>)}
                          </ul>
                        </div>
                      )}
                      {assessment.general_information && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 6 }}>{t("patient.assessment.generalInformation")}</div>
                          <p className="mb-0" style={{ fontSize: "0.94rem", color: "var(--ink-soft)" }}>
                            {assessment.general_information}
                          </p>
                        </div>
                      )}
                      {assessment.recommended_next_step && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 6 }}>{t("patient.assessment.recommendedNextStep")}</div>
                          <p className="mb-0" style={{ fontSize: "0.94rem", color: "var(--ink-soft)" }}>
                            {assessment.recommended_next_step}
                          </p>
                        </div>
                      )}
                      {assessment.sources?.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.assessment.sources")}</div>
                          <ul className="list-plain">
                            {assessment.sources.map((s, i) =>
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
              placeholder={t("patient.assessment.inputPlaceholder")}
              onChange={(e) => {
                setInput(e.target.value);
                setVoiceDraft(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") void send(voiceDraft);
              }}
              disabled={sending}
            />
            <button
              type="button"
              className="chatgpt-send"
              onClick={() => void send(voiceDraft)}
              disabled={sending || !input.trim()}
              aria-label={t("patient.assessment.send")}
              title={t("patient.assessment.send")}
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
