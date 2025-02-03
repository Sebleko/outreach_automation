import React, { useEffect, useState } from "react";
import { useParams } from "react-router-dom";

interface Business {
  id: number;
  name: string;
  website: string;
  email: string;
  phone: string;
  address: string;
  rating: number;
  review_count: number;
  status: string;
}

const BusinessDetailPage: React.FC = () => {
  const { businessId } = useParams();
  const [business, setBusiness] = useState<Business | null>(null);

  // For outreach plan & email
  const [outreachPlan, setOutreachPlan] = useState("");
  const [emailDraft, setEmailDraft] = useState("");

  useEffect(() => {
    fetchBusiness();
  }, [businessId]);

  const fetchBusiness = async () => {
    if (!businessId) return;
    const res = await fetch(`/api/businesses/${businessId}`);
    const data = await res.json();
    setBusiness(data);
    // Potentially load the auto-generated outreach plan from server
    setOutreachPlan("Auto-generated plan: ...");
    setEmailDraft("Hello {{BusinessName}}, ...");
  };

  const approvePlan = () => {
    // Mark the plan as approved in the database
    console.log("Approving plan...");
  };

  const approveEmail = () => {
    // Mark the email as approved, ready to send
    console.log("Approving email...");
  };

  if (!business) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Business Detail: {business.name}</h1>

      <section className="border p-4 bg-white shadow">
        <h2 className="font-semibold mb-2">Basic Info</h2>
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
          <strong>Rating:</strong> {business.rating}
        </p>
        <p>
          <strong>Review Count:</strong> {business.review_count}
        </p>
      </section>

      <section className="border p-4 bg-white shadow">
        <h2 className="font-semibold mb-2">
          Business Research & Outreach Plan
        </h2>
        <label className="block mb-1 font-medium">Plan</label>
        <textarea
          className="border w-full p-2 mb-2"
          rows={3}
          value={outreachPlan}
          onChange={(e) => setOutreachPlan(e.target.value)}
        />
        <button
          className="bg-green-600 text-white px-4 py-2 rounded"
          onClick={approvePlan}
        >
          Approve Plan
        </button>
      </section>

      <section className="border p-4 bg-white shadow">
        <h2 className="font-semibold mb-2">Outreach Email</h2>
        <textarea
          className="border w-full p-2 mb-2"
          rows={5}
          value={emailDraft}
          onChange={(e) => setEmailDraft(e.target.value)}
        />
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded"
          onClick={approveEmail}
        >
          Approve Email
        </button>
      </section>

      <section className="border p-4 bg-white shadow">
        <h2 className="font-semibold mb-2">Outreach History</h2>
        {/* Show timeline of emails, statuses, etc. */}
        <p>No history yet...</p>
      </section>
    </div>
  );
};

export default BusinessDetailPage;
