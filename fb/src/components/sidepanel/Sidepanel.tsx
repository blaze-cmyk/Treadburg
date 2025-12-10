"use client";

import TradeBerg from "../icons/TradeBerg";
import {
  TrendingUp,
  BarChart3,
  Trash2,
  Pencil,
  User as UserIcon,
  Hexagon,
  CreditCard,
  FileText,
  Settings as SettingsIcon,
  HelpCircle,
  LogOut,
} from "lucide-react";
import Link from "next/link";
import NewChat from "../icons/NewChat";
import Search from "../icons/Search";
import NewProject from "../icons/NewProject";
import clsx from "clsx";
import { useState } from "react";
import { useChats } from "@/hooks/chat";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";
import { useUser } from "@/contexts/UserContext";
import { useRouter } from "next/navigation";

export default function Sidepanel() {
  const [collapsed, setCollapsed] = useState(false);
  const [profileMenuOpen, setProfileMenuOpen] = useState(false);
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingTitle, setEditingTitle] = useState("");
  const { profile, getInitials } = useUser();
  const { chats, deleteChat, renameChat } = useChats();
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("tradeberg-user-profile");
    router.push("/login");
  };

  const startRename = (id: string, currentTitle: string) => {
    setEditingChatId(id);
    setEditingTitle(currentTitle);
  };

  const commitRename = async () => {
    if (!editingChatId) return;
    const title = editingTitle.trim();
    if (title) {
      await renameChat(editingChatId, title);
    }
    setEditingChatId(null);
    setEditingTitle("");
  };

  return (
    <div
      ref={scrollRef}
      className={clsx(
        "bg-[var(--sidebar)] transition-all duration-150 flex flex-col box-border h-[100vh] overflow-y-auto show-scrollbar-on-hover border-r border-[var(--sidebar-border)]",
        collapsed ? "w-[50px]" : "w-[260px]"
      )}
    >
      <div className="sticky top-0 z-1 bg-[var(--sidebar)]">
        <div className="flex items-center px-3 py-3 group">
          <Link
            href="/"
            className={clsx("flex items-center gap-2 cursor-pointer", {
              "group-hover:hidden": collapsed,
            })}
          >
            {/* Logo image */}
            <TradeBerg className="w-8 h-8 text-[var(--sidebar-foreground)]" />
            {/* Brand text next to logo for clearer heading */}
            <span className="text-[var(--sidebar-foreground)] text-lg font-semibold">
              TradeBerg
            </span>
          </Link>
          {/* Collapse / expand toggle stays on the far right */}
          <button
            className={clsx(
              "cursor-pointer ml-auto rounded-full border border-[var(--sidebar-border)] p-1.5 bg-transparent",
              {
                "hidden group-hover:block": collapsed,
              }
            )}
            onClick={() => setCollapsed(!collapsed)}
            aria-label={collapsed ? "Open sidebar" : "Close sidebar"}
          >
            {collapsed ? (
              <>
                {/* Arrow pointing right when collapsed */}
                <img
                  src="/arrow-black.png"
                  alt="Open sidebar"
                  className="block dark:hidden w-3.5 h-3.5"
                />
                <img
                  src="/arrow-white.png"
                  alt="Open sidebar"
                  className="hidden dark:block w-3.5 h-3.5"
                />
              </>
            ) : (
              <>
                {/* Arrow pointing left when expanded */}
                <img
                  src="/arrow-black.png"
                  alt="Close sidebar"
                  className="block dark:hidden w-3.5 h-3.5 rotate-180"
                />
                <img
                  src="/arrow-white.png"
                  alt="Close sidebar"
                  className="hidden dark:block w-3.5 h-3.5 rotate-180"
                />
              </>
            )}
          </button>
        </div>
        <div className="px-2">
          <Link
            href="/"
            className="px-2 rounded-sm flex gap-3 py-2 text-md w-full hover:bg-[var(--sidebar-accent)] text-[var(--sidebar-foreground)]"
          >
            <NewChat className="text-[var(--sidebar-foreground)] w-6 h-6 flex-shrink-0" />
            <span
              className={clsx("text-[var(--sidebar-foreground)]", {
                hidden: collapsed,
              })}
            >
              New chat
            </span>
          </Link>
          <Link
            href="/search"
            className="px-2 rounded-sm flex gap-3 py-2 text-md w-full hover:bg-[var(--sidebar-accent)] text-[var(--sidebar-foreground)]"
          >
            <Search className="text-[var(--sidebar-foreground)] w-6 h-6 flex-shrink-0" />
            <span
              className={clsx("text-[var(--sidebar-foreground)]", {
                hidden: collapsed,
              })}
            >
              Search
            </span>
          </Link>
          <Link
            href="/trade"
            className="px-2 rounded-sm flex gap-3 py-2 text-md w-full hover:bg-[var(--sidebar-accent)] text-[var(--sidebar-foreground)]"
          >
            <TrendingUp className="text-[var(--sidebar-foreground)] w-6 h-6 flex-shrink-0" />
            <span
              className={clsx("text-[var(--sidebar-foreground)]", {
                hidden: collapsed,
              })}
            >
              Trade
            </span>
          </Link>
          <Link
            href="/charts"
            className="px-2 rounded-sm flex gap-3 py-2 text-md w-full hover:bg-[var(--sidebar-accent)] text-[var(--sidebar-foreground)]"
          >
            <BarChart3 className="text-[var(--sidebar-foreground)] w-6 h-6 flex-shrink-0" />
            <span
              className={clsx("text-[var(--sidebar-foreground)]", {
                hidden: collapsed,
              })}
            >
              Historical charts
            </span>
          </Link>
        </div>
      </div>

      <div
        className={clsx({
          hidden: collapsed,
        })}
      >
        <div className="my-6 mx-2">
          <div className="px-2 rounded-sm flex gap-3 py-2 text-md w-full text-[var(--sidebar-foreground)] opacity-60 cursor-not-allowed">
            <NewProject className="text-[var(--sidebar-foreground)] w-6 h-6" />
            <div className="flex items-center gap-2">
              <span className="text-[var(--sidebar-foreground)]">
                New Project
              </span>
              <span className="text-xs text-[var(--sidebar-foreground)] opacity-50">
                - Coming soon
              </span>
            </div>
          </div>
        </div>
        <div className="my-6 mx-2">
          <p className="px-2 text-[var(--sidebar-foreground)] opacity-60 text-sm font-semibold tracking-wide uppercase">
            Chats
          </p>
          <div className="mt-2">
            {Array.isArray(chats) && chats.length > 0 ? (
              chats.map((element: any) => (
                <div
                  key={element.id}
                  className="group flex items-center px-2 py-2 rounded-md text-sm hover:bg-[var(--sidebar-accent)] text-[var(--sidebar-foreground)] cursor-pointer"
                  onClick={() => router.push(`/c/${element.id}`)}
                  onDoubleClick={(e) => {
                    e.stopPropagation();
                    startRename(element.id, element.title);
                  }}
                >
                  <div className="flex-1 min-w-0">
                    {editingChatId === element.id ? (
                      <input
                        value={editingTitle}
                        onChange={(e) => setEditingTitle(e.target.value)}
                        onBlur={commitRename}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") {
                            e.preventDefault();
                            commitRename();
                          } else if (e.key === "Escape") {
                            setEditingChatId(null);
                            setEditingTitle("");
                          }
                        }}
                        autoFocus
                        className="w-full bg-transparent outline-none text-[var(--sidebar-foreground)] text-sm"
                      />
                    ) : (
                      <p className="truncate text-sm">
                        {element.title || "New Chat"}
                      </p>
                    )}
                  </div>
                  {editingChatId !== element.id && (
                    <div className="flex items-center gap-1 ml-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <button
                        aria-label="Rename chat"
                        className="text-[var(--sidebar-foreground)] hover:opacity-80"
                        onClick={(e) => {
                          e.stopPropagation();
                          startRename(element.id, element.title);
                        }}
                      >
                        <Pencil className="w-3.5 h-3.5" />
                      </button>
                      <button
                        aria-label="Delete chat"
                        className="text-[var(--sidebar-foreground)] hover:text-red-500"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteChat(element.id);
                        }}
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <p className="px-2 text-[var(--sidebar-foreground)] opacity-40 text-sm">
                No chats yet. Start a new conversation!
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="sticky bottom-0 bg-[var(--sidebar)] flex-0 inset-0 mt-auto border-t border-[var(--sidebar-border)] p-2 relative">
        {!collapsed && profileMenuOpen && (
          <div className="absolute bottom-14 left-2 right-2 rounded-2xl border border-[var(--sidebar-border)] bg-[var(--sidebar)] shadow-xl py-2">
            <div className="px-3 pb-2 flex items-center gap-2 text-xs text-[var(--sidebar-foreground)] opacity-80">
              <UserIcon className="w-4 h-4" />
              <span className="truncate">{profile.email}</span>
            </div>
            <div className="h-px bg-[var(--sidebar-border)] mx-2 mb-1" />

            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)]"
              onClick={() => {
                setProfileMenuOpen(false);
                router.push("/pricing");
              }}
            >
              <Hexagon className="w-4 h-4" />
              Upgrade plan
            </button>
            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)]"
              onClick={() => {
                setProfileMenuOpen(false);
                router.push("/billing");
              }}
            >
              <CreditCard className="w-4 h-4" />
              Billing
            </button>
            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)]"
              onClick={() => {
                setProfileMenuOpen(false);
                router.push("/library");
              }}
            >
              <FileText className="w-4 h-4" />
              Strategy instruction
            </button>
            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)]"
              onClick={() => {
                setProfileMenuOpen(false);
                router.push("/profile");
              }}
            >
              <SettingsIcon className="w-4 h-4" />
              Settings
            </button>
            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)]"
              onClick={() => {
                setProfileMenuOpen(false);
                router.push("/help");
              }}
            >
              <HelpCircle className="w-4 h-4" />
              Help
            </button>

            <div className="h-px bg-[var(--sidebar-border)] mx-2 my-1" />

            <button
              className="w-full flex items-center gap-2 px-3 py-1.5 text-sm text-red-500 hover:bg-red-500/10"
              onClick={handleLogout}
            >
              <LogOut className="w-4 h-4" />
              Log out
            </button>
          </div>
        )}

        <div className="flex items-center justify-between">
          <button
            type="button"
            onClick={() => setProfileMenuOpen((open) => !open)}
            className="flex gap-2 items-center hover:opacity-80 transition-opacity flex-1 text-left"
          >
            <div className="rounded-[100%] w-7 h-7 bg-blue-400 text-white flex items-center justify-center flex-shrink-0">
              {getInitials()}
            </div>
            <div
              className={clsx("flex flex-col gap-.5 flex-shrink-0", {
                hidden: collapsed,
              })}
            >
              <span className="text-sm text-[var(--sidebar-foreground)]">
                {profile.name}
              </span>
              <span className="text-xs text-[var(--sidebar-foreground)] opacity-60">
                Free
              </span>
            </div>
          </button>
          <div
            className={clsx("pr-2", {
              hidden: collapsed,
            })}
          >
            <button
              type="button"
              onClick={() => router.push("/pricing")}
              className="px-2 py-1 bg-[var(--card)] rounded-2xl border border-[var(--border)] outline-0 text-xs font-medium cursor-pointer text-[var(--foreground)] hover:opacity-80 transition-opacity"
            >
              Upgrade to Pro
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
