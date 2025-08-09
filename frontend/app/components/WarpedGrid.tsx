// frontend/app/components/WarpedGrid.tsx
'use client';

import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function RadialWaveGridMaterial() {
  const mat = useRef<THREE.ShaderMaterial>(null!);
  useFrame((_, t) => { if (mat.current) mat.current.uniforms.uTime.value = t; });

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uSpeed: { value: 1.6 },      // wave travel speed
    uWaveAmp: { value: 0.35 },   // vertical displacement strength
    uFreq: { value: 12.0 },      // rings count
    uLineDensity: { value: 22.0 },
    uTilt: { value: 0.95 },      // camera-ish tilt compensation for the grid
    uColorA: { value: new THREE.Color('#0a0a12') },
    uColorB: { value: new THREE.Color('#1a1c37') },
    uLineColor: { value: new THREE.Color('#ff7ee7') },
    uGlowColor: { value: new THREE.Color('#ffd166') }
  }), []);

  // Vertex: radial traveling waves from the center (outward + inward interference)
  const vertex = /* glsl */`
    varying vec2 vUv;
    varying float vWave;
    uniform float uTime, uSpeed, uWaveAmp, uFreq, uTilt;

    void main(){
      vUv = uv;

      // center UV at (0,0), slight non-uniform scale to fake perspective
      vec2 g = (uv - 0.5) * vec2(1.0, uTilt);

      float r = length(g);                         // radius from center
      float t = uTime * uSpeed;

      // two traveling waves (outward & inward) to get that "breathe" feel
      float w1 = sin(r * uFreq - t);
      float w2 = sin(r * (uFreq * 1.35) + t * 0.85);
      float wave = (w1 + 0.65 * w2) * (1.0 - smoothstep(0.55, 1.05, r));

      // fade amplitude a bit with radius
      float falloff = 1.0 / (1.0 + r * 2.0);
      wave *= falloff;

      vWave = wave;

      vec3 pos = position;
      pos.z += wave * uWaveAmp;                    // displace the mesh
      gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
    }
  `;

  // Fragment: curved grid lines + glow modulated by the wave height
  const fragment = /* glsl */`
    varying vec2 vUv;
    varying float vWave;
    uniform float uLineDensity;
    uniform vec3 uColorA, uColorB, uLineColor, uGlowColor;

    float gridLine(float x){
      float d = abs(fract(x) - 0.5);
      return smoothstep(0.495, 0.5, 0.5 - d);
    }

    void main(){
      // UV scaling for nicer spacing
      vec2 st = vUv * vec2(1.7, 1.1);

      // draw the grid
      float gx = gridLine(st.x * uLineDensity);
      float gy = gridLine(st.y * (uLineDensity * 0.8));
      float grid = clamp(gx + gy, 0.0, 1.0);

      // base gradient
      vec3 base = mix(uColorA, uColorB, vUv.y);

      // pulse/glow with the wave height
      float glow = smoothstep(0.0, 0.9, abs(vWave)) * 0.7;
      vec3 color = base + grid * (uLineColor * 0.85 + uGlowColor * glow * 0.75);

      gl_FragColor = vec4(color, 1.0);
    }
  `;

  // @ts-ignore
  return <shaderMaterial ref={mat} uniforms={uniforms} vertexShader={vertex} fragmentShader={fragment} />;
}

export default function WarpedGridPlane() {
  return (
    <mesh rotation={[-Math.PI/3.1, 0, 0]} position={[0, -1.25, -1.8]}>
      <planeGeometry args={[14, 9, 320, 220]} />
      <RadialWaveGridMaterial />
    </mesh>
  );
}

