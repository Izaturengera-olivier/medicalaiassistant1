import { useCallback, useEffect, useRef, useState } from "react";

interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useAsync<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [state, setState] = useState<AsyncState<T>>({ data: null, loading: true, error: null });
  const fnRef = useRef(fn);
  fnRef.current = fn;

  const run = useCallback(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fnRef
      .current()
      .then((data) => {
        if (!cancelled) setState({ data, loading: false, error: null });
      })
      .catch((err) => {
        if (!cancelled) {
          const message =
            err?.response?.data?.detail ||
            err?.response?.data?.error ||
            err?.message ||
            "Request failed";
          setState({ data: null, loading: false, error: String(message) });
        }
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => run(), [run]);

  return { ...state, reload: run };
}

export function errorMessage(err: unknown): string {
  const e = err as { response?: { data?: unknown }; message?: string };
  const data = e?.response?.data;

  if (data && typeof data === "object") {
    const fields = data as Record<string, unknown>;
    // The backend is inconsistent about the envelope key: DRF auth failures use
    // "detail", the AI views use "error", and accounts uses "message".
    for (const key of ["detail", "error", "message"]) {
      const value = fields[key];
      if (typeof value === "string" && value) return value;
    }
    // Serializer errors map each field to a list of messages.
    for (const value of Object.values(fields)) {
      const first = Array.isArray(value) ? value[0] : value;
      if (typeof first === "string" && first) return first;
    }
  }

  return e?.message || "Request failed";
}
