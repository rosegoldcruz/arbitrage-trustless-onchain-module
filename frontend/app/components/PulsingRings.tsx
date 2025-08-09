'use client'

import * as THREE from 'three';
import { Canvas, useFrame } from '@react-three/fiber';
import { useRef } from 'react';

function Rings() {
  const mesh = useRef<THREE.Mesh>(null!);
  const shaderData = useRef({ time: 0 });

  const uniforms = {
    u_time: { value: 0 },
    u_color: { value: new THREE.Color(0x000000) },
  };

  const material = new THREE.ShaderMaterial({
    uniforms,
    vertexShader: `
      varying vec2 vUv;
      void main() {
        vUv = uv;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
      }
    `,
    fragmentShader: `
      uniform float u_time;
      varying vec2 vUv;
      void main() {
        vec2 uv = vUv - 0.5;
        float dist = length(uv);
        float rings = sin(20.0 * dist - u_time * 3.0);
        float alpha = smoothstep(0.5, 0.0, dist);
        float intensity = 0.5 + 0.5 * rings;
        vec3 color = vec3(0.05) + vec3(intensity * 0.15);
        gl_FragColor = vec4(color, alpha);
      }
    `,
    transparent: true,
  });

  useFrame((_, delta) => {
    shaderData.current.time += delta;
    material.uniforms.u_time.value = shaderData.current.time;
  });

  return (
    <mesh ref={mesh}>
      <planeGeometry args={[5, 5, 32, 32]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
}

export default function PulsingRings() {
  return (
    <Canvas camera={{ position: [0, 0, 1] }}>
      <Rings />
    </Canvas>
  );
}
