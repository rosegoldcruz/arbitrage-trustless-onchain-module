'use client';

import { useMemo, useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const GLSL_NOISE = `
vec2 hash22(vec2 p){
  p = vec2(dot(p, vec2(127.1,311.7)), dot(p, vec2(269.5,183.3)));
  return -1.0 + 2.0*fract(sin(p)*43758.5453123);
}
float noise(vec2 p){
  vec2 i=floor(p), f=fract(p), u=f*f*(3.-2.*f);
  return mix(mix(dot(hash22(i+vec2(0,0)), f-vec2(0,0)),
                 dot(hash22(i+vec2(1,0)), f-vec2(1,0)), u.x),
             mix(dot(hash22(i+vec2(0,1)), f-vec2(0,1)),
                 dot(hash22(i+vec2(1,1)), f-vec2(1,1)), u.x), u.y);
}
float fbm(vec2 p){
  float v=0., a=.5; 
  for(int i=0;i<5;i++){ v+=a*noise(p); p*=2.; a*=.5; }
  return v;
}
`;

export function WarpedGridMaterial() {
  const mat = useRef<THREE.ShaderMaterial>(null!);
  useFrame((_, t) => { if (mat.current) mat.current.uniforms.uTime.value = t; });

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uSpeed: { value: 0.6 },
    uWarpAmp: { value: 0.28 },
    uNoiseScale: { value: 1.4 },
    uLineDensity: { value: 18.0 },
    uColorA: { value: new THREE.Color('#0a0a12') },
    uColorB: { value: new THREE.Color('#1d1f3a') },
    uLineColor: { value: new THREE.Color('#8E44AD') },
    uGlowColor: { value: new THREE.Color('#FFD700') }
  }), []);

  const vertex = /* glsl */`
    varying vec2 vUv;
    void main(){ vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.); }
  `;
  const fragment = /* glsl */`
    varying vec2 vUv;
    uniform float uTime,uSpeed,uWarpAmp,uNoiseScale,uLineDensity;
    uniform vec3 uColorA,uColorB,uLineColor,uGlowColor;
    ${GLSL_NOISE}
    float gridLine(float x){ float d=abs(fract(x)-.5); return smoothstep(.49,.495,.5-d); }
    void main(){
      vec2 st = vUv*vec2(1.6,1.);
      vec2 flow = vec2(
        fbm(st*uNoiseScale+vec2(uTime*.15*uSpeed,0.)),
        fbm(st*(uNoiseScale*1.2)+vec2(0.,uTime*.18*uSpeed))
      );
      st += (flow-.5)*uWarpAmp;
      st.x += uTime*.05*uSpeed;
      float grid = clamp(gridLine(st.x*uLineDensity)+gridLine(st.y*(uLineDensity*.7)),0.,1.);
      float pulse = fbm(vUv*3. + uTime*.3*uSpeed);
      vec3 base = mix(uColorB,uColorA,vUv.y);
      vec3 col = base + grid*(uLineColor*.9 + uGlowColor*(.25+.75*pulse));
      gl_FragColor = vec4(col,1.);
    }
  `;

  // @ts-ignore
  return <shaderMaterial ref={mat} uniforms={uniforms} vertexShader={vertex} fragmentShader={fragment} />;
}

export default function WarpedGridPlane() {
  return (
    <mesh rotation={[-Math.PI/3.1,0,0]} position={[0,-1.25,-1.8]}>
      <planeGeometry args={[12,8,2,2]} />
      <WarpedGridMaterial />
    </mesh>
  );
}

