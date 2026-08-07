export default function ConfirmModal({ title, message, confirmLabel = 'Sil', onConfirm, onCancel, loading }) {
  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <h3>{title}</h3>
        <p>{message}</p>
        <div className="modal-actions">
          <button className="secondary-btn" onClick={onCancel}>İptal</button>
          <button className="danger-btn" onClick={onConfirm} disabled={loading}>
            {loading ? 'Siliniyor...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  )
}
