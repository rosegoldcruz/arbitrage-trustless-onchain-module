'use client'

import AtomHero3DBlack from './components/AtomHero3DBlack'
import AitechSections from './components/AitechSections'
import FirstVisitLoader from './components/FirstVisitLoader'

export default function Page(){
  return (
    <FirstVisitLoader>
      <main className="bg-black min-h-screen">
        <AtomHero3DBlack />
        <AitechSections />
      </main>
    </FirstVisitLoader>
  )
}
