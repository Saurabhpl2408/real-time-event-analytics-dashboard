import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const useAuthStore = create(
  persist(
    (set) => ({
      token: null,
      user: null,
      
      setAuth: (token, user) => set({ token, user }),
      
      logout: () => set({ token: null, user: null }),
      
      isAdmin: () => {
        const state = useAuthStore.getState()
        return state.user?.role === 'admin'
      },
    }),
    {
      name: 'auth-storage',
    }
  )
)