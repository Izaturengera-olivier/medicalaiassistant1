import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { patientProfileAPI } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { Field, Loading, ErrorState, PageHeader, Panel, roleLabel } from "../../components/ui";

const GENDERS = ["MALE", "FEMALE", "OTHER"];

interface PatientProfile {
  date_of_birth?: string | null;
  gender?: string;
  phone?: string;
  address?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  blood_type?: string;
  allergies?: string[];
  chronic_conditions?: string[];
}

const toList = (value: string): string[] =>
  value
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

export function ProfilePage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const { data, loading, error, reload } = useAsync<PatientProfile>(
    () => patientProfileAPI.get().then((r) => r.data as PatientProfile)
  );

  const [form, setForm] = useState({
    date_of_birth: "",
    gender: "",
    phone: "",
    address: "",
    emergency_contact_name: "",
    emergency_contact_phone: "",
    blood_type: "",
    allergies: "",
    chronic_conditions: "",
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  useEffect(() => {
    if (data) {
      setForm({
        date_of_birth: data.date_of_birth ?? "",
        gender: data.gender ?? "",
        phone: data.phone ?? "",
        address: data.address ?? "",
        emergency_contact_name: data.emergency_contact_name ?? "",
        emergency_contact_phone: data.emergency_contact_phone ?? "",
        blood_type: data.blood_type ?? "",
        allergies: (data.allergies ?? []).join(", "),
        chronic_conditions: (data.chronic_conditions ?? []).join(", "),
      });
    }
  }, [data]);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) =>
    setForm((f) => ({ ...f, [key]: e.target.value }));

  const save = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSaved(false);
    setSaveError(null);
    try {
      await patientProfileAPI.update({
        date_of_birth: form.date_of_birth || null,
        gender: form.gender,
        phone: form.phone,
        address: form.address,
        emergency_contact_name: form.emergency_contact_name,
        emergency_contact_phone: form.emergency_contact_phone,
        blood_type: form.blood_type,
        allergies: toList(form.allergies),
        chronic_conditions: toList(form.chronic_conditions),
      });
      setSaved(true);
    } catch (err) {
      setSaveError(errorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <PageHeader title={t("patient.profile.title")} subtitle={t("patient.profile.subtitle")} />

      {loading ? (
        <Loading />
      ) : error ? (
        <ErrorState message={error} onRetry={reload} />
      ) : (
        <div className="stack">
          <Panel title={t("patient.profile.account")}>
            <div className="kv-grid">
              <div className="kv-item">
                <span className="kv-label">{t("patient.profile.name")}</span>
                <span className="kv-value">{user?.first_name} {user?.last_name}</span>
              </div>
              <div className="kv-item">
                <span className="kv-label">{t("patient.profile.email")}</span>
                <span className="kv-value">{user?.email}</span>
              </div>
              <div className="kv-item">
                <span className="kv-label">{t("patient.profile.role")}</span>
                <span className="kv-value">{user?.role ? roleLabel(user.role) : "—"}</span>
              </div>
            </div>
          </Panel>

          <Panel title={t("patient.profile.medicalTitle")} subtitle={t("patient.profile.medicalSub")}>
            {saveError && <div className="error-box">{saveError}</div>}
            {saved && <div className="success-box">{t("patient.profile.saved")}</div>}
            <form onSubmit={save}>
              <div className="form-grid">
                <Field label={t("patient.profile.dob")} htmlFor="dob">
                  <input id="dob" type="date" className="input" value={form.date_of_birth} onChange={set("date_of_birth")} />
                </Field>
                <Field label={t("patient.profile.gender")} htmlFor="gender">
                  <select id="gender" className="select" value={form.gender} onChange={set("gender")}>
                    <option value="">{t("status.gender.select")}</option>
                    {GENDERS.map((g) => (
                      <option key={g} value={g}>{t(`status.gender.${g}`)}</option>
                    ))}
                  </select>
                </Field>
                <Field label={t("patient.profile.phone")} htmlFor="phone">
                  <input id="phone" className="input" value={form.phone} onChange={set("phone")} />
                </Field>
                <Field label={t("patient.profile.bloodType")} htmlFor="blood">
                  <input id="blood" className="input" value={form.blood_type} onChange={set("blood_type")} placeholder={t("patient.profile.bloodPlaceholder")} />
                </Field>
                <Field label={t("patient.profile.address")} htmlFor="address" span2>
                  <textarea id="address" className="textarea" value={form.address} onChange={set("address")} />
                </Field>
                <Field label={t("patient.profile.emergencyName")} htmlFor="ecname">
                  <input id="ecname" className="input" value={form.emergency_contact_name} onChange={set("emergency_contact_name")} />
                </Field>
                <Field label={t("patient.profile.emergencyPhone")} htmlFor="ecphone">
                  <input id="ecphone" className="input" value={form.emergency_contact_phone} onChange={set("emergency_contact_phone")} />
                </Field>
                <Field label={t("patient.profile.allergies")} htmlFor="allergies" hint={t("patient.profile.allergiesHint")} span2>
                  <input id="allergies" className="input" value={form.allergies} onChange={set("allergies")} />
                </Field>
                <Field label={t("patient.profile.chronic")} htmlFor="chronic" hint={t("patient.profile.chronicHint")} span2>
                  <input id="chronic" className="input" value={form.chronic_conditions} onChange={set("chronic_conditions")} />
                </Field>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? t("common.saving") : t("patient.profile.saveProfile")}
                </button>
              </div>
            </form>
          </Panel>
        </div>
      )}
    </>
  );
}
