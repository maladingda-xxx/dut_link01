import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'

type ConnectionStatus = 'loading' | 'connected' | 'error'

function App() {
  const [status, setStatus] = useState<ConnectionStatus>('loading')

  useEffect(() => {
    let cancelled = false

    fetch('/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<{ status: string }>
      })
      .then((data) => {
        if (!cancelled) setStatus(data.status === 'ok' ? 'connected' : 'error')
      })
      .catch(() => {
        if (!cancelled) setStatus('error')
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4">
      <h1 className="text-3xl font-semibold tracking-tight">DUT Link</h1>
      <p className="text-muted-foreground">
        {status === 'loading' && '正在连接后端…'}
        {status === 'connected' && '后端已连接'}
        {status === 'error' && '后端连接失败'}
      </p>
      <Button variant="outline" onClick={() => window.location.reload()}>
        重新检测
      </Button>
    </main>
  )
}

export default App
