import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { BusinessPath } from "../../../shared/models";

const FlowDashboard: React.FC = () => {
  const { flowId } = useParams();
  const [flowName, setFlowName] = useState("");
  const [businesses, setBusinesses] = useState<BusinessPath[]>([]);

  useEffect(() => {
    fetchFlowDetails();
    fetchBusinesses();
  }, [flowId]);

  const fetchFlowDetails = async () => {
    if (!flowId) return;
    const res = await fetch(`/api/flows/${flowId}`);
    const data = await res.json();
    setFlowName(data.name);
  };

  const fetchBusinesses = async () => {
    if (!flowId) return;
    // Example endpoint /api/flows/:id/businesses
    const res = await fetch(`/api/flows/${flowId}/businesses`);
    const data = await res.json();
    console.log("Businesses in flow", data);
    setBusinesses(data);
  };

  const approvePlan = (mappingId: number) => {
    // Some API call to mark status as 'outreach_ready'
    console.log("Approving plan for mapping", mappingId);
  };

  const approveEmail = (mappingId: number) => {
    // Some API call to send or queue the email
    console.log("Approving email for mapping", mappingId);
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Search Flow: {flowName}</h1>
      <table className="w-full bg-white border shadow">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-2 text-left">Business Name</th>
            <th className="p-2 text-left">Website</th>
            <th className="p-2 text-left">Status</th>
            <th className="p-2 text-left">Last Contacted</th>
            <th className="p-2 text-left">Actions</th>
          </tr>
        </thead>
        <tbody>
          {businesses.map((bf) => (
            <tr key={bf.id}>
              <td className="p-2">{bf.business.name}</td>
              <td className="p-2">{bf.business.website || "N/A"}</td>
              <td className="p-2">{bf.status}</td>
              <td className="p-2">{bf.last_contacted || "Never"}</td>
              <td className="p-2">
                <Link
                  to={`/flows/${flowId}/${bf.id}`}
                  className="bg-blue-500 text-white px-2 py-1 mr-2 rounded"
                >
                  View
                </Link>
                {bf.status === "profiled" && (
                  <button
                    className="bg-green-600 text-white px-2 py-1 rounded mr-2"
                    onClick={() => approvePlan(bf.id)}
                  >
                    Approve Plan
                  </button>
                )}
                {bf.status === "outreach_ready" && (
                  <button
                    className="bg-blue-600 text-white px-2 py-1 rounded"
                    onClick={() => approveEmail(bf.id)}
                  >
                    Approve Email
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FlowDashboard;
