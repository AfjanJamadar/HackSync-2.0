// src/App.jsx
import React, { useState } from "react";
import UploadDropzone from "./components/UploadDropzone";
import LiveLogs from "./components/LiveLogs";
import FactorList from "./components/FactorList";
import DebateView from "./components/DebateView";
import ChartPanel from "./components/ChartPanel";
import PlaybackControls from "./components/PlaybackControls";

export default function App() {
  const [runId, setRunId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [factors, setFactors] = useState([]);
  const [selectedFactor, setSelectedFactor] = useState(null);

  // ✅ Dummy data for demo
  const dummyFactors = [
    { id: "factor1", name: "Access to Finance", description: "MSME financing availability" },
    { id: "factor2", name: "Gender Inclusion", description: "Women-led MSMEs" },
  ];

  const dummyMessages = [
    { id: "msg1", actor: "Extractor", message: "PDF processed and key factors identified." },
    { id: "msg2", actor: "Pro", message: "Pro arguments added for Access to Finance." },
    { id: "msg3", actor: "Con", message: "Con arguments added for Access to Finance." },
    { id: "msg4", actor: "Synth", message: "Synthesis completed for all factors." },
  ];

  async function createRun(pdfFile, csvFile, text) {
    // For demo: skip backend, just show static data
    setRunId("demo-run-1");
    setFactors(dummyFactors);
    setMessages(dummyMessages);
    setSelectedFactor(dummyFactors[0]);
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <header className="mb-4">
        <h1 className="text-3xl font-bold">AETHER — Live Policy Deliberation</h1>
        <p className="text-sm text-gray-600">Multi-agent debate (Gemini) • Verifiable evidence ledger</p>
      </header>

      <div className="grid grid-cols-3 gap-4">
        <div className="col-span-1 bg-white p-4 rounded shadow">
          <UploadDropzone onCreateRun={createRun} />
          <FactorList factors={factors} onSelect={setSelectedFactor} />
        </div>

        <div className="col-span-2 bg-white p-4 rounded shadow">
          <LiveLogs messages={messages} />
          <DebateView runId={runId} factor={selectedFactor} />
          <ChartPanel runId={runId} />
          <PlaybackControls messages={messages} />
        </div>
      </div>
    </div>
  );
}
