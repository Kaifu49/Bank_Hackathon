import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Shield, ArrowRight, Layers, User, Lock, Eye, EyeOff } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMsg("Please enter both credentials.");
      return;
    }
    
    setIsLoading(true);
    setErrorMsg("");

    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem("finintel_auth", "true");
      navigate("/workspace");
    }, 1200);
  };

  const handleQuickLoginWillis = () => {
    setIsLoading(true);
    setErrorMsg("");
    setEmail("willis@finintel.gov");
    setPassword("••••••••••••");
    
    setTimeout(() => {
      setIsLoading(false);
      localStorage.setItem("finintel_auth", "true");
      navigate("/workspace");
    }, 1000);
  };

  return (
    <div className="min-h-screen bg-[#050505] text-white flex items-center justify-center p-6 relative overflow-hidden font-sans select-none antialiased">
      
      {/* Ambient background glows */}
      <div className="absolute top-[-100px] left-[-100px] w-[500px] h-[500px] bg-blue-900/10 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute bottom-[-100px] right-[-100px] w-[500px] h-[500px] bg-slate-900/20 rounded-full blur-[120px] pointer-events-none"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-white/5 rounded-full blur-[150px] pointer-events-none"></div>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="w-full max-w-md"
      >
        {/* Brand identity */}
        <div className="flex flex-col items-center mb-8">
          <div className="w-10 h-10 bg-white text-black rounded-xl flex items-center justify-center mb-3.5 shadow-xl border border-white/10">
            <Layers className="w-5 h-5" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-white font-display">FinIntel OS Console</h1>
          <p className="text-xs text-zinc-500 font-mono tracking-widest uppercase mt-1">Classification: Secure Access</p>
        </div>

        {/* Login Card (Glassmorphic) */}
        <div className="glass-panel rounded-2xl p-6 md:p-8 shadow-2xl relative">
          
          <div className="absolute top-3 right-4 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[9px] font-mono text-emerald-400 uppercase tracking-widest">Audit Mode Live</span>
          </div>

          <p className="text-xs text-zinc-400 font-light mb-6">
            Enter your credentials to access the forensic database and workflow engine.
          </p>

          <form onSubmit={handleLogin} className="space-y-4">
            
            {/* Email field */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Security ID (Email)</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-500">
                  <User className="w-4 h-4" />
                </div>
                <input 
                  type="email" 
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@agency.gov"
                  className="w-full bg-black/60 border border-white/10 rounded-lg pl-9 pr-4 py-2.5 text-xs text-white placeholder-zinc-650 focus:outline-none focus:border-white duration-200"
                />
              </div>
            </div>

            {/* Password field */}
            <div className="space-y-1.5">
              <label className="text-[10px] font-mono text-zinc-500 uppercase tracking-wider block">Access Passcode</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-zinc-500">
                  <Lock className="w-4 h-4" />
                </div>
                <input 
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••••••"
                  className="w-full bg-black/60 border border-white/10 rounded-lg pl-9 pr-10 py-2.5 text-xs text-white placeholder-zinc-650 focus:outline-none focus:border-white duration-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-zinc-500 hover:text-zinc-300"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {errorMsg && (
              <p className="text-[11px] text-red-400 font-medium">{errorMsg}</p>
            )}

            {/* Login button */}
            <Button
              type="submit"
              disabled={isLoading}
              className="w-full bg-white text-black hover:bg-neutral-200 font-bold py-3 rounded-lg text-xs transition duration-200 flex items-center justify-center gap-1.5 shadow-xl mt-2 cursor-pointer"
            >
              {isLoading ? (
                <span>Verifying Access Keys...</span>
              ) : (
                <>
                  <span>Decrypt Portal</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </>
              )}
            </Button>
          </form>

          {/* Quick Access Helper */}
          <div className="mt-6 pt-5 border-t border-white/5 space-y-3">
            <div className="flex items-center justify-between text-[10px] text-zinc-500 font-mono uppercase">
              <span>Quick Investigator Sign In</span>
            </div>
            
            <button
              onClick={handleQuickLoginWillis}
              disabled={isLoading}
              className="w-full p-3 bg-white/[0.02] border border-white/5 hover:bg-white/[0.04] hover:border-white/20 transition duration-200 rounded-lg text-left flex items-center justify-between group cursor-pointer"
            >
              <div className="flex items-center gap-2.5">
                <div className="w-7 h-7 rounded-full bg-[#18181B] flex items-center justify-center text-white text-[10px] font-bold">
                  AW
                </div>
                <div>
                  <p className="text-xs font-semibold text-zinc-200 group-hover:text-white">Agent Willis</p>
                  <p className="text-[9px] text-zinc-500 font-mono">AML Division • Platform level 4</p>
                </div>
              </div>
              <Shield className="w-3.5 h-3.5 text-zinc-500 group-hover:text-emerald-400 transition duration-200" />
            </button>
          </div>

        </div>

        {/* Back Link to Marketing Landing Page */}
        <div className="text-center mt-6">
          <button
            onClick={() => navigate("/")}
            className="text-[11px] text-zinc-500 hover:text-zinc-300 font-medium transition duration-150 cursor-pointer"
          >
            ← Return to public information page
          </button>
        </div>

      </motion.div>
    </div>
  );
}
