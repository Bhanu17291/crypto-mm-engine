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
  active: boolean
}

export const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', icon: LayoutDashboard, active: true },
  { label: 'Order Book', icon: Layers, active: false },
  { label: 'Strategy', icon: Sparkles, active: false },
  { label: 'Risk', icon: ShieldAlert, active: false },
  { label: 'Execution', icon: ListOrdered, active: false },
  { label: 'Analytics', icon: BarChart3, active: false },
]
