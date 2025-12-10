import Image from "next/image";

// Logo component for the app.
// Uses the PNG file placed in `frontend/public/illuminati-exchange-logo.png`.
// The wrapping div takes `className` so parent controls size (w-32 h-8, etc.).

export default function TradeBerg({ className }: { className?: string }) {
  return (
    <div className={className}>
      <Image
        src="/illuminati-exchange-logo.png"
        alt="TradeBerg logo"
        width={180}
        height={50}
        className="w-full h-full object-contain"
        priority
      />
    </div>
  );
}
