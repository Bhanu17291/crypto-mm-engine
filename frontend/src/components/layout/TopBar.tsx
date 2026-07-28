import { useLocation } from 'react-router-dom'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { NAV_ITEMS } from './nav-config'
import { cn } from '@/lib/utils'

export function TopBar({
  symbol,
  connected,
}: {
  symbol: string | null
  connected: boolean
}) {
  const { pathname } = useLocation()
  const title = NAV_ITEMS.find((item) => (item.path === '/' ? pathname === '/' : pathname.startsWith(item.path)))?.label ?? 'Dashboard'

  return (
    <header className="flex h-14 shrink-0 items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold tracking-tight">{title}</h1>
        {symbol && (
          <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
            {symbol.toUpperCase()}
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div
          className={cn(
            'flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium',
            connected ? 'bg-positive-muted text-positive' : 'bg-negative-muted text-negative',
          )}
        >
          <span className="relative flex size-2">
            {connected && (
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-positive opacity-60" />
            )}
            <span
              className={cn(
                'relative inline-flex size-2 rounded-full',
                connected ? 'bg-positive shadow-[0_0_6px_var(--positive)]' : 'bg-negative',
              )}
            />
          </span>
          {connected ? 'Live' : 'Disconnected'}
        </div>
        <Avatar className="size-7 ring-2 ring-brand/30">
          <AvatarFallback className="bg-gradient-brand text-[11px] text-brand-foreground">
            MM
          </AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
}
