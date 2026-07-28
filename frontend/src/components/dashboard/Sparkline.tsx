export function Sparkline({
  values,
  width = 120,
  height = 32,
}: {
  values: number[]
  width?: number
  height?: number
}) {
  if (values.length < 2) {
    return <svg width={width} height={height} />
  }

  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const points = values
    .map((v, i) => {
      const x = (i / (values.length - 1)) * width
      const y = height - ((v - min) / range) * (height - 4) - 2
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
  const trendUp = values[values.length - 1] >= values[0]

  return (
    <svg width={width} height={height} className="overflow-visible">
      <polyline
        points={points}
        fill="none"
        stroke={trendUp ? 'var(--positive)' : 'var(--negative)'}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
