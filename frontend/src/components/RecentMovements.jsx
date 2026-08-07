export default function RecentMovements({ movements }) {
  return (
    <div className="recent-movements">
      <table className="movements-table">
        <thead>
          <tr>
            <th>Tarih</th>
            <th>Malzeme</th>
            <th>Tip</th>
            <th>Miktar</th>
            <th>Kullanıcı</th>
          </tr>
        </thead>
        <tbody>
          {movements.map((mv) => (
            <tr key={mv.id}>
              <td>{new Date(mv.created_at).toLocaleString('tr-TR')}</td>
              <td>{mv.material_name}</td>
              <td>
                <span className={`movement-type ${mv.movement_type}`}>
                  {mv.movement_type === 'giris' ? 'Giriş' : 'Çıkış'}
                </span>
              </td>
              <td>{mv.quantity}</td>
              <td>{mv.created_by}</td>
            </tr>
          ))}
          {movements.length === 0 && (
            <tr><td colSpan={5} className="empty-row">Henüz hareket yok</td></tr>
          )}
        </tbody>
      </table>
    </div>
  )
}
