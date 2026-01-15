export default function FactorList({factors, onSelect}){
  return (
    <div>
      <h3 className="font-semibold">Factors</h3>
      <div className="mt-2 space-y-2">
        {factors.map(f => (
          <div key={f.id} className="p-2 border rounded hover:bg-gray-50 cursor-pointer" onClick={()=>onSelect(f)}>
            <div className="font-medium">{f.title}</div>
            <div className="text-xs text-gray-600">{f.description}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
