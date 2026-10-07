import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { doctorsAPI } from "../../services/api";
import {
  Badge,
  ErrorState,
  Field,
  Loading,
  PageHeader,
  Panel,
  consultationStatusLabel,
  consultationStatusTone,
  formatDateTime,
  urgencyLabel,
  urgencyTone,
} from "../../components/ui";

interface MedicalHistoryRow {
  condition_name: string;
  diagnosis_date?: string | null;
  notes?: string;
}

interface Detail {
  id: number;
  patient_name: string;
  patient_email: string;
  chief_complaint: string;
  status: string;
  created_at: string;
  assigned_doctor?: number | null;
  medical_history?: MedicalHistoryRow[];
  ai_assessment?: {
    symptoms_identified?: string[];
    possible_conditions?: { name?: string; likelihood?: string; description?: string }[];
    urgency_level?: string;
    warning_signs?: string[];
    recommended_next_step?: string;
  } | null;
}

export function ConsultationDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const consultationId = Number(id);

  const { data, loading, error, reload } = useAsync<Detail>(
    () => doctorsAPI.consultationDetail(consultationId).then((r) => r.data as Detail),
    [consultationId]
  );

  const [form, setForm] = useState({
    status: "IN_PROGRESS",
    diagnosis: "",
    notes: "",
    treatment_recommendation: "",
    follow_up_required: false,
    accept_ai_assessment: false,
  });
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (data) setForm((f) => ({ ...f, status: data.status }));
  }, [data]);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      await doctorsAPI.review(consultationId, {
        consultation_id: consultationId,
        ...form,
      });
      setSaved(true);
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const assignToMe = async () => {
    setSaveError(null);
    try {
      await doctorsAPI.assign(consultationId);
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    }
  };

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return null;

  const ai = data.ai_assessment;

  return (
    <>
      <PageHeader
        title={t("doctor.detail.title", { id: data.id })}
        subtitle={`${data.patient_name} · ${data.patient_email}`}
        actions={
          <>
            <button type="button" className="btn btn-outline" onClick={() => void assignToMe()}>
              {t("doctor.detail.assignToMe")}
            </button>
            <button type="button" className="btn btn-ghost" onClick={() => navigate("/app/consultations")}>
              {t("common.back")}
            </button>
          </>
        }
      />

      {saveError && <div className="error-box">{saveError}</div>}
      {saved && <div className="success-box">{t("doctor.detail.reviewSaved")}</div>}

      <div className="stack">
        <Panel title={t("doctor.detail.overview")}>
          <div className="kv-grid">
            <div className="kv-item">
              <span className="kv-label">{t("doctor.detail.status")}</span>
              <span className="kv-value">
                <Badge tone={consultationStatusTone(data.status)}>{consultationStatusLabel(data.status)}</Badge>
              </span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("common.started")}</span>
              <span className="kv-value">{formatDateTime(data.created_at)}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("common.chiefComplaint")}</span>
              <span className="kv-value">{data.chief_complaint}</span>
            </div>
          </div>
        </Panel>

        <Panel
          title={t("doctor.detail.aiTitle")}
          subtitle={t("doctor.detail.aiSub")}
          actions={
            ai?.urgency_level ? (
              <Badge tone={urgencyTone(ai.urgency_level)}>{urgencyLabel(ai.urgency_level)}</Badge>
            ) : undefined
          }
        >
          {!ai ? (
            <p className="muted mb-0">{t("doctor.detail.noAi")}</p>
          ) : (
            <div className="stack">
              {ai.warning_signs && ai.warning_signs.length > 0 && (
                <div className="error-box mb-0">
                  <strong>{t("doctor.detail.warningSigns")}</strong>
                  <ul className="list-plain" style={{ marginTop: 6 }}>
                    {ai.warning_signs.map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}
              {ai.symptoms_identified && ai.symptoms_identified.length > 0 && (
                <div>
                  <div className="kv-label" style={{ marginBottom: 6 }}>{t("doctor.detail.symptomsIdentified")}</div>
                  <div className="chip-row">
                    {ai.symptoms_identified.map((s, i) => (
                      <Badge key={i} tone="info">{s}</Badge>
                    ))}
                  </div>
                </div>
              )}
              {ai.possible_conditions && ai.possible_conditions.length > 0 && (
                <div>
                  <div className="kv-label" style={{ marginBottom: 8 }}>{t("doctor.detail.possibleConditions")}</div>
                  <ul className="list-plain">
                    {ai.possible_conditions.map((c, i) => (
                      <li key={i}>
                        <strong>{c.name}</strong>
                        {c.likelihood ? ` — ${c.likelihood}` : ""}
                        {c.description ? `: ${c.description}` : ""}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {ai.recommended_next_step && (
                <div>
                  <div className="kv-label" style={{ marginBottom: 6 }}>{t("doctor.detail.aiNextStep")}</div>
                  <p className="mb-0" style={{ fontSize: "0.94rem", color: "var(--ink-soft)" }}>{ai.recommended_next_step}</p>
                </div>
              )}
            </div>
          )}
        </Panel>

        <Panel title={t("doctor.detail.historyTitle")}>
          {data.medical_history && data.medical_history.length > 0 ? (
            <ul className="list-plain">
              {data.medical_history.map((h, i) => (
                <li key={i}>
                  <strong>{h.condition_name}</strong>
                  {h.diagnosis_date ? ` · ${t("doctor.detail.diagnosed", { date: h.diagnosis_date })}` : ""}
                  {h.notes ? ` · ${h.notes}` : ""}
                </li>
              ))}
            </ul>
          ) : (
            <p className="muted mb-0">{t("doctor.detail.noHistory")}</p>
          )}
        </Panel>

        <Panel title={t("doctor.detail.reviewTitle")} subtitle={t("doctor.detail.reviewSub")}>
          <form onSubmit={submit}>
            <div className="form-grid">
              <Field label={t("doctor.detail.status")} htmlFor="status">
                <select
                  id="status"
                  className="select"
                  value={form.status}
                  onChange={(e) => setForm((f) => ({ ...f, status: e.target.value }))}
                >
                  <option value="IN_PROGRESS">{consultationStatusLabel("IN_PROGRESS")}</option>
                  <option value="COMPLETED">{consultationStatusLabel("COMPLETED")}</option>
                  <option value="CANCELLED">{consultationStatusLabel("CANCELLED")}</option>
                </select>
              </Field>
              <Field label={t("doctor.detail.diagnosis")} htmlFor="diagnosis" span2>
                <textarea
                  id="diagnosis"
                  className="textarea"
                  value={form.diagnosis}
                  onChange={(e) => setForm((f) => ({ ...f, diagnosis: e.target.value }))}
                />
              </Field>
              <Field label={t("doctor.detail.clinicalNotes")} htmlFor="notes" span2>
                <textarea
                  id="notes"
                  className="textarea"
                  value={form.notes}
                  onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))}
                />
              </Field>
              <Field label={t("doctor.detail.treatment")} htmlFor="treatment" span2>
                <textarea
                  id="treatment"
                  className="textarea"
                  value={form.treatment_recommendation}
                  onChange={(e) => setForm((f) => ({ ...f, treatment_recommendation: e.target.value }))}
                />
              </Field>
              <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.92rem" }}>
                <input
                  type="checkbox"
                  checked={form.follow_up_required}
                  onChange={(e) => setForm((f) => ({ ...f, follow_up_required: e.target.checked }))}
                />
                {t("doctor.detail.followUpRequired")}
              </label>
              <label style={{ display: "flex", gap: 8, alignItems: "center", fontSize: "0.92rem" }}>
                <input
                  type="checkbox"
                  checked={form.accept_ai_assessment}
                  onChange={(e) => setForm((f) => ({ ...f, accept_ai_assessment: e.target.checked }))}
                />
                {t("doctor.detail.acceptAi")}
              </label>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? t("common.saving") : t("doctor.detail.saveReview")}
              </button>
            </div>
          </form>
        </Panel>
      </div>
    </>
  );
}
