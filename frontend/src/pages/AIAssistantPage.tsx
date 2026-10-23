import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAuth } from "../context/AuthContext";
import { aiAPI } from "../services/api";
import { errorMessage } from "../hooks/useAsync";
import { ConversationSidebar } from "../components/common/ConversationSidebar";
import { MicButton } from "../components/common/MicButton";
import { SpeakButton } from "../components/common/SpeakButton";
import { ThinkingSendButton } from "../components/common/ThinkingSendButton";
import { AssistantReply } from "../components/common/AssistantReply";
import { detectLanguage, speak, stopSpeaking } from "../utils/voice";
import { replyToPlainText } from "../utils/replyText";

interface AttachedDoc {
  id?: number;
  file_name: string;
  file_url?: string;
  file_size?: number;
  document_category?: string;
  exam_type?: string;
}

interface ScanFinding {
  area: string;
  finding: string;
  is_abnormal?: boolean;
}

interface TrustedSolution {
  action: string;
  guideline_source?: string;
  details?: string;
}

interface Source {
  index?: number;
  name?: string;
  title?: string;
  url?: string;
}

interface ProfessionalReply {
  reply?: string;
  exam_type?: string;
  document_category?: string;
  document_summary?: string;
  scan_findings?: ScanFinding[];
  abnormalities?: string[];
  warning_signs?: string[];
  possible_conditions?: { name?: string; likelihood?: string; description?: string }[];
  follow_up_questions?: string[];
  urgency_level?: string;
  trusted_solutions?: TrustedSolution[];
  general_information?: string;
  recommended_next_step?: string;
  sources?: Source[];
}

interface Message {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  document?: AttachedDoc;
  details?: ProfessionalReply | null;
}

export function AIAssistantPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  // Patients get the upload surface too, but their chat must go through the
  // patient endpoint: /ai/professional-chat/ answers 403 for them.
  const isPatient = user?.role === "PATIENT";
  const conversationKind = isPatient ? "patient" : "professional";
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
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const logRef = useRef<HTMLDivElement>(null);
  const nextLocalId = useRef(-1);

  useEffect(() => {
    const node = logRef.current;
    if (!node) return;
    const scroll = () => {
      if (typeof node.scrollTo === "function") {
        node.scrollTo({ top: node.scrollHeight });
      } else {
        node.scrollTop = node.scrollHeight;
      }
    };
    scroll();
    const rafId = requestAnimationFrame(scroll);
    return () => cancelAnimationFrame(rafId);
  }, [messages, sending, showDetails, selectedFile]);

  useEffect(() => stopSpeaking, []);

  // Patients land on this page too, so the empty state must not read like a
  // clinician's differential/interaction tool.
  const suggestions: string[] = [
    isPatient ? t("aiAssistant.patientSuggestion1") : t("aiAssistant.suggestion1"),
    isPatient ? t("aiAssistant.patientSuggestion2") : t("aiAssistant.suggestion2"),
    isPatient ? t("aiAssistant.patientSuggestion3") : t("aiAssistant.suggestion3"),
  ];

  const startNewChat = () => {
    stopSpeaking();
    setActiveId(null);
    setMessages([]);
    setLastReply(null);
    setShowDetails(false);
    setError(null);
    setVoiceDraft(false);
    setSelectedFile(null);
  };

  const openConversation = async (id: number) => {
    stopSpeaking();
    setError(null);
    setSelectedFile(null);
    try {
      const res = await aiAPI.conversation(id);
      const data = res.data as {
        messages: {
          id: number;
          role: "user" | "assistant";
          content: string;
          document?: AttachedDoc;
          details?: any;
        }[];
      };
      setActiveId(id);
      setMessages(
        data.messages.map((m) => {
          const doc = m.document || (m.details?.attachment ? {
            id: m.details.attachment.document_id,
            file_name: m.details.attachment.file_name,
            file_url: m.details.attachment.file_url,
            file_size: m.details.attachment.file_size,
            document_category: m.details.attachment.category,
            exam_type: m.details.attachment.exam_type,
          } : undefined);
          return {
            id: m.id,
            role: m.role,
            content: m.content,
            document: doc,
            details: m.details ?? null,
          };
        })
      );
      const lastAssistant = [...data.messages].reverse().find((m) => m.role === "assistant" && m.details);
      setLastReply(lastAssistant?.details ?? null);
      setShowDetails(false);
    } catch (err) {
      setError(errorMessage(err));
    }
  };

  const send = async (text?: string, viaVoice = false) => {
    const content = (text ?? input).trim();
    if ((!content && !selectedFile) || sending) return;

    setError(null);
    setSending(true);
    const fileToSend = selectedFile;
    setSelectedFile(null);
    setInput("");
    setVoiceDraft(false);

    // Staged user message
    const userMsg: Message = {
      id: nextLocalId.current--,
      role: "user",
      content: content || (fileToSend ? `${t("chat.scanAnalysisTitle")}: ${fileToSend.name}` : ""),
      document: fileToSend ? {
        file_name: fileToSend.name,
        file_size: fileToSend.size,
      } : undefined,
    };
    setMessages((m) => [...m, userMsg]);

    try {
      let data: any;
      if (fileToSend) {
        const formData = new FormData();
        formData.append("file", fileToSend);
        if (content) formData.append("message", content);
        if (activeId) formData.append("conversation_id", String(activeId));
        formData.append("kind", conversationKind);
        const res = await aiAPI.uploadAndAnalyze(formData);
        data = res.data;
      } else {
        const history = messages.map((m) => ({ role: m.role, content: m.content }));
        const res = isPatient
          ? await aiAPI.analyzeSymptoms({
              patient_input: content,
              history,
              conversation_id: activeId ?? undefined,
            })
          : await aiAPI.professionalChat({
              message: content,
              history,
              conversation_id: activeId ?? undefined,
              context: {
                role: user?.role,
                case_notes: caseContext.trim() || undefined,
              },
            });
        data = res.data;
      }

      setLastReply(data);

      if (data.conversation_id && data.conversation_id !== activeId) {
        setActiveId(data.conversation_id);
      }
      setRefreshSignal((s) => s + 1);

      const reply = data.reply?.trim() || data.general_information || t("aiAssistant.emptyReply");
      setMessages((m) => [...m, { id: nextLocalId.current--, role: "assistant", content: reply, details: data }]);
      if (viaVoice) {
        // Speak the plain-text form: never section labels' colons, bullets or [1].
        const spoken = replyToPlainText(reply);
        speak(spoken, detectLanguage(spoken));
      }
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
        kind={conversationKind}
        activeId={activeId}
        refreshSignal={refreshSignal}
        onOpen={(id) => void openConversation(id)}
        onNew={startNewChat}
        footer={
          isPatient ? null : (
            <div className="convo-context">
              <label className="kv-label" htmlFor="case-context">{t("aiAssistant.contextTitle")}</label>
              <textarea
                id="case-context"
                className="convo-context-input"
                rows={3}
                placeholder={t("aiAssistant.contextPlaceholder")}
                value={caseContext}
                onChange={(e) => setCaseContext(e.target.value)}
              />
              <p className="convo-context-sub">{t("aiAssistant.contextSub")}</p>
            </div>
          )
        }
      />

      <div className="chatgpt-main">
        <div className="chatgpt-scroll chatgpt-log" ref={logRef}>
          {messages.length === 0 ? (
            <div className="chatgpt-hero">
              <div className="chatgpt-avatar-large" aria-hidden="true">
                <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z" />
                </svg>
              </div>
              <h1 className="chatgpt-title">{t("aiAssistant.title")}</h1>
              <p className="chatgpt-subtitle">
                {isPatient ? t("aiAssistant.patientSubtitle") : t("aiAssistant.subtitle")}
              </p>
              <p className="chatgpt-greeting">
                {isPatient ? t("aiAssistant.patientGreeting") : t("aiAssistant.greeting")}
              </p>

              <div className="chatgpt-suggestions">
                {suggestions.map((s, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="chatgpt-suggestion"
                    onClick={() => void send(s)}
                    disabled={sending}
                  >
                    <span>{s}</span>
                    <span className="chatgpt-suggestion-arrow" aria-hidden="true">→</span>
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

                    {m.document && (
                      <div className="chat-attachment-card">
                        <div className="att-icon" aria-hidden="true">📄</div>
                        <div className="att-meta">
                          <div className="att-name">{m.document.file_name}</div>
                          <div className="att-info">
                            {m.document.file_size ? `${(m.document.file_size / 1024).toFixed(0)} KB` : ""}
                            {m.document.exam_type && <span className="att-badge">{m.document.exam_type}</span>}
                          </div>
                        </div>
                      </div>
                    )}

                    {m.role === "assistant" ? (
                      <div className="chatgpt-msg-content chatgpt-msg-content--rich">
                        <AssistantReply content={m.content} sources={m.details?.sources} />
                      </div>
                    ) : (
                      <div className="chatgpt-msg-content">{m.content}</div>
                    )}

                    {/* Rich scanner findings card inside assistant message */}
                    {m.role === "assistant" && m.details?.scan_findings && m.details.scan_findings.length > 0 && (
                      <div className="scan-analysis-card">
                        <div className="scan-header">
                          <div className="scan-title">
                            {m.details.exam_type || t("chat.scanAnalysisTitle")}
                          </div>
                          {m.details.document_category && (
                            <span className="scan-badge-category">{m.details.document_category}</span>
                          )}
                        </div>

                        {m.details.document_summary && (
                          <div className="scan-summary-text">{m.details.document_summary}</div>
                        )}

                        <div className="scan-findings-grid">
                          <div className="kv-label">{t("chat.scanFindings")}</div>
                          {m.details.scan_findings.map((f, i) => (
                            <div key={i} className={`finding-item ${f.is_abnormal ? "is-abnormal" : ""}`}>
                              <span className="finding-area">{f.area}</span>
                              <span className="finding-desc">{f.finding}</span>
                              <span className={`finding-tag ${f.is_abnormal ? "abnormal" : "normal"}`}>
                                {f.is_abnormal ? t("chat.abnormalFinding") : t("chat.normalFinding")}
                              </span>
                            </div>
                          ))}
                        </div>

                        {m.details.trusted_solutions && m.details.trusted_solutions.length > 0 && (
                          <div className="trusted-solutions-box">
                            <div className="kv-label" style={{ color: "var(--accent)" }}>
                              {t("chat.trustedSolutionsTitle")}
                            </div>
                            {m.details.trusted_solutions.map((s, idx) => (
                              <div key={idx} className="trusted-solution-item">
                                <span className="trusted-solution-action">{s.action}</span>
                                {s.guideline_source && (
                                  <span className="trusted-solution-guideline">({s.guideline_source})</span>
                                )}
                                {s.details && (
                                  <div className="trusted-solution-details">{s.details}</div>
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}

                    {m.role === "assistant" && (
                      <div className="chatgpt-msg-actions">
                        <SpeakButton text={replyToPlainText(m.content)} />
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
                    <div className="chatgpt-msg-content muted">
                      {selectedFile ? t("chat.analyzingDocument") : t("aiAssistant.thinking")}
                    </div>
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
                      {lastReply.warning_signs && lastReply.warning_signs.length > 0 && (
                        <div className="error-box">
                          <strong>{t("aiAssistant.warningSigns")}</strong>
                          <ul className="list-plain" style={{ marginTop: 6 }}>
                            {lastReply.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                      {lastReply.abnormalities && lastReply.abnormalities.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8, color: "#f07167" }}>
                            {t("chat.abnormalitiesTitle")}
                          </div>
                          <ul className="list-plain">
                            {lastReply.abnormalities.map((a, i) => (
                              <li key={i} style={{ color: "var(--ink)" }}>• {a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {lastReply.possible_conditions && lastReply.possible_conditions.length > 0 && (
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
                      {lastReply.follow_up_questions && lastReply.follow_up_questions.length > 0 && (
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
                      {lastReply.sources && lastReply.sources.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("chat.trustedSourcesTitle")}</div>
                          <ul className="list-plain">
                            {lastReply.sources.map((s, i) =>
                              s.url ? (
                                <li key={i}>
                                  <a href={s.url} target="_blank" rel="noopener noreferrer">
                                    🌐 {s.name || s.title || s.url}
                                  </a>
                                </li>
                              ) : (
                                <li key={i}>🏛️ {s.name || s.title}</li>
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

          {/* Staged file attachment pill */}
          {selectedFile && (
            <div className="staged-file-wrap">
              <div className="staged-file-pill">
                <span className="file-icon" aria-hidden="true">📄</span>
                <span className="file-name" title={selectedFile.name}>{selectedFile.name}</span>
                <span className="file-size">({(selectedFile.size / 1024).toFixed(0)} KB)</span>
                <button
                  type="button"
                  className="file-remove"
                  onClick={() => setSelectedFile(null)}
                  title={t("chat.removeAttachment")}
                  aria-label={t("chat.removeAttachment")}
                >✕</button>
              </div>
            </div>
          )}

          <div className="chatgpt-composer">
            {/* Hidden file input */}
            <input
              type="file"
              ref={fileInputRef}
              style={{ display: "none" }}
              accept=".pdf,.docx,.png,.jpg,.jpeg,.webp,.txt,.csv"
              onChange={(e) => {
                const f = e.target.files?.[0];
                if (f) {
                  setSelectedFile(f);
                  e.target.value = "";
                }
              }}
            />

            {/* Attachment paperclip button */}
            <button
              type="button"
              className={`chatgpt-attach ${selectedFile ? "has-file" : ""}`}
              onClick={() => fileInputRef.current?.click()}
              disabled={sending}
              title={t("chat.attachFile")}
              aria-label={t("chat.attachFile")}
            >
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
              </svg>
            </button>

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
              placeholder={selectedFile ? `${selectedFile.name} — add question or press send` : (isPatient ? t("aiAssistant.patientInputPlaceholder") : t("aiAssistant.inputPlaceholder"))}
              onChange={(e) => {
                setInput(e.target.value);
                setVoiceDraft(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") void send(undefined, voiceDraft);
              }}
              disabled={sending}
            />
            <ThinkingSendButton
              sending={sending}
              disabled={sending || (!input.trim() && !selectedFile)}
              onClick={() => void send(undefined, voiceDraft)}
              label={t("aiAssistant.send")}
              thinkingLabel={t("common.analysing")}
            />
          </div>
          <p className="chatgpt-disclaimer">{t("common.disclaimer")}</p>
        </div>
      </div>
    </div>
  );
}
