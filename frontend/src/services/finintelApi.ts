import { apiRequest } from "./api";
import {
  UploadResponse,
  JobStatus,
  Statement,
  BackendTransaction,
  ValidationReport,
  RoundTripsResponse,
  RoundTripExplanation,
  MoneyFlowResponse,
  MoneyTrailResponse,
  CaseSummary,
} from "../types/api";

export async function uploadStatement(file: File, bankName?: string): Promise<UploadResponse> {
  const formData = new FormData();
  const baseName = file.name.split('/').pop()?.split('\\').pop() || file.name;
  formData.append("file", file, baseName);
  if (bankName) {
    formData.append("bank_name", bankName);
  }

  return apiRequest<UploadResponse>("/api/v1/statements/upload", {
    method: "POST",
    body: formData,
  });
}

export async function getJobStatus(jobId: string): Promise<JobStatus> {
  return apiRequest<JobStatus>(`/api/v1/jobs/${jobId}/status`);
}

export async function getStatements(page = 1, pageSize = 50): Promise<Statement[]> {
  return apiRequest<Statement[]>(`/api/v1/statements?page=${page}&page_size=${pageSize}`);
}

export async function getStatementTransactions(
  statementId: string,
  page = 1,
  pageSize = 50
): Promise<BackendTransaction[]> {
  return apiRequest<BackendTransaction[]>(
    `/api/v1/statements/${statementId}/transactions?page=${page}&page_size=${pageSize}`
  );
}

export async function getStatementValidationReport(statementId: string): Promise<ValidationReport> {
  return apiRequest<ValidationReport>(`/api/v1/statements/${statementId}/validation-report`);
}

export async function getRoundTrips(caseId: string): Promise<RoundTripsResponse> {
  return apiRequest<RoundTripsResponse>(`/api/v1/investigations/${caseId}/round-trips`);
}

export async function getRoundTripExplanation(
  caseId: string,
  chainId: string | number
): Promise<RoundTripExplanation> {
  return apiRequest<RoundTripExplanation>(
    `/api/v1/investigations/${caseId}/round-trips/${chainId}/explanation`
  );
}

export async function getMoneyFlow(caseId: string): Promise<MoneyFlowResponse> {
  return apiRequest<MoneyFlowResponse>(`/api/v1/investigations/${caseId}/money-flow`);
}

export async function getMoneyTrail(caseId: string, transactionId: string): Promise<MoneyTrailResponse> {
  return apiRequest<MoneyTrailResponse>(
    `/api/v1/investigations/${caseId}/money-trail/${transactionId}`
  );
}

export async function getCaseSummary(caseId: string): Promise<CaseSummary> {
  return apiRequest<CaseSummary>(`/api/v1/cases/${caseId}/summary`);
}

export async function getReportJson(caseId: string): Promise<any> {
  return apiRequest<any>(`/api/v1/reports/${caseId}/json`);
}

export async function getHealth(): Promise<any> {
  return apiRequest<any>("/health");
}

export async function getServicesHealth(): Promise<any> {
  return apiRequest<any>("/services/health");
}

export async function deleteStatement(statementId: string): Promise<any> {
  return apiRequest<any>(`/api/v1/statements/${statementId}`, {
    method: "DELETE",
  });
}

export async function clearDatabase(): Promise<any> {
  return apiRequest<any>("/api/v1/database/clear", {
    method: "POST",
  });
}

export async function getTopSuspicious(caseId: string, limit = 20): Promise<any> {
  // Backend route is `top-suspicious-accounts` (not `top-suspicious`).
  return apiRequest<any>(`/api/v1/investigations/${caseId}/top-suspicious-accounts?limit=${limit}`);
}

export async function getTopRisks(caseId: string, limit = 20): Promise<any> {
  return apiRequest<any>(`/api/v1/investigations/${caseId}/top-risks?limit=${limit}`);
}

// ---- Entity intelligence -------------------------------------------------

export async function getEntities(type?: string, page = 1, pageSize = 50): Promise<any[]> {
  const typeParam = type && type !== "ALL" ? `&type=${encodeURIComponent(type)}` : "";
  return apiRequest<any[]>(`/api/v1/entities?page=${page}&page_size=${pageSize}${typeParam}`);
}

export async function getEntity(id: string): Promise<any> {
  return apiRequest<any>(`/api/v1/entities/${id}`);
}

export async function getEntityRiskProfile(id: string): Promise<any> {
  return apiRequest<any>(`/api/v1/entities/${id}/risk-profile`);
}

export async function getEntityExplanation(id: string): Promise<any> {
  return apiRequest<any>(`/api/v1/entities/${id}/explanation`);
}

// ---- Additional investigation views -------------------------------------

export async function getTimeline(caseId: string, account: string): Promise<any> {
  return apiRequest<any>(
    `/api/v1/investigations/${caseId}/timeline?account=${encodeURIComponent(account)}`
  );
}

export async function getCounterparties(caseId: string, account: string): Promise<any> {
  return apiRequest<any>(
    `/api/v1/investigations/${caseId}/counterparties?account=${encodeURIComponent(account)}`
  );
}

export async function getClusters(caseId: string): Promise<any> {
  return apiRequest<any>(`/api/v1/investigations/${caseId}/graph/clusters`);
}
