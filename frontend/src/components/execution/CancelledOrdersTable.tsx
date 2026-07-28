import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { formatTime } from '@/lib/format'
import type { CancelEvent } from '@/types/status'

export function CancelledOrdersTable({
  cancellations,
  loading,
}: {
  cancellations: CancelEvent[]
  loading?: boolean
}) {
  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-none">
      <span className="text-xs font-medium text-muted-foreground">Cancelled Orders</span>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-6 w-full" />
          ))}
        </div>
      ) : cancellations.length === 0 ? (
        <div className="flex h-24 items-center justify-center text-xs text-muted-foreground">
          No cancellations yet
        </div>
      ) : (
        <Table>
          <TableHeader>
            <TableRow className="hover:bg-transparent">
              <TableHead className="h-8 text-[11px] text-muted-foreground">Time</TableHead>
              <TableHead className="h-8 text-[11px] text-muted-foreground">Order ID</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {cancellations.slice(0, 20).map((c, i) => (
              <TableRow key={`${c.order_id}-${i}`} className="border-border/40">
                <TableCell className="py-1.5 font-mono text-xs text-muted-foreground">
                  {formatTime(c.timestamp_ms)}
                </TableCell>
                <TableCell className="py-1.5 font-mono text-xs">#{c.order_id}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  )
}
