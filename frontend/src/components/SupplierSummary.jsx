export default function SupplierSummary({ suppliers }) {
  return (
    <section className="panel">
      <h2>Tedarikçi Özeti</h2>
      <table>
        <thead>
          <tr>
            <th>Tedarikçi</th>
            <th>Teslimat Sayısı</th>
            <th>Son Teslimat</th>
            <th>Malzemeler</th>
          </tr>
        </thead>
        <tbody>
          {suppliers.map((s) => (
            <tr key={s.supplier}>
              <td>{s.supplier}</td>
              <td>{s.deliveries}</td>
              <td>{new Date(s.last_delivery).toLocaleDateString('tr-TR')}</td>
              <td>
                {s.materials.map((m) => `${m.material_name}: ${m.total_quantity} ${m.unit}`).join(', ')}
              </td>
            </tr>
          ))}
          {suppliers.length === 0 && (
            <tr><td colSpan={4} className="empty-row">Henüz tedarikçi kaydı yok</td></tr>
          )}
        </tbody>
      </table>
    </section>
  )
}
