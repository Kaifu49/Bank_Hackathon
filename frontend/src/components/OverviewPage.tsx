import React, { useState, useEffect, useRef } from 'react';
import { 
  UploadCloud, 
  FileText, 
  CheckCircle2, 
  Play, 
  Loader2, 
  ArrowRight,
  GitFork,
  Activity,
  RefreshCw,
  FileCheck,
  Cpu,
  Eraser,
  FileSpreadsheet,
  FileDown,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { useFinintelData } from '../context/FinintelDataContext';
import { uploadStatement, getJobStatus, getStatementValidationReport, getStatementTransactions } from '../services/finintelApi';
import { ValidationReport, BackendTransaction } from '../types/api';

type NodeStatus = 'queued' | 'running' | 'complete' | 'failed';

const nodeCoords: Record<string, { x: number; y: number }> = {
  upload: { x: 20, y: 190 },
  ocr: { x: 240, y: 190 },
  cleaning: { x: 460, y: 190 },
  standardization: { x: 680, y: 190 },
  validation: { x: 900, y: 190 },
  database: { x: 1120, y: 190 },
  loops: { x: 1340, y: 50 },
  flow: { x: 1340, y: 190 },
  trails: { x: 1340, y: 330 },
  report: { x: 1560, y: 190 },
  exportPdf: { x: 1780, y: 100 },
  exportExcel: { x: 1780, y: 280 },
};

const getBezierPath = (startX: number, startY: number, endX: number, endY: number) => {
  const horizontalOffset = Math.max(40, Math.abs(endX - startX) * 0.5);
  return `M ${startX} ${startY} C ${startX + horizontalOffset} ${startY}, ${endX - horizontalOffset} ${endY}, ${endX} ${endY}`;
};

interface OverviewPageProps {
  onNavigateToView: (view: string) => void;
}

const ALLOWED_EXT = ["pdf", "csv", "xlsx", "xls", "docx", "txt", "png", "jpg", "jpeg"];

export default function OverviewPage({ onNavigateToView }: OverviewPageProps) {
  const { 
    latestStatementId, 
    setLatestStatementId, 
    statements,
    refreshStatements, 
    caseSummary, 
    refreshSummary,
    setCaseId,
    deleteUploadedStatement,
    clearDatabaseSession
  } = useFinintelData();

  const [dragActive, setDragActive] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState<'idle' | 'processing' | 'completed'>('idle');
  const [activeLogMsg, setActiveLogMsg] = useState<string>('Ready to initiate diagnostics pipeline.');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Pending files list
  const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  
  // Tracking current job running
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [currentStatementId, setCurrentStatementId] = useState<string | null>(null);
  const pollingTimerRef = useRef<NodeJS.Timeout | null>(null);

  // Validation report and transactions states
  const [validationReport, setValidationReport] = useState<ValidationReport | null>(null);
  const [transactions, setTransactions] = useState<BackendTransaction[]>([]);
  const [isLoadingReport, setIsLoadingReport] = useState(false);

  // Node individual execution states
  const [nodeStates, setNodeStates] = useState<Record<string, NodeStatus>>({
    upload: 'complete',
    ocr: 'queued',
    cleaning: 'queued',
    standardization: 'queued',
    validation: 'queued',
    database: 'queued',
    loops: 'queued',
    flow: 'queued',
    trails: 'queued',
    report: 'queued',
    exportPdf: 'queued',
    exportExcel: 'queued',
  });

  const [ocrProgress, setOcrProgress] = useState<number>(0);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Map backend status and stage to visual nodes
  const updateNodeStates = (status: string, stage: string | null, progress: number) => {
    const states: Record<string, NodeStatus> = {
      upload: 'complete',
      ocr: 'queued',
      cleaning: 'queued',
      standardization: 'queued',
      validation: 'queued',
      database: 'queued',
      loops: 'queued',
      flow: 'queued',
      trails: 'queued',
      report: 'queued',
      exportPdf: 'queued',
      exportExcel: 'queued',
    };

    if (status === 'queued') {
      states.ocr = 'running';
    } else if (status === 'processing') {
      states.upload = 'complete';
      
      const getStageOrder = (s: string | null): number => {
        if (!s) return 0;
        const order: Record<string, number> = {
          'ocr': 1,
          'standardize': 2,
          'validate': 3,
          'entities': 4,
          'graph': 5
        };
        return order[s] || 0;
      };

      const order = getStageOrder(stage);

      // OCR Node
      if (order === 1) {
        states.ocr = 'running';
      } else if (order > 1) {
        states.ocr = 'complete';
      }

      // Cleaning & Standardization
      if (order === 2) {
        states.cleaning = 'running';
        states.standardization = 'running';
      } else if (order > 2) {
        states.cleaning = 'complete';
        states.standardization = 'complete';
      }

      // Validation
      if (order === 3) {
        states.validation = 'running';
      } else if (order > 3) {
        states.validation = 'complete';
      }

      // DB Store (entities)
      if (order === 4) {
        states.database = 'running';
      } else if (order > 4) {
        states.database = 'complete';
      }

      // Downstream analysis (graph)
      if (order === 5) {
        states.loops = 'running';
        states.flow = 'running';
        states.trails = 'running';
      }
    } else if (status === 'completed') {
      Object.keys(states).forEach(k => {
        states[k] = 'complete';
      });
    } else if (status === 'failed') {
      // Mark active node as failed
      states.upload = 'complete';
      if (stage === 'ocr') states.ocr = 'failed';
      else if (stage === 'standardize') {
        states.ocr = 'complete';
        states.cleaning = 'failed';
        states.standardization = 'failed';
      } else if (stage === 'validate') {
        states.ocr = 'complete';
        states.cleaning = 'complete';
        states.standardization = 'complete';
        states.validation = 'failed';
      } else if (stage === 'entities') {
        states.ocr = 'complete';
        states.cleaning = 'complete';
        states.standardization = 'complete';
        states.validation = 'complete';
        states.database = 'failed';
      } else if (stage === 'graph') {
        states.ocr = 'complete';
        states.cleaning = 'complete';
        states.standardization = 'complete';
        states.validation = 'complete';
        states.database = 'complete';
        states.loops = 'failed';
        states.flow = 'failed';
        states.trails = 'failed';
      } else {
        states.ocr = 'failed';
      }
    }
    return states;
  };

  // Fetch report findings when validation or completed stages are reached
  const fetchReportData = async (stmtId: string) => {
    setIsLoadingReport(true);
    try {
      const [report, txs] = await Promise.all([
        getStatementValidationReport(stmtId).catch(() => null),
        getStatementTransactions(stmtId, 1, 100).catch(() => [])
      ]);
      if (report) setValidationReport(report);
      if (txs) setTransactions(txs);
    } catch (err) {
      console.error("Failed to load pipeline results", err);
    } finally {
      setIsLoadingReport(false);
    }
  };

  // Start polling backend job status
  const startJobPolling = (jobId: string, stmtId: string) => {
    if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);

    pollingTimerRef.current = setInterval(async () => {
      try {
        const jobStatus = await getJobStatus(jobId);
        setOcrProgress(jobStatus.progress);
        
        const nextStates = updateNodeStates(jobStatus.status, jobStatus.stage, jobStatus.progress);
        setNodeStates(nextStates);

        if (jobStatus.error) {
          setErrorMsg(jobStatus.error);
          setActiveLogMsg(`Job failed: ${jobStatus.error}`);
          setPipelineStatus('idle');
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          return;
        }

        if (jobStatus.status === 'completed') {
          setPipelineStatus('completed');
          setActiveLogMsg("Forensics core diagnostic sequence terminated. Outputs verified.");
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
          
          // Refresh lists, summaries and reports
          await refreshStatements();
          setLatestStatementId(stmtId);
          await refreshSummary(stmtId);
          await fetchReportData(stmtId);
        } else if (jobStatus.status === 'failed') {
          setErrorMsg(jobStatus.error || "Job failed.");
          setActiveLogMsg("Forensics sequence aborted due to gateway processing failure.");
          setPipelineStatus('idle');
          if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
        } else {
          let stageLabel = 'Initializing';
          if (jobStatus.stage === 'ocr') stageLabel = 'Optical Character Recognition';
          else if (jobStatus.stage === 'standardize') stageLabel = 'Standardization & Purging';
          else if (jobStatus.stage === 'validate') stageLabel = 'Validating compliance checks';
          else if (jobStatus.stage === 'entities') stageLabel = 'Building SQL Database Store';
          else if (jobStatus.stage === 'graph') stageLabel = 'Structuring circular flows';
          
          setActiveLogMsg(`Active Node: ${stageLabel} running (${jobStatus.progress}%)...`);

          // Fetch intermediate reports if validation is reached
          if (jobStatus.stage === 'validate' || jobStatus.stage === 'entities' || jobStatus.stage === 'graph') {
            getStatementValidationReport(stmtId).then(setValidationReport).catch(() => {});
          }
          if (jobStatus.stage === 'entities' || jobStatus.stage === 'graph') {
            getStatementTransactions(stmtId, 1, 100).then(setTransactions).catch(() => {});
          }
        }
      } catch (err: any) {
        console.error("Job status polling error:", err);
      }
    }, 1500);
  };

  // Clean up polling timer on unmount
  useEffect(() => {
    return () => {
      if (pollingTimerRef.current) clearInterval(pollingTimerRef.current);
    };
  }, []);

  // Fetch initial report data if there is an existing statement_id on mount
  useEffect(() => {
    if (latestStatementId) {
      setPipelineStatus('completed');
      fetchReportData(latestStatementId);
      refreshSummary(latestStatementId);
      
      setNodeStates({
        upload: 'complete',
        ocr: 'complete',
        cleaning: 'complete',
        standardization: 'complete',
        validation: 'complete',
        database: 'complete',
        loops: 'complete',
        flow: 'complete',
        trails: 'complete',
        report: 'complete',
        exportPdf: 'complete',
        exportExcel: 'complete',
      });
    }
  }, [latestStatementId]);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  // Traverses directory drops recursively
  const handleDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.items) {
      const files: File[] = [];
      const promises: Promise<void>[] = [];

      const traverseFileTree = (item: any, path = "") => {
        if (item.isFile) {
          promises.push(
            new Promise<void>((resolve) => {
              item.file((file: File) => {
                files.push(file);
                resolve();
              });
            })
          );
        } else if (item.isDirectory) {
          const dirReader = item.createReader();
          promises.push(
            new Promise<void>((resolve) => {
              const readAllEntries = () => {
                dirReader.readEntries((entries: any[]) => {
                  if (entries.length > 0) {
                    entries.forEach(entry => traverseFileTree(entry, path + item.name + "/"));
                    readAllEntries();
                  } else {
                    resolve();
                  }
                });
              };
              readAllEntries();
            })
          );
        }
      };

      for (let i = 0; i < e.dataTransfer.items.length; i++) {
        const item = e.dataTransfer.items[i].webkitGetAsEntry();
        if (item) {
          traverseFileTree(item);
        }
      }

      await Promise.all(promises);
      if (files.length > 0) {
        addFiles(files);
      }
    } else if (e.dataTransfer.files) {
      addFiles(e.dataTransfer.files);
    }
  };

  const triggerSearchFile = (e: React.MouseEvent) => {
    e.stopPropagation();
    const fileSelector = document.createElement('input');
    fileSelector.type = 'file';
    fileSelector.multiple = true;
    fileSelector.accept = '.pdf,.csv,.xlsx,.xls,.docx,.txt,image/*';
    fileSelector.onchange = (evt: any) => {
      if (evt.target.files && evt.target.files.length > 0) {
        addFiles(evt.target.files);
      }
    };
    fileSelector.click();
  };

  const triggerSearchFolder = (e: React.MouseEvent) => {
    e.stopPropagation();
    const fileSelector = document.createElement('input');
    fileSelector.type = 'file';
    fileSelector.webkitdirectory = true;
    // @ts-ignore
    fileSelector.directory = true;
    fileSelector.multiple = true;
    fileSelector.onchange = (evt: any) => {
      if (evt.target.files && evt.target.files.length > 0) {
        addFiles(evt.target.files);
      }
    };
    fileSelector.click();
  };

  const addFiles = (files: FileList | File[]) => {
    const arr = Array.from(files).filter(file => {
      const ext = file.name.split('.').pop()?.toLowerCase() || '';
      return ALLOWED_EXT.includes(ext);
    });
    setPendingFiles(prev => [...prev, ...arr]);
    if (pipelineStatus === 'completed') {
      setPipelineStatus('idle');
      resetNodeStatesToInitial();
    }
  };

  // Upload and execute the pipeline sequentially for all selected files
  const executePipelineForPendingFiles = async () => {
    if (pendingFiles.length === 0) return;
    
    setPipelineStatus('processing');
    setErrorMsg(null);
    resetNodeStatesToInitial();
    setActiveLogMsg("Starting batch uploads to gateway...");

    try {
      let lastJobId = '';
      let lastStmtId = '';
      
      for (let i = 0; i < pendingFiles.length; i++) {
        const file = pendingFiles[i];
        setActiveLogMsg(`Uploading [${i + 1}/${pendingFiles.length}]: ${file.name}...`);
        const response = await uploadStatement(file);
        lastJobId = response.job_id;
        lastStmtId = response.statement_id;
      }
      
      setCurrentJobId(lastJobId);
      setCurrentStatementId(lastStmtId);
      setLatestStatementId(lastStmtId);
      setCaseId(lastStmtId);
      
      // Clear pending list now that uploads are in process
      setPendingFiles([]);
      
      setActiveLogMsg(`Uploaded. Enqueueing forensics worker (Job ID: ${lastJobId})...`);
      startJobPolling(lastJobId, lastStmtId);
    } catch (err: any) {
      console.error("Upload pipeline execution failed:", err);
      setPipelineStatus('idle');
      setErrorMsg(err.message || "Failed to process files. Verify gateway connection.");
      setActiveLogMsg("Forensics sequence aborted due to upload error.");
    }
  };

  const resetNodeStatesToInitial = () => {
    setNodeStates({
      upload: 'complete',
      ocr: 'queued',
      cleaning: 'queued',
      standardization: 'queued',
      validation: 'queued',
      database: 'queued',
      loops: 'queued',
      flow: 'queued',
      trails: 'queued',
      report: 'queued',
      exportPdf: 'queued',
      exportExcel: 'queued',
    });
    setOcrProgress(0);
    setValidationReport(null);
    setTransactions([]);
  };

  // Format bytes helper
  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-12 animate-fade-in select-none">
      
      {/* Dynamic flow styling */}
      <style>{`
        @keyframes flowingPath {
          from { stroke-dashoffset: 24; }
          to { stroke-dashoffset: 0; }
        }
        @keyframes pulseAmberNode {
          0%, 100% { box-shadow: 0 0 0 0px rgba(245, 158, 11, 0.4); border-color: rgba(245, 158, 11, 1); }
          50% { box-shadow: 0 0 14px 4px rgba(245, 158, 11, 0.35); border-color: rgba(245, 158, 11, 0.6); }
        }
        .flow-line {
          stroke-dasharray: 6, 8;
          animation: flowingPath 1.2s linear infinite;
        }
        .flow-line-fast {
          stroke-dasharray: 5, 5;
          animation: flowingPath 0.8s linear infinite;
        }
        .node-running-glow {
          animation: pulseAmberNode 1.6s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }
      `}</style>

      {/* Header Block Centered in Middle */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold tracking-tight text-[#18181B] font-display">
          Forensic Processing Engine
        </h1>
        <p className="text-sm text-[#71717A] max-w-lg mx-auto leading-relaxed font-sans font-light">
          The intake control and analysis workshop. Upload multi-jurisdictional ledger records to trigger physical parsing, data cleaning, loop tracking and audit brief exports.
        </p>
      </div>

      {/* SECTION 1: CENTERED EVIDENCE UPLOAD AREA & PORTFOLIO */}
      <div className="space-y-6 max-w-3xl mx-auto">
        
        {/* Evidence Intake Portal */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xs font-bold text-[#52525B] uppercase tracking-wider">
              Evidence Intake Portal
            </h2>
            <span className="text-[10px] text-[#A1A1AA] font-medium bg-[#F4F4F5] border border-[#E4E4E7] px-2 py-0.5 rounded-md font-sans">
              PDF, CSV, XLSX, DOCX, Images
            </span>
          </div>

          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            onClick={(e) => triggerSearchFile(e)}
            className={`border border-dashed rounded-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 ${
              dragActive 
                ? 'border-[#2563EB] bg-[#EFF6FF] ring-2 ring-[#EFF6FF]' 
                : 'border-[#E4E4E7] bg-white hover:border-[#18181B] shadow-[0_2px_8px_rgba(0,0,0,0.015)]'
            }`}
          >
            <div className="w-12 h-12 rounded-full bg-[#FAF9F6] flex items-center justify-center text-[#71717A] mb-4 border border-[#F4F4F5]">
              <UploadCloud className="w-6 h-6 text-[#18181B]" />
            </div>
            <div className="space-y-2">
              <p className="text-sm font-semibold text-[#18181B]">
                Drag & drop files or folders, or{' '}
                <span onClick={(e) => triggerSearchFile(e)} className="text-[#2563EB] underline font-bold cursor-pointer hover:text-blue-700">browse files</span>
                {' '}or{' '}
                <span onClick={(e) => triggerSearchFolder(e)} className="text-[#2563EB] underline font-bold cursor-pointer hover:text-blue-700">browse folder</span>
              </p>
              <p className="text-[11px] text-[#71717A] font-light">
                Maximum dataset ingestion limit: 100MB per bundle
              </p>
            </div>
          </div>

          {/* Selected Pending Files with red X button */}
          {pendingFiles.length > 0 && (
            <div className="space-y-3 pt-2">
              <div className="flex items-center justify-between">
                <h3 className="text-[10px] font-bold text-[#52525B] uppercase tracking-wider">
                  Pending Files Queue ({pendingFiles.length})
                </h3>
              </div>
              
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-48 overflow-y-auto pr-1">
                {pendingFiles.map((file, idx) => (
                  <div 
                    key={idx} 
                    className="bg-white border border-[#E4E4E7] p-3 px-4 rounded-xl flex items-center justify-between hover:border-[#A1A1AA] transition-all relative shadow-[0_2px_6px_rgba(0,0,0,0.01)] text-xs animate-fade-in"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 bg-[#FAF9F6] rounded-lg border border-[#F4F4F5] text-[#18181B] shrink-0">
                        <FileText className="w-3.5 h-3.5" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-xs font-bold text-[#18181B] truncate pr-4">{file.name}</h3>
                        <p className="text-[10px] text-[#71717A] mt-0.5 font-light">
                          {formatBytes(file.size)} • Ready
                        </p>
                      </div>
                    </div>
                    
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        setPendingFiles(prev => prev.filter((_, i) => i !== idx));
                      }}
                      className="absolute -top-1.5 -right-1.5 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-full w-5 h-5 flex items-center justify-center font-bold text-[10px] cursor-pointer shadow-xs transition-colors focus:outline-none"
                      title="Remove file"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>

              {/* Manual Start Pipeline Trigger Button */}
              {pipelineStatus === 'idle' && (
                <div className="flex justify-center pt-2">
                  <button
                    type="button"
                    onClick={executePipelineForPendingFiles}
                    className="px-6 py-2.5 bg-[#18181B] hover:bg-black text-white text-xs font-semibold rounded-lg flex items-center justify-center gap-2 transition-colors cursor-pointer shadow-md hover:shadow-lg focus:outline-none"
                  >
                    <Play className="w-3.5 h-3.5 fill-white" />
                    <span>Start Forensic Analysis Pipeline</span>
                  </button>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Ingested Statements Portfolio */}
        {statements.length > 0 && (
          <div className="space-y-3 pt-6 border-t border-[#E4E4E7] animate-fade-in">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-[#52525B] uppercase tracking-wider">
                Ingested Statements Portfolio
              </h3>
              <span className="text-[10px] text-[#71717A] font-mono">
                {statements.length} statements active in session
              </span>
            </div>

            {/* Scrollable Container with border to look unified and clean */}
            <div className="max-h-[19.5rem] overflow-y-auto pr-1 border border-[#E4E4E7] bg-[#FAF9F6]/30 p-4 rounded-xl shadow-[0_2px_8px_rgba(0,0,0,0.01)]">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {statements.map(file => (
                  <div 
                    key={file.id} 
                    onClick={() => {
                      setLatestStatementId(file.id);
                      setCaseId(file.id);
                    }}
                    className={`bg-white border p-3 px-4 rounded-xl flex items-center justify-between hover:border-[#A1A1AA] transition-all cursor-pointer relative shadow-[0_2px_6px_rgba(0,0,0,0.015)] ${
                      latestStatementId === file.id ? 'border-[#18181B] ring-1 ring-zinc-950' : 'border-[#E4E4E7]'
                    }`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className="p-2 bg-[#FAF9F6] rounded-lg border border-[#F4F4F5] text-[#18181B] shrink-0">
                        <FileText className="w-4 h-4" />
                      </div>
                      <div className="min-w-0 pr-4">
                        <h3 className="text-xs font-bold text-[#18181B] truncate">{file.filename}</h3>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <p className="text-[9px] text-[#71717A] font-mono select-all bg-zinc-50 px-1 py-0.5 rounded border border-zinc-200/50 truncate max-w-[100px]" title={file.id}>
                            Statement ID: {file.id}
                          </p>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              navigator.clipboard.writeText(file.id);
                              setCopiedId(file.id);
                              setTimeout(() => setCopiedId(null), 2000);
                            }}
                            className={`text-[9px] font-semibold cursor-pointer hover:underline ${
                              copiedId === file.id ? 'text-green-600 hover:text-green-700' : 'text-[#2563EB] hover:text-blue-700'
                            }`}
                          >
                            {copiedId === file.id ? 'Copied!' : 'Copy'}
                          </button>
                        </div>
                        <p className="text-[9.5px] text-[#71717A] mt-0.5 font-light">
                          Bank: {file.bank_name || 'Generic'}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <div className={`flex items-center gap-1 text-[8px] font-bold px-1.5 py-0.5 rounded-full uppercase tracking-wider ${
                        file.status === 'completed' ? 'text-[#065F46] bg-[#ECFDF5] border border-[#A7F3D0]' :
                        file.status === 'failed' ? 'text-red-800 bg-red-50 border border-red-200' : 'text-blue-800 bg-blue-50 border border-blue-200'
                      }`}>
                        <span className={`w-1 h-1 rounded-full inline-block ${
                          file.status === 'completed' ? 'bg-[#10B981]' : file.status === 'failed' ? 'bg-red-500' : 'bg-blue-500 animate-pulse'
                        }`}></span>
                        {file.status}
                      </div>

                      {/* Delete button (small red x in right corner of uploaded statements) */}
                      <button
                        type="button"
                        onClick={async (e) => {
                          e.stopPropagation();
                          if (window.confirm(`Delete statement "${file.filename}" and its associated transactions from DB?`)) {
                            try {
                              await deleteUploadedStatement(file.id);
                            } catch (err: any) {
                              alert(`Failed to delete: ${err.message}`);
                            }
                          }
                        }}
                        className="bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 rounded-full w-5 h-5 flex items-center justify-center font-bold text-[10px] cursor-pointer shadow-xs transition-colors focus:outline-none"
                        title="Delete Statement"
                      >
                        ×
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Clear Database Session Button positioned at bottom-right */}
        <div className="flex justify-end pt-1">
          <button
            type="button; e.stopPropagation()"
            onClick={async () => {
              if (window.confirm("Are you sure you want to clear the entire PostgreSQL database? This will purge all statements and analysis results.")) {
                setActiveLogMsg("Clearing database...");
                try {
                  await clearDatabaseSession();
                  setActiveLogMsg("Database successfully cleared.");
                  setPipelineStatus('idle');
                  resetNodeStatesToInitial();
                } catch (err: any) {
                  alert(`Error: ${err.message}`);
                }
              }
            }}
            className="px-3.5 py-1.5 bg-red-50 hover:bg-red-100 text-red-600 border border-red-200 text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 cursor-pointer shadow-xs focus:outline-none transition-colors"
          >
            <Eraser className="w-3.5 h-3.5" />
            <span>Clear Database</span>
          </button>
        </div>
      </div>

      {/* Prominent live pipeline progress bar (stage + %) */}
      {pipelineStatus === 'processing' && (
        <div className="max-w-3xl mx-auto">
          <div className="bg-white border border-[#E4E4E7] rounded-xl p-4 shadow-sm space-y-2.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-[#18181B] flex items-center gap-2">
                <Loader2 className="w-3.5 h-3.5 animate-spin text-[#2563EB]" />
                Processing pipeline
              </span>
              <span className="font-mono font-bold text-[#2563EB]">{ocrProgress}%</span>
            </div>
            <div className="w-full h-2 bg-[#F4F4F5] rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#2563EB] to-[#10B981] rounded-full transition-all duration-500"
                style={{ width: `${Math.max(5, ocrProgress)}%` }}
              />
            </div>
            <p className="text-[11px] text-[#71717A] font-light truncate">{activeLogMsg}</p>
          </div>
        </div>
      )}

      {/* SECTION 2: INTERACTIVE VISUAL WORKFLOW CANVASES */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <div className="space-y-1">
            <h2 className="text-xs font-bold text-[#52525B] uppercase tracking-wider">
              Investigation Execution Blueprint
            </h2>
            <p className="text-[11px] text-[#71717A] font-light">
              Watch real-time data flow connections cascade through localized orchestration pipelines.
            </p>
          </div>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            {/* Live Pipeline Status Log */}
            <div className="hidden lg:flex items-center gap-2 bg-white border border-[#E4E4E7] px-3.5 py-1.5 rounded-lg text-xs text-[#52525B] max-w-sm">
              <span className={`w-2 h-2 rounded-full shrink-0 ${
                pipelineStatus === 'processing' ? 'bg-[#2563EB] animate-pulse' :
                pipelineStatus === 'completed' ? 'bg-[#10B981]' : 'bg-[#71717A]'
              }`} />
              <span className="truncate font-light text-[11px]">{activeLogMsg}</span>
            </div>

            {errorMsg && (
              <div className="flex items-center gap-1.5 text-xs text-red-700 bg-red-50 border border-red-200 px-3 py-1.5 rounded-lg">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span className="truncate max-w-[200px]">{errorMsg}</span>
              </div>
            )}

            {pipelineStatus === 'completed' && (
              <button
                onClick={() => {
                  setLatestStatementId(null);
                  resetNodeStatesToInitial();
                  setPipelineStatus('idle');
                  setActiveLogMsg("Canvas reset. Ready for new audit.");
                }}
                className="w-full sm:w-auto px-4 py-1.8 bg-white border border-[#E4E4E7] hover:border-[#18181B] text-[#52525B] text-xs font-semibold rounded-lg flex items-center justify-center gap-1.5 cursor-pointer font-sans"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                <span>Reset Workflow Canvas</span>
              </button>
            )}
          </div>
        </div>

        {/* WORKFLOW VIEWPORT CONTROLLER */}
        <div className="bg-[#FAFDFB] border border-[#E4E4E7] rounded-xl overflow-x-auto shadow-sm relative" style={{ backgroundImage: 'radial-gradient(#e4e4e7 1.5px, transparent 1.5px)', backgroundSize: '18px 18px' }}>
          
          <div className="min-w-[2000px] w-[2000px] h-[450px] relative p-8 select-none">
            
            {/* SVG Base Connection Layer */}
            <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 0 }}>
              {(() => {
                const drawConnection = (fromKey: string, toKey: string, targetStatus: NodeStatus, outPortYOffset = 38, inPortYOffset = 38) => {
                  const from = nodeCoords[fromKey];
                  const to = nodeCoords[toKey];
                  if (!from || !to) return null;
                  
                  const startX = from.x + 180;
                  const startY = from.y + outPortYOffset;
                  const endX = to.x;
                  const endY = to.y + inPortYOffset;
                  const path = getBezierPath(startX, startY, endX, endY);
                  
                  return (
                    <g key={`${fromKey}-${toKey}`}>
                      <path d={path} fill="none" stroke="#f4f4f5" strokeWidth="5" strokeLinecap="round" opacity="0.4" />
                      <path 
                        d={path} 
                        fill="none" 
                        stroke={targetStatus === 'complete' ? '#10b981' : targetStatus === 'failed' ? '#ef4444' : '#e4e4e7'} 
                        strokeWidth={targetStatus === 'running' ? '2.5' : '1.8'} 
                        strokeLinecap="round" 
                      />
                      {targetStatus === 'running' && (
                        <path 
                          d={path} 
                          fill="none" 
                          stroke={fromKey === 'upload' || fromKey === 'ocr' || fromKey === 'cleaning' || fromKey === 'standardization' || fromKey === 'validation' || fromKey === 'database' ? '#3b82f6' : '#f59e0b'} 
                          strokeWidth="2.5" 
                          strokeLinecap="round"
                          className="flow-line-fast"
                        />
                      )}
                    </g>
                  );
                };

                return (
                  <>
                    {drawConnection('upload', 'ocr', nodeStates.ocr)}
                    {drawConnection('ocr', 'cleaning', nodeStates.cleaning)}
                    {drawConnection('cleaning', 'standardization', nodeStates.standardization)}
                    {drawConnection('standardization', 'validation', nodeStates.validation)}
                    {drawConnection('validation', 'database', nodeStates.database)}

                    {/* Database branches out in parallel */}
                    {drawConnection('database', 'loops', nodeStates.loops, 20, 38)}
                    {drawConnection('database', 'flow', nodeStates.flow, 38, 38)}
                    {drawConnection('database', 'trails', nodeStates.trails, 56, 38)}

                    {/* Branches merge into Report */}
                    {drawConnection('loops', 'report', nodeStates.report === 'running' ? 'running' : (nodeStates.report === 'complete' ? 'complete' : 'queued'))}
                    {drawConnection('flow', 'report', nodeStates.report === 'running' ? 'running' : (nodeStates.report === 'complete' ? 'complete' : 'queued'))}
                    {drawConnection('trails', 'report', nodeStates.report === 'running' ? 'running' : (nodeStates.report === 'complete' ? 'complete' : 'queued'))}

                    {/* Report yields PDF & Excel */}
                    {drawConnection('report', 'exportPdf', nodeStates.exportPdf, 25, 38)}
                    {drawConnection('report', 'exportExcel', nodeStates.exportExcel, 51, 38)}
                  </>
                );
              })()}
            </svg>

            {/* DOM Overlay of Interactive Node Cards */}
            {Object.entries(nodeCoords).map(([key, coords]) => {
              const status = nodeStates[key];
              
              let title = '';
              let sub = '';
              let IconComponent = UploadCloud;
              let iconBg = 'bg-zinc-100 text-zinc-700';
              
              switch(key) {
                case 'upload':
                  title = 'Evidence Ingestion';
                  sub = currentStatementId ? 'Document enqueued' : 'Ingest statement';
                  IconComponent = UploadCloud;
                  iconBg = 'bg-indigo-50 text-indigo-700 border border-indigo-100';
                  break;
                case 'ocr':
                  title = 'OCR Extraction';
                  sub = status === 'queued' ? 'PDF parsing queued' : (status === 'running' ? `Extracting text (${ocrProgress}%)` : 'Document mapped');
                  IconComponent = Cpu;
                  iconBg = 'bg-emerald-50 text-emerald-700 border border-emerald-100';
                  break;
                case 'cleaning':
                  title = 'Data Cleaning';
                  sub = status === 'queued' ? 'Deduplication' : (status === 'running' ? `Polishing data...` : 'Duplicates purged');
                  IconComponent = Eraser;
                  iconBg = 'bg-amber-50 text-amber-700 border border-amber-100';
                  break;
                case 'standardization':
                  title = 'Standardization';
                  sub = status === 'queued' ? 'Schema mapping' : (status === 'running' ? `Mapping keys...` : 'Structure normalized');
                  IconComponent = ShieldCheck;
                  iconBg = 'bg-sky-50 text-sky-700 border border-sky-100';
                  break;
                case 'validation':
                  title = 'Validation Engine';
                  sub = status === 'queued' ? 'Integrity checks' : (status === 'running' ? `Scanning rows...` : 'Constraints verified');
                  IconComponent = ShieldCheck;
                  iconBg = 'bg-rose-50 text-rose-700 border border-rose-100';
                  break;
                case 'database':
                  title = 'Data Base Store';
                  sub = status === 'queued' ? 'Saving transaction DB' : (status === 'running' ? `Writing DB store...` : 'Persisted to SQL');
                  IconComponent = FileText;
                  iconBg = 'bg-teal-50 text-teal-700 border border-teal-100';
                  break;
                case 'loops':
                  title = 'Round Trip Seek';
                  sub = status === 'queued' ? 'Trace loops' : (status === 'running' ? 'Circular scan...' : 'Loops parsed');
                  IconComponent = RefreshCw;
                  iconBg = 'bg-pink-50 text-pink-700 border border-pink-100';
                  break;
                case 'flow':
                  title = 'Money Flow Map';
                  sub = status === 'queued' ? 'Account graphs' : (status === 'running' ? 'Mapping nodes...' : 'Topology complete');
                  IconComponent = GitFork;
                  iconBg = 'bg-violet-50 text-violet-700 border border-violet-100';
                  break;
                case 'trails':
                  title = 'Money Trail Trace';
                  sub = status === 'queued' ? 'FIFO sequences' : (status === 'running' ? 'Resolving trails...' : 'FIFO trails computed');
                  IconComponent = Activity;
                  iconBg = 'bg-blue-50 text-blue-700 border border-blue-100';
                  break;
                case 'report':
                  title = 'Report Builder';
                  sub = status === 'queued' ? 'Dossier compiling' : (status === 'running' ? 'Layering details...' : 'Summary constructed');
                  IconComponent = FileCheck;
                  iconBg = 'bg-orange-50 text-orange-700 border border-orange-100';
                  break;
                case 'exportPdf':
                  title = 'PDF Vector Brief';
                  sub = status === 'complete' ? '✓ PDF Compiled' : 'Queued';
                  IconComponent = FileDown;
                  iconBg = 'bg-red-50 text-red-700 border border-red-100';
                  break;
                case 'exportExcel':
                  title = 'Excel Data Ledger';
                  sub = status === 'complete' ? '✓ Spreadsheet Ready' : 'Queued';
                  IconComponent = FileSpreadsheet;
                  iconBg = 'bg-green-50 text-green-700 border border-green-100';
                  break;
              }

              const isRunning = status === 'running';
              const isComplete = status === 'complete';
              const isFailed = status === 'failed';

              return (
                <div 
                  key={key}
                  className={`absolute bg-white rounded-xl border p-3 flex flex-col justify-between w-[180px] h-[76px] transition-all duration-300 shadow-[0_2px_8px_rgba(0,0,0,0.03)] group hover:scale-[1.03] hover:-translate-y-0.5 hover:shadow-[0_8px_16px_rgba(0,0,0,0.05)] ${
                    isRunning ? 'border-amber-500 node-running-glow ring-2 ring-amber-400/25 z-20' : 
                    isFailed ? 'border-red-500 z-20 shadow-[0_0_12px_rgba(239,68,68,0.2)]' :
                    isComplete ? 'border-[#10B981] z-10' : 'border-zinc-200 z-10'
                  }`}
                  style={{ left: `${coords.x}px`, top: `${coords.y}px` }}
                >
                  {/* Left input port marker */}
                  {key !== 'upload' && (
                    <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -left-1.25 top-1/2 -translate-y-1/2 flex items-center justify-center shadow-xs z-30">
                      <div className="w-1 h-1 rounded-full bg-zinc-600" />
                    </div>
                  )}

                  {/* Right output port markers */}
                  {key !== 'exportPdf' && key !== 'exportExcel' && (
                    <>
                      {key === 'database' ? (
                        <>
                          <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-[20px] flex items-center justify-center shadow-xs z-30">
                            <div className="w-1 h-1 rounded-full bg-zinc-600" />
                          </div>
                          <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-1/2 -translate-y-1/2 flex items-center justify-center shadow-xs z-30">
                            <div className="w-1 h-1 rounded-full bg-zinc-600" />
                          </div>
                          <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-[56px] flex items-center justify-center shadow-xs z-30">
                            <div className="w-1 h-1 rounded-full bg-zinc-600" />
                          </div>
                        </>
                      ) : key === 'report' ? (
                        <>
                          <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-[25px] flex items-center justify-center shadow-xs z-30">
                            <div className="w-1 h-1 rounded-full bg-zinc-600" />
                          </div>
                          <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-[51px] flex items-center justify-center shadow-xs z-30">
                            <div className="w-1 h-1 rounded-full bg-zinc-600" />
                          </div>
                        </>
                      ) : (
                        <div className="w-2.5 h-2.5 rounded-full bg-white border border-zinc-400 absolute -right-1.25 top-1/2 -translate-y-1/2 flex items-center justify-center shadow-xs z-30">
                          <div className="w-1 h-1 rounded-full bg-zinc-600" />
                        </div>
                      )}
                    </>
                  )}

                  {/* Header */}
                  <div className="flex items-start gap-2.5 min-w-0">
                    <div className={`p-1.5 rounded-lg shrink-0 ${iconBg}`}>
                      <IconComponent className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 leading-tight">
                      <p className="text-[11px] font-bold text-zinc-950 truncate">{title}</p>
                      <p className="text-[9px] text-zinc-500 font-light truncate mt-0.5">{sub}</p>
                    </div>
                  </div>

                  {/* Details block */}
                  <div className="flex items-center justify-between pt-1 border-t border-zinc-100/80 font-mono">
                    <span className="text-[8px] tracking-wider uppercase font-semibold text-zinc-400">
                      {key === 'upload' ? 'source' : 
                       key.startsWith('export') ? 'export' : 'action'}
                    </span>
                    <div className="flex items-center gap-1">
                      {isRunning && (
                        <div className="flex items-center gap-1 text-amber-500 text-[8px] font-bold">
                          <Loader2 className="w-2.5 h-2.5 animate-spin" />
                          <span>Active</span>
                        </div>
                      )}
                      {isFailed && (
                        <span className="text-red-500 text-[8px] font-bold">Error</span>
                      )}
                      {isComplete && (
                        <div className="flex items-center gap-1 text-[#10B981] text-[8px] font-bold">
                          <CheckCircle2 className="w-2.5 h-2.5 stroke-[3]" />
                          <span>Done</span>
                        </div>
                      )}
                      {!isRunning && !isComplete && !isFailed && (
                        <span className="text-zinc-400 text-[8px] font-medium">Idle</span>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* SECTION 3: AFTER PROCESSING SUMMARY & ANALYSIS ACTIONS */}
      {(pipelineStatus === 'completed' || pipelineStatus === 'processing' || latestStatementId) && (
        <div className="space-y-8 animate-fade-in max-w-5xl mx-auto pt-4">
          
          {/* Real-time Summary Box */}
          <div className="bg-white border border-[#E4E4E7] rounded-xl p-6 space-y-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xs font-bold text-[#18181B] uppercase tracking-wider">
                  Ingestion Extraction Results
                </h3>
                <p className="text-[11px] text-[#71717A] font-light mt-0.5">
                  Extracted analytical models matched against sovereign enforcement intelligence constraints.
                </p>
              </div>
              <span className="text-[10px] text-[#10B981] font-bold bg-[#ECFDF5] border border-[#A7F3D0] px-2.5 py-0.5 rounded-full uppercase">
                {pipelineStatus === 'completed' ? 'Success' : 'Processing'}
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-6 gap-3.5 pt-1">
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">Extracted Tx</span>
                <p className="text-base font-bold text-[#18181B]">
                  {validationReport?.summary.total ?? transactions.length ?? 0}
                </p>
              </div>
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">Entities / Accs</span>
                <p className="text-base font-bold text-[#18181B]">{caseSummary?.entities || 0}</p>
              </div>
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">De-Duplicated</span>
                <p className="text-base font-bold text-[#18181B]">{validationReport?.summary.duplicates || 0}</p>
              </div>
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">Failures Logged</span>
                <p className="text-base font-bold text-[#18181B]">
                  {validationReport?.summary.failed_or_reversed || 0}
                </p>
              </div>
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] text-orange-950 rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">Avg Confidence</span>
                <p className="text-base font-bold text-[#C2410C]">
                  {validationReport?.summary.average_confidence 
                    ? `${(validationReport.summary.average_confidence * 100).toFixed(1)}%` 
                    : 'N/A'}
                </p>
              </div>
              <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-lg p-3 text-center space-y-0.5">
                <span className="text-[9px] uppercase tracking-wider text-[#71717A] font-medium block">Credit Trails</span>
                <p className="text-base font-bold text-[#18181B]">
                  {transactions.filter(t => t.debit_credit === 'CREDIT').length}
                </p>
              </div>
            </div>
          </div>

          {/* NEW SECTION: DATA CLEANING AND VALIDATION REPORT */}
          {validationReport && (
            <div className="bg-white border border-[#E4E4E7] rounded-xl p-6 space-y-4 shadow-sm animate-fade-in">
              <div>
                <h3 className="text-xs font-bold text-[#18181B] uppercase tracking-wider">
                  Ledger Quality & Validation Findings
                </h3>
                <p className="text-[11px] text-[#71717A] font-light mt-0.5">
                  Deduplication metrics and schema constraints violations flagged during canonical ingestion validation.
                </p>
              </div>

              {validationReport.issues.length === 0 ? (
                <div className="p-4 bg-[#F0FDF4] border border-[#A7F3D0] rounded-lg text-xs flex items-center gap-2 text-[#065F46]">
                  <CheckCircle2 className="w-4 h-4 text-[#10B981]" />
                  <span>No data cleaning anomalies or validation issues detected for this statement! Ledger adheres perfectly to bank format.</span>
                </div>
              ) : (
                <div className="overflow-x-auto border border-[#E4E4E7] rounded-lg text-xs max-h-72 overflow-y-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-[#FAF9F6] border-b border-[#E4E4E7] text-[10px] uppercase font-bold text-[#71717A] font-mono sticky top-0">
                        <th className="p-2.5 pl-4">Date</th>
                        <th className="p-2.5">Narration</th>
                        <th className="p-2.5 text-right">Amount</th>
                        <th className="p-2.5 text-center">Type</th>
                        <th className="p-2.5 text-center">Validation Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-[#E4E4E7]">
                      {validationReport.issues.map((issue) => {
                        const notes = Array.isArray(issue.validation_notes)
                          ? issue.validation_notes
                          : typeof issue.validation_notes === 'string'
                            ? [issue.validation_notes]
                            : [];

                        return (
                          <tr key={issue.id} className="hover:bg-[#FAFAFA] align-top">
                            <td className="p-2.5 pl-4 font-mono font-medium text-zinc-600 whitespace-nowrap">
                              {issue.date || 'N/A'}
                            </td>
                            <td className="p-2.5 text-zinc-950 font-sans font-light max-w-sm truncate" title={issue.narration || ''}>
                              {issue.narration || 'Unknown Narration'}
                            </td>
                            <td className="p-2.5 text-right font-mono font-bold text-zinc-950 whitespace-nowrap">
                              {issue.amount !== null ? `₹${issue.amount.toLocaleString(undefined, {minimumFractionDigits:2, maximumFractionDigits:2})}` : '₹0.00'}
                            </td>
                            <td className="p-2.5 text-center whitespace-nowrap font-mono text-[10px]">
                              <span className={`px-2 py-0.5 rounded ${
                                issue.debit_credit === 'DEBIT' ? 'bg-red-50 text-red-700' : 'bg-green-50 text-green-700'
                              }`}>
                                {issue.debit_credit || 'N/A'}
                              </span>
                            </td>
                            <td className="p-2.5 pr-4">
                              <div className="flex flex-wrap gap-1 items-center justify-center">
                                {issue.is_duplicate && (
                                  <span className="px-1.5 py-0.2 rounded bg-amber-100 text-amber-800 text-[9px] font-bold font-mono">DUPLICATE</span>
                                )}
                                {issue.is_failed && (
                                  <span className="px-1.5 py-0.2 rounded bg-red-100 text-red-800 text-[9px] font-bold font-mono">FAILED_TX</span>
                                )}
                                {!issue.is_valid && (
                                  <span className="px-1.5 py-0.2 rounded bg-rose-100 text-rose-800 text-[9px] font-bold font-mono">INVALID</span>
                                )}
                                {notes.map((n, i) => (
                                  <span key={i} className="px-1.5 py-0.2 rounded bg-gray-100 text-gray-700 text-[9px] font-light max-w-[150px] truncate" title={String(n)}>
                                    {String(n)}
                                  </span>
                                ))}
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {/* LARGE INTERACTIVE ANALYSIS ACTION CARDS */}
          {pipelineStatus === 'completed' && (
            <div className="space-y-4">
              <h3 className="text-xs font-bold text-[#52525B] uppercase tracking-wider">
                Investigate Extracted Findings
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                
                {/* 1. Round Trips Action */}
                <button
                  onClick={() => onNavigateToView('round-trips')}
                  className="bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-xl p-5 text-left transition-all duration-200 group cursor-pointer shadow-xs focus:outline-none flex flex-col justify-between h-44 animate-fade-in"
                >
                  <div className="space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-[#FFF2F2] border border-[#FCA5A5] flex items-center justify-center text-[#DC2626]">
                      <RefreshCw className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-[#18181B]">View Round Trips</h4>
                      <p className="text-xs text-[#71717A] mt-1 font-light leading-snug">
                        Investigate circular loops inflating entity values.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-950 font-semibold pt-2">
                    <span>Inspect Loops</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>

                {/* 2. Money Flow Action */}
                <button
                  onClick={() => onNavigateToView('money-flow')}
                  className="bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-xl p-5 text-left transition-all duration-200 group cursor-pointer shadow-xs focus:outline-none flex flex-col justify-between h-44 animate-fade-in"
                >
                  <div className="space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-[#EFF6FF] border border-[#BFDBFE] flex items-center justify-center text-[#2563EB]">
                      <GitFork className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-[#18181B]">View Money Flow</h4>
                      <p className="text-xs text-[#71717A] mt-1 font-light leading-snug">
                        Interrogate full multi-party transit graphs.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-950 font-semibold pt-2">
                    <span>Trace Flow Map</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>

                {/* 3. Money Trails Action */}
                <button
                  onClick={() => onNavigateToView('money-trails')}
                  className="bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-xl p-5 text-left transition-all duration-200 group cursor-pointer shadow-xs focus:outline-none flex flex-col justify-between h-44 animate-fade-in"
                >
                  <div className="space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-[#F0FDF4] border border-[#A7F3D0] flex items-center justify-center text-[#16A34A]">
                      <Activity className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-[#18181B]">View Money Trails</h4>
                      <p className="text-xs text-[#71717A] mt-1 font-light leading-snug">
                        Resolve FIFO dispersion trace sequences.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-950 font-semibold pt-2">
                    <span>View FIFO Trails</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>

                {/* 4. Generate Report Action */}
                <button
                  onClick={() => onNavigateToView('reports')}
                  className="bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-xl p-5 text-left transition-all duration-200 group cursor-pointer shadow-xs focus:outline-none flex flex-col justify-between h-44 animate-fade-in"
                >
                  <div className="space-y-2">
                    <div className="w-8 h-8 rounded-lg bg-[#FAF9F6] border border-[#E4E4E7] flex items-center justify-center text-zinc-700">
                      <FileCheck className="w-4 h-4" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-[#18181B]">Generate Brief</h4>
                      <p className="text-xs text-[#71717A] mt-1 font-light leading-snug">
                        Export formatted PDF and Excel ledger portfolios.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1.5 text-xs text-zinc-950 font-semibold pt-2">
                    <span>Access Reports</span>
                    <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>

              </div>
            </div>
          )}

        </div>
      )}

    </div>
  );
}
