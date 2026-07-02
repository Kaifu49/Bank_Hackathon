import { Routes, Route, useNavigate } from "react-router-dom";
import { Demo } from "@/components/ui/demo";
import LoginPage from "./components/LoginPage";
import WorkspaceLayout from "./components/WorkspaceLayout";
import OverviewPage from "./components/OverviewPage";
import MoneyFlowPage from "./components/MoneyFlowPage";
import RoundTripsPage from "./components/RoundTripsPage";
import MoneyTrailPage from "./components/MoneyTrailPage";
import ReportsPage from "./components/ReportsPage";
import SettingsPage from "./components/SettingsPage";
import { FinintelDataProvider } from "./context/FinintelDataContext";

export default function App() {
  const navigate = useNavigate();

  const handleEnterPlatform = () => {
    const isAuth = localStorage.getItem("finintel_auth") === "true";
    if (isAuth) {
      navigate("/workspace");
    } else {
      navigate("/login");
    }
  };

  return (
    <FinintelDataProvider>
      <Routes>
        {/* Public Landing Page */}
        <Route path="/" element={
          <div id="app-root" className="min-h-screen bg-[#050505] antialiased">
            <Demo onEnter={handleEnterPlatform} />
          </div>
        } />

        {/* Authentication Layer */}
        <Route path="/login" element={<LoginPage />} />

        {/* Authenticated Workspace */}
        <Route path="/workspace" element={<WorkspaceLayout />}>
          <Route index element={<OverviewPage onNavigateToView={(view) => navigate(`/workspace/${view}`)} />} />
          <Route path="round-trips" element={<RoundTripsPage onNavigateToView={(view) => navigate(`/workspace/${view}`)} />} />
          <Route path="money-flow" element={<MoneyFlowPage />} />
          <Route path="money-trails" element={<MoneyTrailPage />} />
          <Route path="reports" element={<ReportsPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>

        {/* Fallback Redirect */}
        <Route path="*" element={<LoginPage />} />
      </Routes>
    </FinintelDataProvider>
  );
}
