import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

export function TopBar({
  symbol,
  connected,
}: {
  symbol: string | null
  connected: boolean
}) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold tracking-tight">Dashboard</h1>
        {symbol && (
          <span className="rounded-md bg-muted px-2 py-0.5 font-mono text-xs text-muted-foreground">
            {symbol.toUpperCase()}
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span className="relative flex size-2">
            {connected && (
              <span className="absolute inline-flex size-full animate-ping rounded-full bg-positive opacity-60" />
            )}
            <span
              className={cn(
                'relative inline-flex size-2 rounded-full',
                connected ? 'bg-positive' : 'bg-negative',
              )}
            />
          </span>
          {connected ? 'Live' : 'Disconnected'}
        </div>
        <Avatar className="size-7">
          <AvatarFallback className="bg-secondary text-[11px]">MM</AvatarFallback>
        </Avatar>
      </div>
    </header>
  )
}
