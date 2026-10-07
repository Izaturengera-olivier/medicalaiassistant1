import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { medicationsAPI } from "../../services/api";
import {
  Badge,
  EmptyState,
  ErrorState,
  Field,
  Loading,
  PageHeader,
  Panel,
  formatDate,
  titleCase,
  unwrapList,
} from "../../components/ui";

interface Medication {
  id: number;
  name: string;
  generic_name?: string;
  drug_class?: string;
  indications?: string[];
  contraindications?: string[];
  known_interactions?: string[];
  allergy_warnings?: string[];
  precautions?: string[];
  reference_source?: string;
  last_verified_date?: string | null;
}

export function MedicationsPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [applied, setApplied] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);

  const [showAddModal, setShowAddModal] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [newMed, setNewMed] = useState({
    name: "",
    generic_name: "",
    drug_class: "analgesic",
    reference_source: "WHO Essential Medicines",
    indications: "",
    contraindications: "",
  });

  const { data, loading, error, reload } = useAsync<Medication[]>(
    () => medicationsAPI.list(applied ? { search: applied } : undefined).then((r) => unwrapList<Medication>(r.data)),
    [applied]
  );

  const selected = data?.find((m) => m.id === selectedId) ?? null;

  const handleCreateMedication = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    try {
      const payload = {
        name: newMed.name,
        generic_name: newMed.generic_name,
        drug_class: newMed.drug_class,
        reference_source: newMed.reference_source,
        indications: newMed.indications ? newMed.indications.split(",").map((s) => s.trim()) : [],
        contraindications: newMed.contraindications ? newMed.contraindications.split(",").map((s) => s.trim()) : [],
      };
      await medicationsAPI.create(payload);
      setShowAddModal(false);
      setNewMed({
        name: "",
        generic_name: "",
        drug_class: "analgesic",
        reference_source: "WHO Essential Medicines",
        indications: "",
        contraindications: "",
      });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const handleDeleteMedication = async (med: Medication) => {
    if (!window.confirm(`Are you sure you want to delete ${med.name}?`)) return;
    setActionError(null);
    try {
      await medicationsAPI.delete(med.id);
      setSelectedId(null);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <PageHeader title={t("admin.medications.title")} subtitle={t("admin.medications.subtitle")} />
        <button type="button" className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          + Add Medication
        </button>
      </div>

      {actionError && <div className="error-box" style={{ marginBottom: 16 }}>{actionError}</div>}

      <Panel title={t("admin.medications.search")} bodyless>
        <div className="panel-body form-grid">
          <Field label={t("admin.medications.nameLabel")} htmlFor="medsearch">
            <input
              id="medsearch"
              className="input"
              placeholder={t("admin.medications.searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") setApplied(search);
              }}
            />
          </Field>
          <div className="field" style={{ justifyContent: "flex-end" }}>
            <button type="button" className="btn btn-outline" onClick={() => setApplied(search)}>
              {t("common.apply")}
            </button>
          </div>
        </div>
      </Panel>

      <div style={{ height: 20 }} />

      <div className="grid-2">
        <Panel title={t("admin.medications.catalog")} bodyless>
          {loading ? (
            <Loading />
          ) : error ? (
            <ErrorState message={error} onRetry={reload} />
          ) : !data || data.length === 0 ? (
            <EmptyState title={t("admin.medications.emptyTitle")} message={t("admin.medications.emptyMessage")} />
          ) : (
            <div className="table-wrap" style={{ maxHeight: 480, overflowY: "auto" }}>
              <table className="table">
                <thead>
                  <tr>
                    <th>{t("admin.medications.name")}</th>
                    <th>{t("admin.medications.generic")}</th>
                    <th>{t("admin.medications.class")}</th>
                  </tr>
                </thead>
                <tbody>
                  {data.map((m) => (
                    <tr
                      key={m.id}
                      onClick={() => setSelectedId(m.id)}
                      style={{ cursor: "pointer", background: m.id === selectedId ? "#eef6f8" : undefined }}
                    >
                      <td className="cell-strong">{m.name}</td>
                      <td>{m.generic_name || "—"}</td>
                      <td>
                        <Badge>{titleCase(m.drug_class)}</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Panel>

        <Panel title={selected ? selected.name : t("admin.medications.detail")} subtitle={t("admin.medications.detailSub")}>
          {!selected ? (
            <EmptyState title={t("admin.medications.selectTitle")} message={t("admin.medications.selectMessage")} />
          ) : (
            <div className="stack">
              <div className="kv-grid">
                <div className="kv-item">
                  <span className="kv-label">{t("admin.medications.genericName")}</span>
                  <span className="kv-value">{selected.generic_name || "—"}</span>
                </div>
                <div className="kv-item">
                  <span className="kv-label">{t("admin.medications.drugClass")}</span>
                  <span className="kv-value">{titleCase(selected.drug_class)}</span>
                </div>
                <div className="kv-item">
                  <span className="kv-label">{t("admin.medications.lastVerified")}</span>
                  <span className="kv-value">{formatDate(selected.last_verified_date)}</span>
                </div>
                <div className="kv-item">
                  <span className="kv-label">{t("admin.medications.reference")}</span>
                  <span className="kv-value">{selected.reference_source || "—"}</span>
                </div>
              </div>
              <SafetyList label={t("admin.medications.indications")} items={selected.indications} tone="info" />
              <SafetyList label={t("admin.medications.contraindications")} items={selected.contraindications} tone="danger" />
              <SafetyList label={t("admin.medications.knownInteractions")} items={selected.known_interactions} tone="warn" />
              <SafetyList label={t("admin.medications.allergyWarnings")} items={selected.allergy_warnings} tone="danger" />
              <SafetyList label={t("admin.medications.precautions")} items={selected.precautions} tone="neutral" />

              <div style={{ marginTop: 16, paddingTop: 16, borderTop: "1px solid #e2e8f0" }}>
                <button
                  type="button"
                  className="btn btn-outline"
                  style={{ color: "#d9534f", borderColor: "#d9534f" }}
                  onClick={() => handleDeleteMedication(selected)}
                >
                  Delete Medication
                </button>
              </div>
            </div>
          )}
        </Panel>
      </div>

      {/* Add Medication Modal */}
      {showAddModal && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000,
          display: "flex", justifyContent: "center", alignItems: "center"
        }}>
          <div style={{ background: "#fff", padding: 24, borderRadius: 8, width: 450, maxWidth: "90%" }}>
            <h3 style={{ marginTop: 0 }}>Add New Medication</h3>
            <form onSubmit={handleCreateMedication} className="stack">
              <Field label="Brand / Trade Name">
                <input className="input" required value={newMed.name} onChange={(e) => setNewMed({...newMed, name: e.target.value})} />
              </Field>
              <Field label="Generic Name">
                <input className="input" required value={newMed.generic_name} onChange={(e) => setNewMed({...newMed, generic_name: e.target.value})} />
              </Field>
              <Field label="Drug Class">
                <input className="input" required value={newMed.drug_class} onChange={(e) => setNewMed({...newMed, drug_class: e.target.value})} />
              </Field>
              <Field label="Indications (comma separated)">
                <input className="input" placeholder="e.g. Fever, Pain, Inflammation" value={newMed.indications} onChange={(e) => setNewMed({...newMed, indications: e.target.value})} />
              </Field>
              <Field label="Contraindications (comma separated)">
                <input className="input" placeholder="e.g. Severe liver impairment, Allergy" value={newMed.contraindications} onChange={(e) => setNewMed({...newMed, contraindications: e.target.value})} />
              </Field>
              <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Save Medication</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowAddModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

function SafetyList({ label, items, tone }: { label: string; items?: string[]; tone: "info" | "danger" | "warn" | "neutral" }) {
  const { t } = useTranslation();
  return (
    <div>
      <div className="kv-label" style={{ marginBottom: 6 }}>{label}</div>
      {items && items.length > 0 ? (
        <div className="chip-row">
          {items.map((i, idx) => (
            <Badge key={idx} tone={tone}>{i}</Badge>
          ))}
        </div>
      ) : (
        <p className="muted mb-0" style={{ fontSize: "0.9rem" }}>{t("common.noneRecorded")}</p>
      )}
    </div>
  );
}
