import { useEffect, useState } from 'react'
import { MoonIcon, SunIcon } from './icons'

function getInitialTheme() {
  const stored = localStorage.getItem('theme')
  if (stored === 'light' || stored === 'dark') return stored
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

export default function ThemeToggle() {
  const [theme, setTheme] = useState(getInitialTheme)

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('theme', theme)
  }, [theme])

  function toggle() {
    setTheme((t) => (t === 'dark' ? 'light' : 'dark'))
  }

  return (
    <button className="sidebar-logout" onClick={toggle}>
      {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
      {theme === 'dark' ? 'Aydınlık Mod' : 'Karanlık Mod'}
    </button>
  )
}
