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
  severityLabel,
  severityTone,
  titleCase,
  unwrapList,
} from "../../components/ui";

interface Medication {
  id: number;
  name: string;
  generic_name?: string;
  drug_class?: string;
}

interface Interaction {
  id: number;
  medication_1_name: string;
  medication_2_name: string;
  interaction_type: string;
  severity: string;
  description: string;
  evidence_source?: string;
  recommendation?: string;
}

interface InteractionsResponse {
  medication: string;
  interactions: Interaction[];
}

export function InteractionCheckerPage() {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [checkError, setCheckError] = useState<string | null>(null);

  const meds = useAsync<Medication[]>(
    () => medicationsAPI.list(search ? { search } : undefined).then((r) => unwrapList<Medication>(r.data)),
    [search]
  );

  const interactions = useAsync<InteractionsResponse | null>(
    () =>
      selectedId === null
        ? Promise.resolve(null)
        : medicationsAPI.interactions(selectedId).then((r) => r.data as InteractionsResponse),
    [selectedId]
  );

  const pick = (id: number) => {
    setSelectedId(id);
    setCheckError(null);
  };

  return (
    <>
      <PageHeader
        title={t("pharmacist.interactions.title")}
        subtitle={t("pharmacist.interactions.subtitle")}
      />

      <div className="grid-2">
        <Panel title={t("pharmacist.interactions.chooseTitle")}>
          <Field label={t("pharmacist.interactions.searchLabel")} htmlFor="medsearch">
            <input
              id="medsearch"
              className="input"
              placeholder={t("pharmacist.interactions.searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </Field>
          <div style={{ marginTop: 14 }}>
            {meds.loading ? (
              <Loading />
            ) : meds.error ? (
              <ErrorState message={meds.error} onRetry={meds.reload} />
            ) : !meds.data || meds.data.length === 0 ? (
              <EmptyState title={t("pharmacist.interactions.emptyMedsTitle")} message={t("pharmacist.interactions.emptyMedsMessage")} />
            ) : (
              <div className="table-wrap" style={{ maxHeight: 320, overflowY: "auto" }}>
                <table className="table">
                  <tbody>
                    {meds.data.map((m) => (
                      <tr
                        key={m.id}
                        onClick={() => pick(m.id)}
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
          </div>
        </Panel>

        <Panel title={t("pharmacist.interactions.resultsTitle")} subtitle={selectedId ? undefined : t("pharmacist.interactions.resultsSubUnselected")}>
          {checkError && <div className="error-box">{checkError}</div>}
          {selectedId === null ? (
            <EmptyState title={t("pharmacist.interactions.nothingTitle")} message={t("pharmacist.interactions.nothingMessage")} />
          ) : interactions.loading ? (
            <Loading />
          ) : interactions.error ? (
            <ErrorState
              message={errorMessage(interactions.error)}
              onRetry={interactions.reload}
            />
          ) : !interactions.data || interactions.data.interactions.length === 0 ? (
            <EmptyState
              title={t("pharmacist.interactions.noneTitle")}
              message={t("pharmacist.interactions.noneMessage", { medication: interactions.data?.medication ?? t("pharmacist.interactions.thisMedication") })}
            />
          ) : (
            <div className="stack">
              {interactions.data.interactions.map((i) => (
                <div key={i.id} className="card" style={{ padding: 14 }}>
                  <div className="row-between" style={{ marginBottom: 6 }}>
                    <strong style={{ color: "var(--ink)" }}>
                      {i.medication_1_name} + {i.medication_2_name}
                    </strong>
                    <Badge tone={severityTone(i.severity)}>{severityLabel(i.severity)}</Badge>
                  </div>
                  <p className="muted" style={{ margin: "0 0 6px", fontSize: "0.9rem" }}>
                    {titleCase(i.interaction_type)} · {i.description}
                  </p>
                  {i.recommendation && (
                    <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--ink-soft)" }}>
                      <strong>{t("pharmacist.interactions.recommendation")}</strong> {i.recommendation}
                    </p>
                  )}
                  {i.evidence_source && (
                    <p className="muted" style={{ margin: "6px 0 0", fontSize: "0.8rem" }}>
                      {t("pharmacist.interactions.source")} {i.evidence_source}
                    </p>
                  )}
                </div>
              ))}
              <div className="banner">
                {t("pharmacist.interactions.banner")}
              </div>
            </div>
          )}
        </Panel>
      </div>
    </>
  );
}
