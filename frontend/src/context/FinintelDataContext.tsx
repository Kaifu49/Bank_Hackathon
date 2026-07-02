import React, { createContext, useContext, useState, useEffect, useCallback } from "react";
import { Statement, CaseSummary } from "../types/api";
import { getStatements, getCaseSummary, deleteStatement, clearDatabase } from "../services/finintelApi";

interface FinintelDataContextProps {
  caseId: string;
  setCaseId: (id: string) => void;
  latestStatementId: string | null;
  setLatestStatementId: (id: string | null) => void;
  statements: Statement[];
  refreshStatements: () => Promise<void>;
  caseSummary: CaseSummary | null;
  refreshSummary: (id?: string) => Promise<void>;
  isLoadingSummary: boolean;
  summaryError: string | null;
  deleteUploadedStatement: (id: string) => Promise<void>;
  clearDatabaseSession: () => Promise<void>;
}

const FinintelDataContext = createContext<FinintelDataContextProps | undefined>(undefined);

export const FinintelDataProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [caseId, setCaseIdState] = useState<string>("all");
  const [latestStatementId, setLatestStatementId] = useState<string | null>(null);
  const [statements, setStatements] = useState<Statement[]>([]);
  const [caseSummary, setCaseSummary] = useState<CaseSummary | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState<boolean>(false);
  const [summaryError, setSummaryError] = useState<string | null>(null);

  const refreshStatements = useCallback(async () => {
    try {
      const data = await getStatements(1, 100);
      setStatements(data);
      // Determine if there is a completed statement we can treat as the latestStatementId
      const completed = data.filter((s) => s.status === "completed");
      if (completed.length > 0) {
        setLatestStatementId(completed[0].id);
      } else {
        setLatestStatementId(null);
      }
    } catch (err: any) {
      console.error("Failed to load statements list:", err);
    }
  }, []);

  const refreshSummary = useCallback(async (id?: string) => {
    const targetId = id || caseId;
    setIsLoadingSummary(true);
    setSummaryError(null);
    try {
      const summary = await getCaseSummary(targetId);
      setCaseSummary(summary);
    } catch (err: any) {
      console.error("Failed to fetch case summary:", err);
      setSummaryError(err.message || "Failed to load case summary.");
    } finally {
      setIsLoadingSummary(false);
    }
  }, [caseId]);

  const setCaseId = useCallback((id: string) => {
    setCaseIdState(id);
    refreshSummary(id);
  }, [refreshSummary]);

  const deleteUploadedStatement = useCallback(async (id: string) => {
    try {
      await deleteStatement(id);
      await refreshStatements();
      if (caseId === id) {
        setCaseIdState("all");
      } else {
        await refreshSummary();
      }
    } catch (err) {
      console.error("Failed to delete statement:", err);
      throw err;
    }
  }, [caseId, refreshStatements, refreshSummary]);

  const clearDatabaseSession = useCallback(async () => {
    try {
      await clearDatabase();
      setLatestStatementId(null);
      setCaseIdState("all");
      setStatements([]);
      setCaseSummary(null);
      await refreshStatements();
      await refreshSummary("all");
    } catch (err) {
      console.error("Failed to clear database session:", err);
      throw err;
    }
  }, [refreshStatements, refreshSummary]);

  // Initialize database session on app mount/page reload
  useEffect(() => {
    const startFreshSession = async () => {
      try {
        console.log("Session started: loading existing database records...");
      } catch (err) {
        console.error("Initialize database session failed:", err);
      } finally {
        await refreshStatements();
        await refreshSummary("all");
      }
    };
    startFreshSession();
  }, []);

  // Load summary whenever caseId changes
  useEffect(() => {
    refreshSummary(caseId);
  }, [caseId, refreshSummary]);

  return (
    <FinintelDataContext.Provider
      value={{
        caseId,
        setCaseId,
        latestStatementId,
        setLatestStatementId,
        statements,
        refreshStatements,
        caseSummary,
        refreshSummary,
        isLoadingSummary,
        summaryError,
        deleteUploadedStatement,
        clearDatabaseSession,
      }}
    >
      {children}
    </FinintelDataContext.Provider>
  );
};

export const useFinintelData = () => {
  const context = useContext(FinintelDataContext);
  if (!context) {
    throw new Error("useFinintelData must be used within a FinintelDataProvider");
  }
  return context;
};
