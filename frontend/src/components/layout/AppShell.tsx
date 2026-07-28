import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'
import { useEngineStore } from '@/store/engine-store'
import { useInitialStatus } from '@/hooks/useInitialStatus'
import { useStatusSocket } from '@/hooks/useStatusSocket'

export function AppShell() {
  useInitialStatus()
  useStatusSocket()

  const symbol = useEngineStore((s) => s.status?.symbol ?? null)
  const connected = useEngineStore((s) => s.connected)

  return (
    <div className="flex h-svh w-full bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar symbol={symbol} connected={connected} />
        <main className="min-h-0 flex-1 overflow-y-auto px-6 pb-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
