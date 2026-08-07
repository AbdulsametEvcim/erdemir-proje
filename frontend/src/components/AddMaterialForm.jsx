import { useState } from 'react'
import api from '../api'
import { useToast } from './Toast'

export default function AddMaterialForm({ onSaved, onCancel }) {
  const [name, setName] = useState('')
  const [unit, setUnit] = useState('ton')
  const [currentStock, setCurrentStock] = useState('')
  const [criticalThreshold, setCriticalThreshold] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const showToast = useToast()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!name || currentStock === '' || criticalThreshold === '') {
      setError('Tüm alanlar zorunludur')
      return
    }
    setSaving(true)
    try {
      await api.post('/materials', {
        name,
        unit,
        current_stock: Number(currentStock),
        critical_threshold: Number(criticalThreshold),
      })
      showToast(`"${name}" malzemesi eklendi`, 'success')
      onSaved()
    } catch (err) {
      const message = err.response?.data?.detail || 'Malzeme eklenemedi'
      setError(message)
      showToast(message, 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="movement-form" onSubmit={handleSubmit}>
      <h3>Yeni Malzeme Ekle</h3>
      <div className="movement-form-row">
        <input
          type="text"
          placeholder="Malzeme adı"
          value={name}
          onChange={(e) => setName(e.target.value)}
          autoFocus
        />
        <select value={unit} onChange={(e) => setUnit(e.target.value)}>
          <option value="ton">ton</option>
          <option value="adet">adet</option>
          <option value="kg">kg</option>
          <option value="litre">litre</option>
        </select>
        <input
          type="number"
          step="0.01"
          placeholder="Başlangıç stoğu"
          value={currentStock}
          onChange={(e) => setCurrentStock(e.target.value)}
        />
        <input
          type="number"
          step="0.01"
          placeholder="Kritik eşik"
          value={criticalThreshold}
          onChange={(e) => setCriticalThreshold(e.target.value)}
        />
        <button type="submit" disabled={saving}>{saving ? 'Ekleniyor...' : 'Ekle'}</button>
        <button type="button" className="secondary-btn" onClick={onCancel}>İptal</button>
      </div>
      {error && <div className="login-error">{error}</div>}
    </form>
  )
}
