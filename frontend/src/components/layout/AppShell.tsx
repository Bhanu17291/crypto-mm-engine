import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'
import { TopBar } from './TopBar'

export function AppShell({
  symbol,
  connected,
  children,
}: {
  symbol: string | null
  connected: boolean
  children: ReactNode
}) {
  return (
    <div className="flex h-svh w-full bg-background text-foreground">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col">
        <TopBar symbol={symbol} connected={connected} />
        <main className="min-h-0 flex-1 overflow-y-auto px-6 pb-6">{children}</main>
      </div>
    </div>
  )
}
