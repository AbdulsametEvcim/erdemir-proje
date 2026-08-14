import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const res = await api.post('/login', { username, password })
      localStorage.setItem('token', res.data.access_token)
      navigate('/')
    } catch {
      setError('Kullanıcı adı veya şifre hatalı')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-page">
      <img className="login-bg-photo" src="/login-bg.jpg" alt="" />
      <div className="login-bg-overlay" />

      <div className="login-content">
        <div className="login-brand">
          <div className="login-illustration-logo">
            <img src="/favicon.svg" alt="Erdemir" />
          </div>
          <h2>Envanter / Stok Takip ve Tahmin Sistemi</h2>
          <p>Hammadde ve malzeme stoklarını gerçek zamanlı izleyin, kritik seviyeleri önceden görün.</p>
        </div>

        <form className="login-card" onSubmit={handleSubmit}>
          <h1>Giriş Yap</h1>
          <p className="login-subtitle">Erdemir ERP ve Çevresel Uygulamalar Stajı</p>

          <label>Kullanıcı Adı</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />

          <label>Şifre</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

          {error && <div className="login-error">{error}</div>}

          <button type="submit" disabled={loading}>
            {loading ? 'Giriş yapılıyor...' : 'Giriş Yap'}
          </button>
        </form>
      </div>
    </div>
  )
}
