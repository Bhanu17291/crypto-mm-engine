import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import { TooltipProvider } from '@/components/ui/tooltip'
import { AppShell } from '@/components/layout/AppShell'
import { DashboardPage } from '@/pages/DashboardPage'
import { OrderBookPage } from '@/pages/OrderBookPage'
import { StrategyPage } from '@/pages/StrategyPage'
import { RiskPage } from '@/pages/RiskPage'
import { ExecutionPage } from '@/pages/ExecutionPage'
import { AnalyticsPage } from '@/pages/AnalyticsPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={200}>
        <BrowserRouter basename="/crypto">
          <Routes>
            <Route element={<AppShell />}>
              <Route index element={<DashboardPage />} />
              <Route path="order-book" element={<OrderBookPage />} />
              <Route path="strategy" element={<StrategyPage />} />
              <Route path="risk" element={<RiskPage />} />
              <Route path="execution" element={<ExecutionPage />} />
              <Route path="analytics" element={<AnalyticsPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  )
}

export default App
