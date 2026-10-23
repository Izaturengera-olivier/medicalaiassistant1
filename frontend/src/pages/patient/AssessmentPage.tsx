import { useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import { aiAPI, consultationsAPI } from "../../services/api";
import { errorMessage } from "../../hooks/useAsync";
import { Badge, urgencyLabel, urgencyTone } from "../../components/ui";
import { ConversationSidebar } from "../../components/common/ConversationSidebar";
import { MicButton } from "../../components/common/MicButton";
import { SpeakButton } from "../../components/common/SpeakButton";
import { ThinkingSendButton } from "../../components/common/ThinkingSendButton";
import { AssistantReply } from "../../components/common/AssistantReply";
import { detectLanguage, speak, stopSpeaking } from "../../utils/voice";
import { replyToPlainText } from "../../utils/replyText";

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
  exam_type?: string;
  document_category?: string;
  document_summary?: string;
  scan_findings?: ScanFinding[];
  abnormalities?: string[];
  symptoms_identified?: string[];
  follow_up_questions?: string[];
  possible_conditions?: PossibleCondition[];
  warning_signs?: string[];
  urgency_level?: string;
  trusted_solutions?: TrustedSolution[];
  general_information?: string;
  medication_information?: unknown[];
  recommended_next_step?: string;
  sources?: Source[];
  consultation_id?: number;
}

interface Message {
  id: number | string;
  role: "user" | "assistant";
  content: string;
  document?: AttachedDoc;
  details?: Assessment | null;
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
          details?: Assessment | null;
        }[];
      };
      setActiveId(id);
      setMessages(
        data.messages.map((m) => {
          const doc = m.document || (m.details && (m.details as any).attachment ? {
            id: (m.details as any).attachment.document_id,
            file_name: (m.details as any).attachment.file_name,
            file_url: (m.details as any).attachment.file_url,
            file_size: (m.details as any).attachment.file_size,
            document_category: (m.details as any).attachment.category,
            exam_type: (m.details as any).attachment.exam_type,
          } : undefined);
          return {
            id: m.id,
            role: m.role,
            content: m.content,
            document: doc,
            details: m.details,
          };
        })
      );

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
    if ((!text && !selectedFile) || sending) return;

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
      content: text || (fileToSend ? `${t("chat.scanAnalysisTitle")}: ${fileToSend.name}` : ""),
      document: fileToSend ? {
        file_name: fileToSend.name,
        file_size: fileToSend.size,
      } : undefined,
    };
    setMessages((m) => [...m, userMsg]);

    try {
      let cid = consultationId;
      if (cid === null) {
        const initialReason = text || (fileToSend ? `Medical report: ${fileToSend.name}` : "Symptom check");
        const created = await consultationsAPI.create({ chief_complaint: initialReason });
        cid = created.data.id as number;
        setConsultationId(cid);
      }

      let data: any;
      if (fileToSend) {
        const formData = new FormData();
        formData.append("file", fileToSend);
        if (text) formData.append("message", text);
        if (cid) formData.append("consultation_id", String(cid));
        if (activeId) formData.append("conversation_id", String(activeId));
        formData.append("kind", "patient");
        const res = await aiAPI.uploadAndAnalyze(formData);
        data = res.data;
      } else {
        const history = messages.map((m) => ({ role: m.role, content: m.content }));
        const res = await aiAPI.analyzeSymptoms({
          patient_input: text,
          consultation_id: cid,
          conversation_id: activeId ?? undefined,
          history,
        });
        data = res.data;
      }

      setAssessment(data);

      if (data.conversation_id && data.conversation_id !== activeId) {
        setActiveId(data.conversation_id);
      }
      setRefreshSignal((s) => s + 1);

      const reply = data.reply?.trim() || buildSummary(data);
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
        { id: nextLocalId.current--, role: "assistant", content: t("patient.assessment.failed") },
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
        footer={
          <div className="convo-context">
            <span className="convo-sidebar-footnote">{t("patient.assessment.sidebarNotice")}</span>
          </div>
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
              <h1 className="chatgpt-title">{t("patient.assessment.heroTitle")}</h1>
              <p className="chatgpt-subtitle">{t("patient.assessment.heroSub")}</p>
              <p className="chatgpt-greeting">{t("patient.assessment.heroHint")}</p>
            </div>
          ) : (
            <div className="chatgpt-thread">
              {messages.map((m) => (
                <div key={m.id} className={`chatgpt-msg chatgpt-msg--${m.role}`}>
                  <div className="chatgpt-msg-avatar" aria-hidden="true">
                    {m.role === "user" ? (
                      "Y"
                    ) : (
                      <svg viewBox="0 0 24 24" width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 3l1.9 5.8a2 2 0 0 0 1.3 1.3L21 12l-5.8 1.9a2 2 0 0 0-1.3 1.3L12 21l-1.9-5.8a2 2 0 0 0-1.3-1.3L3 12l5.8-1.9a2 2 0 0 0 1.3-1.3L12 3z" />
                      </svg>
                    )}
                  </div>
                  <div className="chatgpt-msg-body">
                    <div className="chatgpt-msg-name">
                      {m.role === "user" ? t("patient.assessment.you") : t("patient.assessment.assistant")}
                    </div>

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
                        <AssistantReply content={m.content} />
                      </div>
                    ) : (
                      <div className="chatgpt-msg-content">{m.content}</div>
                    )}

                    {/* Rich scanner / lab findings card */}
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
                    <div className="chatgpt-msg-name">{t("patient.assessment.assistant")}</div>
                    <div className="chatgpt-msg-content muted">
                      {selectedFile ? t("chat.analyzingDocument") : t("patient.assessment.thinking")}
                    </div>
                  </div>
                </div>
              )}

              {assessment && !sending && (
                <div className="chatgpt-details">
                  <button type="button" className="chatgpt-details-toggle" onClick={() => setShowDetails((v) => !v)}>
                    {showDetails ? t("chat.detailsHide") : t("chat.detailsToggle")}
                    <span aria-hidden="true">{showDetails ? "▾" : "▸"}</span>
                  </button>
                  {showDetails && (
                    <div className="chatgpt-details-body">
                      {assessment.urgency_level && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 6 }}>{t("patient.assessment.urgencyLevel")}</div>
                          <Badge tone={urgencyTone(assessment.urgency_level)}>
                            {urgencyLabel(assessment.urgency_level)}
                          </Badge>
                        </div>
                      )}
                      {assessment.warning_signs && assessment.warning_signs.length > 0 && (
                        <div className="error-box">
                          <strong>{t("patient.assessment.warningSigns")}</strong>
                          <ul className="list-plain" style={{ marginTop: 6 }}>
                            {assessment.warning_signs.map((w, i) => <li key={i}>{w}</li>)}
                          </ul>
                        </div>
                      )}
                      {assessment.abnormalities && assessment.abnormalities.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8, color: "#f07167" }}>
                            {t("chat.abnormalitiesTitle")}
                          </div>
                          <ul className="list-plain">
                            {assessment.abnormalities.map((a, i) => (
                              <li key={i} style={{ color: "var(--ink)" }}>• {a}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                      {assessment.symptoms_identified && assessment.symptoms_identified.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.assessment.identifiedSymptoms")}</div>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                            {assessment.symptoms_identified.map((s, i) => <Badge key={i} tone="neutral">{s}</Badge>)}
                          </div>
                        </div>
                      )}
                      {assessment.possible_conditions && assessment.possible_conditions.length > 0 && (
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
                      {assessment.recommended_next_step && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 6 }}>{t("patient.assessment.recommendedNextStep")}</div>
                          <p className="mb-0" style={{ fontSize: "0.94rem", color: "var(--ink-soft)" }}>
                            {assessment.recommended_next_step}
                          </p>
                        </div>
                      )}
                      {assessment.sources && assessment.sources.length > 0 && (
                        <div>
                          <div className="kv-label" style={{ marginBottom: 8 }}>{t("chat.trustedSourcesTitle")}</div>
                          <ul className="list-plain">
                            {assessment.sources.map((s, i) =>
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
              accept=".pdf,.png,.jpg,.jpeg,.webp,.txt,.csv"
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
              placeholder={selectedFile ? `${selectedFile.name} — add question or press send` : t("patient.assessment.inputPlaceholder")}
              onChange={(e) => {
                setInput(e.target.value);
                setVoiceDraft(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") void send(voiceDraft);
              }}
              disabled={sending}
            />
            <ThinkingSendButton
              sending={sending}
              disabled={sending || (!input.trim() && !selectedFile)}
              onClick={() => void send(voiceDraft)}
              label={t("patient.assessment.send")}
              thinkingLabel={t("common.analysing")}
            />
          </div>
          <p className="chatgpt-disclaimer">{t("common.disclaimer")}</p>
        </div>
      </div>
    </div>
  );
}
