import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

export default function ComparisonChart({ data, days }) {
  return (
    <section className="panel">
      <h2>Malzemeler Arası Tüketim Karşılaştırması</h2>
      <p className="panel-subtitle">Son {days} gündeki toplam tüketim — ton bazlı malzemeler (m³, adet birimli malzemeler farklı ölçekte olduğu için dahil edilmemiştir)</p>
      <ResponsiveContainer width="100%" height={280}>
        <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
          <XAxis dataKey="material_name" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} unit=" ton" />
          <Tooltip
            formatter={(value, _name, props) => [`${value} ${props.payload.unit}`, 'Tüketim']}
          />
          <Bar dataKey="total_consumption" fill="#2563eb" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </section>
  )
}
