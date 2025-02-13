import React, { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { BusinessPath, PathStatus } from "../../../shared/models";

const FlowDashboard: React.FC = () => {
  const { flowId } = useParams();
  const [flowName, setFlowName] = useState("");
  const [businessPaths, setBusinessPaths] = useState<BusinessPath[]>([]);

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
    setBusinessPaths(data);
  };

  const approveReport = async (mappingId: number) => {
    // Some API call to mark status as 'outreach_ready'
    if (!flowId) throw new Error("Flow ID not found.");

    const res = await fetch(`/api/flows/approve/${mappingId}/report`, {
      method: "PUT",
    });

    if (res.ok) {
      console.log("Report phase approved.");
    } else {
      console.error("Failed to approve report phase.");
    }
  };

  const approveEmail = async (mappingId: number) => {
    if (!flowId) throw new Error("Flow ID not found.");
    const res = await fetch(`/api/flows/approve/${mappingId}/outreach`, {
      method: "PUT",
    });

    if (res.ok) {
      console.log("Outreach phase approved.");
    } else {
      console.error("Failed to approve outreach phase.");
    }
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
          {businessPaths.map((bp) => (
            <tr key={bp.id}>
              <td className="p-2">{bp.business.name}</td>
              <td className="p-2">{bp.business.website || "N/A"}</td>
              <td className="p-2">{bp.status}</td>
              <td className="p-2">{bp.last_contacted || "Never"}</td>
              <td className="p-2">
                <Link
                  to={`/flows/${flowId}/${bp.business.id}`}
                  className="bg-blue-500 text-white px-2 py-1 mr-2 rounded"
                >
                  View
                </Link>
                {bp.status === PathStatus.AwaitingReportApproval && (
                  <button
                    className="bg-green-600 text-white px-2 py-1 rounded mr-2"
                    onClick={() => approveReport(bp.id)}
                  >
                    Approve Report
                  </button>
                )}
                {bp.status === PathStatus.AwaitingOutreachApproval && (
                  <button
                    className="bg-blue-600 text-white px-2 py-1 rounded"
                    onClick={() => approveEmail(bp.id)}
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
