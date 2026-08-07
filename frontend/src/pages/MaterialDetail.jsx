import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import api from '../api'
import Layout from '../components/Layout'
import EditMaterialForm from '../components/EditMaterialForm'
import ConfirmModal from '../components/ConfirmModal'
import { Spinner } from '../components/Loading'
import { useToast } from '../components/Toast'

export default function MaterialDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [analysis, setAnalysis] = useState(null)
  const [error, setError] = useState('')
  const [editing, setEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const showToast = useToast()

  function loadAnalysis() {
    api.get(`/materials/${id}/analysis`)
      .then((res) => setAnalysis(res.data))
      .catch(() => setError('Malzeme verisi yüklenemedi'))
  }

  useEffect(() => {
    loadAnalysis()
  }, [id])

  async function handleDelete() {
    setDeleting(true)
    try {
      await api.delete(`/materials/${id}`)
      showToast(`"${analysis.material_name}" silindi`, 'success')
      navigate('/')
    } catch {
      showToast('Malzeme silinemedi', 'error')
      setConfirmingDelete(false)
      setDeleting(false)
    }
  }

  if (error) {
    return (
      <Layout>
        <p>{error}</p>
      </Layout>
    )
  }

  if (!analysis) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  const isCritical = analysis.current_stock <= analysis.critical_threshold

  return (
    <Layout>
      <button className="back-link" onClick={() => navigate('/')}>← Dashboard'a dön</button>

      <div className="detail-header">
        <h2>{analysis.material_name}</h2>
        <span className={`status-badge ${isCritical ? 'kritik' : 'normal'}`}>
          {isCritical ? 'Kritik' : 'Normal'}
        </span>
        <div className="detail-header-actions">
          <button className="secondary-btn" onClick={() => setEditing((v) => !v)}>Düzenle</button>
          <button className="danger-btn" onClick={() => setConfirmingDelete(true)} disabled={deleting}>
            {deleting ? 'Siliniyor...' : 'Sil'}
          </button>
        </div>
      </div>

      {confirmingDelete && (
        <ConfirmModal
          title="Malzemeyi sil"
          message={`"${analysis.material_name}" malzemesini silmek istediğine emin misin? Bu işlem geri alınamaz.`}
          onConfirm={handleDelete}
          onCancel={() => setConfirmingDelete(false)}
          loading={deleting}
        />
      )}

      {editing && (
        <EditMaterialForm
          material={analysis}
          onSaved={() => {
            setEditing(false)
            loadAnalysis()
          }}
          onCancel={() => setEditing(false)}
        />
      )}

      <div className="summary-cards">
        <div className="summary-card">
          <div className="summary-card-value">{analysis.current_stock} {analysis.unit}</div>
          <div className="summary-card-label">Mevcut Stok</div>
        </div>
        <div className="summary-card">
          <div className="summary-card-value">{analysis.critical_threshold} {analysis.unit}</div>
          <div className="summary-card-label">Kritik Eşik</div>
        </div>
        <div className="summary-card">
          <div className="summary-card-value">{analysis.avg_daily_consumption} {analysis.unit}/gün</div>
          <div className="summary-card-label">Ortalama Günlük Tüketim</div>
        </div>
      </div>

      <div className={`forecast-box ${isCritical ? 'danger' : ''}`}>
        {analysis.forecast_message}
      </div>

      <section className="panel">
        <h2>Son 90 Günlük Tüketim Grafiği</h2>
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={analysis.daily_consumption}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
              interval={Math.floor(analysis.daily_consumption.length / 8)}
            />
            <YAxis tick={{ fontSize: 11 }} unit={` ${analysis.unit}`} />
            <Tooltip />
            <Line type="monotone" dataKey="quantity" stroke="#2563eb" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </section>
    </Layout>
  )
}
