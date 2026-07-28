import { useState } from 'react'
import { motion } from 'framer-motion'
import { NavLink } from 'react-router-dom'
import { ChevronsLeft, ChevronsRight, Activity } from 'lucide-react'
import { NAV_ITEMS } from './nav-config'
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { cn } from '@/lib/utils'

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false)

  return (
    <motion.aside
      animate={{ width: collapsed ? 72 : 232 }}
      transition={{ type: 'spring', stiffness: 340, damping: 32 }}
      className="m-3 mr-0 hidden shrink-0 flex-col rounded-2xl border border-sidebar-border bg-sidebar shadow-[0_1px_2px_rgba(0,0,0,0.04)] md:flex"
    >
      <div className="flex h-14 items-center gap-2 px-4">
        <div className="flex size-7 shrink-0 items-center justify-center rounded-lg bg-brand text-brand-foreground">
          <Activity className="size-4" strokeWidth={2.5} />
        </div>
        {!collapsed && (
          <span className="truncate text-sm font-semibold tracking-tight text-sidebar-foreground">
            crypto-mm-engine
          </span>
        )}
      </div>

      <Separator />

      <nav className="flex flex-1 flex-col gap-1 p-2">
        {NAV_ITEMS.map((item) => (
          <NavRow key={item.path} item={item} collapsed={collapsed} />
        ))}
      </nav>

      <Separator />

      <div className="p-2">
        <button
          type="button"
          onClick={() => setCollapsed((v) => !v)}
          className="flex w-full items-center justify-center rounded-lg py-2 text-sidebar-foreground/60 transition-colors hover:bg-sidebar-accent hover:text-sidebar-foreground"
        >
          {collapsed ? (
            <ChevronsRight className="size-4" />
          ) : (
            <ChevronsLeft className="size-4" />
          )}
        </button>
      </div>
    </motion.aside>
  )
}

function Separator() {
  return <div className="mx-2 h-px bg-sidebar-border" />
}

function NavRow({
  item,
  collapsed,
}: {
  item: (typeof NAV_ITEMS)[number]
  collapsed: boolean
}) {
  const Icon = item.icon

  const row = ({ isActive }: { isActive: boolean }) => (
    <div
      className={cn(
        'group relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors',
        isActive
          ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium'
          : 'text-sidebar-foreground/65 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground',
      )}
    >
      {isActive && (
        <motion.span
          layoutId="active-nav-indicator"
          className="absolute left-0 top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-brand"
        />
      )}
      <Icon className="size-4 shrink-0" strokeWidth={2} />
      {!collapsed && <span className="truncate">{item.label}</span>}
    </div>
  )

  const link = (
    <NavLink to={item.path} end={item.path === '/'}>
      {({ isActive }) => row({ isActive })}
    </NavLink>
  )

  if (collapsed) {
    return (
      <Tooltip delayDuration={150}>
        <TooltipTrigger asChild>{link}</TooltipTrigger>
        <TooltipContent side="right">{item.label}</TooltipContent>
      </Tooltip>
    )
  }

  return link
}
