import React, { useState, useEffect, useCallback } from 'react';
import { GitFork, Loader2, AlertTriangle, HelpCircle, Copy, Calendar, ArrowRight, ArrowLeft, ChevronDown, Check } from 'lucide-react';
import { useFinintelData } from '../context/FinintelDataContext';
import { getMoneyFlow } from '../services/finintelApi';

interface NetworkNode {
  id: string;
  label: string;
  role: 'sender' | 'receiver' | 'accumulator';
  totalIn: number;
  totalOut: number;
  amountStr: string;
  desc: string;
  notes: string;
  x: number;
  y: number;
}

interface NetworkConnection {
  from: string;
  to: string;
  amount: number;
  amountStr: string;
  txn_count: number;
  first_date: string | null;
  last_date: string | null;
}

export default function MoneyFlowPage() {
  const { caseId, setCaseId, latestStatementId } = useFinintelData();

  const [nodes, setNodes] = useState<Record<string, NetworkNode>>({});
  const [connections, setConnections] = useState<NetworkConnection[]>([]);
  const [activeNodeId, setActiveNodeId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hiddenCount, setHiddenCount] = useState(0);
  const [totalNodesCount, setTotalNodesCount] = useState(0);

  // View mode state (filtering vs full network)
  const [showAllNodes, setShowAllNodes] = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [isScopeDropdownOpen, setIsScopeDropdownOpen] = useState(false);
  const [isViewDropdownOpen, setIsViewDropdownOpen] = useState(false);

  const fetchFlow = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await getMoneyFlow(caseId);
      const rawNodes = response.nodes || [];
      const rawEdges = response.edges || [];

      if (rawNodes.length === 0) {
        setNodes({});
        setConnections([]);
        setTotalNodesCount(0);
        setHiddenCount(0);
        return;
      }

      // Compute total in/out for role classification
      const computedNodes = rawNodes.map(node => {
        const id = node.id;
        const totalIn = node.total_in ?? rawEdges
          .filter(e => e.target === id)
          .reduce((sum, e) => sum + (e.total_amount ?? 0), 0);
        
        const totalOut = node.total_out ?? rawEdges
          .filter(e => e.source === id)
          .reduce((sum, e) => sum + (e.total_amount ?? 0), 0);

        let role: 'sender' | 'receiver' | 'accumulator' = 'receiver';
        if (node.is_accumulation) {
          role = 'accumulator';
        } else if (totalOut > totalIn) {
          role = 'sender';
        }

        const formattedAmt = totalIn > 0 
          ? `₹${totalIn.toLocaleString(undefined, {maximumFractionDigits:0})} Inflow`
          : `₹${totalOut.toLocaleString(undefined, {maximumFractionDigits:0})} Outflow`;

        return {
          id,
          label: node.label || id,
          role,
          totalIn,
          totalOut,
          amountStr: formattedAmt,
          desc: `Ledger account node acting as a ${role} conduit. Extracted in-flow volume is ₹${totalIn.toLocaleString()} and out-flow is ₹${totalOut.toLocaleString()}.`,
          notes: node.is_accumulation ? 'Identified accumulation sink point.' : `Active ${role} transit router.`
        };
      });

      setTotalNodesCount(computedNodes.length);

      // Filter to top 15 nodes by size if showAllNodes is false
      const maxNodes = 15;
      let finalNodes = computedNodes;
      let finalEdges = rawEdges;
      let hiddenNodesCount = 0;

      // Sort by volume so concentric circles place key hubs in the center
      const sortedNodes = [...computedNodes].sort((a, b) => (b.totalIn + b.totalOut) - (a.totalIn + a.totalOut));

      if (!showAllNodes && computedNodes.length > maxNodes) {
        const keepIds = new Set(sortedNodes.slice(0, maxNodes).map(n => n.id));
        finalNodes = computedNodes.filter(n => keepIds.has(n.id));
        finalEdges = rawEdges.filter(e => keepIds.has(e.source) && keepIds.has(e.target));
        hiddenNodesCount = computedNodes.length - maxNodes;
      }
      setHiddenCount(hiddenNodesCount);

      // Sort final nodes to keep main hubs centered in concentric shells
      const sortedFinalNodes = [...finalNodes].sort((a, b) => (b.totalIn + b.totalOut) - (a.totalIn + a.totalOut));

      // Compute dynamic concentric ellipse positions for final nodes to prevent overlapping
      const N = sortedFinalNodes.length;
      const cx = 450;
      const cy = 200;
      const nodesMap: Record<string, NetworkNode> = {};

      if (N <= 15) {
        // Standard single ellipse for clean/filtered layouts
        const rx = 310;
        const ry = 120;
        sortedFinalNodes.forEach((node, i) => {
          const angle = (2 * Math.PI * i) / N - Math.PI / 2;
          const x = cx + rx * Math.cos(angle);
          const y = cy + ry * Math.sin(angle);
          nodesMap[node.id] = { ...node, x, y };
        });
      } else {
        // Concentric shell layout for dense full network view (N > 15)
        const innerCount = Math.min(8, Math.floor(N * 0.15) + 3);
        const middleCount = Math.min(16, Math.floor(N * 0.35) + 5);
        const outerCount = N - innerCount - middleCount;

        const innerRx = 110;
        const innerRy = 55;
        
        const middleRx = 240;
        const middleRy = 105;
        
        const outerRx = 355;
        const outerRy = 145;

        sortedFinalNodes.forEach((node, i) => {
          let layerRx = outerRx;
          let layerRy = outerRy;
          let layerIdx = i;
          let layerTotal = outerCount;
          let angleOffset = 0;

          if (i < innerCount) {
            layerRx = innerRx;
            layerRy = innerRy;
            layerIdx = i;
            layerTotal = innerCount;
            angleOffset = Math.PI / 6; // offset to stagger layers visually
          } else if (i < innerCount + middleCount) {
            layerRx = middleRx;
            layerRy = middleRy;
            layerIdx = i - innerCount;
            layerTotal = middleCount;
            angleOffset = -Math.PI / 6;
          } else {
            layerRx = outerRx;
            layerRy = outerRy;
            layerIdx = i - innerCount - middleCount;
            layerTotal = outerCount;
            angleOffset = 0;
          }

          const angle = (2 * Math.PI * layerIdx) / layerTotal - Math.PI / 2 + angleOffset;
          const x = cx + layerRx * Math.cos(angle);
          const y = cy + layerRy * Math.sin(angle);
          nodesMap[node.id] = { ...node, x, y };
        });
      }

      setNodes(nodesMap);

      // Build connections with complete metadata
      const conns: NetworkConnection[] = finalEdges.map(edge => {
        return {
          from: edge.source,
          to: edge.target,
          amount: edge.total_amount ?? 0,
          amountStr: `₹${(edge.total_amount ?? 0).toLocaleString(undefined, {maximumFractionDigits:0})}`,
          txn_count: edge.txn_count ?? 1,
          first_date: edge.first_date || null,
          last_date: edge.last_date || null
        };
      });
      setConnections(conns);

      // Pick default active node
      if (sortedFinalNodes.length > 0) {
        setActiveNodeId(sortedFinalNodes[0].id);
      }
    } catch (err: any) {
      console.error(err);
      setError(err.message || "Failed to load money flow graph from gateway.");
    } finally {
      setIsLoading(false);
    }
  }, [caseId, showAllNodes]);

  useEffect(() => {
    fetchFlow();
  }, [fetchFlow]);

  const currentNode = nodes[activeNodeId] || Object.values(nodes)[0] || null;

  // Connected nodes highlighting logic
  const connectedNodeIds = new Set<string>();
  if (activeNodeId) {
    connectedNodeIds.add(activeNodeId);
    connections.forEach(conn => {
      if (conn.from === activeNodeId) connectedNodeIds.add(conn.to);
      if (conn.to === activeNodeId) connectedNodeIds.add(conn.from);
    });
  }

  // Get associated connections list for details panel
  const associatedConnections = connections.filter(
    conn => conn.from === activeNodeId || conn.to === activeNodeId
  );

  const formatCurrency = (val: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0
    }).format(val);
  };

  const N = Object.keys(nodes).length;
  // Node layout constants that scale down for large sets
  const nodeRadius = N > 15 ? 18 : 28;
  const iconScale = N > 15 ? 0.55 : 0.8;
  const selectorRadius = nodeRadius + 8;
  const labelOffset = nodeRadius + 13;
  const labelRoleOffset = nodeRadius + 21;

  return (
    <div className="max-w-7xl mx-auto px-6 py-8 space-y-8 animate-fade-in select-none">
      
      {/* Title section */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-[#E4E4E7] pb-6">
        <div className="space-y-1">
          <div className="inline-flex items-center gap-1.5 text-xs text-[#DC2626] font-semibold bg-[#FEF2F2] border border-[#FCA5A5] px-2.5 py-0.5 rounded-full font-mono">
            <GitFork className="w-3.5 h-3.5" />
            <span>Intel Ledger Mapping</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-[#18181B] font-display">Money Flow Network</h1>
          <p className="text-sm text-[#71717A] max-w-xl leading-relaxed font-sans font-light">
            Visual ledger network mapping outflows, transit shells, and final integration accumulation nodes.
          </p>
        </div>

        {/* Custom Case Scope Dropdown */}
        <div className={`relative self-start shrink-0 ${isScopeDropdownOpen ? 'z-50' : 'z-30'}`}>
          {isScopeDropdownOpen && (
            <div className="fixed inset-0 z-40" onClick={() => setIsScopeDropdownOpen(false)} />
          )}
          <button
            type="button"
            onClick={() => setIsScopeDropdownOpen(!isScopeDropdownOpen)}
            className="flex items-center justify-between gap-2.5 bg-white border border-[#E4E4E7] hover:border-zinc-400 rounded-lg p-2 px-3 text-xs font-semibold text-zinc-950 shadow-xs cursor-pointer min-w-[170px] relative transition-all"
          >
            <div className="flex items-center gap-1.5">
              <span className="text-[10px] uppercase font-bold text-[#71717A] font-mono pr-2 border-r border-[#E4E4E7]">Scope</span>
              <span className="truncate max-w-[130px] font-medium text-zinc-900">
                {caseId === 'all' 
                  ? 'Whole Network (all)' 
                  : `Current Statement (${caseId.slice(0, 8)}...)`}
              </span>
            </div>
            <ChevronDown className="w-3 h-3 text-[#71717A] ml-1" />
          </button>
          
          {isScopeDropdownOpen && (
            <div className="absolute right-0 mt-1.5 w-64 bg-white border border-[#E4E4E7] rounded-xl shadow-lg z-50 py-1.5 max-h-60 overflow-y-auto animate-fade-in">
              <button
                type="button"
                onClick={() => {
                  setCaseId('all');
                  setIsScopeDropdownOpen(false);
                }}
                className={`w-full text-left px-3.5 py-2 text-xs transition-colors flex items-center justify-between hover:bg-[#FAF9F6] ${
                  caseId === 'all' ? 'bg-zinc-50 font-bold text-[#18181B]' : 'text-zinc-700 font-light'
                }`}
              >
                <span>Whole Network (all)</span>
                {caseId === 'all' && <Check className="w-3.5 h-3.5 text-zinc-800" />}
              </button>
              
              {latestStatementId && (
                <button
                  type="button"
                  onClick={() => {
                    setCaseId(latestStatementId);
                    setIsScopeDropdownOpen(false);
                  }}
                  className={`w-full text-left px-3.5 py-2 text-xs transition-colors flex items-center justify-between hover:bg-[#FAF9F6] ${
                    caseId === latestStatementId ? 'bg-zinc-50 font-bold text-[#18181B]' : 'text-zinc-700 font-light'
                  }`}
                >
                  <span>Current Statement ({latestStatementId.slice(0, 8)}...)</span>
                  {caseId === latestStatementId && <Check className="w-3.5 h-3.5 text-zinc-800" />}
                </button>
              )}
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="h-[36rem] border border-[#E4E4E7] bg-white rounded-xl flex flex-col items-center justify-center gap-3">
          <Loader2 className="w-8 h-8 animate-spin text-zinc-800" />
          <p className="text-xs text-[#71717A] font-light">Synthesizing network topology...</p>
        </div>
      ) : error ? (
        <div className="border border-red-200 bg-red-50/50 rounded-xl p-12 text-center space-y-4 h-[36rem] flex flex-col items-center justify-center">
          <AlertTriangle className="w-10 h-10 text-red-500 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-sm font-bold text-red-950">Graph Visualization Error</h3>
            <p className="text-xs text-red-700 font-light max-w-md mx-auto">{error}</p>
          </div>
          <button
            onClick={fetchFlow}
            className="px-4 py-1.8 bg-red-950 text-white text-xs font-semibold rounded-lg hover:bg-red-900 transition-colors"
          >
            Reload Graph Data
          </button>
        </div>
      ) : Object.keys(nodes).length === 0 ? (
        <div className="border border-dashed border-[#E4E4E7] bg-white rounded-xl p-12 text-center h-[36rem] flex flex-col items-center justify-center space-y-3">
          <HelpCircle className="w-10 h-10 text-zinc-400 mx-auto" />
          <div>
            <h3 className="text-sm font-bold text-[#18181B]">No Flow Data</h3>
            <p className="text-xs text-[#71717A] font-light max-w-sm mx-auto mt-1 leading-relaxed">
              No transactions or entities found matching this scope to map out a money flow graph. Try uploading a statement first.
            </p>
          </div>
        </div>
      ) : (
        /* Primary Grid Workspace */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* Left Column: Stable SVG Canvas Board */}
          <div className="lg:col-span-8 flex flex-col space-y-3">
            
            {/* Canvas Header View Controls */}
            <div className="flex items-center justify-between bg-white border border-[#E4E4E7] rounded-xl px-4 py-2.5 shadow-xs">
              <span className="text-[10px] text-[#71717A] font-light font-sans">
                Select a node to inspect its associated flows and highlight connections.
              </span>
              
              <div className={`relative ${isViewDropdownOpen ? 'z-50' : 'z-30'}`}>
                {isViewDropdownOpen && (
                  <div className="fixed inset-0 z-40" onClick={() => setIsViewDropdownOpen(false)} />
                )}
                <button
                  type="button"
                  onClick={() => setIsViewDropdownOpen(!isViewDropdownOpen)}
                  className="flex items-center justify-between gap-1.5 bg-[#FAF9F6] border border-[#E4E4E7] hover:border-zinc-400 rounded p-1 px-2.5 text-[10px] font-semibold text-zinc-950 cursor-pointer min-w-[150px] relative transition-all"
                >
                  <div className="flex items-center gap-1">
                    <span className="text-[9px] uppercase font-bold text-[#71717A] font-mono pr-1.5 border-r border-[#E4E4E7]">View</span>
                    <span className="truncate max-w-[100px] font-medium text-zinc-900">
                      {showAllNodes ? `Full Network (${totalNodesCount} nodes)` : 'Top 15 Nodes (Clean)'}
                    </span>
                  </div>
                  <ChevronDown className="w-2.5 h-2.5 text-[#71717A] ml-0.5" />
                </button>

                {isViewDropdownOpen && (
                  <div className="absolute right-0 mt-1 w-52 bg-white border border-[#E4E4E7] rounded-lg shadow-md z-50 py-1 max-h-48 overflow-y-auto animate-fade-in">
                    <button
                      type="button"
                      onClick={() => {
                        setShowAllNodes(false);
                        setIsViewDropdownOpen(false);
                      }}
                      className={`w-full text-left px-3 py-1.5 text-[10px] transition-colors flex items-center justify-between hover:bg-[#FAF9F6] ${
                        !showAllNodes ? 'bg-zinc-50 font-bold text-[#18181B]' : 'text-zinc-700 font-light'
                      }`}
                    >
                      <span>Top 15 Nodes (Clean)</span>
                      {!showAllNodes && <Check className="w-3 h-3 text-zinc-800" />}
                    </button>

                    {(totalNodesCount > 15 || showAllNodes) && (
                      <button
                        type="button"
                        onClick={() => {
                          setShowAllNodes(true);
                          setIsViewDropdownOpen(false);
                        }}
                        className={`w-full text-left px-3 py-1.5 text-[10px] transition-colors flex items-center justify-between hover:bg-[#FAF9F6] ${
                          showAllNodes ? 'bg-zinc-50 font-bold text-[#18181B]' : 'text-zinc-700 font-light'
                        }`}
                      >
                        <span>Full Network ({totalNodesCount} nodes)</span>
                        {showAllNodes && <Check className="w-3 h-3 text-zinc-800" />}
                      </button>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Stable Canvas Board Wrapper */}
            <div className="w-full h-[36rem] bg-[#FAF9F6] rounded-xl border border-[#E4E4E7] relative overflow-hidden select-none">
              {/* Overlay warning for hidden nodes */}
              {!showAllNodes && hiddenCount > 0 && (
                <div className="absolute top-4 right-4 bg-amber-50 border border-amber-200 rounded-md px-2.5 py-1 text-[10px] text-amber-800 font-mono shadow-sm z-30">
                  Showing top 15 nodes. {hiddenCount} smaller nodes hidden from view.
                </div>
              )}

              {/* Stable SVG Canvas Board */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 900 400" preserveAspectRatio="xMidYMid meet">
                <defs>
                  {/* Connection line arrowheads (normal scale) */}
                  <marker
                    id="arrow-flow"
                    viewBox="0 0 10 10"
                    refX="33"
                    refY="5"
                    markerWidth="5"
                    markerHeight="5"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4D4D8" />
                  </marker>
                  <marker
                    id="arrow-flow-active"
                    viewBox="0 0 10 10"
                    refX="33"
                    refY="5"
                    markerWidth="5.5"
                    markerHeight="5.5"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#DC2626" />
                  </marker>

                  {/* Connection line arrowheads (small scale for concentric flow layers) */}
                  <marker
                    id="arrow-flow-small"
                    viewBox="0 0 10 10"
                    refX="23"
                    refY="5"
                    markerWidth="5"
                    markerHeight="5"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#D4D4D8" />
                  </marker>
                  <marker
                    id="arrow-flow-small-active"
                    viewBox="0 0 10 10"
                    refX="23"
                    refY="5"
                    markerWidth="5.5"
                    markerHeight="5.5"
                    orient="auto-start-reverse"
                  >
                    <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#DC2626" />
                  </marker>

                  <radialGradient id="glow" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" stopColor="#FF8A8A" />
                    <stop offset="100%" stopColor="#DC2626" />
                  </radialGradient>
                </defs>

                <g>
                  {/* Dynamic path animations */}
                  <style>{`
                    @keyframes flowingPath {
                      from { stroke-dashoffset: 24; }
                      to { stroke-dashoffset: 0; }
                    }
                    .flow-line {
                      stroke-dasharray: 6, 8;
                      animation: flowingPath 1.5s linear infinite;
                    }
                  `}</style>

                  {/* Draw connections */}
                  {connections.map((conn, idx) => {
                    const startPos = nodes[conn.from];
                    const endPos = nodes[conn.to];
                    if (!startPos || !endPos) return null;

                    const isEdgeActive = activeNodeId === conn.from || activeNodeId === conn.to;
                    const isEdgeDimmed = activeNodeId && !isEdgeActive;
                    const pathD = `M ${startPos.x} ${startPos.y} L ${endPos.x} ${endPos.y}`;

                    const midX = (startPos.x + endPos.x) / 2;
                    const midY = (startPos.y + endPos.y) / 2;

                    const markerId = N > 15
                      ? (isEdgeActive ? 'url(#arrow-flow-small-active)' : 'url(#arrow-flow-small)')
                      : (isEdgeActive ? 'url(#arrow-flow-active)' : 'url(#arrow-flow)');

                    return (
                      <g 
                        key={idx} 
                        className="transition-all duration-300"
                        style={{ opacity: isEdgeDimmed ? 0.12 : 1 }}
                      >
                        {/* Background connection track */}
                        <path 
                          d={pathD} 
                          fill="none" 
                          stroke={isEdgeActive ? '#EF4444' : '#E4E4E7'} 
                          strokeWidth={isEdgeActive ? '2.2' : '1.2'} 
                          markerEnd={markerId}
                          strokeLinecap="round"
                        />
                        
                        {/* Animated dash flow */}
                        {isEdgeActive && (
                          <path 
                            d={pathD} 
                            fill="none" 
                            stroke="#DC2626" 
                            strokeWidth="2.2" 
                            strokeDasharray="6 6"
                            className="flow-line"
                          />
                        )}

                        {/* Glowing energy pulse dot */}
                        {isEdgeActive && (
                          <circle r="3.5" fill="url(#glow)">
                            <animateMotion dur="2.2s" repeatCount="indefinite" path={pathD} />
                          </circle>
                        )}

                        {/* Edge text label container */}
                        {!isEdgeDimmed && (
                          <g transform={`translate(${midX}, ${midY})`}>
                            <rect 
                              x="-30" 
                              y="-6.5" 
                              width="60" 
                              height="13" 
                              rx="2.5" 
                              fill="#FFFFFF" 
                              stroke={isEdgeActive ? '#DC2626' : '#E4E4E7'} 
                              strokeWidth="0.8"
                              className="shadow-xs"
                            />
                            <text 
                              y="2.5" 
                              textAnchor="middle" 
                              fill={isEdgeActive ? '#991B1B' : '#71717A'} 
                              fontSize={N > 15 ? 6.5 : 7.5} 
                              fontWeight="bold"
                              className="font-mono"
                            >
                              {conn.amountStr}
                            </text>
                          </g>
                        )}
                      </g>
                    );
                  })}

                  {/* Draw Nodes */}
                  {Object.values(nodes).map((node) => {
                    const isSelected = activeNodeId === node.id;
                    const isNodeDimmed = activeNodeId && !connectedNodeIds.has(node.id);

                    const roleColor = 
                      node.role === 'sender' ? 'fill-[#EFF6FF] stroke-[#93C5FD]' : 
                      node.role === 'accumulator' ? 'fill-[#FEF2F2] stroke-[#FCA5A5]' : 
                      'fill-[#F0FDF4] stroke-[#86EFAC]';

                    const roleLabelColor = 
                      node.role === 'sender' ? 'fill-[#1D4ED8]' : 
                      node.role === 'accumulator' ? 'fill-[#DC2626]' : 
                      'fill-[#047857]';

                    // Save horizontal space by abbreviating labels even shorter in concentric mode
                    const labelText = N > 15
                      ? (node.label.length > 9 ? `${node.label.slice(0, 6)}...` : node.label)
                      : (node.label.length > 14 ? `${node.label.slice(0, 11)}...` : node.label);

                    return (
                      <g 
                        key={node.id} 
                        transform={`translate(${node.x}, ${node.y})`}
                        className="cursor-pointer select-none"
                        onClick={() => setActiveNodeId(node.id)}
                        style={{ opacity: isNodeDimmed ? 0.35 : 1, transition: 'opacity 0.3s' }}
                      >
                        {/* Spinning dashed selector circle when selected */}
                        {isSelected && (
                          <circle 
                            r={selectorRadius} 
                            fill="none" 
                            stroke="#18181B" 
                            strokeWidth="1.5" 
                            strokeDasharray="4 4" 
                            className="animate-spin" 
                            style={{ animationDuration: '8s' }} 
                          />
                        )}

                        <circle 
                          r={nodeRadius} 
                          className={`${roleColor}`} 
                          strokeWidth={isSelected ? '2.5' : '1.5'} 
                          stroke={isSelected ? '#18181B' : undefined}
                        />

                        {/* Node Icon backdrop */}
                        <circle r={nodeRadius * 0.5} fill="#FFFFFF" stroke="#E4E4E7" strokeWidth="1" />

                        {/* Embedded micro-SVGs based on node type */}
                        {(() => {
                          if (node.id.startsWith("STMT:")) {
                            return (
                              <g stroke="#4b5563" strokeWidth="1.2" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.85" transform={`scale(${iconScale})`}>
                                <path d="M -6 -9 L 2 -9 L 8 -3 L 8 9 L -6 9 Z" />
                                <path d="M 2 -9 L 2 -3 L 8 -3" />
                                <line x1="-3" y1="1" x2="4" y2="1" />
                                <line x1="-3" y1="5" x2="4" y2="5" />
                              </g>
                            );
                          } else if (node.id === "CASH") {
                            return (
                              <g stroke="#16a34a" strokeWidth="1.2" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.85" transform={`scale(${iconScale})`}>
                                <rect x="-9" y="-6" width="18" height="12" rx="1.5" />
                                <circle cx="0" cy="0" r="2.5" />
                                <path d="M -6 0 L -4 0 M 4 0 L 6 0" />
                              </g>
                            );
                          } else {
                            return (
                              <g stroke="#2563eb" strokeWidth="1.2" fill="none" strokeLinecap="round" strokeLinejoin="round" opacity="0.85" transform={`scale(${iconScale})`}>
                                <rect x="-9" y="-6" width="18" height="12" rx="1.5" />
                                <line x1="-9" y1="-2" x2="9" y2="-2" />
                                <line x1="-5" y1="2" x2="-2" y2="2" />
                                <line x1="2" y1="2" x2="5" y2="2" />
                              </g>
                            );
                          }
                        })()}

                        <text 
                          y={labelOffset} 
                          textAnchor="middle" 
                          className="fill-[#18181B] font-bold text-[8.5px] font-sans"
                          style={{ fontSize: N > 15 ? '7px' : '9px' }}
                        >
                          {labelText}
                        </text>
                        <text 
                          y={labelRoleOffset} 
                          textAnchor="middle" 
                          className={`${roleLabelColor} font-semibold text-[6.5px] uppercase tracking-wider font-mono`}
                          style={{ fontSize: N > 15 ? '5.5px' : '7px' }}
                        >
                          {node.role}
                        </text>
                      </g>
                    );
                  })}
                </g>
              </svg>
            </div>
          </div>

          {/* Right Column: Dynamic Flow Details Sidebar */}
          <div className="lg:col-span-4 bg-white border border-[#E4E4E7] rounded-xl p-5 flex flex-col space-y-4 h-[39.5rem] overflow-y-auto shadow-xs">
            
            {currentNode ? (
              <>
                {/* Node details header */}
                <div className="border-b border-[#F4F4F5] pb-4 space-y-2.5">
                  <div className="flex items-center justify-between gap-2">
                    <span className={`text-[9px] uppercase tracking-wider font-bold px-2 py-0.5 rounded font-mono ${
                      currentNode.role === 'sender' ? 'bg-blue-50 text-blue-800' :
                      currentNode.role === 'accumulator' ? 'bg-red-50 text-red-800' : 'bg-green-50 text-green-800'
                    }`}>
                      {currentNode.role} Point
                    </span>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText(currentNode.id);
                        setCopiedId(currentNode.id);
                        setTimeout(() => setCopiedId(null), 2000);
                      }}
                      className={`inline-flex items-center gap-1 text-[9px] font-semibold cursor-pointer hover:underline ${
                        copiedId === currentNode.id ? 'text-green-600 hover:text-green-700' : 'text-[#2563EB] hover:text-blue-700'
                      }`}
                    >
                      <Copy className="w-3 h-3" />
                      <span>{copiedId === currentNode.id ? 'Copied!' : 'Copy ID'}</span>
                    </button>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-bold text-[#18181B] truncate" title={currentNode.id}>
                      {currentNode.label}
                    </h3>
                    <p className="text-[10px] text-[#71717A] mt-1 font-mono break-all font-light">
                      {currentNode.id}
                    </p>
                  </div>
                  
                  <p className="text-xs text-[#52525B] leading-relaxed font-sans font-light">
                    {currentNode.desc}
                  </p>
                </div>

                {/* financial aggregate figures */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-[#F0FDF4] border border-[#DCFCE7] rounded-xl p-3 text-left">
                    <span className="text-[9px] text-[#15803D] uppercase font-bold tracking-wider font-mono block">Total Inflow</span>
                    <strong className="text-sm font-extrabold text-[#166534] font-mono mt-1 block">
                      {formatCurrency(currentNode.totalIn)}
                    </strong>
                  </div>
                  <div className="bg-[#EFF6FF] border border-[#DBEAFE] rounded-xl p-3 text-left">
                    <span className="text-[9px] text-[#1D4ED8] uppercase font-bold tracking-wider font-mono block">Total Outflow</span>
                    <strong className="text-sm font-extrabold text-[#1E40AF] font-mono mt-1 block">
                      {formatCurrency(currentNode.totalOut)}
                    </strong>
                  </div>
                </div>

                {/* Net Flow Balance Badge */}
                <div className="bg-[#FAF9F6] border border-[#E4E4E7] rounded-xl p-3.5 flex items-center justify-between">
                  <span className="text-[10px] text-[#71717A] font-semibold uppercase tracking-wider font-mono">Net Flow Volume</span>
                  <span className={`text-xs font-bold font-mono px-2 py-0.5 rounded ${
                    (currentNode.totalIn - currentNode.totalOut) >= 0 
                      ? 'bg-emerald-100 text-emerald-800' 
                      : 'bg-rose-100 text-rose-800'
                  }`}>
                    {(currentNode.totalIn - currentNode.totalOut) >= 0 ? '+' : ''}
                    {formatCurrency(currentNode.totalIn - currentNode.totalOut)}
                  </span>
                </div>

                {/* Flow Transaction directory list */}
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between border-b border-[#F4F4F5] pb-1.5">
                    <span className="text-[10px] font-bold text-[#71717A] uppercase tracking-wider font-mono">
                      Associated Transfers
                    </span>
                    <span className="text-[9px] text-[#71717A] font-mono">
                      {associatedConnections.length} connection{associatedConnections.length !== 1 ? 's' : ''}
                    </span>
                  </div>

                  <div className="space-y-2 max-h-[17.5rem] overflow-y-auto pr-1">
                    {associatedConnections.map((conn, cIdx) => {
                      const isIncoming = conn.to === activeNodeId;
                      const otherNodeId = isIncoming ? conn.from : conn.to;
                      const otherNode = nodes[otherNodeId];
                      const otherLabel = otherNode ? otherNode.label : otherNodeId;

                      return (
                        <div 
                          key={cIdx}
                          onClick={() => {
                            if (otherNodeId) {
                              setActiveNodeId(otherNodeId);
                            }
                          }}
                          className="w-full text-left p-3 rounded-lg border border-[#E4E4E7] hover:border-[#18181B] bg-[#FAF9F6] hover:bg-white transition-all text-xs flex flex-col justify-between cursor-pointer space-y-2 select-none"
                        >
                          <div className="flex items-center justify-between w-full">
                            <div className="flex items-center gap-1.5">
                              {isIncoming ? (
                                <span className="inline-flex items-center gap-1 text-[9px] font-bold uppercase font-mono px-1.5 py-0.5 bg-green-50 text-green-700 border border-green-200 rounded">
                                  <ArrowLeft className="w-2.5 h-2.5" />
                                  <span>In</span>
                                </span>
                              ) : (
                                <span className="inline-flex items-center gap-1 text-[9px] font-bold uppercase font-mono px-1.5 py-0.5 bg-blue-50 text-blue-700 border border-blue-200 rounded">
                                  <ArrowRight className="w-2.5 h-2.5" />
                                  <span>Out</span>
                                </span>
                              )}
                              <span className="font-bold text-[#18181B] truncate max-w-[130px]" title={otherNodeId}>
                                {otherLabel}
                              </span>
                            </div>
                            <span className="text-[10px] font-bold text-[#18181B] font-mono">
                              {conn.amountStr}
                            </span>
                          </div>

                          <div className="flex items-center justify-between text-[9px] text-[#71717A] font-mono">
                            <span className="flex items-center gap-1">
                              <span>Txns:</span>
                              <span className="font-bold text-[#52525B]">{conn.txn_count}</span>
                            </span>
                            {conn.first_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-2.5 h-2.5" />
                                <span>{conn.first_date.slice(2)} to {conn.last_date?.slice(2) || 'N/A'}</span>
                              </span>
                            )}
                          </div>
                        </div>
                      );
                    })}

                    {associatedConnections.length === 0 && (
                      <p className="text-[11px] text-[#71717A] font-light text-center py-6">
                        No direct ledger connections mapped to this node.
                      </p>
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-center space-y-2">
                <HelpCircle className="w-8 h-8 text-zinc-300" />
                <p className="text-xs text-[#71717A] font-light">Select a node in the graph workspace to analyze flow aggregates.</p>
              </div>
            )}

          </div>

        </div>
      )}

    </div>
  );
}
