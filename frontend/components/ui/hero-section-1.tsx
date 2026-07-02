import React, { useState, useEffect, useRef } from "react"
import { 
  Building, 
  Coins, 
  DollarSign, 
  FileText, 
  ShieldAlert, 
  Network, 
  ArrowRight, 
  Menu, 
  X, 
  Send, 
  Terminal, 
  FileSpreadsheet,
  CheckCircle,
  AlertTriangle,
  Download,
  Flame,
  ArrowUpRight,
  Globe,
  RefreshCw,
  Activity,
  FileCheck,
  Check
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { AnimatedGroup } from "@/components/ui/animated-group"
import { cn } from "@/lib/utils"

// Transition variants for animated-group
const transitionVariants = {
  item: {
    hidden: {
      opacity: 0,
      filter: 'blur(12px)',
      y: 12,
    },
    visible: {
      opacity: 1,
      filter: 'blur(0px)',
      y: 0,
      transition: {
        type: 'spring',
        bounce: 0.3,
        duration: 1.5,
      },
    },
  },
}

// Interfaces for our interactive workspace simulation
interface TraceNode {
  id: string;
  label: string;
  type: 'corporation' | 'crypto' | 'mule' | 'offshore';
  risk: number;
  country: string;
  amount: string;
  flag: string;
  x: number;
  y: number;
  description: string;
}

interface ChatMessage {
  sender: 'ai' | 'user';
  text: string;
  timestamp: string;
}

export function HeroSection({ onEnterPlatform }: { onEnterPlatform?: () => void }) {
  const [selectedDoc, setSelectedDoc] = useState<string>("MegaCorp_Statement.csv");
  const [isIngesting, setIsIngesting] = useState<boolean>(false);
  const [ingestionStep, setIngestionStep] = useState<string>("");
  const [selectedNode, setSelectedNode] = useState<string>("delta");
  const [activeTab, setActiveTab] = useState<'graph' | 'copilot' | 'report'>("graph");
  
  // Chat state for copilot
  const [chatInput, setChatInput] = useState<string>("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([
    {
      sender: "ai",
      text: "### Ingested Intelligence File: `MegaCorp_Bank_Statement_Oct2026.csv`\n\nI have cross-matched corporate registries and resolved 5 active entities.\n\nType or select one of the core investigative directives below to begin tracing the fund flows:",
      timestamp: "05:46:07"
    }
  ]);
  const [isTyping, setIsTyping] = useState<boolean>(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Auto scroll chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isTyping]);

  // Handle ingestion simulation
  const triggerIngestion = (docName: string) => {
    setSelectedDoc(docName);
    setIsIngesting(true);
    setIngestionStep("1. Reading raw CSV file bytes and sanitizing data headers...");
    
    setTimeout(() => {
      setIngestionStep("2. Applying automated Entity Resolution (matching business tax IDs with SEC files)...");
    }, 800);

    setTimeout(() => {
      setIngestionStep("3. Running transaction loop identification algorithms (Tarjan cycle detection)...");
    }, 1600);

    setTimeout(() => {
      setIngestionStep("4. Resolving offshore beneficial ownership & bearer token contracts...");
    }, 2400);

    setTimeout(() => {
      setIsIngesting(false);
      setIngestionStep("");
      // Add system message
      const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
      setChatHistory(prev => [
        ...prev,
        {
          sender: "ai",
          text: `### 📂 Successfully Re-Indexed Workspace Evidence: \`${docName}\`
- Resolved \`4\` high probability shell entities.
- Flags: Circular round-tripping alert active ($1.2M cycle volume).
- Dynamic risk score updated to: **0.91** (Extreme).`,
          timestamp
        }
      ]);
      setActiveTab("graph");
    }, 3200);
  };

  // Chat request with server API
  const handleSendMessage = async (textToSend?: string) => {
    const rawMsg = textToSend || chatInput;
    if (!rawMsg.trim()) return;

    if (!textToSend) setChatInput("");
    
    const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
    setChatHistory(prev => [...prev, { sender: "user", text: rawMsg, timestamp }]);
    setIsTyping(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: rawMsg })
      });
      const data = await response.json();
      setChatHistory(prev => [
        ...prev, 
        { 
          sender: "ai", 
          text: data.text || "No intelligence generated. Please try again.", 
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false }) 
        }
      ]);
    } catch (err) {
      console.error("Failed to query FinIntel Copilot:", err);
      setChatHistory(prev => [
        ...prev,
        {
          sender: "ai",
          text: "⚠️ Intelligence pipeline error. Server is unresponsive. Please retry.",
          timestamp: new Date().toLocaleTimeString('en-US', { hour12: false })
        }
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  // Trace interactive nodes definition
  const nodes: Record<string, TraceNode> = {
    apex: {
      id: "apex",
      label: "Apex Venture Corp",
      type: "corporation",
      risk: 42,
      country: "United States",
      flag: "🇺🇸",
      amount: "$1.20M USD",
      x: 15,
      y: 38,
      description: "US-registered LLC. Initiated Consultative SLA agreements sending $1.2M directly to Caribbean bank."
    },
    delta: {
      id: "delta",
      label: "Delta Shell Holdings",
      type: "offshore",
      risk: 91,
      country: "Cayman Islands",
      flag: "🇰🇾",
      amount: "$1.18M Layers",
      x: 50,
      y: 18,
      description: "Secrecy-jurisdiction corporation. Possesses nominee directors. Forwards 98% of inflows within 48 hours."
    },
    vanguard: {
      id: "vanguard",
      label: "Vanguard Seychelles Trading",
      type: "corporation",
      risk: 76,
      country: "Seychelles",
      flag: "🇸🇨",
      amount: "$1.15M Equity",
      x: 85,
      y: 38,
      description: "Offshore trade agent. Re-routes funds back into US Venture LLC as 'Capital injections' to close laundering loop."
    },
    mule: {
      id: "mule",
      label: "Carlos Santana (Acct #39281)",
      type: "mule",
      risk: 94,
      country: "United States",
      flag: "🇺🇸",
      amount: "$390K Deposited",
      x: 28,
      y: 74,
      description: "Nominee mule node. Student holding account. 42 physical structured branch deposits made consecutively under $10K limit."
    },
    crypto: {
      id: "crypto",
      label: "ERC20 Mixer (0x7a84...)",
      type: "crypto",
      risk: 98,
      country: "Decentralized",
      flag: "🌐",
      amount: "USDT Swap Desks",
      x: 72,
      y: 74,
      description: "Smart contract linked to state-sanctioned digital asset mixing pools & token anonymizers."
    }
  };

  return (
    <>
      <HeroHeader onEnterPlatform={onEnterPlatform} />
      <main className="relative pt-20 overflow-hidden bg-[#050505] text-white select-none">
        
        {/* Ambient Radial Glows matching theme */}
        <div className="absolute top-[-100px] left-[-100px] w-[500px] h-[500px] bg-blue-900/20 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute bottom-[-100px] right-[-100px] w-[500px] h-[500px] bg-slate-900/10 rounded-full blur-[120px] pointer-events-none"></div>
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-white/5 rounded-full blur-[150px] pointer-events-none"></div>

        {/* Hero Section */}
        <section className="relative z-10 px-6 pt-16 mx-auto max-w-7xl md:pt-28">
          <div className="flex flex-col items-center text-center">

            {/* Massive Display Title with ultra bold font display and tight tracking */}
            <h1 className="mt-8 font-display font-bold tracking-tighter text-balance text-5xl sm:text-6xl md:text-7xl lg:text-[76px] xl:text-[84px] text-white max-w-4xl leading-[0.95]">
              Turn Financial Evidence <br />
              Into <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-white/40">Intelligence.</span>
            </h1>

            {/* Subtitle */}
            <p className="mt-6 text-sm sm:text-base md:text-lg lg:text-xl text-white/50 max-w-2xl font-medium leading-relaxed font-sans">
              Upload bank statements, transactional records, PDFs, spreadsheets, and imagery. 
              FinIntel uncovers suspicious entities, traces fund flows, and reveals hidden networks in seconds.
            </p>

            {/* Call To Actions */}
            <div className="flex flex-col sm:flex-row gap-4 items-center justify-center mt-10 md:mt-12 w-full max-w-lg">
              {onEnterPlatform ? (
                <Button 
                  onClick={onEnterPlatform}
                  className="w-full sm:w-auto px-8 py-6 bg-white text-black hover:bg-neutral-200 font-bold rounded-lg transition-all cursor-pointer text-sm shadow-xl flex items-center justify-center gap-1.5"
                >
                  <span>Launch Operations Center</span>
                  <ArrowRight className="w-4 h-4 text-black" />
                </Button>
              ) : (
                <Button 
                  onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                  className="w-full sm:w-auto px-8 py-6 bg-white text-black hover:bg-neutral-200 font-semibold rounded-lg transition-colors cursor-pointer text-sm shadow-xl"
                >
                  Request Demo
                  <ArrowRight className="w-4 h-4 text-black ml-1" />
                </Button>
              )}
              <Button 
                onClick={() => document.getElementById("scroll-story")?.scrollIntoView({ behavior: "smooth" })}
                className="w-full sm:w-auto px-8 py-6 bg-white/5 border border-white/10 text-white hover:bg-white/10 font-semibold rounded-lg transition-colors cursor-pointer text-sm"
              >
                See How It Works
              </Button>
            </div>

            {/* Sub-footer indicators as high-contrast subtle text */}
            <div className="flex flex-wrap gap-x-12 gap-y-4 justify-center mt-14 opacity-40 font-display text-[11px] uppercase tracking-[0.2em] font-bold text-white max-w-4xl">
              <div>Global Graph Intelligence</div>
              <div>Real-time Risk Mapping</div>
              <div>Evidence Provenance Engine</div>
            </div>

          </div>
        </section>
        
        {/* Cinematic Workspace Container (Hero Visual) */}
        <section id="workspace" className="relative z-10 max-w-7xl mx-auto mt-16 md:mt-24 px-4 lg:px-6">
          <div className="relative bg-[#09090b] border border-white/5 rounded-2xl p-5 lg:p-7 shadow-2xl shadow-zinc-950/95 overflow-hidden ring-1 ring-white/5">
            
            {/* Workspace Overlay Grid */}
            <div className="absolute inset-0 opacity-[0.02] pointer-events-none z-0" style={{ backgroundImage: "radial-gradient(#fff 1px, transparent 1px)", backgroundSize: "24px 24px" }} />

            {/* Ambient Background Grid for visualizer */}
            <div className="absolute inset-x-0 bottom-0 top-1/2 bg-gradient-to-t from-black/95 to-transparent pointer-events-none z-10" />

            {/* Workspace Header Panel controls */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 pb-5 border-b border-white/5 z-20 relative">
              <div className="flex items-center gap-3">
                <div className="flex gap-2">
                  <span className="w-3 h-3 rounded-full bg-[#ff5f56] opacity-90" />
                  <span className="w-3 h-3 rounded-full bg-[#ffbd2e] opacity-90" />
                  <span className="w-3 h-3 rounded-full bg-[#27c93f] opacity-90" />
                </div>
                <div className="h-4 w-px bg-zinc-800" />
                <span className="text-xs font-mono text-zinc-400">FININTEL CORE // WORKSPACE</span>
                <span className="px-2 py-0.5 text-[10px] font-mono rounded bg-zinc-900 text-zinc-400 border border-zinc-800 flex items-center gap-1.5 font-medium">
                  <Globe className="w-3 h-3 text-zinc-500" /> MULTI-SOVEREIGN ASSESSMENT ACTIVE
                </span>
              </div>

              {/* Document Selection Tabs */}
              <div className="flex items-center gap-2 overflow-x-auto w-full md:w-auto">
                <span className="text-xs text-zinc-500 font-mono hidden lg:inline mr-2">INGEST EVIDENCE:</span>
                <button 
                  onClick={() => triggerIngestion("MegaCorp_Statement.csv")}
                  disabled={isIngesting}
                  className={cn(
                    "px-3 py-1.5 rounded text-xs font-mono border duration-200 flex items-center gap-1.5 whitespace-nowrap cursor-pointer",
                    selectedDoc === "MegaCorp_Statement.csv" 
                      ? "bg-zinc-900 border-zinc-800 text-zinc-100" 
                      : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-350"
                  )}
                >
                  <FileSpreadsheet className="w-3.5 h-3.5" /> Statement_Oct.csv
                </button>
                <button 
                  onClick={() => triggerIngestion("Cayman_Holdings_Reg.pdf")}
                  disabled={isIngesting}
                  className={cn(
                    "px-3 py-1.5 rounded text-xs font-mono border duration-200 flex items-center gap-1.5 whitespace-nowrap cursor-pointer",
                    selectedDoc === "Cayman_Holdings_Reg.pdf" 
                      ? "bg-zinc-900 border-zinc-800 text-zinc-100" 
                      : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-350"
                  )}
                >
                  <FileText className="w-3.5 h-3.5" /> Cayman_Holdings.pdf
                </button>
                <button 
                  onClick={() => triggerIngestion("USDT_Token_Flow.json")}
                  disabled={isIngesting}
                  className={cn(
                    "px-3 py-1.5 rounded text-xs font-mono border duration-200 flex items-center gap-1.5 whitespace-nowrap cursor-pointer",
                    selectedDoc === "USDT_Token_Flow.json" 
                      ? "bg-zinc-900 border-zinc-800 text-zinc-100" 
                      : "bg-transparent border-transparent text-zinc-500 hover:text-zinc-350"
                  )}
                >
                  <Coins className="w-3.5 h-3.5" /> Crypto_Trace.json
                </button>
              </div>
            </div>

            {/* Ingestion Scanning Overlay */}
            {isIngesting && (
              <div className="absolute inset-0 bg-black/85 z-30 flex flex-col items-center justify-center font-mono">
                <div className="max-w-md p-6 bg-zinc-950 border border-white/5 rounded-xl shadow-2xl text-center">
                  <RefreshCw className="w-9 h-9 text-slate-400 animate-spin mx-auto mb-4" />
                  <h3 className="text-xs font-semibold text-zinc-200 mb-2">Resolving Network Records</h3>
                  <div className="text-xs text-zinc-400 bg-zinc-900 p-3.5 rounded border border-white/5 text-left space-y-1.5">
                    <p className="text-slate-300 font-mono text-[11px]">{ingestionStep}</p>
                    <p className="text-zinc-600 text-[10px]">Analyzing transaction nodes with structural heuristics...</p>
                  </div>
                </div>
              </div>
            )}

            {/* Main Workspace Frame */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-6 mt-5">
              
              {/* Left Column: Realistic Investigation Context Side Panel */}
              <div className="xl:col-span-3 flex flex-col gap-4">
                <div className="border border-white/5 p-4 rounded-xl bg-[#09090b]/80 backdrop-blur-sm shadow-xl flex flex-col gap-4 relative z-20">
                  
                  {/* Case Name Section */}
                  <div>
                    <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Case Name</span>
                    <h3 className="text-sm font-semibold text-zinc-200 mt-1 font-sans">Project Apex-Delta Loop</h3>
                    <p className="text-[10px] text-zinc-400 font-mono mt-0.5">Ref: #SAR-2026-09A</p>
                  </div>

                  <div className="h-px bg-white/5" />

                  {/* Entities Identified Section */}
                  <div>
                    <div className="flex justify-between items-center text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-bold">
                      <span>Entities Identified</span>
                      <span className="text-zinc-400 font-normal">5 Mapped</span>
                    </div>
                    <div className="mt-2 space-y-1.5">
                      <div className="flex items-center justify-between text-[11px] p-2 bg-white/[0.01] border border-white/5 rounded-lg hover:bg-white/[0.03] transition-all">
                        <span className="text-zinc-300 font-sans font-medium">Apex Venture Corp</span>
                        <span className="text-[8.5px] font-mono px-1.5 py-0.5 bg-zinc-900 text-zinc-500 rounded border border-white/5">US Corp</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] p-2 bg-white/[0.01] border border-white/5 rounded-lg hover:bg-white/[0.03] transition-all">
                        <span className="text-zinc-300 font-sans font-medium">Delta Shell Holdings</span>
                        <span className="text-[8.5px] font-mono px-1.5 py-0.5 bg-zinc-900 text-zinc-500 rounded border border-white/5">Offshore</span>
                      </div>
                      <div className="flex items-center justify-between text-[11px] p-2 bg-white/[0.01] border border-white/5 rounded-lg hover:bg-white/[0.03] transition-all">
                        <span className="text-zinc-300 font-sans font-medium">Vanguard Trading</span>
                        <span className="text-[8.5px] font-mono px-1.5 py-0.5 bg-zinc-900 text-zinc-500 rounded border border-white/5">Seychelles</span>
                      </div>
                    </div>
                  </div>

                  <div className="h-px bg-white/5" />

                  {/* Evidence Sources Section */}
                  <div>
                    <div className="flex justify-between items-center text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-bold">
                      <span>Evidence Sources</span>
                      <span className="text-zinc-400 font-normal">3 Repositories</span>
                    </div>
                    <div className="mt-2 space-y-1.5">
                      <div className="flex items-center gap-2 text-xs text-zinc-400 p-1.5 hover:text-white duration-150">
                        <FileSpreadsheet className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                        <span className="truncate font-sans font-light">Statement_Oct.csv</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-zinc-400 p-1.5 hover:text-white duration-150">
                        <FileText className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                        <span className="truncate font-sans font-light">Cayman_Holdings.pdf</span>
                      </div>
                      <div className="flex items-center gap-2 text-xs text-zinc-400 p-1.5 hover:text-white duration-150">
                        <Coins className="w-3.5 h-3.5 text-zinc-500 shrink-0" />
                        <span className="truncate font-sans font-light">Crypto_Trace.json</span>
                      </div>
                    </div>
                  </div>

                  <div className="h-px bg-white/5" />

                  {/* Relationship Count Section */}
                  <div>
                    <div className="flex justify-between items-center text-[9px] font-mono text-zinc-500 uppercase tracking-widest font-bold">
                      <span>Relationship Count</span>
                    </div>
                    <div className="mt-2 flex items-baseline gap-2">
                      <span className="text-3xl font-display font-medium text-white">14</span>
                      <span className="text-xs text-zinc-400 font-sans">Traceable Vectors Linked</span>
                    </div>
                  </div>

                  <div className="h-px bg-white/5" />

                  {/* Investigation Findings Section */}
                  <div>
                    <span className="text-[9px] font-mono text-zinc-500 uppercase tracking-widest block font-bold">Investigation Findings</span>
                    <div className="mt-3 space-y-2.5">
                      <div className="flex gap-2 p-2 rounded-lg bg-white/[0.01] border border-white/5">
                        <Check className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                        <p className="text-[11px] font-sans font-light text-zinc-400 leading-normal">
                          <strong className="text-zinc-200 font-medium">Circular flow:</strong> Round-trip structure mapped returning 96% of volume.
                        </p>
                      </div>
                      <div className="flex gap-2 p-2 rounded-lg bg-white/[0.01] border border-white/5">
                        <Check className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                        <p className="text-[11px] font-sans font-light text-zinc-400 leading-normal">
                          <strong className="text-zinc-200 font-medium">Offshore links:</strong> Registrar resolved UBO match with proxy directors.
                        </p>
                      </div>
                      <div className="flex gap-2 p-2 rounded-lg bg-white/[0.01] border border-white/5">
                        <Check className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                        <p className="text-[11px] font-sans font-light text-zinc-400 leading-normal">
                          <strong className="text-zinc-200 font-medium">Structuring:</strong> Cash flows suggest smurfing beneath reporting thresholds.
                        </p>
                      </div>
                    </div>
                  </div>

                </div>
              </div>

              {/* Right Column: Premium Investigation Workspace Panel */}
              <div className="xl:col-span-9 border border-white/5 rounded-xl bg-[#080809]/95 p-5 relative min-h-[520px] flex flex-col justify-between overflow-hidden shadow-2xl z-20 backdrop-blur-md">
                
                {/* Active Segment Navigation */}
                <div className="flex bg-black/40 p-1 rounded-lg border border-white/5 w-full max-w-lg mb-4 z-10">
                  <button 
                    onClick={() => setActiveTab("graph")}
                    className={cn(
                      "flex-1 text-center py-1.5 rounded-md text-xs font-semibold font-sans transition-all cursor-pointer",
                      activeTab === "graph" ? "bg-white text-black shadow-sm" : "text-white/60 hover:text-white"
                    )}
                  >
                    Asset Flow Network
                  </button>
                  <button 
                    onClick={() => setActiveTab("copilot")}
                    className={cn(
                      "flex-1 text-center py-1.5 rounded-md text-xs font-semibold font-sans transition-all cursor-pointer flex items-center justify-center gap-1.5",
                      activeTab === "copilot" ? "bg-white text-black shadow-sm" : "text-white/60 hover:text-white"
                    )}
                  >
                    Analyst Copilot
                  </button>
                  <button 
                    onClick={() => setActiveTab("report")}
                    className={cn(
                      "flex-1 text-center py-1.5 rounded-md text-xs font-semibold font-sans transition-all cursor-pointer",
                      activeTab === "report" ? "bg-white text-black shadow-sm" : "text-white/60 hover:text-white"
                    )}
                  >
                    Investigation Report (PDF)
                  </button>
                </div>

                {/* VIEW A: GRAPH VIEW */}
                {activeTab === "graph" && (
                  <div className="relative flex-1 bg-black/20 border border-white/5 rounded-lg p-4 overflow-hidden flex flex-col justify-between min-h-[440px]">
                    
                    {/* Quiet Indicator Header */}
                    <div className="absolute top-3 left-3 z-30 text-[10px] font-mono text-zinc-400 bg-[#0e0e11]/90 px-3 py-1.5 rounded-md border border-white/5 shadow-md flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-pulse" />
                      <span>INVESTIGATION STAGE // DETERMINISTIC CAPITAL TOPOLOGY</span>
                    </div>

                    {/* Interactive Drawing Stage */}
                    <div className="relative w-full h-[360px] mt-8 flex items-center justify-center">
                      <svg className="absolute inset-0 w-full h-full pointer-events-none">
                        <defs>
                          {/* Slate directional arrows */}
                          <marker id="arrow-slate-custom" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                            <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#64748b" />
                          </marker>
                          <marker id="arrow-gold-custom" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
                            <path d="M 0 1.5 L 9 5 L 0 8.5 z" fill="#d97706" />
                          </marker>
                        </defs>

                        {/* Concentric rings to suggest structured intelligence zones */}
                        <circle cx="50%" cy="50%" r="130" fill="none" stroke="rgba(255,255,255,0.02)" strokeWidth="1" strokeDasharray="3,6" />
                        <circle cx="50%" cy="50%" r="240" fill="none" stroke="rgba(255,255,255,0.015)" strokeWidth="1" strokeDasharray="3,6" />

                        {/* Paths with arrows */}
                        
                        {/* 1. Apex (13, 38) -> Delta Shell (50, 20) */}
                        <path 
                          d="M13% 38% Q 31.5% 20% 50% 20%" 
                          fill="none" 
                          stroke="#475569" 
                          strokeWidth="1.5" 
                          strokeDasharray="4,4"
                          markerEnd="url(#arrow-slate-custom)" 
                        />
                        
                        {/* 2. Delta Shell (50, 20) -> Vanguard Seychelles (87, 38) */}
                        <path 
                          d="M50% 20% Q 68.5% 20% 87% 38%" 
                          fill="none" 
                          stroke="#475569" 
                          strokeWidth="1.5" 
                          strokeDasharray="4,4"
                          markerEnd="url(#arrow-slate-custom)" 
                        />
                        
                        {/* 3. Vanguard Seychelles (87, 38) -> Apex Corp (13, 38) (CLOSED LOOP) */}
                        <path 
                          d="M87% 38% Q 50% 64% 13% 38%" 
                          fill="none" 
                          stroke="#d97706" 
                          strokeWidth="2" 
                          className="animate-[dash_8s_linear_infinite]"
                          strokeDasharray="5,5"
                          markerEnd="url(#arrow-gold-custom)" 
                        />

                        {/* 4. Delta (50, 20) -> Crypto Mixer (72, 84) */}
                        <path 
                          d="M50% 20% Q 61% 52% 72% 84%" 
                          fill="none" 
                          stroke="#334155" 
                          strokeWidth="1.5" 
                          strokeDasharray="3,3"
                          markerEnd="url(#arrow-slate-custom)" 
                        />

                        {/* 5. Carlos Santana (28, 84) -> Apex Venture (13, 38) */}
                        <path 
                          d="M28% 84% Q 20.5% 61% 13% 38%" 
                          fill="none" 
                          stroke="#334155" 
                          strokeWidth="1.5" 
                          strokeDasharray="3,3"
                          markerEnd="url(#arrow-slate-custom)" 
                        />

                        {/* Text labels on SVG paths */}
                        <text x="31.5%" y="22%" fill="#94a3b8" fontSize="9" className="font-mono text-center" textAnchor="middle">$1.20M Wire Primary</text>
                        <text x="68.5%" y="22%" fill="#94a3b8" fontSize="9" className="font-mono text-center" textAnchor="middle">$1.18M Structured Layers</text>
                        <text x="50%" y="57%" fill="#d97706" fontSize="9" className="font-mono font-semibold text-center" textAnchor="middle">🔄 CLOSED ROUND-TRIP: $1.15M RECYCLED</text>
                        <text x="63%" y="50%" fill="#64748b" fontSize="9" className="font-mono text-center" textAnchor="middle">$450K Token Transfer</text>
                        <text x="22%" y="64%" fill="#64748b" fontSize="9" className="font-mono text-center" textAnchor="middle">$390K Physical Drops</text>
                      </svg>

                      {/* Node Entities */}
                      {Object.values(nodes).map((n) => {
                        const isSelected = selectedNode === n.id;
                        
                        return (
                          <div
                            key={n.id}
                            onClick={() => setSelectedNode(n.id)}
                            className={cn(
                              "absolute cursor-pointer p-3 rounded-xl transition-all duration-300 min-w-[150px] font-mono select-none text-left shadow-lg",
                              isSelected 
                                ? "bg-[#0b0c10] border-2 border-zinc-200 scale-105 z-20 shadow-zinc-950/80" 
                                : "bg-[#090a0d]/95 border border-white/5 text-zinc-400 hover:border-zinc-700 z-10"
                            )}
                            style={{ left: `${n.x}%`, top: `${n.y}%`, transform: 'translate(-50%, -50%)' }}
                          >
                            <div className="flex items-center justify-between gap-1">
                              <span className="text-[9px] text-zinc-500 uppercase tracking-wider">{n.type}</span>
                              <span className="text-xs">{n.flag}</span>
                            </div>
                            
                            <h4 className="font-sans font-medium text-xs text-white mt-1 truncate">{n.label}</h4>
                            
                            <div className="mt-2 flex items-center justify-between border-t border-white/5 pt-1.5 text-[9px]">
                              <span className="text-zinc-500 font-mono">{n.amount}</span>
                              <span className={cn(
                                "font-mono font-bold px-1.5 py-0.5 rounded",
                                n.risk > 80 
                                  ? "bg-zinc-850 text-zinc-300 border border-white/5" 
                                  : "bg-zinc-900 text-zinc-500"
                              )}>
                                {n.risk}% Risk
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>

                    {/* Floating Detailed Context Overlay Inspector (cornered like Palantir) */}
                    <div className="bg-[#0c0d12]/95 p-4 rounded-xl border border-white/5 text-xs font-sans absolute bottom-3 right-3 left-3 md:left-auto md:max-w-md shadow-2xl backdrop-blur-md z-30">
                      <div className="absolute top-3 right-3 flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                        <span className="text-[9px] font-mono text-zinc-500 uppercase">ACTIVE RECORD</span>
                      </div>
                      
                      <p className="text-zinc-500 uppercase tracking-widest text-[9px] font-mono font-bold">NODE DOSSIER</p>
                      
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-base">{nodes[selectedNode].flag}</span>
                        <h4 className="text-white font-semibold text-sm">
                          {nodes[selectedNode].label}
                        </h4>
                        <span className="px-2 py-0.5 rounded bg-zinc-800/80 text-[9px] font-mono text-zinc-400 border border-white/5">
                          {nodes[selectedNode].country}
                        </span>
                      </div>
                      
                      <p className="text-zinc-300 mt-2 leading-relaxed font-sans font-light text-[11px]">
                        {nodes[selectedNode].description}
                      </p>

                      <div className="mt-3 grid grid-cols-2 gap-3 border-t border-white/5 pt-2.5 text-[10px] font-mono text-zinc-500">
                        <div>
                          <p className="uppercase tracking-wider text-[8px]">Resolved UBO Profile</p>
                          <p className="text-zinc-300 font-sans mt-0.5">Parent Org: Ultimate Holding Group</p>
                        </div>
                        <div>
                          <p className="uppercase tracking-wider text-[8px]">Analytical Risk Index</p>
                          <p className="text-zinc-300 mt-0.5 font-bold font-mono">Risk Index: {nodes[selectedNode].risk / 100}</p>
                        </div>
                      </div>
                    </div>

                  </div>
                )}

                {/* VIEW B: INTEGRATED COPILET CHAT */}
                {activeTab === "copilot" && (
                  <div className="relative flex-1 bg-black/20 border border-white/5 rounded-lg p-4 flex flex-col justify-between overflow-hidden min-h-[440px]">
                    
                    {/* Chat Messages Scrolling History */}
                    <div className="flex-1 overflow-y-auto space-y-3 pr-1 text-xs max-h-[300px]">
                      {chatHistory.map((c, i) => (
                        <div 
                           key={i} 
                           className={cn(
                            "p-3 rounded-lg border leading-relaxed font-sans",
                            c.sender === 'user' 
                              ? "bg-white/[0.02] border-white/10 text-white ml-8 text-right font-light" 
                              : "bg-black/40 border-white/5 text-white/95 mr-8 text-left space-y-1.5"
                          )}
                        >
                          <div className={cn("text-[9px] font-mono text-zinc-500 mb-0.5", c.sender === "user" ? "text-right" : "text-left")}>
                            {c.sender === "ai" ? "ANALYSIS COPILOT" : "ANALYST"} • {c.timestamp}
                          </div>
                          
                          {/* Rendering Markdown formatted text cleanly */}
                          <div className="text-zinc-300 font-light prose prose-invert font-sans whitespace-pre-line text-[11.5px] leading-relaxed">
                            {c.text}
                          </div>
                        </div>
                      ))}

                      {isTyping && (
                        <div className="bg-black/40 border border-white/5 p-2.5 rounded-lg mr-8 text-left text-[10px] uppercase font-mono text-zinc-500 flex items-center gap-2">
                          <RefreshCw className="w-3.5 h-3.5 text-zinc-450 animate-spin" />
                          <span>Generating analytical intelligence report...</span>
                        </div>
                      )}
                      
                      <div ref={chatEndRef} />
                    </div>

                    {/* Prepackaged Intelligent Queries */}
                    <div className="flex flex-wrap gap-1.5 pt-2 border-t border-white/5 mt-3 z-10 bg-transparent">
                      <button 
                        onClick={() => handleSendMessage("Show accounts involved in Delta circular flow")}
                        disabled={isTyping}
                        className="text-[10px] font-mono bg-white/[0.02] border border-white/5 hover:border-white/20 hover:text-white duration-150 px-2.5 py-1.5 rounded text-zinc-400 cursor-pointer"
                      >
                        🔍 Trace Delta Loop
                      </button>
                      <button 
                        onClick={() => handleSendMessage("Analyze transaction patterns for mule Account #39281")}
                        disabled={isTyping}
                        className="text-[10px] font-mono bg-white/[0.02] border border-white/5 hover:border-white/20 hover:text-white duration-150 px-2.5 py-1.5 rounded text-zinc-400 cursor-pointer"
                      >
                        🔍 Check Nominee Mule Santana
                      </button>
                      <button 
                        onClick={() => handleSendMessage("Has high risk crypto mixing been detected in USDT file?")}
                        disabled={isTyping}
                        className="text-[10px] font-mono bg-white/[0.02] border border-white/5 hover:border-white/20 hover:text-white duration-150 px-2.5 py-1.5 rounded text-zinc-400 cursor-pointer"
                      >
                        🔍 Find Sanctioned Mixers
                      </button>
                    </div>

                    {/* Input Area */}
                    <div className="flex gap-2 mt-3 pt-3 border-t border-white/5">
                      <input 
                        type="text"
                        value={chatInput}
                        onChange={(e) => setChatInput(e.target.value)}
                        onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                        disabled={isTyping}
                        placeholder="Ask AI Copilot (e.g. Is there circular flow registered here?)..."
                        className="flex-1 bg-black/60 border border-white/5 rounded-lg px-3 py-2 text-xs font-sans text-white placeholder-zinc-600 focus:outline-none focus:border-zinc-550 duration-200"
                      />
                      <button 
                        onClick={() => handleSendMessage()}
                        disabled={isTyping}
                        className="bg-white text-black hover:bg-neutral-200 font-bold px-4 py-2 rounded-lg text-xs transition duration-200 flex items-center justify-center gap-1 cursor-pointer"
                      >
                        <Send className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                )}

                {/* VIEW C: REPORT PREVIEW VIEW */}
                {activeTab === "report" && (
                  <div className="relative flex-1 bg-black/20 border border-white/5 rounded-lg p-4 font-mono text-xs overflow-y-auto max-h-[360px] space-y-4 min-h-[440px]">
                    <div className="flex justify-between items-start border-b border-white/5 pb-3">
                      <div>
                        <span className="text-[9px] text-zinc-500">CLASSIFICATION: AUDITED INTERNAL CASE</span>
                        <h3 className="text-white font-bold text-sm font-sans">FORENSIC AUDIT RECORD #99-0128</h3>
                        <p className="text-[10px] text-zinc-400">Subject: APEX-DELTA SHELL CAPITAL DRAIN</p>
                      </div>
                      <button className="bg-white text-black font-semibold px-2.5 py-1 rounded text-[10px] hover:bg-neutral-200 duration-150 flex items-center gap-1 cursor-pointer">
                        <Download className="w-3 h-3 text-black" /> Export PDF
                      </button>
                    </div>

                    <div className="space-y-3">
                      <div className="border border-white/5 p-3 bg-black/60 rounded-xl space-y-1">
                        <span className="text-[9.5px] text-amber-500 font-bold flex items-center gap-1">
                          SECTION 1: EXECUTIVE AUDIT
                        </span>
                        <p className="text-zinc-400 text-[11px] mt-1.5 leading-relaxed font-sans font-light">
                          Our transaction neural engine resolved high-probability round-tripping layers. Apex Venture Corp routed $1.2M USD offshore to Cayman Entity 'Delta Holdings', which was laundered through crypto mixer platforms and sub-entities, returning 96% back to initiator Apex LLC.
                        </p>
                      </div>

                      <div className="border border-white/5 p-3 bg-black/60 rounded-xl space-y-2">
                        <span className="text-[9.5px] text-zinc-400 font-bold">SECTION 2: RESOLVED VECTORS</span>
                        <div className="text-[10px] space-y-1.5 text-zinc-500 font-mono">
                          <p className="text-zinc-300 flex items-center gap-2"><Check className="w-3 h-3 text-zinc-500" /> Account 0x7a84...38c9: Swapped $450,000 to anonymity nodes</p>
                          <p className="text-zinc-300 flex items-center gap-2"><Check className="w-3 h-3 text-zinc-500" /> Nominee Carlos Santana: Initiated smurfing wires totaling $390,000 USD</p>
                          <p className="text-zinc-300 flex items-center gap-2"><Check className="w-3 h-3 text-zinc-500" /> Cayman Holdings: Possesses shared director signatures with primary target</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

            </div>

            {/* Bottom Legend/Status Bar */}
            <div className="h-8 border-t border-white/5 bg-[#09090b]/90 flex items-center px-4 justify-between text-[10px] font-mono text-zinc-500 mt-5 rounded-b-xl z-30 font-light">
              <div className="flex gap-4">
                <span>STAGE: DETERMINISTIC PATH VERIFICATION COMPLETE</span>
                <span>INVESTIGATION ID: CORE-RECON-7729</span>
              </div>
              <div className="flex gap-4" id="stat-indicators">
                <span>CAPITAL INDEXED: $1,200,000</span>
                <span>UTC {new Date().toISOString().substring(11, 19)}</span>
              </div>
            </div>
            
          </div>
        </section>

        {/* Scroll Story Telling Narrative Section */}
        <section id="scroll-story" className="relative z-10 mt-28 md:mt-40 max-w-7xl mx-auto px-6 space-y-36 pb-32">
          
          {/* Section 1: Fragments */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-5 space-y-6">
              <span className="text-xs font-mono font-bold text-slate-400 tracking-widest uppercase block">// SECTION 01 // EVIDENCE</span>
              <h2 className="text-4xl md:text-5xl font-display font-medium text-balance tracking-tight leading-snug">
                Financial Investigations Start With Fragments.
              </h2>
              <p className="text-zinc-400 text-sm md:text-base font-light leading-relaxed font-sans">
                Bank statements. PDFs. Spreadsheets. Transaction exports. Investigators rarely receive complete intelligence. They receive disconnected pieces of evidence. FinIntel transforms fragmented evidence into a connected investigation.
              </p>
              <div className="pt-2">
                <Button 
                  onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                  variant="outline" 
                  className="rounded-xl border-zinc-800 text-zinc-300 hover:text-zinc-100 hover:bg-zinc-900 border"
                >
                  Start Forensic Trace
                </Button>
              </div>
            </div>
            <div className="lg:col-span-7 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 relative overflow-hidden min-h-[340px] flex flex-col justify-between shadow-2xl">
              <div className="absolute top-2 left-2 text-[10px] font-mono text-zinc-500">WORKSPACE // COMILING DISCONNECTED EVIDENCE</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mt-8">
                <div className="space-y-3">
                  <div className="p-3.5 border border-white/10 bg-white/5 rounded-xl space-y-1 hover:border-slate-400/30 duration-200">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-zinc-300 font-bold">• bank_ledger.csv</span>
                      <span className="text-[9px] text-zinc-500">14.2k items</span>
                    </div>
                    <p className="text-[10px] text-zinc-400 font-sans leading-relaxed">Raw ledger of corporate bank wire entries; unstandardized formats.</p>
                  </div>
                  <div className="p-3.5 border border-white/10 bg-white/5 rounded-xl space-y-1 hover:border-slate-400/30 duration-200">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-zinc-300 font-bold">• cayman_registry.pdf</span>
                      <span className="text-[9px] text-zinc-500">48 pgs</span>
                    </div>
                    <p className="text-[10px] text-zinc-400 font-sans leading-relaxed">Disconnected offshore beneficial ownership files; scan artifacts.</p>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="p-3.5 border border-white/10 bg-white/5 rounded-xl space-y-1 hover:border-slate-400/30 duration-200">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-zinc-300 font-bold">• transfer_audits.xlsx</span>
                      <span className="text-[9px] text-zinc-500">3 sheets</span>
                    </div>
                    <p className="text-[10px] text-zinc-400 font-sans leading-relaxed">Excel exports of sub-ledger transfers and corresponding bank audits.</p>
                  </div>
                  <div className="p-3.5 border border-white/10 bg-white/5 rounded-xl space-y-1 hover:border-slate-400/30 duration-200">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="text-zinc-300 font-bold">• wallet_sign.json</span>
                      <span className="text-[9px] text-zinc-500">45 txs</span>
                    </div>
                    <p className="text-[10px] text-zinc-400 font-sans leading-relaxed">Fragmented node records and wallet signatures with no linked identity.</p>
                  </div>
                </div>
              </div>
              <div className="mt-6 p-3 bg-white/5 rounded border border-white/10 border-dashed text-xs text-zinc-400 font-sans text-center font-light">
                📊 FinIntel transforms fragmented evidence files, ingesting and structuring them into a deterministic connected workspace.
              </div>
            </div>
          </div>

          {/* Section 2: Flow Trail */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-7 lg:order-2 space-y-6">
              <span className="text-xs font-mono font-bold text-slate-400 tracking-widest uppercase block">// SECTION 02 // EXTRACTION</span>
              <h2 className="text-4xl md:text-5xl font-display font-medium text-balance tracking-tight leading-snug">
                Every Transaction Leaves A Trail.
              </h2>
              <p className="text-zinc-400 text-sm md:text-base font-light leading-relaxed font-sans">
                Money moves through accounts, entities, businesses, and intermediaries. FinIntel reconstructs these paths automatically and reveals connections that would otherwise remain hidden.
              </p>
              <div className="space-y-2 mt-4 font-mono text-xs">
                <div className="flex items-center gap-3 text-zinc-300 py-1.5 border-b border-zinc-900">
                  <span className="w-5 h-5 rounded bg-zinc-800 text-zinc-300 flex items-center justify-center font-bold">1</span>
                  <span>Instant transaction ledger mapping</span>
                </div>
                <div className="flex items-center gap-3 text-zinc-300 py-1.5 border-b border-zinc-900">
                  <span className="w-5 h-5 rounded bg-zinc-800 text-zinc-300 flex items-center justify-center font-bold">2</span>
                  <span>Autonomous reconstruction of complex fund routes</span>
                </div>
                <div className="flex items-center gap-3 text-zinc-300 py-1.5 border-b border-zinc-900">
                  <span className="w-5 h-5 rounded bg-zinc-800 text-zinc-300 flex items-center justify-center font-bold">3</span>
                  <span>Interactive transactional vector matching</span>
                </div>
              </div>
            </div>
            <div className="lg:col-span-5 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 relative overflow-hidden min-h-[300px] flex flex-col justify-between lg:order-1 shadow-2xl">
              <div className="absolute top-2 left-2 text-[10px] font-mono text-zinc-500">GRAPH EXTRACTION // FUND FLOW SEQUENCE</div>
              
              <div className="space-y-3 font-mono text-xs mt-6">
                <div className="p-3 border border-white/10 rounded-xl bg-black/40 flex items-center justify-between hover:border-slate-400/20 duration-150">
                  <span className="text-[10px] font-bold text-zinc-300 flex items-center gap-1"><Building className="w-3.5 h-3.5" /> Apex LLC</span>
                  <span className="text-zinc-500 text-[9px]">➖➖ $1.20M Wire ➡️</span>
                  <span className="text-[10px] font-bold text-slate-300 flex items-center gap-1">Delta Cayman</span>
                </div>
                
                <div className="p-3 border border-white/10 rounded-xl bg-black/40 flex items-center justify-between hover:border-slate-400/20 duration-150">
                  <span className="text-[10px] font-bold text-slate-300 flex items-center gap-1">Delta Cayman</span>
                  <span className="text-zinc-500 text-[9px]">➖➖ $1.18M Layer ➡️</span>
                  <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1">Vanguard Trading</span>
                </div>

                <div className="p-3 border border-white/10 rounded-xl bg-black/40 flex items-center justify-between hover:border-slate-400/20 duration-150">
                  <span className="text-[10px] font-bold text-slate-400 flex items-center gap-1">Vanguard Trading</span>
                  <span className="text-zinc-500 text-[9px]">➖➖ $1.15M Equity ➡️</span>
                  <span className="text-[10px] font-bold text-zinc-300 flex items-center gap-1">Apex LLC</span>
                </div>
              </div>

              <div className="p-3 bg-white/5 rounded border border-white/10 text-xs text-zinc-300 font-sans text-center mt-6">
                🛡️ Closed round-tripping transfer loop fully mapped. Total volume of cycled capital: $1,200,000.
              </div>
            </div>
          </div>

          {/* Section 3: Graph Intelligence Centerpiece */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-5 space-y-6">
              <span className="text-xs font-mono font-bold text-slate-400 tracking-widest uppercase block">// SECTION 03 // RESOLUTION</span>
              <h2 className="text-4xl md:text-5xl font-display font-medium text-balance tracking-tight leading-snug">
                See Relationships Hidden In Plain Sight.
              </h2>
              <p className="text-zinc-400 text-sm md:text-base font-light leading-relaxed font-sans">
                What appears to be isolated activity often belongs to a larger network. FinIntel resolves entities, links accounts, and uncovers suspicious structures across entire transaction ecosystems.
              </p>
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="p-3 border border-white/10 rounded-xl hover:bg-white/5 duration-150">
                  <h4 className="text-xs font-mono font-bold text-zinc-300 uppercase">Entity Resolution</h4>
                  <p className="text-[11px] text-zinc-500 font-sans mt-1">Cross-registers nominee directories against global corporate databases.</p>
                </div>
                <div className="p-3 border border-white/10 rounded-xl hover:bg-white/5 duration-150">
                  <h4 className="text-xs font-mono font-bold text-zinc-300 uppercase">Network Unfolding</h4>
                  <p className="text-[11px] text-zinc-500 font-sans mt-1">Traces and exposes nested ultimate beneficial owners (UBO).</p>
                </div>
              </div>
            </div>
            <div className="lg:col-span-7 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 relative overflow-hidden min-h-[380px] flex flex-col justify-between shadow-2xl">
              <div className="absolute top-2 left-2 text-[10px] font-mono text-zinc-500">FORENSIC TERMINAL // STRUCTURAL RELATIONSHIP GRAPH</div>
              
              {/* Centerpiece SVG and Node Network Container */}
              <div className="relative w-full h-[240px] mt-8 border border-white/5 bg-black/40 rounded-xl overflow-hidden">
                <svg className="absolute inset-0 w-full h-full" xmlns="http://www.w3.org/2000/svg">
                  {/* Connection lines representing resolved links */}
                  <line x1="25%" y1="30%" x2="50%" y2="50%" stroke="#475569" strokeWidth="1.5" strokeDasharray="4 4" />
                  <line x1="75%" y1="30%" x2="50%" y2="50%" stroke="#475569" strokeWidth="1.5" strokeDasharray="4 4" />
                  <line x1="25%" y1="75%" x2="50%" y2="50%" stroke="#475569" strokeWidth="1.5" />
                  <line x1="75%" y1="75%" x2="50%" y2="50%" stroke="#e2e8f0" strokeWidth="1.5" strokeOpacity="0.4" strokeDasharray="4 4" />
                </svg>

                {/* Nodes on top of connection lines */}
                {/* Center Node: Delta Shell LTD (Cayman) */}
                <div className="absolute left-[50%] top-[50%] -translate-x-1/2 -translate-y-1/2 bg-zinc-950 border border-slate-400 p-2.5 rounded-lg text-center z-10 min-w-[120px] shadow-lg">
                  <p className="text-[10px] font-mono font-bold text-white font-sans">Delta Shell LTD</p>
                  <p className="text-[8px] text-slate-400 font-mono">Cayman Islands // Shell</p>
                </div>

                {/* Node Top Left: Apex Venture Corp (Holding) */}
                <div className="absolute left-[8%] top-[15%] bg-zinc-950 border border-white/10 p-2 rounded-lg z-10 min-w-[100px] shadow-md">
                  <p className="text-[9px] font-mono font-bold text-zinc-300 font-sans">Apex Venture Corp</p>
                  <p className="text-[7.5px] text-zinc-500 font-mono">US Holdings LLC</p>
                </div>

                {/* Node Top Right: Vanguard Trading */}
                <div className="absolute right-[8%] top-[15%] bg-zinc-950 border border-white/10 p-2 rounded-lg z-10 min-w-[100px] shadow-md">
                  <p className="text-[9px] font-mono font-bold text-zinc-300 font-sans">Vanguard Trading</p>
                  <p className="text-[7.5px] text-zinc-500 font-mono">Seychelles Corp</p>
                </div>

                {/* Node Bottom Left: Carlos Santana (Student) */}
                <div className="absolute left-[8%] top-[65%] bg-zinc-950 border border-white/10 p-2 rounded-lg z-10 min-w-[100px] shadow-md">
                  <p className="text-[9px] font-mono font-medium text-zinc-300 font-sans">Carlos Santana</p>
                  <p className="text-[7.5px] text-slate-400 font-mono">Mule Account #39281</p>
                </div>

                {/* Node Bottom Right: Sanctioned Mixer */}
                <div className="absolute right-[8%] top-[65%] bg-zinc-950 border border-white/15 p-2 rounded-lg z-10 min-w-[100px] shadow-lg">
                  <p className="text-[9px] font-mono font-bold text-zinc-300 font-sans">Privacy Mixer</p>
                  <p className="text-[7.5px] text-slate-400 font-mono">Sanctioned Node ERC20</p>
                </div>
              </div>

              <div className="p-3 bg-white/5 rounded border border-white/10 text-xs text-zinc-400 font-sans text-center mt-6">
                Mapped Ultimate Beneficial Ownership (UBO) structures across multiple nested shelf corporations.
              </div>
            </div>
          </div>

          {/* Section 4: Explainable Intelligence */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-12 lg:grid lg:grid-cols-12 gap-12 items-center">
              <div className="lg:col-span-7 lg:order-2 space-y-6">
                <span className="text-xs font-mono font-bold text-slate-400 tracking-widest uppercase block">// SECTION 04 // EXPLAINABILITY</span>
                <h2 className="text-4xl md:text-5xl font-display font-medium text-balance tracking-tight leading-snug">
                  Intelligence You Can Explain.
                </h2>
                <p className="text-zinc-400 text-sm md:text-base font-light leading-relaxed font-sans">
                  Investigators need evidence, not black-box predictions. Every finding is supported by traceable relationships, transaction paths, and explainable reasoning.
                </p>
                
                <div className="p-4 border border-white/10 bg-[#0A0A0A] rounded-xl font-mono text-xs max-w-xl shadow-xl space-y-3">
                  <div className="flex justify-between border-b border-white/10 pb-2 text-[10px] text-zinc-500">
                    <span>ANALYSIS OBSERVER // DELTA LOOP</span>
                    <span>CONFIDENCE INDEX: 99.1%</span>
                  </div>
                  <div className="space-y-2 text-zinc-300">
                    <p className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-zinc-400" /> Loop alert: Circular transaction pattern confirmed</p>
                    <p className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-zinc-400" /> Speed alert: Hop propagation time below 48 hours</p>
                    <p className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-zinc-400" /> Owner alert: Cayman bearer company nominee director resolved</p>
                    <p className="flex items-center gap-2"><Check className="w-3.5 h-3.5 text-red-400/80" /> Jurisdictional swap: Funds offshore routed to sanctioned mixer</p>
                  </div>
                </div>
              </div>
              
              <div className="lg:col-span-5 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 relative overflow-hidden min-h-[300px] flex flex-col justify-center lg:order-1 shadow-2xl">
                <div className="absolute top-2 left-2 text-[10px] font-mono text-zinc-500">EXPLAINABILITY DIAGNOSTIC TERMINAL</div>
                
                <div className="p-4 bg-black border border-white/10 rounded-lg shadow-inner font-mono text-xs text-zinc-300">
                  <span className="text-slate-300 font-semibold font-sans">FinIntel_Model_v3.14_Audit:</span>
                  <p className="mt-2 text-zinc-400 font-sans font-light text-[11px] leading-relaxed">
                    "Target account Carlos Santana resembles student nominee layout. 42 consecutive fiat deposits made physically below CTR limits ($9.5K median) constitute high probability structured smurfing to circumvent Bank Secrecy Act (BSA) compliance reporting."
                  </p>
                  <div className="mt-3 flex justify-between items-center text-[10px] text-zinc-500 border-t border-zinc-900 pt-2">
                    <span>Confidence: 98.42%</span>
                    <span>Class: Smurfing // Structuring</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Section 5: Report Generation */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            <div className="lg:col-span-12 lg:grid lg:grid-cols-12 gap-12 items-center">
              <div className="lg:col-span-5 space-y-6">
                <span className="text-xs font-mono font-bold text-slate-400 tracking-widest uppercase block">// SECTION 05 // REPORTING</span>
                <h2 className="text-4xl md:text-5xl font-display font-medium text-balance tracking-tight leading-snug">
                  From Investigation To Report.
                </h2>
                <p className="text-zinc-400 text-sm md:text-base font-light leading-relaxed font-sans">
                  Generate investigation-ready reports with supporting evidence, relationship diagrams, transaction analysis, and executive summaries.
                </p>
                <div className="pt-2">
                  <Button 
                    onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                    className="bg-white hover:bg-neutral-200 text-black px-6 py-5 rounded-xl text-xs flex items-center gap-1.5 duration-200 cursor-pointer font-semibold shadow-md"
                  >
                    <FileCheck className="w-4 h-4 text-black" /> Run Investigation Report (PDF)
                  </Button>
                </div>
              </div>
              
              <div className="lg:col-span-7 bg-[#0A0A0A] border border-white/10 rounded-2xl p-6 relative overflow-hidden min-h-[300px] flex flex-col justify-between shadow-2xl">
                <div className="absolute top-2 left-2 text-[10px] font-mono text-zinc-500">OFFICIAL RECONSTRUCTION REPORT PREVIEW</div>
                
                <div className="border border-white/10 bg-black/80 rounded-lg p-5 font-mono text-xs text-zinc-400 space-y-3 mt-6">
                  <div className="flex justify-between items-center border-b border-white/10 pb-2 text-[10px]">
                    <span className="font-bold text-zinc-300">FORM SAR-2026 // INVESTIGATION CASE #991</span>
                    <span className="text-zinc-500 font-semibold text-[9px] px-1.5 py-0.5 rounded bg-zinc-900 border border-white/5">VERIFIED SUBMISSION READY</span>
                  </div>
                  <div className="space-y-1.5 text-[11px] font-sans">
                    <p><b className="text-zinc-200 font-semibold font-sans">Executive Narrative Summary:</b> Traced anomalous asset round-tripping loop originating from Apex LLC US, layered through Seychelles Shell registries and bridged onto sanitized TRON digital mixer nodes.</p>
                    <p><b className="text-zinc-200 font-semibold font-sans">Resolved Transaction Volume:</b> $1,200,000 USD primary wires; $450,000 crypto OTC integration swaps.</p>
                    <p><b className="text-zinc-200 font-semibold font-sans">Linked Jurisdictions:</b> United States (origin), Cayman Islands, Seychelles, Panama.</p>
                  </div>
                  <div className="border-t border-white/10 pt-2 text-[9px] text-zinc-500 flex justify-between">
                    <span>Generated by FinIntel Core Terminal Engine</span>
                    <span>Standard Compliance Directives Met</span>
                  </div>
                </div>

                <div className="p-3.5 bg-white/5 rounded border border-white/10 text-xs text-zinc-400 font-sans text-center mt-6">
                  Our official briefings map to professional regulatory filing specs, reducing reporting timelines from days to minutes.
                </div>
              </div>
            </div>
          </div>

        </section>

        {/* Final Call To Action Section */}
        <section className="relative z-10 bg-[#050505] py-24 md:py-32 border-t border-white/10 overflow-hidden">
          <div className="absolute inset-0 pointer-events-none">
            <div className="absolute bottom-[-10%] left-1/2 -translate-x-1/2 w-[70rem] h-[30rem] rounded-full ambient-radial-glow blur-3xl opacity-30" />
          </div>

          <div className="max-w-4xl mx-auto text-center px-6 space-y-8 relative z-10">
            <h2 className="text-4xl sm:text-5xl md:text-6xl font-display font-bold tracking-tighter text-white leading-tight">
              See The Network. <br />
              Follow The Money. <br />
              Understand The Risk.
            </h2>
            <p className="text-zinc-400 text-sm sm:text-base md:text-lg max-w-2xl mx-auto font-sans font-light leading-relaxed">
              Built for forensic investigators, enterprise compliance teams, top banks, and regulatory bodies. 
              Equip your security desk with an operating system for financial crime intelligence.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row gap-4 justify-center items-center">
              {onEnterPlatform ? (
                <Button 
                  onClick={onEnterPlatform}
                  className="bg-white text-black hover:bg-neutral-200 px-8 py-6 rounded-xl text-sm font-bold shadow-lg shadow-white/5 cursor-pointer flex items-center justify-center gap-1.5"
                >
                  <span>Launch Operations Center</span>
                </Button>
              ) : (
                <Button 
                  onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                  className="bg-white text-black hover:bg-neutral-200 px-8 py-6 rounded-xl text-sm font-semibold shadow-lg shadow-white/5 cursor-pointer"
                >
                  Request Access Demo
                </Button>
              )}
              <Button 
                onClick={() => document.getElementById("workspace")?.scrollIntoView({ behavior: "smooth" })}
                variant="ghost" 
                className="px-8 py-6 border border-white/10 text-zinc-300 hover:text-white hover:bg-white/5 rounded-xl text-sm font-medium cursor-pointer"
              >
                See How It Works
              </Button>
            </div>
          </div>
        </section>

        {/* Premium Corporate Footer */}
        <footer className="relative z-10 py-12 border-t border-white/10 bg-[#050505] text-zinc-500 text-xs text-center font-mono">
          <div className="max-w-7xl mx-auto px-6 flex flex-col sm:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-2">
              <Logo className="h-4 w-auto text-zinc-300" />
              <span className="text-zinc-500 font-sans font-light">| Crime Intelligence Operating System</span>
            </div>
            <div className="flex gap-6 text-zinc-500 font-sans font-light">
              <a href="#link" className="hover:text-zinc-300 duration-150">Security Policy</a>
              <a href="#link" className="hover:text-zinc-300 duration-150">FATF Guidelines</a>
              <a href="#link" className="hover:text-zinc-300 duration-150">Terms of Service</a>
            </div>
            <div>
              <p className="text-[11px] font-sans font-light text-zinc-600">© 2026 FinIntel Corp. Confidential enterprise system.</p>
            </div>
          </div>
        </footer>

      </main>
    </>
  )
}

const menuItems = [
  { name: 'How It Works', href: '#scroll-story' },
  { name: 'Intelligence Engine', href: '#workspace' },
  { name: 'Investigations', href: '#workspace' },
  { name: 'AI Copilot', href: '#workspace' },
  { name: 'Reports', href: '#workspace' },
]

const HeroHeader = ({ onEnterPlatform }: { onEnterPlatform?: () => void }) => {
  const [menuState, setMenuState] = useState(false)
  const [isScrolled, setIsScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <header className="relative z-50">
      <nav
        data-state={menuState && 'active'}
        className="fixed z-40 w-full px-2 group mt-2"
      >
        <div className={cn(
          'mx-auto max-w-6xl transition-all duration-300 py-3 lg:py-4 px-6', 
          isScrolled 
            ? 'bg-black/90 border border-white/10 max-w-[940px] rounded-xl shadow-2xl shadow-black/80 backdrop-blur-md lg:px-6' 
            : 'bg-transparent border-transparent lg:px-12'
        )}>
          <div className="relative flex flex-wrap items-center justify-between gap-6">
            
            {/* Elegant Vector Logo */}
            <div className="flex w-full justify-between lg:w-auto">
              <a
                href="/"
                aria-label="home"
                className="flex items-center space-x-2 text-zinc-100 font-display font-bold tracking-tight text-lg"
              >
                <Logo className="text-slate-400" />
                <span className="font-semibold text-zinc-200 tracking-tight font-display">FinIntel</span>
              </a>

              {/* Mobile Menu Icon */}
              <button
                onClick={() => setMenuState(!menuState)}
                aria-label={menuState ? 'Close Menu' : 'Open Menu'}
                className="relative z-20 -m-2.5 -mr-4 block cursor-pointer p-2.5 lg:hidden text-zinc-350"
              >
                {menuState ? <X className="size-6" /> : <Menu className="size-6" />}
              </button>
            </div>

            {/* Desktop Navigation Links */}
            <div className="absolute inset-0 m-auto hidden size-fit lg:block">
              <ul className={cn(
                "flex text-xs font-mono tracking-wider uppercase text-zinc-400 font-medium transition-all duration-300",
                isScrolled ? "gap-3 lg:gap-3.5" : "gap-6 lg:gap-8"
              )}>
                {menuItems.map((item, index) => (
                  <li key={index}>
                    <a
                      href={item.href}
                      className="text-zinc-400 hover:text-zinc-200 block duration-150"
                    >
                      <span>{item.name}</span>
                    </a>
                  </li>
                ))}
              </ul>
            </div>

            {/* Desktop CTA Action Button / Mobile Drawers */}
            <div className={cn(
              "mb-6 hidden w-full flex-wrap items-center justify-end space-y-8 rounded-3xl p-6 lg:m-0 lg:flex lg:w-fit lg:gap-6 lg:space-y-0 lg:p-0",
              menuState ? "block bg-zinc-950/95 border border-zinc-800 rounded-2xl mt-4" : "hidden"
            )}>
              <div className="lg:hidden w-full">
                <ul className="space-y-6 text-sm font-mono tracking-wider uppercase text-zinc-400">
                  {menuItems.map((item, index) => (
                    <li key={index}>
                      <a
                        href={item.href}
                        onClick={() => setMenuState(false)}
                        className="text-zinc-300 hover:text-white block duration-150"
                      >
                        <span>{item.name}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="flex w-full flex-col space-y-3 sm:flex-row sm:gap-2.5 sm:space-y-0 md:w-fit mt-4 lg:mt-0 items-center">
                <Button
                  onClick={onEnterPlatform}
                  variant="outline"
                  size="sm"
                  className="w-full sm:w-auto rounded-xl border hover:bg-zinc-900 border-zinc-800 text-zinc-350 cursor-pointer text-xs"
                >
                  Request Demo
                </Button>
              </div>
            </div>

          </div>
        </div>
      </nav>
    </header>
  )
}

const Logo = ({ className }: { className?: string }) => {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn('h-5 w-auto', className)}
    >
      <path
        d="M12 2L2 7L12 12L22 7L12 2Z"
        stroke="url(#prism-logo)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M2 17L12 22L22 17"
        stroke="url(#prism-logo)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <path
        d="M2 12L12 17L22 12"
        stroke="url(#prism-logo)"
        strokeWidth="2"
        strokeLinejoin="round"
      />
      <defs>
        <linearGradient
          id="prism-logo"
          x1="2"
          y1="2"
          x2="22"
          y2="22"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#94a3b8" />
          <stop offset="1" stopColor="#475569" />
        </linearGradient>
      </defs>
    </svg>
  )
}
