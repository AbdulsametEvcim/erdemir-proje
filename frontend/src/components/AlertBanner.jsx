export default function AlertBanner({ alerts }) {
  if (!alerts || alerts.length === 0) return null

  const names = alerts.map((a) => a.name).join(', ')

  return (
    <div className="alert-banner">
      ⚠ {alerts.length} malzeme kritik seviyede: {names}
    </div>
  )
}
