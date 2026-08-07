export default function MovementFilters({ materials, materialId, movementType, onChange }) {
  return (
    <div className="movement-filters">
      <select value={materialId} onChange={(e) => onChange({ materialId: e.target.value, movementType })}>
        <option value="">Tüm malzemeler</option>
        {materials.map((m) => (
          <option key={m.id} value={m.id}>{m.name}</option>
        ))}
      </select>
      <select value={movementType} onChange={(e) => onChange({ materialId, movementType: e.target.value })}>
        <option value="">Tüm tipler</option>
        <option value="cikis">Çıkış</option>
        <option value="giris">Giriş</option>
      </select>
    </div>
  )
}
