"use client";

import Header from "@/components/header/Header";
import Sidepanel from "@/components/sidepanel/Sidepanel";
import { SidebarProvider } from "@/components/ui/sidebar";
import PageTransitionProvider from "@/components/providers/page-transition-provider";

export default function MainLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <SidebarProvider className="min-h-screen flex">
      <div>
        <Sidepanel />
      </div>
      <div className="flex-1 flex flex-col h-[100vh] relative overflow-hidden bg-background">
        <div className="flex-shrink-0">
          <Header />
        </div>
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
          <PageTransitionProvider>{children}</PageTransitionProvider>
        </div>
      </div>
    </SidebarProvider>
  );
}
