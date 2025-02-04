import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";

interface Flow {
  id: number;
  name: string;
  filters: any;
  outreachTemplate: string;
}

const FlowListPage: React.FC = () => {
  const [flows, setFlows] = useState<Flow[]>([]);
  const [newFlowName, setNewFlowName] = useState("");
  const [newFlowTemplate, setNewFlowTemplate] = useState("");

  // Example simple filter object
  const [newFlowFilters, setNewFlowFilters] = useState({
    websiteRequired: true,
    minReviews: 10,
  });

  useEffect(() => {
    fetchFlows();
  }, []);

  const fetchFlows = async () => {
    const res = await fetch("/api/flows");
    res
      .json()
      .then((data) => setFlows(data))
      .catch(console.error);
  };

  const createFlow = async () => {
    try {
      const body = {
        name: newFlowName,
        filters: newFlowFilters,
        outreachTemplate: newFlowTemplate,
      };
      const res = await fetch("/api/flows", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        throw res;
      }
      // Refresh list
      fetchFlows();
      // Reset form
      setNewFlowName("");
      setNewFlowTemplate("");
    } catch (error) {
      console.error("Error creating flow", error);
    }
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Search Flows</h1>

      <div className="mb-6 border p-4">
        <h2 className="font-semibold">Create New Search Flow</h2>
        <div className="mt-2">
          <label className="block mb-1">Flow Name</label>
          <input
            type="text"
            className="border w-full p-2"
            value={newFlowName}
            onChange={(e) => setNewFlowName(e.target.value)}
          />
        </div>

        <div className="mt-2">
          <label className="block mb-1">Outreach Template</label>
          <textarea
            className="border w-full p-2"
            rows={3}
            value={newFlowTemplate}
            onChange={(e) => setNewFlowTemplate(e.target.value)}
          />
        </div>

        <div className="mt-4">
          <button
            className="bg-blue-600 text-white px-4 py-2 rounded"
            onClick={createFlow}
          >
            Save & Start Scraping
          </button>
        </div>
      </div>

      <table className="w-full bg-white border shadow">
        <thead>
          <tr className="bg-gray-100">
            <th className="p-2 text-left">Name</th>
            <th className="p-2 text-left">Template</th>
            <th className="p-2">Actions</th>
          </tr>
        </thead>
        <tbody>
          {flows.map((flow) => (
            <tr key={flow.id}>
              <td className="p-2">{flow.name}</td>
              <td className="p-2">
                {flow.outreachTemplate
                  ? flow.outreachTemplate.substring(0, 30) + "..."
                  : "None"}
              </td>
              <td className="p-2">
                <Link
                  to={`/flows/${flow.id}`}
                  className="bg-blue-500 text-white px-2 py-1 mr-2 rounded"
                >
                  View
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default FlowListPage;
