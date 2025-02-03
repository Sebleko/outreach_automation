import { Routes, Route, Link } from "react-router-dom";
import SearchFlowListPage from "./pages/SearchFlowListPage";
import SearchFlowDashboard from "./pages/SearchFlowDashboard";
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
          <Route path="/" element={<SearchFlowListPage />} />
          <Route path="/flows/:flowId" element={<SearchFlowDashboard />} />
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
