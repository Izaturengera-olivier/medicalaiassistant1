import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { medicalAPI } from "../../services/api";
import { Badge, EmptyState, ErrorState, Field, Loading, PageHeader, Panel, titleCase, unwrapList } from "../../components/ui";

interface Condition {
  id: number;
  name: string;
  description?: string;
  icd_code?: string;
  category?: string;
  common_symptoms?: string[];
}

export function ConditionsPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [applied, setApplied] = useState("");

  const [showAddModal, setShowAddModal] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);
  const [newCond, setNewCond] = useState({
    name: "",
    icd_code: "",
    category: "General",
    description: "",
    common_symptoms: "",
  });

  const { data, loading, error, reload } = useAsync<Condition[]>(
    () => medicalAPI.conditions(applied ? { search: applied } : undefined).then((r) => unwrapList<Condition>(r.data)),
    [applied]
  );

  const handleCreateCondition = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    try {
      const payload = {
        name: newCond.name,
        icd_code: newCond.icd_code,
        category: newCond.category,
        description: newCond.description,
        common_symptoms: newCond.common_symptoms ? newCond.common_symptoms.split(",").map((s) => s.trim()) : [],
      };
      await medicalAPI.createCondition(payload);
      setShowAddModal(false);
      setNewCond({
        name: "",
        icd_code: "",
        category: "General",
        description: "",
        common_symptoms: "",
      });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  const handleDeleteCondition = async (cond: Condition) => {
    if (!window.confirm(`Are you sure you want to delete ${cond.name}?`)) return;
    setActionError(null);
    try {
      await medicalAPI.deleteCondition(cond.id);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <PageHeader title={t("admin.conditions.title")} subtitle={t("admin.conditions.subtitle")} />
        <button type="button" className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          + Add Condition
        </button>
      </div>

      {actionError && <div className="error-box" style={{ marginBottom: 16 }}>{actionError}</div>}

      <Panel title={t("admin.conditions.search")} bodyless>
        <div className="panel-body form-grid">
          <Field label={t("admin.conditions.nameLabel")} htmlFor="condsearch">
            <input
              id="condsearch"
              className="input"
              placeholder={t("admin.conditions.searchPlaceholder")}
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

      <Panel bodyless>
        {loading ? (
          <Loading />
        ) : error ? (
          <ErrorState message={error} onRetry={reload} />
        ) : !data || data.length === 0 ? (
          <EmptyState title={t("admin.conditions.emptyTitle")} message={t("admin.conditions.emptyMessage")} />
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("admin.conditions.name")}</th>
                  <th>{t("admin.conditions.icdCode")}</th>
                  <th>{t("admin.conditions.category")}</th>
                  <th>{t("admin.conditions.commonSymptoms")}</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {data.map((c) => (
                  <tr key={c.id}>
                    <td className="cell-strong">{c.name}</td>
                    <td>{c.icd_code || "—"}</td>
                    <td>
                      <Badge>{titleCase(c.category)}</Badge>
                    </td>
                    <td>
                      <div className="chip-row">
                        {(c.common_symptoms ?? []).slice(0, 6).map((s, i) => (
                          <Badge key={i} tone="info">{s}</Badge>
                        ))}
                      </div>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm btn-outline"
                        style={{ color: "#d9534f", borderColor: "#d9534f" }}
                        onClick={() => handleDeleteCondition(c)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </Panel>

      {/* Add Condition Modal */}
      {showAddModal && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000,
          display: "flex", justifyContent: "center", alignItems: "center"
        }}>
          <div style={{ background: "#fff", padding: 24, borderRadius: 8, width: 450, maxWidth: "90%" }}>
            <h3 style={{ marginTop: 0 }}>Add New Medical Condition</h3>
            <form onSubmit={handleCreateCondition} className="stack">
              <Field label="Condition Name">
                <input className="input" required value={newCond.name} onChange={(e) => setNewCond({...newCond, name: e.target.value})} />
              </Field>
              <div className="form-grid">
                <Field label="ICD Code">
                  <input className="input" placeholder="e.g. R51" value={newCond.icd_code} onChange={(e) => setNewCond({...newCond, icd_code: e.target.value})} />
                </Field>
                <Field label="Category">
                  <input className="input" required value={newCond.category} onChange={(e) => setNewCond({...newCond, category: e.target.value})} />
                </Field>
              </div>
              <Field label="Clinical Description">
                <textarea className="input" rows={3} value={newCond.description} onChange={(e) => setNewCond({...newCond, description: e.target.value})} />
              </Field>
              <Field label="Common Symptoms (comma separated)">
                <input className="input" placeholder="e.g. Fever, Headache, Fatigue" value={newCond.common_symptoms} onChange={(e) => setNewCond({...newCond, common_symptoms: e.target.value})} />
              </Field>
              <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Save Condition</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowAddModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
