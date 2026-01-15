import React, {useEffect, useState} from "react";
import { collection, query, where, onSnapshot } from "firebase/firestore";
import { db } from "../firebaseConfig";

export default function DebateView({runId, factor}){
  const [rounds, setRounds] = useState([]);
  useEffect(()=>{
    if(!runId || !factor) return;
    const roundsRef = collection(db, "runs", runId, "debates", factor.id, "rounds");
    const unsub = onSnapshot(roundsRef, snap => {
      setRounds(snap.docs.map(d => ({id:d.id, ...d.data()})));
    });
    return ()=>unsub();
  }, [runId, factor]);

  if(!factor) return <div>Select a factor to view debates</div>;
  return (
    <div className="mt-4">
      <h3 className="font-semibold">Debate — {factor.title}</h3>
      {rounds.map(r => (
        <div key={r.id} className="mt-2 p-2 border rounded">
          <div className="text-sm text-gray-700">Pro claims:</div>
          <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(r.pro, null, 2)}</pre>
          <div className="text-sm text-gray-700 mt-2">Con rebuttals:</div>
          <pre className="bg-gray-100 p-2 rounded">{JSON.stringify(r.con, null, 2)}</pre>
        </div>
      ))}
    </div>
  );
}
