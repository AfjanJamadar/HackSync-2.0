import React, {useEffect, useRef} from "react";
import embed from "vega-embed";
import { collection, query, where, onSnapshot } from "firebase/firestore";
import { db } from "../firebaseConfig";

export default function ChartPanel({runId}){
  const ref = useRef();
  useEffect(()=>{
    if(!runId) return;
    const artsRef = collection(db, "runs", runId, "artifacts");
    const unsub = onSnapshot(artsRef, snap => {
      const charts = snap.docs.map(d => d.data()).filter(a => a.type === "chart");
      if(charts.length){
        const spec = charts[0].spec;
        embed(ref.current, spec, {actions:false});
      }
    });
    return ()=>unsub();
  }, [runId]);
  return <div className="mt-4"><h3 className="font-semibold">Charts</h3><div ref={ref} /></div>
}
