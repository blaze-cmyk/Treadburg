import type { Metadata } from "next";
import { Geist_Mono } from "next/font/google";
import localFont from "next/font/local";
import "./globals.css";
import ThemeProvider from "@/components/providers/theme-provider";
import SmoothScrollProvider from "@/components/providers/smooth-scroll-provider";
import CursorGlowProvider from "@/components/providers/cursor-glow-provider";
import { UserProvider } from "@/contexts/UserContext";

// FK Grotesk as the primary sans font for the entire app.
// We bind it to --font-geist-sans so existing theme config keeps working.
const geistSans = localFont({
  src: [
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Light.otf",
      weight: "300",
      style: "normal",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Regular.otf",
      weight: "400",
      style: "normal",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Medium.otf",
      weight: "500",
      style: "normal",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Bold.otf",
      weight: "700",
      style: "normal",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Black.otf",
      weight: "900",
      style: "normal",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-LightItalic.otf",
      weight: "300",
      style: "italic",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-Italic.otf",
      weight: "400",
      style: "italic",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-MediumItalic.otf",
      weight: "500",
      style: "italic",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-BoldItalic.otf",
      weight: "700",
      style: "italic",
    },
    {
      path: "../../FK-Grotesk-Font-Family/FKGroteskTrial-BlackItalic.otf",
      weight: "900",
      style: "italic",
    },
  ],
  variable: "--font-geist-sans",
  display: "swap",
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "TradeBerg - AI Chat Assistant",
  description:
    "TradeBerg AI Chat Assistant - Your intelligent trading partner for real-time market analysis",
  icons: {
    icon: [
      { url: "/icon.svg", type: "image/svg+xml" },
      { url: "/favicon.ico", sizes: "any" },
    ],
    apple: [{ url: "/apple-icon.png", sizes: "180x180", type: "image/png" }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
        suppressHydrationWarning
      >
        <ThemeProvider>
          <UserProvider>
            <SmoothScrollProvider>
              <CursorGlowProvider>{children}</CursorGlowProvider>
            </SmoothScrollProvider>
          </UserProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
