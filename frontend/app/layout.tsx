import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "BIJLI MITRA AI | తెలంగాణ విద్యుత్ బిల్లింగ్ సహాయ వేదిక (TGSPDCL & TGNPDCL)",
  description:
    "Official AI Electricity Billing Assistance & Tariff Transparency Portal for Telangana State Consumers. Grounded in TGERC Retail Supply Tariff Orders.",
  appleWebApp: {
    title: "Bijli Mitra",
    statusBarStyle: "black-translucent",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: "#022c22",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}
