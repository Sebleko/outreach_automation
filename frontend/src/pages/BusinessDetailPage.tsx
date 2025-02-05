import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Business } from "../../../shared/models";

const BusinessDetailPage: React.FC = () => {
  const { businessId, flowId } = useParams();
  const [business, setBusiness] = useState<Business | null>(null);

  // --- Flow data states ---
  const [report, setReport] = useState("Auto-generated Report: ...");
  const [reportPrompt, setReportPrompt] = useState("");
  const [reportApproved, setReportApproved] = useState(false);

  const [emailDraft, setEmailDraft] = useState("Hello {{BusinessName}}, ...");
  const [emailPrompt, setEmailPrompt] = useState("");
  const [emailApproved, setEmailApproved] = useState(false);

  // For tab switching within the flow
  type FlowTab = "report" | "email";
  const [activeTab, setActiveTab] = useState<FlowTab>("report");

  useEffect(() => {
    fetchBusiness();
  }, [businessId]);

  const fetchBusiness = async () => {
    if (!businessId) return;
    const res = await fetch(`/api/businesses/${businessId}`);
    const data = await res.json();
    setBusiness(data);
    // Optionally, load generated content from your API
    // setReport(data.generatedReport);
    // setEmailDraft(data.generatedEmailDraft);
  };

  // --- Handlers for the Report tab ---
  const handleReportPromptSubmit = () => {
    // Send `reportPrompt` to your backend or AI service for amendments.
    console.log("Submitting report prompt: ", reportPrompt);
    // Clear the prompt once submitted
    setReportPrompt("");
  };

  const approveReport = () => {
    // Approve the report phase and lock it down.
    setReportApproved(true);
    console.log("Report phase approved. Proceeding to the Email stage...");
    // Automatically switch to the Email tab.
    setActiveTab("email");
  };

  // --- Handlers for the Email tab ---
  const handleEmailPromptSubmit = () => {
    console.log("Submitting email prompt: ", emailPrompt);
    setEmailPrompt("");
  };

  const polishEmail = () => {
    // Call an API or AI service to polish the email.
    console.log("Polishing the email draft...");
  };

  const approveEmail = () => {
    setEmailApproved(true);
    console.log(
      "Email phase approved. Finalizing flow (e.g., sending email)..."
    );
    // Trigger any final actions here.
  };

  if (!business) return <div>Loading...</div>;

  return (
    <div className="space-y-6 p-4">
      <h1 className="text-2xl font-bold">Business Detail: {business.name}</h1>

      {/* Basic Info Section */}
      <section className="border p-4 bg-white shadow rounded">
        <h2 className="font-semibold mb-2">Basic Info</h2>
        <p>
          <strong>Title:</strong> {business.name}
        </p>
        <p>
          <strong>Category:</strong> {business.category}
        </p>
        <p>
          <strong>Website:</strong> {business.website}
        </p>
        <p>
          <strong>Email:</strong> {business.email}
        </p>
        <p>
          <strong>Phone:</strong> {business.phone}
        </p>
        <p>
          <strong>Address:</strong> {business.address}
        </p>
        <p>
          <strong>Rating:</strong> {business.rating}
        </p>
        <p>
          <strong>Review Count:</strong> {business.review_count}
        </p>
      </section>

      {/* Flow Section */}
      {flowId && (
        <div className="p-4 bg-white shadow rounded">
          <h1 className="text-xl font-bold mb-4">Flow</h1>

          {/* Tabs */}
          <div className="flex mb-4">
            {/* Report Generation Tab */}
            <button
              onClick={() => setActiveTab("report")}
              className={`relative flex-1 py-2 text-white font-medium rounded-l 
                transition-colors duration-200 focus:outline-none
                ${activeTab === "report" ? "bg-blue-600" : "bg-blue-400"}
                ${reportApproved ? "cursor-default" : "cursor-pointer"}
              `}
              style={{
                clipPath:
                  "polygon(0 0, calc(100% - 10px) 0, 100% 50%, calc(100% - 10px) 100%, 0 100%)",
              }}
            >
              Report Generation
            </button>
            {/* Email Draft Tab */}
            <button
              onClick={() => reportApproved && setActiveTab("email")}
              className={`relative flex-1 py-2 text-white font-medium rounded-r 
                transition-colors duration-200 focus:outline-none
                ${activeTab === "email" ? "bg-blue-600" : "bg-blue-400"}
                ${
                  !reportApproved
                    ? "opacity-50 cursor-not-allowed"
                    : "cursor-pointer"
                }
              `}
              style={{
                clipPath:
                  "polygon(0 0, calc(100% - 10px) 0, 100% 50%, calc(100% - 10px) 100%, 0 100%)",
              }}
              disabled={!reportApproved}
            >
              Email Draft
            </button>
          </div>

          {/* Tab Content */}
          {activeTab === "report" && (
            <section className="p-4 bg-gray-50 rounded shadow mb-4">
              <h2 className="font-semibold mb-2">Auto-Generated Report</h2>
              {reportApproved && (
                <p className="text-green-700 font-medium mb-2">
                  Report Approved
                </p>
              )}
              {/* Read-only text area (not focusable) */}
              <textarea
                className="w-full p-2 mb-2 border rounded bg-gray-100 text-gray-700 cursor-default"
                rows={5}
                value={report}
                readOnly
                tabIndex={-1}
              />
              <label className="block mb-1 font-medium">
                Add Amendments / Prompt
              </label>
              <input
                type="text"
                className={`w-full p-2 mb-2 border rounded focus:outline-none transition-colors ${
                  reportApproved ? "bg-gray-200 cursor-not-allowed" : "bg-white"
                }`}
                value={reportPrompt}
                onChange={(e) => setReportPrompt(e.target.value)}
                disabled={reportApproved}
              />
              <div className="flex space-x-2">
                <button
                  onClick={handleReportPromptSubmit}
                  disabled={reportApproved || !reportPrompt.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Prompt
                </button>
                <button
                  onClick={approveReport}
                  disabled={reportApproved}
                  className="px-4 py-2 bg-green-600 text-white rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Approve & Continue
                </button>
              </div>
            </section>
          )}

          {activeTab === "email" && (
            <section className="p-4 bg-gray-50 rounded shadow">
              <h2 className="font-semibold mb-2">Draft Outreach Email</h2>
              {emailApproved && (
                <p className="text-green-700 font-medium mb-2">
                  Email Approved
                </p>
              )}
              <textarea
                className={`w-full p-2 mb-2 border rounded transition-colors ${
                  emailApproved ? "bg-gray-200 cursor-default" : "bg-white"
                }`}
                rows={5}
                value={emailDraft}
                onChange={(e) => setEmailDraft(e.target.value)}
                disabled={emailApproved}
              />
              <div className="flex space-x-2 mb-2">
                <button
                  onClick={polishEmail}
                  disabled={emailApproved}
                  className="px-4 py-2 bg-blue-600 text-white rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Polish Email
                </button>
                <button
                  onClick={handleEmailPromptSubmit}
                  disabled={emailApproved || !emailPrompt.trim()}
                  className="px-4 py-2 bg-blue-600 text-white rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Submit Prompt
                </button>
              </div>
              <label className="block mb-1 font-medium">
                Add Amendments / Prompt
              </label>
              <input
                type="text"
                className={`w-full p-2 mb-2 border rounded focus:outline-none transition-colors ${
                  emailApproved ? "bg-gray-200 cursor-not-allowed" : "bg-white"
                }`}
                value={emailPrompt}
                onChange={(e) => setEmailPrompt(e.target.value)}
                disabled={emailApproved}
              />
              <button
                onClick={approveEmail}
                disabled={emailApproved}
                className="px-4 py-2 bg-green-600 text-white rounded transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Approve & Continue
              </button>
            </section>
          )}
        </div>
      )}

      {/* Outreach History */}
      <section className="border p-4 bg-white shadow rounded">
        <h2 className="font-semibold mb-2">Outreach History</h2>
        {/* Timeline or list of email statuses could go here */}
        <p>No history yet...</p>
      </section>
    </div>
  );
};

export default BusinessDetailPage;
