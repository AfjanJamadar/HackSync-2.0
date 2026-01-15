import React, { useRef } from "react";

export default function UploadDropzone({ onCreateRun }) {
  const fileRef = useRef();

  async function handleUpload(e) {
    const f = e.target.files[0];
    if (!f) return;

    // ✅ For demo: ignore real PDF content, send static text
    const dummyText = `Executive Summary: 
Between 2012 and 2018, the World Bank and IFC established the MENA MSME TA Facility...
Total WBG investments in MSME-supporting activities reached US$2.32 billion.`;

    // Call onCreateRun with static data
    onCreateRun(f, null, dummyText);
  }

  return (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700">
        Upload PDF (drag & drop)
      </label>
      <input
        ref={fileRef}
        type="file"
        accept=".pdf"
        onChange={handleUpload}
        className="mt-2"
      />
      <p className="text-xs text-gray-500 mt-2">
        Drop a World Bank evaluation PDF & press Run.
      </p>
    </div>
  );
}
