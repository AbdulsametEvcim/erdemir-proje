import { useCallback, useEffect, useState } from 'react'
import api from '../api'
import Layout from '../components/Layout'
import SummaryCards from '../components/SummaryCards'
import AlertBanner from '../components/AlertBanner'
import MaterialsTable from '../components/MaterialsTable'
import AddMaterialForm from '../components/AddMaterialForm'
import ComparisonChart from '../components/ComparisonChart'
import { DashboardSkeleton } from '../components/Loading'

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [alerts, setAlerts] = useState([])
  const [materials, setMaterials] = useState([])
  const [search, setSearch] = useState('')
  const [sortBy, setSortBy] = useState('name')
  const [order, setOrder] = useState('asc')
  const [loading, setLoading] = useState(true)
  const [showAddMaterial, setShowAddMaterial] = useState(false)
  const [comparison, setComparison] = useState([])

  const loadAll = useCallback(async () => {
    const [summaryRes, alertsRes, materialsRes, comparisonRes] = await Promise.all([
      api.get('/summary'),
      api.get('/alerts'),
      api.get('/materials', { params: { search, sort_by: sortBy, order } }),
      api.get('/reports/consumption-comparison', { params: { days: 30 } }),
    ])
    setSummary(summaryRes.data)
    setAlerts(alertsRes.data)
    setMaterials(materialsRes.data)
    setComparison(comparisonRes.data)
    setLoading(false)
  }, [search, sortBy, order])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  function handleSort(column, newOrder) {
    setSortBy(column)
    setOrder(newOrder)
  }

  async function handleExport() {
    const res = await api.get('/materials/export', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'malzemeler.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  async function handleSummaryReport() {
    const res = await api.get('/reports/summary-pdf', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([res.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'envanter_genel_rapor.pdf')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <Layout>
        <DashboardSkeleton />
      </Layout>
    )
  }

  return (
    <Layout>
      <AlertBanner alerts={alerts} />
      <SummaryCards summary={summary} />

      <ComparisonChart data={comparison} days={30} />

      <section className="panel">
        <div className="panel-header">
          <h2>Malzeme Listesi</h2>
          <div className="panel-actions">
            <input
              type="text"
              placeholder="Malzeme ara..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <button className="secondary-btn" onClick={() => setShowAddMaterial((v) => !v)}>
              + Yeni Malzeme
            </button>
            <button className="secondary-btn" onClick={handleSummaryReport}>Genel Rapor İndir</button>
            <button onClick={handleExport}>Excel'e Aktar</button>
          </div>
        </div>

        {showAddMaterial && (
          <AddMaterialForm
            onSaved={() => {
              setShowAddMaterial(false)
              loadAll()
            }}
            onCancel={() => setShowAddMaterial(false)}
          />
        )}

        <MaterialsTable materials={materials} sortBy={sortBy} order={order} onSort={handleSort} />
      </section>
    </Layout>
  )
}
