export default function LiveLogs({messages}){
  return (
    <div className="mb-4">
      <h3 className="font-semibold">Live Debate Log</h3>
      <div className="mt-2 h-48 overflow-auto p-2 border rounded bg-gray-50">
        {messages.map(m => (
          <div key={m.createdAt?.seconds || m.id} className="mb-2">
            <b className="text-sm">{m.role}</b>: <span className="text-sm">{m.content}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
