import { useState } from 'react'
import api from '../api'
import { useToast } from './Toast'

export default function MovementForm({ materials, onSaved }) {
  const [materialId, setMaterialId] = useState('')
  const [movementType, setMovementType] = useState('cikis')
  const [quantity, setQuantity] = useState('')
  const [note, setNote] = useState('')
  const [supplier, setSupplier] = useState('')
  const [error, setError] = useState('')
  const [saving, setSaving] = useState(false)
  const showToast = useToast()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    if (!materialId || !quantity) {
      setError('Malzeme ve miktar zorunludur')
      return
    }
    setSaving(true)
    try {
      const material = materials.find((m) => String(m.id) === materialId)
      await api.post('/movements', {
        material_id: Number(materialId),
        movement_type: movementType,
        quantity: Number(quantity),
        note: note || null,
        supplier: movementType === 'giris' ? (supplier || null) : null,
      })
      const typeLabel = movementType === 'giris' ? 'girişi' : 'çıkışı'
      showToast(`${material?.name ?? 'Malzeme'} için ${quantity} birim ${typeLabel} kaydedildi`, 'success')
      setQuantity('')
      setNote('')
      setSupplier('')
      onSaved()
    } catch (err) {
      const message = err.response?.data?.detail || 'Hareket kaydedilemedi'
      setError(message)
      showToast(message, 'error')
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="movement-form" onSubmit={handleSubmit}>
      <h3>Yeni Stok Hareketi</h3>
      <div className="movement-form-row">
        <select value={materialId} onChange={(e) => setMaterialId(e.target.value)}>
          <option value="">Malzeme seç...</option>
          {materials.map((m) => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>

        <select value={movementType} onChange={(e) => setMovementType(e.target.value)}>
          <option value="cikis">Çıkış (kullanım)</option>
          <option value="giris">Giriş (tedarik)</option>
        </select>

        <input
          type="number"
          step="0.01"
          placeholder="Miktar"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
        />

        {movementType === 'giris' && (
          <input
            type="text"
            placeholder="Tedarikçi"
            value={supplier}
            onChange={(e) => setSupplier(e.target.value)}
          />
        )}

        <input
          type="text"
          placeholder="Not (opsiyonel)"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />

        <button type="submit" disabled={saving}>{saving ? 'Kaydediliyor...' : 'Kaydet'}</button>
      </div>
      {error && <div className="login-error">{error}</div>}
    </form>
  )
}
