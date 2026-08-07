export default function SummaryCards({ summary }) {
  if (!summary) return null

  const cards = [
    { label: 'Toplam Malzeme', value: summary.total_materials },
    { label: 'Kritik Malzeme', value: summary.critical_materials, danger: summary.critical_materials > 0 },
    { label: 'Son 7 Günde Toplam Tüketim', value: `${summary.total_consumption_7d} ton` },
  ]

  return (
    <div className="summary-cards">
      {cards.map((c) => (
        <div key={c.label} className={`summary-card ${c.danger ? 'danger' : ''}`}>
          <div className="summary-card-value">{c.value}</div>
          <div className="summary-card-label">{c.label}</div>
        </div>
      ))}
    </div>
  )
}
