'use client'
import { useRouter } from 'next/navigation'

export default function Home() {
  const router = useRouter()

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-black text-white">
      <h1 className="text-5xl font-bold mb-6">Arbitrage Trustless On-chain Module</h1>
      <p className="text-lg mb-8 text-center max-w-xl">
        Real-time on-chain arbitrage powered by MEV agents and AI optimization.
      </p>
      <button
        onClick={() => router.push('/login')}
        className="bg-purple-600 px-8 py-3 rounded text-lg hover:bg-purple-700"
      >
        Try ATOM
      </button>
    </main>
  )
}
