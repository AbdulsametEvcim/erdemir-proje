export function Spinner({ label = 'Yükleniyor...' }) {
  return (
    <div className="loading-wrap">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  )
}

export function DashboardSkeleton() {
  return (
    <div>
      <div className="summary-cards">
        <div className="skeleton skeleton-card" />
        <div className="skeleton skeleton-card" />
        <div className="skeleton skeleton-card" />
      </div>
      <div className="panel">
        <div className="skeleton skeleton-row" style={{ width: '40%' }} />
        <div className="skeleton skeleton-row" />
        <div className="skeleton skeleton-row" />
        <div className="skeleton skeleton-row" style={{ width: '70%' }} />
      </div>
    </div>
  )
}
