import { useMemo } from 'react'
import { type ColumnDef, flexRender, getCoreRowModel, useReactTable } from '@tanstack/react-table'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { cn } from '@/lib/utils'
import { formatPrice, formatQty, formatTime, formatUsd } from '@/lib/format'
import type { FillEvent } from '@/types/status'

const columns: ColumnDef<FillEvent>[] = [
  {
    accessorKey: 'timestamp_ms',
    header: 'Time',
    cell: (ctx) => (
      <span className="font-mono text-xs text-muted-foreground">
        {formatTime(ctx.getValue<number>())}
      </span>
    ),
  },
  {
    accessorKey: 'side',
    header: 'Side',
    cell: (ctx) => {
      const side = ctx.getValue<string>()
      return (
        <span
          className={cn(
            'font-mono text-xs font-medium uppercase',
            side === 'bid' ? 'text-positive' : 'text-negative',
          )}
        >
          {side}
        </span>
      )
    },
  },
  {
    accessorKey: 'price',
    header: 'Price',
    cell: (ctx) => (
      <span className="font-mono text-xs tabular-nums">{formatPrice(ctx.getValue<number>())}</span>
    ),
  },
  {
    accessorKey: 'quantity',
    header: 'Qty',
    cell: (ctx) => (
      <span className="font-mono text-xs tabular-nums">{formatQty(ctx.getValue<number>())}</span>
    ),
  },
  {
    accessorKey: 'fee',
    header: 'Fee',
    cell: (ctx) => (
      <span className="font-mono text-xs tabular-nums text-muted-foreground">
        {formatUsd(ctx.getValue<number>())}
      </span>
    ),
  },
]

export function FillsTable({ fills, loading }: { fills: FillEvent[]; loading?: boolean }) {
  const data = useMemo(() => fills.slice(0, 20), [fills])
  const table = useReactTable({ data, columns, getCoreRowModel: getCoreRowModel() })

  return (
    <Card className="gap-3 border-border/60 bg-card p-4 shadow-lg shadow-black/20">
      <span className="text-xs font-medium text-muted-foreground">Recent Fills</span>

      {loading ? (
        <div className="space-y-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-6 w-full" />
          ))}
        </div>
      ) : data.length === 0 ? (
        <div className="flex h-24 items-center justify-center text-xs text-muted-foreground">
          No fills yet
        </div>
      ) : (
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id} className="hover:bg-transparent">
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="h-8 text-[11px] text-muted-foreground">
                    {flexRender(header.column.columnDef.header, header.getContext())}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id} className="border-border/40">
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id} className="py-1.5">
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </Card>
  )
}
