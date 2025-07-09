import React from 'react'
import type { Metadata, Viewport } from 'next'
import './globals.css'
import { AuthProvider } from '../contexts'
import QueryProvider from '../providers/QueryProvider'

export const metadata: Metadata = {
  title: {
    default: 'SCADA System',
    template: '%s | SCADA System'
  },
  description: 'Industrial monitoring and data acquisition system for real-time process control and automation',
  keywords: ['SCADA', 'Industrial Control', 'Automation', 'Monitoring', 'Data Acquisition'],
  authors: [{ name: 'SCADA Team' }],
  creator: 'SCADA Team',
  publisher: 'SCADA System',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'SCADA System',
    description: 'Industrial monitoring and data acquisition system',
    siteName: 'SCADA System',
    images: [
      {
        url: '/logo-large.svg',
        width: 120,
        height: 40,
        alt: 'SCADA System Logo',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'SCADA System',
    description: 'Industrial monitoring and data acquisition system',
    images: ['/logo-large.svg'],
  },
  robots: {
    index: true,
    follow: true,
  },
  icons: {
    icon: [
      { url: '/favicon.svg', type: 'image/svg+xml' },
      { url: '/favicon.ico', sizes: 'any' },
    ],
    apple: [
      { url: '/apple-touch-icon.png', sizes: '180x180', type: 'image/png' },
    ],
    shortcut: '/favicon.ico',
  },
  manifest: '/site.webmanifest',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: 'white' },
    { media: '(prefers-color-scheme: dark)', color: 'black' },
  ],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <title>SCADA System</title>
        <meta name="description" content="Industrial monitoring and data acquisition system for real-time process control and automation" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1" />
        <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)" />
        <meta name="theme-color" content="#000000" media="(prefers-color-scheme: dark)" />
        <link rel="icon" href="/favicon.ico" />
        <link rel="icon" href="/favicon.svg" type="image/svg+xml" />
        <link rel="apple-touch-icon" href="/apple-touch-icon.png" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        <QueryProvider>
          <AuthProvider>
            {children}
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  )
} 