import {
  BarChart3,
  Layers,
  LayoutDashboard,
  ListOrdered,
  ShieldAlert,
  Sparkles,
  type LucideIcon,
} from 'lucide-react'

export interface NavItem {
  label: string
  icon: LucideIcon
  path: string
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, path: '/' },
  { label: 'Order Book', icon: Layers, path: '/order-book' },
  { label: 'Strategy', icon: Sparkles, path: '/strategy' },
  { label: 'Risk', icon: ShieldAlert, path: '/risk' },
  { label: 'Execution', icon: ListOrdered, path: '/execution' },
  { label: 'Analytics', icon: BarChart3, path: '/analytics' },
]
