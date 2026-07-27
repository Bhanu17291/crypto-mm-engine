import { useEffect } from 'react'
import { motion, useMotionValue, useTransform, animate } from 'framer-motion'

export function AnimatedNumber({
  value,
  format,
}: {
  value: number
  format: (v: number) => string
}) {
  const motionValue = useMotionValue(value)
  const display = useTransform(motionValue, (v) => format(v))

  useEffect(() => {
    const controls = animate(motionValue, value, { duration: 0.5, ease: 'easeOut' })
    return controls.stop
  }, [value, motionValue])

  return <motion.span>{display}</motion.span>
}
