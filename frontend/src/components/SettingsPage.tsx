import React, { useState, useEffect } from 'react';
import { Key, Shield, User, RefreshCw, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { getApiBaseUrl } from '../services/api';
import { getHealth, getServicesHealth } from '../services/finintelApi';

export default function SettingsPage() {
  const [investigatorName, setInvestigatorName] = useState('Agent Willis');
  const [agencyCode, setAgencyCode] = useState('AML-US-UNIT4');
  const [modelType, setModelType] = useState('gemini-2.5-flash');
  
  // API base URL configuration
  const [apiBaseUrl, setApiBaseUrl] = useState('');
  const [isSaved, setIsSaved] = useState(false);

  // Connection testing state
  const [isTesting, setIsTesting] = useState(false);
  const [testResult, setTestResult] = useState<{
    status: 'success' | 'warning' | 'error' | null;
    message: string;
  }>({ status: null, message: '' });

  // Initialize values
  useEffect(() => {
    setApiBaseUrl(getApiBaseUrl());
    
    const savedName = localStorage.getItem('finintel_investigator_name');
    if (savedName) setInvestigatorName(savedName);

    const savedCode = localStorage.getItem('finintel_agency_code');
    if (savedCode) setAgencyCode(savedCode);
  }, []);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    let sanitizedUrl = apiBaseUrl.trim();
    if (sanitizedUrl.toLowerCase().includes("localhot")) {
      sanitizedUrl = sanitizedUrl.replace(/localhot/i, "localhost");
      setApiBaseUrl(sanitizedUrl);
    }
    localStorage.setItem('finintel_api_base_url', sanitizedUrl);
    localStorage.setItem('finintel_investigator_name', investigatorName);
    localStorage.setItem('finintel_agency_code', agencyCode);
    
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  const handleTestConnection = async () => {
    setIsTesting(true);
    setTestResult({ status: null, message: '' });
    
    let sanitizedUrl = apiBaseUrl.trim();
    if (sanitizedUrl.toLowerCase().includes("localhot")) {
      sanitizedUrl = sanitizedUrl.replace(/localhot/i, "localhost");
      setApiBaseUrl(sanitizedUrl);
    }
    
    // Save temporary URL override for test fetch call
    localStorage.setItem('finintel_api_base_url', sanitizedUrl);

    try {
      // Test gateway main health endpoint
      const health = await getHealth();
      
      try {
        // Test upstream microservices
        const servicesHealth = await getServicesHealth();
        // Check if any services are down
        const services = servicesHealth?.services || servicesHealth || {};
        const downServices = Object.entries(services)
          .filter(([_, status]) => status !== 'healthy' && status !== 'ok' && status !== true)
          .map(([name]) => name);

        if (downServices.length > 0) {
          setTestResult({
            status: 'warning',
            message: `Connected. Warning: upstream services [${downServices.join(', ')}] appear offline.`
          });
        } else {
          setTestResult({
            status: 'success',
            message: "Success! Gateway and all upstream microservices are online."
          });
        }
      } catch (upstreamErr) {
        setTestResult({
          status: 'warning',
          message: "Connected to Gateway, but upstream microservices health check failed."
        });
      }
    } catch (err: any) {
      console.error(err);
      setTestResult({
        status: 'error',
        message: "Connection failed. Check API Base URL and confirm backend is running."
      });
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-10 animate-fade-in select-none">
      
      {/* Header and subtitle */}
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-[#18181B] font-display">Profile & Configurations</h1>
        <p className="text-sm text-[#71717A] max-w-xl leading-relaxed font-sans font-light">
          Configure local workspace descriptors, operational handles, and language model defaults.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-8 items-start">
        
        {/* Settings form (Left) */}
        <form onSubmit={handleSave} className="md:col-span-7 bg-white border border-[#E4E4E7] rounded-xl p-6 space-y-5 shadow-xs">
          <div>
            <h3 className="text-xs font-bold text-[#18181B] uppercase tracking-wider font-mono">
              Workspace Profile Settings
            </h3>
            <p className="text-xs text-[#71717A] mt-1 font-light font-sans">
              These details identify the investigator on compiled briefs or export audit trails.
            </p>
          </div>

          <div className="space-y-4 text-xs font-sans">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[#52525B] uppercase block font-mono">
                  Investigator Handle
                </label>
                <input
                  type="text"
                  value={investigatorName}
                  onChange={(e) => setInvestigatorName(e.target.value)}
                  className="w-full bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-md px-3 py-1.5 text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#18181B] font-semibold font-sans"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-[#52525B] uppercase block font-mono">
                  Division Identifier Code
                </label>
                <input
                  type="text"
                  value={agencyCode}
                  onChange={(e) => setAgencyCode(e.target.value)}
                  className="w-full bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-md px-3 py-1.5 text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#18181B] font-semibold font-sans"
                />
              </div>
            </div>

            {/* API Base URL Configuration */}
            <div className="space-y-1.5 border-t border-[#E4E4E7] pt-4">
              <label className="text-[10px] font-bold text-[#52525B] uppercase block font-mono">
                API Base URL Address
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={apiBaseUrl}
                  onChange={(e) => setApiBaseUrl(e.target.value)}
                  placeholder="http://localhost:8080"
                  className="flex-1 bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-md px-3 py-1.5 text-[#18181B] focus:outline-none focus:ring-1 focus:ring-[#18181B] font-semibold font-mono"
                />
                <button
                  type="button"
                  onClick={handleTestConnection}
                  disabled={isTesting || !apiBaseUrl}
                  className="px-3 py-1.5 bg-white border border-[#E4E4E7] hover:border-[#18181B] text-[#52525B] rounded-md text-[11px] font-semibold flex items-center gap-1 shrink-0 disabled:opacity-50 cursor-pointer"
                >
                  {isTesting ? (
                    <>
                      <RefreshCw className="w-3 animate-spin" />
                      <span>Testing...</span>
                    </>
                  ) : (
                    <span>Test Connection</span>
                  )}
                </button>
              </div>
              <p className="text-[10px] text-[#71717A] font-light">
                Base gateway address for API requests (e.g. <code>http://localhost:8080</code>).
              </p>

              {/* Connection Test Results badge/alert */}
              {testResult.status && (
                <div className={`p-2.5 rounded-lg border text-[11px] font-semibold flex items-start gap-2 mt-2 animate-fade-in ${
                  testResult.status === 'success' ? 'bg-[#ECFDF5] border-[#A7F3D0] text-[#065F46]' :
                  testResult.status === 'warning' ? 'bg-amber-50 border-amber-200 text-amber-800' :
                  'bg-red-50 border-red-200 text-red-800'
                }`}>
                  {testResult.status === 'success' && <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0" />}
                  {testResult.status === 'warning' && <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />}
                  {testResult.status === 'error' && <XCircle className="w-4 h-4 text-red-500 shrink-0" />}
                  <span>{testResult.message}</span>
                </div>
              )}
            </div>

            {/* Models selection */}
            <div className="space-y-1.5 border-t border-[#E4E4E7] pt-4">
              <label className="text-[10px] font-bold text-[#52525B] uppercase block font-mono">
                Default Extraction Model
              </label>
              <select
                value={modelType}
                onChange={(e) => setModelType(e.target.value)}
                className="w-full bg-white border border-[#E4E4E7] hover:border-[#18181B] rounded-md px-3 py-1.5 text-[#18181B] focus:outline-none cursor-pointer font-medium font-sans"
              >
                <option value="gemini-2.5-flash">Gemini 2.5 Flash (High Efficiency)</option>
                <option value="gemini-2.5-pro">Gemini 2.5 Pro (Precision Logic Reasoning)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-between items-center pt-4 border-t border-[#E4E4E7]">
            <span className="text-[10px] text-[#71717A] font-mono">Forensics Core v2.4</span>
            <button
              type="submit"
              className="px-4 py-1.5 bg-[#18181B] hover:bg-black text-white rounded-md text-xs font-semibold cursor-pointer transition-colors font-sans"
            >
              Save Configurations
            </button>
          </div>

          {isSaved && (
            <div className="p-3 bg-[#ECFDF5] border border-[#A7F3D0] text-[#065F46] rounded-lg text-xs font-bold flex items-center gap-2 animate-fade-in font-sans">
              <Shield className="w-4 h-4 text-[#10B981]" />
              <span>Configurations successfully synchronized.</span>
            </div>
          )}
        </form>

        {/* Security guidelines policy (Right) */}
        <div className="md:col-span-5 bg-white border border-[#E4E4E7] rounded-xl p-6 space-y-4 shadow-xs text-xs font-sans">
          <div>
            <h3 className="text-xs font-bold text-[#18181B] uppercase tracking-wider font-mono">
              Legal Compliance Policy
            </h3>
            <p className="text-xs text-[#71717A] mt-1 font-light">
              Workspace legal jurisdiction constraints.
            </p>
          </div>

          <div className="space-y-4 pt-1 text-[#52525B] font-light leading-relaxed font-sans">
            <div className="space-y-1.5">
              <span className="text-[9px] text-[#18181B] font-bold uppercase block font-mono">
                1. Account Auditing Clearance
              </span>
              <p>
                Compliance parameters are governed by active international AML agreements. All downloaded files and compiled briefs are logged for ledger audit trail accountability reviews.
              </p>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-[#E4E4E7]">
              <span className="text-[9px] text-[#18181B] font-bold uppercase block font-mono">
                2. Data Privacy Limits
              </span>
              <p>
                Beneficial Ownership Registry extracts are sourced purely from active corporate registries. Retransmissions must conform to sovereign confidentiality covenants.
              </p>
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
