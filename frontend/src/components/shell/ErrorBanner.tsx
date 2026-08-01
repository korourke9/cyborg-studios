"use client";

import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
} from "react";

type ErrorBannerContextValue = {
  reportError: (message: string) => void;
  clearError: () => void;
};

const ErrorBannerContext = createContext<ErrorBannerContextValue | null>(null);

export function useErrorBanner(): ErrorBannerContextValue {
  const value = useContext(ErrorBannerContext);
  if (!value) {
    throw new Error("useErrorBanner must be used within ErrorBannerProvider");
  }
  return value;
}

export function ErrorBannerProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [message, setMessage] = useState<string | null>(null);

  const reportError = useCallback((next: string) => {
    setMessage(next.trim() || "Something went wrong.");
  }, []);

  const clearError = useCallback(() => {
    setMessage(null);
  }, []);

  const value = useMemo(
    () => ({ reportError, clearError }),
    [reportError, clearError],
  );

  return (
    <ErrorBannerContext.Provider value={value}>
      {message ? (
        <div
          role="alert"
          className="flex items-start justify-between gap-3 border-b-4 border-coral bg-ink-panel px-4 py-3 text-sm text-foam"
        >
          <p className="leading-relaxed">{message}</p>
          <button
            type="button"
            onClick={clearError}
            className="shrink-0 font-[family-name:var(--font-pixel)] text-[8px] text-muted hover:text-foam"
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      ) : null}
      {children}
    </ErrorBannerContext.Provider>
  );
}
