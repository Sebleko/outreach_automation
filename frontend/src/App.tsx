import { Routes, Route, Link } from "react-router-dom";
import FlowListPage from "./pages/FlowListPage";
import FlowDashboard from "./pages/FlowDashboard";
import BusinessDetailPage from "./pages/BusinessDetailPage";

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-800">
      <nav className="bg-white shadow p-4 mb-4">
        <div className="container mx-auto">
          <Link to="/" className="text-xl font-bold">
            Business Outreach
          </Link>
        </div>
      </nav>

      <div className="container mx-auto">
        <Routes>
          <Route path="/" element={<FlowListPage />} />
          <Route path="/flows/:flowId" element={<FlowDashboard />} />
          <Route
            path="/flows/:flowId/:businessId"
            element={<BusinessDetailPage />}
          />
          <Route
            path="/business/:businessId"
            element={<BusinessDetailPage />}
          />
        </Routes>
      </div>
    </div>
  );
}

export default App;
