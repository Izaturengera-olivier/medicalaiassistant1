import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { pharmacistsAPI } from "../../services/api";
import {
  Badge,
  ErrorState,
  Field,
  Loading,
  PageHeader,
  Panel,
  approvalLabel,
  formatDateTime,
  prescriptionStatusLabel,
  prescriptionStatusTone,
  severityLabel,
  severityTone,
} from "../../components/ui";

interface Interaction {
  id: number;
  interacting_medication: string;
  severity: string;
  description: string;
  recommendation?: string;
}

interface Detail {
  id: number;
  patient_name: string;
  patient_email: string;
  doctor_name: string;
  medication_name: string;
  dosage: string;
  frequency: string;
  duration: string;
  instructions: string;
  status: string;
  prescribed_at: string;
  pharmacist_notes?: string;
  patient_allergies?: string[];
  patient_chronic_conditions?: string[];
  interactions?: Interaction[];
  interaction_count?: number;
}

export function PrescriptionDetailPage() {
  const { t } = useTranslation();
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const prescriptionId = Number(id);

  const { data, loading, error, reload } = useAsync<Detail>(
    () => pharmacistsAPI.prescriptionDetail(prescriptionId).then((r) => r.data as Detail),
    [prescriptionId]
  );

  const [reviewStatus, setReviewStatus] = useState("APPROVED");
  const [notes, setNotes] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaveError(null);
    setSaved(false);
    try {
      await pharmacistsAPI.review(prescriptionId, {
        review_status: reviewStatus,
        pharmacist_notes: notes,
        interaction_flags: data?.interactions?.map((i) => i.interacting_medication) ?? [],
      });
      setSaved(true);
      reload();
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <Loading />;
  if (error) return <ErrorState message={error} onRetry={reload} />;
  if (!data) return null;

  return (
    <>
      <PageHeader
        title={t("pharmacist.detail.title", { id: data.id })}
        subtitle={t("pharmacist.detail.subtitle", { medication: data.medication_name, patient: data.patient_name })}
        actions={
          <button type="button" className="btn btn-ghost" onClick={() => navigate("/app/prescriptions")}>
            {t("common.back")}
          </button>
        }
      />

      {saveError && <div className="error-box">{saveError}</div>}
      {saved && <div className="success-box">{t("pharmacist.detail.reviewRecorded")}</div>}

      <div className="stack">
        <Panel title={t("pharmacist.detail.prescription")}>
          <div className="kv-grid">
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.status")}</span>
              <span className="kv-value">
                <Badge tone={prescriptionStatusTone(data.status)}>{prescriptionStatusLabel(data.status)}</Badge>
              </span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.patient")}</span>
              <span className="kv-value">{data.patient_name} · {data.patient_email}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.prescriber")}</span>
              <span className="kv-value">{data.doctor_name}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.medication")}</span>
              <span className="kv-value">{data.medication_name}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.dosage")}</span>
              <span className="kv-value">{data.dosage || "—"}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.frequency")}</span>
              <span className="kv-value">{data.frequency || "—"}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.duration")}</span>
              <span className="kv-value">{data.duration || "—"}</span>
            </div>
            <div className="kv-item">
              <span className="kv-label">{t("pharmacist.detail.prescribed")}</span>
              <span className="kv-value">{formatDateTime(data.prescribed_at)}</span>
            </div>
            {data.instructions && (
              <div className="kv-item" style={{ gridColumn: "1 / -1" }}>
                <span className="kv-label">{t("pharmacist.detail.instructions")}</span>
                <span className="kv-value">{data.instructions}</span>
              </div>
            )}
          </div>
        </Panel>

        <div className="grid-2">
          <Panel title={t("pharmacist.detail.safetyProfile")}>
            <div className="stack">
              <div>
                <div className="kv-label" style={{ marginBottom: 6 }}>{t("pharmacist.detail.recordedAllergies")}</div>
                {data.patient_allergies?.length ? (
                  <div className="chip-row">
                    {data.patient_allergies.map((a, i) => (
                      <Badge key={i} tone="danger">{a}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="muted mb-0" style={{ fontSize: "0.9rem" }}>{t("common.noneRecorded")}</p>
                )}
              </div>
              <div>
                <div className="kv-label" style={{ marginBottom: 6 }}>{t("pharmacist.detail.chronicConditions")}</div>
                {data.patient_chronic_conditions?.length ? (
                  <div className="chip-row">
                    {data.patient_chronic_conditions.map((c, i) => (
                      <Badge key={i} tone="warn">{c}</Badge>
                    ))}
                  </div>
                ) : (
                  <p className="muted mb-0" style={{ fontSize: "0.9rem" }}>{t("common.noneRecorded")}</p>
                )}
              </div>
            </div>
          </Panel>

          <Panel title={t("pharmacist.detail.interactionsTitle")} subtitle={t("pharmacist.detail.interactionsSub")}>
            {data.interactions && data.interactions.length > 0 ? (
              <ul className="list-plain">
                {data.interactions.map((i) => (
                  <li key={i.id}>
                    <Badge tone={severityTone(i.severity)}>{severityLabel(i.severity)}</Badge>{" "}
                    <strong>{i.interacting_medication}</strong> — {i.description}
                    {i.recommendation ? <em> {t("pharmacist.detail.recommendation")} {i.recommendation}</em> : null}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted mb-0">{t("pharmacist.detail.noInteractions")}</p>
            )}
          </Panel>
        </div>

        <Panel title={t("pharmacist.detail.reviewTitle")} subtitle={t("pharmacist.detail.reviewSub")}>
          <form onSubmit={submit}>
            <div className="form-grid">
              <Field label={t("pharmacist.detail.reviewDecision")} htmlFor="review">
                <select id="review" className="select" value={reviewStatus} onChange={(e) => setReviewStatus(e.target.value)}>
                  <option value="APPROVED">{approvalLabel("APPROVED")}</option>
                  <option value="FLAGGED">{approvalLabel("FLAGGED")}</option>
                  <option value="REJECTED">{approvalLabel("REJECTED")}</option>
                </select>
              </Field>
              <Field label={t("pharmacist.detail.pharmacistNotes")} htmlFor="pnotes" span2>
                <textarea id="pnotes" className="textarea" value={notes} onChange={(e) => setNotes(e.target.value)} />
              </Field>
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? t("common.saving") : t("pharmacist.detail.submitReview")}
              </button>
            </div>
          </form>
        </Panel>
      </div>
    </>
  );
}
