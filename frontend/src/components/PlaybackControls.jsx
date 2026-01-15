import React, {useState, useEffect} from "react";

export default function PlaybackControls({messages}) {
  const [playing, setPlaying] = useState(false);
  const [index, setIndex] = useState(0);
  const [speed, setSpeed] = useState(1000);

  useEffect(()=>{
    if(!playing) return;
    const id = setInterval(()=>{
      setIndex(i => {
        if(i+1 >= messages.length){
          setPlaying(false);
          return i;
        }
        return i+1;
      });
    }, speed);
    return ()=>clearInterval(id);
  }, [playing, speed, messages]);

  return (
    <div className="mt-4 p-2 border rounded">
      <div className="flex items-center space-x-4">
        <button className="px-3 py-1 bg-blue-600 text-white rounded" onClick={()=>{setPlaying(!playing); if(!playing) setIndex(0);}}>
          {playing ? "Pause" : "Play"}
        </button>
        <label>Speed ms</label>
        <input type="number" value={speed} onChange={e=>setSpeed(Number(e.target.value))} className="w-24 p-1 border rounded"/>
        <div>Index: {index}/{messages.length}</div>
      </div>
      <div className="mt-2 bg-gray-50 p-2 rounded">
        <b>{messages[index]?.role}</b>: {messages[index]?.content}
      </div>
    </div>
  );
}
