import type { ReactNode } from "react";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";

export type BadgeTone = "neutral" | "info" | "success" | "warn" | "danger";

// DRF list endpoints are paginated as { count, next, previous, results }.
// Normalize either a bare array or a paginated envelope into an array.
export function unwrapList<T>(data: unknown): T[] {
  if (Array.isArray(data)) return data as T[];
  if (data && typeof data === "object") {
    const results = (data as { results?: unknown }).results;
    if (Array.isArray(results)) return results as T[];
  }
  return [];
}

// Total record count for a list response (paginated or bare array).
export function countOf(data: unknown): number {
  if (Array.isArray(data)) return data.length;
  if (data && typeof data === "object") {
    const count = (data as { count?: unknown }).count;
    if (typeof count === "number") return count;
  }
  return unwrapList(data).length;
}

export function Badge({ tone = "neutral", children }: { tone?: BadgeTone; children: ReactNode }) {
  return <span className={`badge badge--${tone}`}>{children}</span>;
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: string;
  subtitle?: string;
  actions?: ReactNode;
}) {
  return (
    <div className="row-between" style={{ marginBottom: 20 }}>
      <div>
        <h1 style={{ margin: 0, fontSize: "1.5rem", letterSpacing: "-0.01em", color: "var(--ink)" }}>
          {title}
        </h1>
        {subtitle && (
          <p className="muted" style={{ margin: "4px 0 0", fontSize: "0.92rem" }}>
            {subtitle}
          </p>
        )}
      </div>
      {actions && <div className="form-actions">{actions}</div>}
    </div>
  );
}

export function Panel({
  title,
  subtitle,
  actions,
  children,
  bodyless,
}: {
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  children: ReactNode;
  bodyless?: boolean;
}) {
  return (
    <section className="panel">
      {(title || actions) && (
        <div className="panel-head">
          <div>
            {title && <h2 className="panel-title">{title}</h2>}
            {subtitle && <p className="panel-sub">{subtitle}</p>}
          </div>
          {actions}
        </div>
      )}
      <div className={bodyless ? "" : "panel-body"}>{children}</div>
    </section>
  );
}

export function StatCard({
  label,
  value,
  tone,
}: {
  label: string;
  value: ReactNode;
  tone?: "accent" | "danger";
}) {
  const cls = tone ? `stat-card stat-card--${tone}` : "stat-card";
  return (
    <div className={cls}>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export function Loading() {
  const { t } = useTranslation();
  return (
    <div className="loading-wrap" role="status" aria-label={t("common.loading")}>
      <div className="spinner" />
    </div>
  );
}

export function EmptyState({ title, message }: { title: string; message?: string }) {
  return (
    <div className="state-box">
      <h3>{title}</h3>
      {message && <p>{message}</p>}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  const { t } = useTranslation();
  return (
    <div className="state-box">
      <h3>{t("common.errorTitle")}</h3>
      <p>{message}</p>
      {onRetry && (
        <div className="form-actions" style={{ justifyContent: "center", marginTop: 12 }}>
          <button type="button" className="btn btn-outline btn-sm" onClick={onRetry}>
            {t("common.retry")}
          </button>
        </div>
      )}
    </div>
  );
}

export function Field({
  label,
  hint,
  htmlFor,
  children,
  span2,
}: {
  label: string;
  hint?: string;
  htmlFor?: string;
  children: ReactNode;
  span2?: boolean;
}) {
  return (
    <div className={span2 ? "field span-2" : "field"}>
      <label htmlFor={htmlFor}>{label}</label>
      {children}
      {hint && <span className="hint">{hint}</span>}
    </div>
  );
}

export function consultationStatusTone(status: string): BadgeTone {
  switch (status) {
    case "COMPLETED":
      return "success";
    case "CANCELLED":
      return "danger";
    default:
      return "info";
  }
}

export function prescriptionStatusTone(status: string): BadgeTone {
  switch (status) {
    case "ACTIVE":
      return "info";
    case "COMPLETED":
      return "success";
    case "DISCONTINUED":
      return "danger";
    default:
      return "neutral";
  }
}

export function urgencyTone(level: string): BadgeTone {
  switch (level) {
    case "URGENT_MEDICAL_ATTENTION":
      return "danger";
    case "PROMPT_MEDICAL_REVIEW":
      return "warn";
    case "ROUTINE_CONSULTATION":
      return "info";
    default:
      return "neutral";
  }
}

export function severityTone(severity: string): BadgeTone {
  switch ((severity || "").toLowerCase()) {
    case "severe":
    case "contraindicated":
      return "danger";
    case "moderate":
      return "warn";
    case "mild":
      return "info";
    default:
      return "neutral";
  }
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function titleCase(value?: string | null): string {
  if (!value) return "—";
  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

// Localized labels for enumerated backend values. Fall back to a readable
// title-cased form when a value is not present in the catalog.
export function consultationStatusLabel(status: string): string {
  return i18n.t(`status.consultation.${status}`, { defaultValue: titleCase(status) });
}

export function prescriptionStatusLabel(status: string): string {
  return i18n.t(`status.prescription.${status}`, { defaultValue: titleCase(status) });
}

export function urgencyLabel(level: string): string {
  return i18n.t(`status.urgency.${level}`, { defaultValue: titleCase(level) });
}

export function severityLabel(severity: string): string {
  const key = (severity || "").toLowerCase();
  return i18n.t(`status.severity.${key}`, { defaultValue: titleCase(severity) });
}

export function roleLabel(role: string): string {
  return i18n.t(`status.role.${role}`, { defaultValue: titleCase(role) });
}

export function approvalLabel(status: string): string {
  const key = (status || "").toLowerCase();
  return i18n.t(`status.approval.${key}`, { defaultValue: titleCase(status) });
}

export function reviewLabel(status: string): string {
  return i18n.t(`status.review.${status}`, { defaultValue: titleCase(status) });
}

export function actionLabel(action: string): string {
  const key = (action || "").toLowerCase();
  return i18n.t(`status.action.${key}`, { defaultValue: titleCase(action) });
}
