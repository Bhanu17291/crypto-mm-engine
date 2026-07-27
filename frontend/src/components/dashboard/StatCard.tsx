import { motion } from 'framer-motion'
import type { LucideIcon } from 'lucide-react'
import { Card } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { AnimatedNumber } from './AnimatedNumber'
import { cn } from '@/lib/utils'

type Tone = 'neutral' | 'positive' | 'negative' | 'auto'

export function StatCard({
  label,
  value,
  format,
  icon: Icon,
  tone = 'neutral',
  sublabel,
  loading,
}: {
  label: string
  value: number | null
  format: (v: number) => string
  icon: LucideIcon
  tone?: Tone
  sublabel?: string
  loading?: boolean
}) {
  const resolvedTone: Tone =
    tone === 'auto' ? (value != null && value < 0 ? 'negative' : 'positive') : tone

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <Card className="gap-2 border-border/60 bg-card p-4 shadow-none transition-colors hover:border-border">
        <div className="flex items-center justify-between text-muted-foreground">
          <span className="text-xs font-medium">{label}</span>
          <Icon className="size-3.5" strokeWidth={2} />
        </div>

        {loading || value == null ? (
          <Skeleton className="h-7 w-24" />
        ) : (
          <div
            className={cn(
              'font-mono text-2xl font-medium tabular-nums tracking-tight',
              resolvedTone === 'positive' && 'text-positive',
              resolvedTone === 'negative' && 'text-negative',
              resolvedTone === 'neutral' && 'text-foreground',
            )}
          >
            <AnimatedNumber value={value} format={format} />
          </div>
        )}

        {sublabel && !loading && (
          <span className="text-[11px] text-muted-foreground">{sublabel}</span>
        )}
      </Card>
    </motion.div>
  )
}
