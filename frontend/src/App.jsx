import { Navigate, Route, Routes } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Movements from './pages/Movements'
import Environmental from './pages/Environmental'
import MaterialDetail from './pages/MaterialDetail'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/hareketler"
        element={
          <ProtectedRoute>
            <Movements />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cevresel-etki"
        element={
          <ProtectedRoute>
            <Environmental />
          </ProtectedRoute>
        }
      />
      <Route
        path="/materials/:id"
        element={
          <ProtectedRoute>
            <MaterialDetail />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default App
