import { create } from 'zustand'
import type { StatusSnapshot } from '@/types/status'

const MAX_HISTORY = 300

interface EngineState {
  status: StatusSnapshot | null
  history: StatusSnapshot[]
  connected: boolean
  setStatus: (status: StatusSnapshot) => void
  setConnected: (connected: boolean) => void
}

export const useEngineStore = create<EngineState>((set) => ({
  status: null,
  history: [],
  connected: false,
  setStatus: (status) =>
    set((state) => ({
      status,
      history: [...state.history, status].slice(-MAX_HISTORY),
    })),
  setConnected: (connected) => set({ connected }),
}))
