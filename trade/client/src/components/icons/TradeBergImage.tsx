import Image from "next/image";

export default function TradeBergImage({ className }: { className?: string }) {
  // If you have the TradeBerg logo image file, place it in public/logo.png
  // and uncomment the Image component below
  return (
    <div className={className}>
      {/* Option 1: Use SVG (current implementation) */}
      {/* Option 2: Use image file - uncomment below if you have logo.png */}
      {/* 
      <Image
        src="/logo.png"
        alt="TradeBerg Logo"
        width={150}
        height={40}
        className="dark:invert"
        priority
      />
      */}
    </div>
  );
}
