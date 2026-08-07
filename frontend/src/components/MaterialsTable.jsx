import { useNavigate } from 'react-router-dom'

const TREND_ICON = {
  artiyor: { symbol: '▲', className: 'trend-up', label: 'Tüketim artıyor' },
  azaliyor: { symbol: '▼', className: 'trend-down', label: 'Tüketim azalıyor' },
  sabit: { symbol: '→', className: 'trend-flat', label: 'Tüketim sabit' },
}

export default function MaterialsTable({ materials, sortBy, order, onSort }) {
  const navigate = useNavigate()

  function handleSort(column) {
    if (sortBy === column) {
      onSort(column, order === 'asc' ? 'desc' : 'asc')
    } else {
      onSort(column, 'asc')
    }
  }

  return (
    <table className="materials-table">
      <thead>
        <tr>
          <th onClick={() => handleSort('name')} className="sortable">
            Malzeme Adı {sortBy === 'name' && (order === 'asc' ? '▲' : '▼')}
          </th>
          <th onClick={() => handleSort('current_stock')} className="sortable">
            Stok Miktarı {sortBy === 'current_stock' && (order === 'asc' ? '▲' : '▼')}
          </th>
          <th>Trend</th>
          <th>Durum</th>
        </tr>
      </thead>
      <tbody>
        {materials.map((m) => {
          const trend = TREND_ICON[m.trend] || TREND_ICON.sabit
          return (
            <tr key={m.id} onClick={() => navigate(`/materials/${m.id}`)} className="clickable-row">
              <td>{m.name}</td>
              <td>{m.current_stock} {m.unit}</td>
              <td>
                <span className={`trend-badge ${trend.className}`} title={trend.label}>
                  {trend.symbol}
                </span>
              </td>
              <td>
                <span className={`status-badge ${m.status}`}>
                  {m.status === 'kritik' ? 'Kritik' : 'Normal'}
                </span>
              </td>
            </tr>
          )
        })}
        {materials.length === 0 && (
          <tr>
            <td colSpan={4} className="empty-row">Sonuç bulunamadı</td>
          </tr>
        )}
      </tbody>
    </table>
  )
}
