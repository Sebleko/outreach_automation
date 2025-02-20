import React, { useState, useEffect, useRef } from "react";

type TaskState = "idle" | "submitting" | "polling" | "done" | "error";

const SingleOutreach: React.FC = () => {
  const [sellerProfile, setSellerProfile] = useState("");
  const [website, setWebsite] = useState("");
  const [taskId, setTaskId] = useState<string | null>(null);
  const [finalEmail, setFinalEmail] = useState<string | null>(null);
  const [status, setStatus] = useState<TaskState>("idle");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const pollingIntervalRef = useRef<number | null>(null);

  // Submit the initial task and retrieve a taskId
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");
    setErrorMessage(null);

    try {
      console.log("Submitting outreach request...");
      const response = await fetch("/api/single-outreach", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sellerProfile, website }),
      });
      console.log("Response", response);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Submission failed");
      }

      const data = await response.json();
      console.log("Data", data);
      setTaskId(data.taskId);
      setStatus("polling");
    } catch (error: any) {
      setErrorMessage(error.message || "An error occurred");
      setStatus("error");
    }
  };

  // Poll for task status until complete
  const pollTaskStatus = async () => {
    if (!taskId) return;

    try {
      const response = await fetch(`/api/task/state?taskId=${taskId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Error checking task status");
      }
      const data = await response.json();
      // Expected data.state values: "pending", "done", "error"
      if (data.state === "done") {
        // Stop polling and fetch the final email result
        if (pollingIntervalRef.current)
          clearInterval(pollingIntervalRef.current);
        setStatus("done");
        await fetchFinalEmail();
      } else if (data.state === "error") {
        if (pollingIntervalRef.current)
          clearInterval(pollingIntervalRef.current);
        throw new Error(data.message || "Task failed");
      }
      // If still pending, continue polling...
    } catch (error: any) {
      setErrorMessage(error.message || "An error occurred during polling");
      setStatus("error");
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
    }
  };

  // Fetch the final outreach email when the task is done
  const fetchFinalEmail = async () => {
    if (!taskId) return;
    try {
      const response = await fetch(`/api/task/result?taskId=${taskId}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Error fetching result");
      }
      const data = await response.json();
      setFinalEmail(data.email);
    } catch (error: any) {
      setErrorMessage(error.message || "Error retrieving the email");
      setStatus("error");
    }
  };

  // Start polling when taskId is set and status is polling
  useEffect(() => {
    if (status === "polling" && taskId) {
      pollingIntervalRef.current = setInterval(pollTaskStatus, 1000); // Poll every second
    }
    return () => {
      if (pollingIntervalRef.current) clearInterval(pollingIntervalRef.current);
    };
  }, [status, taskId]);

  // Reset the form and state to start over
  const reset = () => {
    setSellerProfile("");
    setWebsite("");
    setTaskId(null);
    setFinalEmail(null);
    setErrorMessage(null);
    setStatus("idle");
  };

  // Copy the final email text to the clipboard
  const handleCopy = () => {
    if (finalEmail) {
      navigator.clipboard.writeText(finalEmail);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">
        Single Outreach: Generate a Personalized Outreach Email
      </h1>
      {status === "idle" && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="sellerProfile" className="block font-semibold mb-1">
              Describe your business and what you offer
            </label>
            <textarea
              id="sellerProfile"
              className="w-full border rounded p-2"
              placeholder="E.g., We offer AI-powered customer service chatbots for e-commerce businesses."
              value={sellerProfile}
              onChange={(e) => setSellerProfile(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="website" className="block font-semibold mb-1">
              Enter the website of the company you want to contact
            </label>
            <input
              type="url"
              id="website"
              className="w-full border rounded p-2"
              placeholder="https://example.com"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="bg-blue-500 text-white px-4 py-2 rounded disabled:opacity-50"
            disabled={!sellerProfile || !website}
          >
            Generate Outreach Email
          </button>
        </form>
      )}

      {(status === "submitting" || status === "polling") && (
        <div className="mt-6">
          <p className="text-lg font-medium">
            Generating your outreach email... Please wait.
          </p>
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mx-auto mt-4"></div>
        </div>
      )}

      {status === "done" && finalEmail && (
        <div className="mt-6 space-y-4">
          <h2 className="text-xl font-bold">Your Outreach Email</h2>
          <textarea
            readOnly
            className="w-full border rounded p-2"
            rows={10}
            value={finalEmail}
          />
          <div className="flex space-x-4">
            <button
              onClick={handleCopy}
              className="bg-green-500 text-white px-4 py-2 rounded"
            >
              Copy Email
            </button>
            <button
              onClick={reset}
              className="bg-gray-500 text-white px-4 py-2 rounded"
            >
              Start Over
            </button>
          </div>
        </div>
      )}

      {status === "error" && errorMessage && (
        <div className="mt-6 space-y-4">
          <p className="text-red-500 font-semibold">{errorMessage}</p>
          <button
            onClick={reset}
            className="bg-gray-500 text-white px-4 py-2 rounded"
          >
            Back to Start
          </button>
        </div>
      )}
    </div>
  );
};

export default SingleOutreach;
