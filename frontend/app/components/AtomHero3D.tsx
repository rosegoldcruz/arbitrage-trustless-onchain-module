'use client';

import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { Environment, OrbitControls, useTexture } from '@react-three/drei';
import { EffectComposer, Bloom } from '@react-three/postprocessing';
import * as THREE from 'three';
import { useEffect, useMemo, useRef, useState } from 'react';
import WarpedGridPlane from './WarpedGrid';

function useMouseParallax(strength=0.35){
  const { camera, size } = useThree();
  const target = useRef(new THREE.Vector3());
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const x = (e.clientX/size.width - 0.5) * strength;
      const y = (e.clientY/size.height - 0.5) * strength;
      target.current.set(x, -y, camera.position.z);
    };
    window.addEventListener('mousemove', onMove);
    return () => window.removeEventListener('mousemove', onMove);
  }, [size, strength, camera.position.z]);
  useFrame(() => {
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, target.current.x, 0.05);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, target.current.y, 0.05);
    camera.lookAt(0,0,0);
  });
}

function useScrollDolly(baseZ=4.2, range=0.9){
  const { camera } = useThree();
  const [scroll, setScroll] = useState(0);
  useEffect(() => {
    const onScroll = () => setScroll(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  useFrame(() => {
    const t = Math.min(scroll/400, 1);
    camera.position.z = THREE.MathUtils.lerp(baseZ, baseZ - range, t);
  });
}

function FoxCoin({ front='/33f.png', back='/back.png' }:{front?:string; back?:string}){
  const [texFront, texBack] = useTexture([front, back]);
  const matFront = useMemo(() => new THREE.MeshBasicMaterial({ map: texFront, transparent: true, depthWrite: false, side: THREE.FrontSide }), [texFront]);
  const matBack = useMemo(() => new THREE.MeshBasicMaterial({ map: texBack, transparent: true, depthWrite: false, side: THREE.BackSide }), [texBack]);
  const mesh = useRef<THREE.Mesh>(null!);
  useFrame((_, t) => {
    if (!mesh.current) return;
    mesh.current.rotation.y = t*0.9;
    mesh.current.position.y = Math.sin(t*0.9)*0.06;
  });
  return (
    <mesh ref={mesh} position={[0,0,0.2]} renderOrder={2}>
      {/* Back and front planes to show both coin sides while spinning */}
      <group>
        <mesh rotation={[0, Math.PI, 0]}>
          <planeGeometry args={[3.4,3.4,1,1]} />
          <primitive object={matBack} attach="material" />
        </mesh>
        <mesh>
          <planeGeometry args={[3.4,3.4,1,1]} />
          <primitive object={matFront} attach="material" />
        </mesh>
      </group>
    </mesh>
  );
}

function ParallaxAndScroll(){
  useMouseParallax(0.35);
  useScrollDolly(4.2, 0.9);
  return null;
}

export default function AtomHero3D() {
  return (
    <section className="relative h-[92vh] w-full bg-black">
      <Canvas camera={{ position: [0, 0.35, 4.2], fov: 40 }} gl={{ antialias: true }}>
        <color attach="background" args={['#000']} />
        <ambientLight intensity={0.45} />
        <directionalLight position={[3,4,2]} intensity={1.2} />
        <Environment preset="studio" />
        <WarpedGridPlane />
        <FoxCoin front="/33f.png" back="/back.png" />
        <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.25} />
        <EffectComposer>
          <Bloom luminanceThreshold={0.2} luminanceSmoothing={0.7} intensity={0.7} />
        </EffectComposer>
        <ParallaxAndScroll />
      </Canvas>

      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-white/95">
          The Arbitrage Trustless On-Chain Module
        </h1>
        <p className="mt-4 max-w-2xl text-gray-300 md:text-xl">
          Cinematic hero. Warped grid. Fox front. Alpha in the back.
        </p>
      </div>

      <div className="pointer-events-auto absolute bottom-8 left-1/2 -translate-x-1/2">
        <a href="/sign-in" className="px-8 py-3 rounded-2xl font-bold text-black bg-gradient-to-r from-[#FFD700] via-[#8E44AD] to-[#4361EE] hover:scale-105 transition">
          Log In with Clerk
        </a>
      </div>

      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,transparent_60%,#000_100%)] pointer-events-none" />
    </section>
  );
}

