// ================================================
// FILE: frontend/app/components/WarpedGrid.tsx
// Black, radial wave grid (center-out), subtle wireframe lines
// ================================================
'use client'

import { useMemo, useRef } from 'react'
import { useFrame } from '@react-three/fiber'
import * as THREE from 'three'

export function RadialWaveGridMaterial() {
  const mat = useRef<THREE.ShaderMaterial>(null!)
  useFrame((_, t) => { if (mat.current) mat.current.uniforms.uTime.value = t })

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uSpeed: { value: 1.35 },   // wave travel speed
    uWaveAmp: { value: 0.42 }, // vertical displacement strength
    uFreq: { value: 14.0 },    // ring count
    uTilt: { value: 0.9 },     // perspective squish
    uLineDensity: { value: 26.0 },
    uBaseA: { value: new THREE.Color('#000000') },
    uBaseB: { value: new THREE.Color('#07070a') },
    uLineColor: { value: new THREE.Color('#2a2a2f') }, // dim graphite lines
    uSparkColor: { value: new THREE.Color('#ffffff') }, // micro highlights
  }), [])

  const vertex = /* glsl */`
    varying vec2 vUv;
    varying float vWave;
    uniform float uTime, uSpeed, uWaveAmp, uFreq, uTilt;
    void main(){
      vUv = uv;
      vec2 g = (uv - 0.5) * vec2(1.0, uTilt);
      float r = length(g);
      float t = uTime * uSpeed;
      float w1 = sin(r * uFreq - t);
      float w2 = sin(r * (uFreq*1.27) + t*0.8);
      float wave = (w1 + 0.7*w2) * (1.0 - smoothstep(0.55, 1.05, r));
      float falloff = 1.0/(1.0 + r*2.2);
      vWave = wave * falloff;
      vec3 pos = position; pos.z += vWave * uWaveAmp;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos,1.0);
    }
  `

  const fragment = /* glsl */`
    varying vec2 vUv; varying float vWave;
    uniform float uLineDensity; uniform vec3 uBaseA,uBaseB,uLineColor,uSparkColor;
    float gridLine(float x){ float d=abs(fract(x)-0.5); return smoothstep(0.495,0.5,0.5-d); }
    void main(){
      vec2 st = vUv * vec2(1.7,1.05);
      float gx = gridLine(st.x * uLineDensity);
      float gy = gridLine(st.y * (uLineDensity*0.85));
      float grid = clamp(gx+gy, 0.0, 1.0);
      vec3 base = mix(uBaseA, uBaseB, vUv.y);
      float sparkle = smoothstep(0.0, 0.9, abs(vWave)) * 0.25; // subtle glow on peaks
      vec3 color = base + grid * (uLineColor + uSparkColor * sparkle*0.6);
      gl_FragColor = vec4(color, 1.0);
    }
  `

  // @ts-ignore
  return <shaderMaterial ref={mat} uniforms={uniforms} vertexShader={vertex} fragmentShader={fragment} />
}

export default function WarpedGridPlane() {
  return (
    <mesh rotation={[-Math.PI/3.1, 0, 0]} position={[0, -1.25, -1.8]}>
      <planeGeometry args={[16, 10, 360, 260]} />
      <RadialWaveGridMaterial />
    </mesh>
  )
}

