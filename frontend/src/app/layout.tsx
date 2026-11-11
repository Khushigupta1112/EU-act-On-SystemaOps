"use client"

import React, { createContext, useContext, useEffect, useState } from "react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import "./globals.css"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <title>SystemaOps — AI Compliance & Governance Control Plane</title>
        <meta name="description" content="Enterprise AI Compliance Orchestration for EU AI Act & Regulatory Governance" />
      </head>
      <body className="bg-slate-950 text-slate-100 min-h-screen antialiased">
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </body>
    </html>
  )
}
