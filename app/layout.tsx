import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'TRACEBACK — AI Production Incident Investigation',
  description: 'Find what changed. Fix what broke.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" data-theme="dark">
      <body className="bg-[#0B0F19] text-textPrimary min-h-screen">
        {children}
      </body>
    </html>
  );
}
