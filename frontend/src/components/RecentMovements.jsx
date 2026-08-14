import { useState } from 'react'

const PAGE_SIZE = 8

export default function RecentMovements({ movements }) {
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const visible = movements.slice(0, visibleCount)
  const hasMore = movements.length > visibleCount

  return (
    <div className="recent-movements">
      <table className="movements-table">
        <thead>
          <tr>
            <th>Tarih</th>
            <th>Malzeme</th>
            <th>Tip</th>
            <th>Miktar</th>
            <th>Tedarikçi</th>
            <th>Kullanıcı</th>
          </tr>
        </thead>
        <tbody>
          {visible.map((mv) => (
            <tr key={mv.id}>
              <td>{new Date(mv.created_at).toLocaleString('tr-TR')}</td>
              <td>{mv.material_name}</td>
              <td>
                <span className={`movement-type ${mv.movement_type}`}>
                  {mv.movement_type === 'giris' ? 'Giriş' : 'Çıkış'}
                </span>
              </td>
              <td>{mv.quantity}</td>
              <td>{mv.supplier || '—'}</td>
              <td>{mv.created_by}</td>
            </tr>
          ))}
          {movements.length === 0 && (
            <tr><td colSpan={6} className="empty-row">Henüz hareket yok</td></tr>
          )}
        </tbody>
      </table>

      {(hasMore || visibleCount > PAGE_SIZE) && (
        <div className="table-more-actions">
          {hasMore && (
            <button className="secondary-btn" onClick={() => setVisibleCount((c) => c + PAGE_SIZE)}>
              Daha Fazla Göster
            </button>
          )}
          {visibleCount > PAGE_SIZE && (
            <button className="secondary-btn" onClick={() => setVisibleCount(PAGE_SIZE)}>
              Daha Az Göster
            </button>
          )}
        </div>
      )}
    </div>
  )
}
