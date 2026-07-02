import { getApiBaseUrl } from "./api";

export function getDownloadUrl(caseId: string, format: "pdf" | "excel" | "docx"): string {
  const baseUrl = getApiBaseUrl();
  return `${baseUrl}/api/v1/reports/${caseId}/${format}`;
}

export function downloadReport(caseId: string, format: "pdf" | "excel" | "docx", filename?: string) {
  const url = getDownloadUrl(caseId, format);
  const a = document.createElement("a");
  a.href = url;
  // The server returns Content-Disposition: attachment, but having download attribute is a good client-side fallback.
  const ext = format === "excel" ? "xlsx" : format;
  a.download = filename || `Forensic_Report_${caseId}.${ext}`;
  a.target = "_blank";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
