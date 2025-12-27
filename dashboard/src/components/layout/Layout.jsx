import { useEffect } from 'react'
import { useThemeStore } from '@/stores/themeStore'
import Header from './Header'
import Sidebar from './Sidebar'

export default function Layout({ children }) {
  const theme = useThemeStore((state) => state.theme)

  useEffect(() => {
    document.documentElement.classList.toggle('dark', theme === 'dark')
  }, [theme])

  return (
    <div className={`min-h-screen ${theme}`}>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50 to-cyan-50 dark:from-gray-950 dark:via-blue-950 dark:to-gray-950">
        <Header />
        <div className="flex">
          <Sidebar />
          <main className="flex-1 p-8 ml-0 lg:ml-64 mt-16">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}