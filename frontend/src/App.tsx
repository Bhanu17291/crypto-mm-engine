import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TooltipProvider } from '@/components/ui/tooltip'
import { DashboardPage } from '@/pages/DashboardPage'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider delayDuration={200}>
        <DashboardPage />
      </TooltipProvider>
    </QueryClientProvider>
  )
}

export default App
