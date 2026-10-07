import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useAsync, errorMessage } from "../../hooks/useAsync";
import { usersAPI } from "../../services/api";
import { Badge, ErrorState, Field, Loading, PageHeader, Panel, formatDate, roleLabel, unwrapList } from "../../components/ui";

interface UserRow {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
}

const ROLES = ["PATIENT", "DOCTOR", "PHARMACIST", "ADMIN"];

export function UsersPage() {
  const { t } = useTranslation();
  const [role, setRole] = useState("");
  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUser, setNewUser] = useState({
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role: "PATIENT",
    is_verified: true,
    is_active: true,
  });

  const { data, loading, error, reload } = useAsync<UserRow[]>(
    () =>
      usersAPI
        .list({ role: role || undefined, search: appliedSearch || undefined })
        .then((r) => unwrapList<UserRow>(r.data)),
    [role, appliedSearch]
  );

  const [busyId, setBusyId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);

  const patch = async (user: UserRow, changes: Partial<UserRow>) => {
    setBusyId(user.id);
    setActionError(null);
    try {
      await usersAPI.update(user.id, changes);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (user: UserRow) => {
    if (!window.confirm(`Are you sure you want to delete user ${user.email}? This action cannot be undone.`)) {
      return;
    }
    setBusyId(user.id);
    setActionError(null);
    try {
      await usersAPI.delete(user.id);
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    } finally {
      setBusyId(null);
    }
  };

  const handleCreateUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setActionError(null);
    try {
      await usersAPI.create(newUser);
      setShowAddModal(false);
      setNewUser({
        first_name: "",
        last_name: "",
        email: "",
        password: "",
        role: "PATIENT",
        is_verified: true,
        is_active: true,
      });
      reload();
    } catch (err) {
      setActionError(errorMessage(err));
    }
  };

  return (
    <>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <PageHeader title={t("admin.users.title")} subtitle={t("admin.users.subtitle")} />
        <button type="button" className="btn btn-primary" onClick={() => setShowAddModal(true)}>
          + Add New User
        </button>
      </div>

      {actionError && <div className="error-box" style={{ marginBottom: 16 }}>{actionError}</div>}

      <Panel title={t("admin.users.filters")} bodyless>
        <div className="panel-body form-grid">
          <Field label={t("admin.users.role")} htmlFor="rolefilter">
            <select id="rolefilter" className="select" value={role} onChange={(e) => setRole(e.target.value)}>
              <option value="">{t("admin.users.allRoles")}</option>
              {ROLES.map((r) => (
                <option key={r} value={r}>{roleLabel(r)}</option>
              ))}
            </select>
          </Field>
          <Field label={t("admin.users.search")} htmlFor="usersearch">
            <input
              id="usersearch"
              className="input"
              placeholder={t("admin.users.searchPlaceholder")}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") setAppliedSearch(search);
              }}
            />
          </Field>
          <div className="field" style={{ justifyContent: "flex-end" }}>
            <button type="button" className="btn btn-outline" onClick={() => setAppliedSearch(search)}>
              {t("common.applySearch")}
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
          <div className="state-box">{t("admin.users.empty")}</div>
        ) : (
          <div className="table-wrap">
            <table className="table">
              <thead>
                <tr>
                  <th>{t("admin.users.name")}</th>
                  <th>{t("admin.users.email")}</th>
                  <th>{t("admin.users.role")}</th>
                  <th>Verification</th>
                  <th>Status</th>
                  <th>{t("admin.users.joined")}</th>
                  <th>{t("admin.users.actions")}</th>
                </tr>
              </thead>
              <tbody>
                {data.map((u) => (
                  <tr key={u.id}>
                    <td className="cell-strong">{u.first_name} {u.last_name}</td>
                    <td>{u.email}</td>
                    <td>
                      <select
                        className="select"
                        style={{ minWidth: 120, padding: "6px 8px", fontSize: "0.85rem" }}
                        value={u.role}
                        disabled={busyId === u.id}
                        onChange={(e) => void patch(u, { role: e.target.value })}
                      >
                        {ROLES.map((r) => (
                          <option key={r} value={r}>{roleLabel(r)}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm"
                        style={{
                          background: u.is_verified ? "#e6f6ec" : "#fff3cd",
                          color: u.is_verified ? "#1c7c3c" : "#856404",
                          border: "1px solid transparent",
                        }}
                        disabled={busyId === u.id}
                        onClick={() => void patch(u, { is_verified: !u.is_verified })}
                      >
                        {u.is_verified ? t("common.verified") : t("common.unverified")}
                      </button>
                    </td>
                    <td>
                      <button
                        type="button"
                        className="btn btn-sm"
                        style={{
                          background: u.is_active !== false ? "#e6f6ec" : "#f8d7da",
                          color: u.is_active !== false ? "#1c7c3c" : "#721c24",
                          border: "1px solid transparent",
                        }}
                        disabled={busyId === u.id}
                        onClick={() => void patch(u, { is_active: u.is_active === false ? true : false })}
                      >
                        {u.is_active !== false ? "Active" : "Disabled"}
                      </button>
                    </td>
                    <td>{formatDate(u.created_at)}</td>
                    <td style={{ display: "flex", gap: 8, alignItems: "center" }}>
                      {busyId === u.id ? <Badge>{t("admin.users.saving")}</Badge> : null}
                      <button
                        type="button"
                        className="btn btn-sm btn-outline"
                        style={{ color: "#d9534f", borderColor: "#d9534f" }}
                        disabled={busyId === u.id}
                        onClick={() => void handleDelete(u)}
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

      {/* Add User Modal */}
      {showAddModal && (
        <div style={{
          position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", zIndex: 1000,
          display: "flex", justifyContent: "center", alignItems: "center"
        }}>
          <div style={{ background: "#fff", padding: 24, borderRadius: 8, width: 450, maxWidth: "90%" }}>
            <h3 style={{ marginTop: 0 }}>Add New System User</h3>
            <form onSubmit={handleCreateUser} className="stack">
              <div className="form-grid">
                <Field label="First Name">
                  <input className="input" required value={newUser.first_name} onChange={(e) => setNewUser({...newUser, first_name: e.target.value})} />
                </Field>
                <Field label="Last Name">
                  <input className="input" required value={newUser.last_name} onChange={(e) => setNewUser({...newUser, last_name: e.target.value})} />
                </Field>
              </div>
              <Field label="Email Address">
                <input type="email" className="input" required value={newUser.email} onChange={(e) => setNewUser({...newUser, email: e.target.value})} />
              </Field>
              <Field label="Initial Password">
                <input type="password" className="input" required minLength={6} value={newUser.password} onChange={(e) => setNewUser({...newUser, password: e.target.value})} />
              </Field>
              <Field label="Role">
                <select className="select" value={newUser.role} onChange={(e) => setNewUser({...newUser, role: e.target.value})}>
                  {ROLES.map((r) => <option key={r} value={r}>{roleLabel(r)}</option>)}
                </select>
              </Field>
              <div style={{ display: "flex", gap: 16, marginTop: 12 }}>
                <button type="submit" className="btn btn-primary" style={{ flex: 1 }}>Create User</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowAddModal(false)}>Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
