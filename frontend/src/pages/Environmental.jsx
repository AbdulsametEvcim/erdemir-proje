import { useEffect, useState } from 'react'
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import api from '../api'
import Layout from '../components/Layout'
import { Spinner } from '../components/Loading'

export default function Environmental() {
  const [data, setData] = useState(null)
  const [days, setDays] = useState(30)

  useEffect(() => {
    api.get('/environmental/summary', { params: { days } }).then((res) => setData(res.data))
  }, [days])

  if (!data) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  const chartData = data.items.map((i) => ({ ...i, total_co2_ton: Math.round((i.total_co2_kg / 1000) * 100) / 100 }))
  const topImpact = [...data.items].sort((a, b) => b.total_co2_kg - a.total_co2_kg)[0]

  return (
    <Layout>
      <h2>Çevresel Etki</h2>
      <p className="panel-subtitle">
        Malzeme tüketimine bağlı tahmini karbon salımı — sektör ortalamalarına dayalı kaba bir yaklaşımdır, ölçülmüş değer değildir.
      </p>

      <div className="summary-cards">
        <div className="summary-card eco">
          <div className="summary-card-value">{data.total_co2_ton.toLocaleString('tr-TR')} ton</div>
          <div className="summary-card-label">Tahmini Toplam CO₂ (son {data.days} gün)</div>
        </div>
        <div className="summary-card">
          <div className="summary-card-value">{topImpact ? topImpact.material_name : '-'}</div>
          <div className="summary-card-label">En Yüksek Etkili Malzeme</div>
        </div>
        <div className="summary-card">
          <div className="summary-card-value">{data.items.length}</div>
          <div className="summary-card-label">İzlenen Malzeme</div>
        </div>
      </div>

      <section className="panel">
        <div className="panel-header">
          <h2>Malzeme Bazlı Tahmini CO₂ Emisyonu</h2>
          <div className="panel-actions">
            <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
              <option value={7}>Son 7 gün</option>
              <option value={30}>Son 30 gün</option>
              <option value={90}>Son 90 gün</option>
            </select>
          </div>
        </div>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis dataKey="material_name" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} unit=" ton" />
            <Tooltip formatter={(value) => [`${value} ton CO₂`, 'Tahmini Emisyon']} />
            <Bar dataKey="total_co2_ton" fill="#16a34a" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </section>

      <section className="panel">
        <h2>Detaylar</h2>
        <table>
          <thead>
            <tr>
              <th>Malzeme</th>
              <th>Tüketim (son {data.days} gün)</th>
              <th>Emisyon Faktörü</th>
              <th>Tahmini CO₂</th>
            </tr>
          </thead>
          <tbody>
            {data.items.map((i) => (
              <tr key={i.material_id}>
                <td>{i.material_name}</td>
                <td>{i.total_consumption} {i.unit}</td>
                <td>{i.co2_factor} kg/{i.unit}</td>
                <td>{(i.total_co2_kg / 1000).toFixed(2)} ton</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </Layout>
  )
}
