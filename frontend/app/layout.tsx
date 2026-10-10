import type { Metadata } from "next";
import "./globals.css";
export const metadata: Metadata = { title: "ModaMix | Fashion search, made personal", description: "Keep what you love. Find what you'd change." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body>{children}</body></html>; }
