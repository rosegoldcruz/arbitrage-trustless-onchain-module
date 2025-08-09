import Image from 'next/image';
import PulsingRings from './PulsingRings';

export default function FoxHero() {
  return (
    <section className="relative w-full min-h-screen overflow-hidden bg-black">
      <PulsingRings />
      <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
        <Image
          src="/33f.png"
          alt="Fox"
          width={400}
          height={400}
          className="object-contain"
        />
        <p className="mt-4 text-white text-lg font-semibold">
          Powered by the <span className="text-orange-400">Advanced Efficient Optimized Network</span>
        </p>
      </div>
    </section>
  );
}
