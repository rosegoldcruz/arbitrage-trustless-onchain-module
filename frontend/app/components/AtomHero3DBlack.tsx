import Image from 'next/image';
import WarpedGrid from './WarpedGrid';

export default function AtomHero3DBlack() {
  return (
    <section className="relative w-full h-[600px] overflow-hidden bg-black">
      <WarpedGrid />
      <div className="absolute inset-0 flex flex-col items-center justify-center z-10">
        <Image
          src="/33f.png"
          alt="Fox"
          width={400}
          height={400}
          className="object-contain"
        />
        <p className="mt-4 text-white text-lg font-semibold">
          Powered by the <span className="text-orange-300">Advanced Efficient Optimized Network</span>
        </p>
      </div>
    </section>
  );
}
