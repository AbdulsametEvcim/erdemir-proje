import { useCallback, useEffect, useState } from 'react'
import api from '../api'
import Layout from '../components/Layout'
import MovementForm from '../components/MovementForm'
import RecentMovements from '../components/RecentMovements'
import MovementFilters from '../components/MovementFilters'
import SupplierSummary from '../components/SupplierSummary'
import { Spinner } from '../components/Loading'

export default function Movements() {
  const [allMaterials, setAllMaterials] = useState([])
  const [movements, setMovements] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [movementMaterialId, setMovementMaterialId] = useState('')
  const [movementType, setMovementType] = useState('')
  const [loading, setLoading] = useState(true)

  const loadAll = useCallback(async () => {
    const [materialsRes, movementsRes, suppliersRes] = await Promise.all([
      api.get('/materials'),
      api.get('/movements', {
        params: {
          limit: 30,
          material_id: movementMaterialId || undefined,
          movement_type: movementType || undefined,
        },
      }),
      api.get('/suppliers/summary'),
    ])
    setAllMaterials(materialsRes.data)
    setMovements(movementsRes.data)
    setSuppliers(suppliersRes.data)
    setLoading(false)
  }, [movementMaterialId, movementType])

  useEffect(() => {
    loadAll()
  }, [loadAll])

  if (loading) {
    return (
      <Layout>
        <Spinner />
      </Layout>
    )
  }

  return (
    <Layout>
      <section className="panel">
        <MovementForm materials={allMaterials} onSaved={loadAll} />
      </section>

      <section className="panel">
        <div className="recent-movements-header">
          <h3>Son Hareketler</h3>
          <MovementFilters
            materials={allMaterials}
            materialId={movementMaterialId}
            movementType={movementType}
            onChange={({ materialId, movementType: type }) => {
              setMovementMaterialId(materialId)
              setMovementType(type)
            }}
          />
        </div>
        <RecentMovements movements={movements} />
      </section>

      <SupplierSummary suppliers={suppliers} />
    </Layout>
  )
}
