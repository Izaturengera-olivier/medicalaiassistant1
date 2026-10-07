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
  const e = err as { response?: { data?: { detail?: string; error?: string } }; message?: string };
  return (
    e?.response?.data?.detail ||
    e?.response?.data?.error ||
    e?.message ||
    "Request failed"
  );
}
