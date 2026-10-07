import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync } from "../../hooks/useAsync";
import { consultationsAPI } from "../../services/api";
import {
  Badge,
  EmptyState,
  ErrorState,
  Loading,
  PageHeader,
  Panel,
  consultationStatusLabel,
  consultationStatusTone,
  formatDateTime,
  severityLabel,
  unwrapList,
} from "../../components/ui";

interface PatientSymptom {
  id: number;
  symptom?: { name: string };
  severity: string;
  duration?: string;
  notes?: string;
}

interface FollowUp {
  id: number;
  question: string;
  answer?: string;
}

interface Consultation {
  id: number;
  status: string;
  chief_complaint: string;
  created_at: string;
  completed_at?: string | null;
  patient_symptoms?: PatientSymptom[];
  follow_up_questions?: FollowUp[];
}

export function ConsultationHistoryPage() {
  const { t } = useTranslation();
  const { data, loading, error, reload } = useAsync<Consultation[]>(
    () => consultationsAPI.list().then((r) => unwrapList<Consultation>(r.data))
  );
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const consultations = data ?? [];
  const selected = consultations.find((c) => c.id === selectedId) ?? null;

  return (
    <>
      <PageHeader title={t("patient.history.title")} subtitle={t("patient.history.subtitle")} />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : consultations.length === 0 ? (
        <Panel>
          <EmptyState title={t("patient.history.emptyTitle")} message={t("patient.history.emptyMessage")} />
        </Panel>
      ) : (
        <div className="grid-2">
          <Panel title={t("patient.history.listTitle")} bodyless>
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("common.id")}</th>
                    <th>{t("common.chiefComplaint")}</th>
                    <th>{t("common.status")}</th>
                    <th>{t("common.started")}</th>
                  </tr>
                </thead>
                <tbody>
                  {consultations.map((c) => (
                    <tr
                      key={c.id}
                      onClick={() => setSelectedId(c.id)}
                      style={{ cursor: "pointer", background: c.id === selectedId ? "#eef6f8" : undefined }}
                    >
                      <td className="cell-strong">{c.id}</td>
                      <td>{c.chief_complaint}</td>
                      <td>
                        <Badge tone={consultationStatusTone(c.status)}>
                          {consultationStatusLabel(c.status)}
                        </Badge>
                      </td>
                      <td>{formatDateTime(c.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>

          <Panel
            title={selected ? t("patient.history.detailTitle", { id: selected.id }) : t("patient.history.detailFallback")}
            subtitle={t("patient.history.detailSub")}
          >
            {!selected ? (
              <EmptyState title={t("patient.history.selectTitle")} message={t("patient.history.selectMessage")} />
            ) : (
              <div className="stack">
                <div className="kv-grid">
                  <div className="kv-item">
                    <span className="kv-label">{t("common.status")}</span>
                    <span className="kv-value">
                      <Badge tone={consultationStatusTone(selected.status)}>{consultationStatusLabel(selected.status)}</Badge>
                    </span>
                  </div>
                  <div className="kv-item">
                    <span className="kv-label">{t("common.started")}</span>
                    <span className="kv-value">{formatDateTime(selected.created_at)}</span>
                  </div>
                  <div className="kv-item">
                    <span className="kv-label">{t("common.completed")}</span>
                    <span className="kv-value">{formatDateTime(selected.completed_at)}</span>
                  </div>
                  <div className="kv-item">
                    <span className="kv-label">{t("common.chiefComplaint")}</span>
                    <span className="kv-value">{selected.chief_complaint}</span>
                  </div>
                </div>

                <div>
                  <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.history.reportedSymptoms")}</div>
                  {selected.patient_symptoms?.length ? (
                    <ul className="list-plain">
                      {selected.patient_symptoms.map((s) => (
                        <li key={s.id}>
                          <strong>{s.symptom?.name ?? t("patient.history.symptomFallback")}</strong> — {severityLabel(s.severity)}
                          {s.duration ? ` · ${s.duration}` : ""}
                          {s.notes ? ` · ${s.notes}` : ""}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted mb-0" style={{ fontSize: "0.9rem" }}>{t("patient.history.noSymptoms")}</p>
                  )}
                </div>

                <div>
                  <div className="kv-label" style={{ marginBottom: 8 }}>{t("patient.history.followUpQuestions")}</div>
                  {selected.follow_up_questions?.length ? (
                    <ul className="list-plain">
                      {selected.follow_up_questions.map((f) => (
                        <li key={f.id}>
                          {f.question}
                          {f.answer ? <em> — {t("patient.history.answered", { answer: f.answer })}</em> : <em> — {t("patient.history.awaitingAnswer")}</em>}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="muted mb-0" style={{ fontSize: "0.9rem" }}>{t("patient.history.noFollowUps")}</p>
                  )}
                </div>
              </div>
            )}
          </Panel>
        </div>
      )}
    </>
  );
}
