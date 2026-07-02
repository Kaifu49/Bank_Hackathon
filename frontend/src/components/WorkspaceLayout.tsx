import React, { useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Shield, Layers, LogOut } from "lucide-react";

export default function WorkspaceLayout() {
  const navigate = useNavigate();
  const location = useLocation();

  // Route auth guard: redirect if not authenticated
  useEffect(() => {
    const isAuth = localStorage.getItem("finintel_auth") === "true";
    if (!isAuth) {
      navigate("/login");
    }
  }, [navigate]);

  const handleSignOut = () => {
    localStorage.removeItem("finintel_auth");
    navigate("/login");
  };

  const navItems = [
    { id: 'overview', label: 'Overview', path: '/workspace' },
    { id: 'round-trips', label: 'Round Trips', path: '/workspace/round-trips' },
    { id: 'money-flow', label: 'Money Flow', path: '/workspace/money-flow' },
    { id: 'money-trails', label: 'Money Trails', path: '/workspace/money-trails' },
    { id: 'reports', label: 'Reports', path: '/workspace/reports' },
    { id: 'settings', label: 'Settings', path: '/workspace/settings' }
  ];

  const getIsActive = (path: string) => {
    if (path === '/workspace') {
      return location.pathname === '/workspace';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <div className="workspace-root min-h-screen bg-[#FAFAFA] flex flex-col font-sans select-none antialiased text-[#18181B]">
      
      {/* Pristine Modern Top Header Navigation Bar (Stripe/Vercel Aesthetic) */}
      <nav className="h-14 bg-white border-b border-[#E4E4E7] px-6 flex items-center justify-between sticky top-0 z-50 shadow-[0_1px_2px_rgba(0,0,0,0.02)]">
        
        {/* Brand identity */}
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 bg-zinc-950 rounded-md flex items-center justify-center text-[#FAFAFA] shrink-0 shadow-xs border border-zinc-800">
            <Layers className="w-3.5 h-3.5" />
          </div>
          <div className="flex flex-col select-none">
            <span className="font-bold text-[13px] tracking-tight text-zinc-950 leading-none">FinIntel OS</span>
            <span className="text-[7.5px] font-mono font-medium uppercase tracking-[0.16em] text-zinc-500 mt-1 leading-none">Platform Level 4</span>
          </div>
        </div>

        {/* Clean horizontal nav links */}
        <div className="hidden md:flex items-center gap-1">
          {navItems.map((item) => {
            const isActive = getIsActive(item.path);
            return (
              <button
                key={item.id}
                onClick={() => navigate(item.path)}
                className={`px-4 py-1.5 rounded-md text-xs font-medium transition-colors cursor-pointer ${
                  isActive 
                    ? 'bg-[#18181B] text-white font-semibold' 
                    : 'text-[#52525B] hover:text-[#18181B] hover:bg-[#F4F4F5]'
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>

        {/* User Identity Pill & Security Badge / Sign Out */}
        <div className="flex items-center gap-4">
          <div className="hidden lg:flex items-center gap-1.5 text-xs text-[#065F46] font-medium bg-[#ECFDF5] border border-[#A7F3D0] px-2 py-0.5 rounded-full">
            <Shield className="w-3 h-3" />
            <span className="text-[10px] tracking-tight uppercase">Audit Locked</span>
          </div>
          
          <div className="flex items-center gap-3 border-l border-[#E4E4E7] pl-4">
            <div className="w-6 h-6 rounded-full bg-[#18181B] flex items-center justify-center text-white text-[10px] font-bold">
              AW
            </div>
            <div className="hidden sm:block text-left select-none leading-none">
              <p className="text-[11px] font-semibold text-[#18181B]">Agent Willis</p>
              <p className="text-[9px] text-[#71717A] mt-1">AML Division</p>
            </div>
            <button
              onClick={handleSignOut}
              className="text-[#71717A] hover:text-red-600 transition-colors p-1.5 rounded-md hover:bg-red-50 cursor-pointer ml-1"
              title="Sign Out"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile-only visible sub-navigation rail to ensure 100% responsiveness */}
      <div className="md:hidden flex items-center justify-around bg-white border-b border-[#E4E4E7] py-2 px-2 overflow-x-auto gap-2">
        {navItems.map((item) => {
          const isActive = getIsActive(item.path);
          return (
            <button
              key={item.id}
              onClick={() => navigate(item.path)}
              className={`px-3 py-1 rounded text-xs whitespace-nowrap font-medium transition-all ${
                isActive 
                  ? 'bg-[#18181B] text-white font-semibold' 
                  : 'text-[#52525B] hover:text-[#18181B]'
              }`}
            >
              {item.label}
            </button>
          );
        })}
      </div>

      {/* Content Area Rendering the Selected Workspace Module */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <div className="flex-1 overflow-y-auto">
          <Outlet />
        </div>
      </main>

    </div>
  );
}
