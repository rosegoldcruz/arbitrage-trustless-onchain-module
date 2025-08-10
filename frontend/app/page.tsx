'use client'

import FoxHero from './components/FoxHero'
import AtomHero3DBlack from './components/AtomHero3DBlack'
import AitechSections from './components/AitechSections'
import FirstVisitLoader from './components/FirstVisitLoader'

export default function Page(){
  return (
    <FirstVisitLoader>
      <main className="bg-black min-h-screen">
        {/* Fox hero with cursor-reactive head */}
        <FoxHero src="/33f.png" />
        {/* Keep the 3D section below if desired */}
        <AtomHero3DBlack />
        <AitechSections />
      </main>
    </FirstVisitLoader>
  )
}
