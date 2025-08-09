// ================================================
// FILE: frontend/app/components/AtomHero3DBlack.tsx
// Cinematic hero: black palette, radial grid, fox image plane, pulsing eye beacons, bloom, parallax
// ================================================
'use client'

import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { Environment, OrbitControls, useTexture } from '@react-three/drei'
import { EffectComposer, Bloom } from '@react-three/postprocessing'
import * as THREE from 'three'
import { useEffect, useMemo, useRef, useState } from 'react'
import WarpedGridPlane from './WarpedGrid'

function useMouseParallax(strength=0.3){
  const { camera, size } = useThree()
  const target = useRef(new THREE.Vector3())
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const x=(e.clientX/size.width-0.5)*strength
      const y=(e.clientY/size.height-0.5)*strength
      target.current.set(x,-y,camera.position.z)
    }
    window.addEventListener('mousemove', onMove)
    return () => window.removeEventListener('mousemove', onMove)
  }, [size, strength, camera.position.z])
  useFrame(()=>{
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, target.current.x, 0.06)
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, target.current.y, 0.06)
    camera.lookAt(0,0,0)
  })
}

function useScrollDolly(baseZ=4.2, range=0.8){
  const { camera } = useThree()
  const [s, setS] = useState(0)
  useEffect(()=>{
    const onScroll=()=>setS(window.scrollY)
    window.addEventListener('scroll', onScroll, { passive: true })
    return ()=>window.removeEventListener('scroll', onScroll)
  },[])
  useFrame(()=>{
    const t=Math.min(s/380,1)
    camera.position.z = THREE.MathUtils.lerp(baseZ, baseZ-range, t)
  })
}

function FoxImagePlane({ src='/33f.png' }:{src?:string}){
  const tex = useTexture(src)
  const mat = useMemo(()=> new THREE.MeshBasicMaterial({ map: tex, transparent: true, depthWrite:false, color: 0xffffff }),[tex])
  const mesh = useRef<THREE.Mesh>(null!)
  useFrame((_, t)=>{
    if(!mesh.current) return
    mesh.current.rotation.y = Math.sin(t*0.32)*0.12
    mesh.current.position.y = Math.sin(t*0.85)*0.05
  })
  return (
    <mesh ref={mesh} position={[0,0,0.22]} renderOrder={3}>
      <planeGeometry args={[2.1,2.1,1,1]} />
      {/* @ts-ignore */}
      <primitive object={mat} attach="material" />
    </mesh>
  )
}

// Radial gradient glow planes for eyes, additive + bloom
function EyeBeacon({ position=[0,0,0.24] as [number,number,number], radius=0.18 }){
  const mat = useMemo(()=>{
    const uniforms = { uR: { value: radius } }
    const vs = /* glsl */`varying vec2 vUv; void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`
    const fs = /* glsl */`
      varying vec2 vUv; uniform float uR;
      void main(){ vec2 p=vUv*2.0-1.0; float d=length(p); float a=smoothstep(uR, uR*0.2, d); float core=smoothstep(0.25,0.0,d); vec3 col=vec3(1.0)*(0.6*core+0.6*(1.0-a)); gl_FragColor=vec4(col,1.0-a); }
    `
    return new THREE.ShaderMaterial({ vertexShader: vs, fragmentShader: fs, transparent:true, blending: THREE.AdditiveBlending, depthWrite:false })
  },[radius])
  const mesh = useRef<THREE.Mesh>(null!)
  useFrame((_, t)=>{ if(mesh.current){ const s=1.0+Math.sin(t*2.2)*0.08; mesh.current.scale.setScalar(s) } })
  return (
    <mesh ref={mesh} position={position} renderOrder={4}>
      <planeGeometry args={[0.55,0.55]} />
      {/* @ts-ignore */}
      <primitive object={mat} attach="material" />
    </mesh>
  )
}

function ParallaxAndScroll(){ useMouseParallax(0.28); useScrollDolly(4.2,0.8); return null }

export default function AtomHero3DBlack(){
  return (
    <section className="relative h-[92vh] w-full bg-black">
      <Canvas camera={{ position:[0,0.32,4.2], fov:40 }} gl={{ antialias:true, powerPreference:'high-performance' }}>
        <color attach="background" args={["#000"]} />
        <ambientLight intensity={0.35} />
        <directionalLight position={[3,4,2]} intensity={0.9} />
        <Environment preset="city" />
        <WarpedGridPlane />
        <FoxImagePlane src="/33f.png" />
        <EyeBeacon position={[-0.42,0.15,0.26]} radius={0.22} />
        <EyeBeacon position={[ 0.42,0.15,0.26]} radius={0.22} />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.18} />
        <EffectComposer>
          <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.85} intensity={1.1} />
        </EffectComposer>
        <ParallaxAndScroll />
      </Canvas>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white">The Arbitrage Trustless On-Chain Module</h1>
        <p className="mt-4 max-w-2xl text-white/60 md:text-xl">Powered by the Advanced Efficient Optimized Network</p>
      </div>

      <div className="pointer-events-auto absolute bottom-8 left-1/2 -translate-x-1/2">
        <a href="/sign-in" className="px-8 py-3 rounded-2xl font-bold text-black bg-white hover:opacity-90 transition">Log In with Clerk</a>
      </div>

      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,transparent_60%,#000_100%)] pointer-events-none" />
    </section>
  )
}
