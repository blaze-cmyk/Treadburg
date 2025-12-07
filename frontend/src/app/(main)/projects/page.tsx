"use client";

import { motion } from "framer-motion";
import { FolderPlus, Folder, Calendar, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";

const mockProjects = [
  {
    id: "1",
    name: "Tech Stocks Portfolio",
    description: "Long-term investment strategy for tech sector",
    status: "active",
    members: 3,
    lastUpdated: "2 days ago",
  },
  {
    id: "2",
    name: "Crypto Trading Bot",
    description: "Automated trading strategy for cryptocurrency markets",
    status: "planning",
    members: 5,
    lastUpdated: "1 week ago",
  },
  {
    id: "3",
    name: "Options Strategy Analysis",
    description: "Q1 options trading strategies and performance",
    status: "completed",
    members: 4,
    lastUpdated: "3 weeks ago",
  },
];

export default function ProjectsPage() {
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-6xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="flex items-center justify-between mb-8"
        >
          <div>
            <h1 className="text-2xl font-semibold text-foreground mb-2">
              Trading Projects
            </h1>
            <p className="text-muted-foreground">
              Organize and manage your trading portfolios, strategies, and
              market analysis projects.
            </p>
          </div>
          <Button>
            <FolderPlus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {mockProjects.map((project, index) => {
            const statusColors = {
              active:
                "bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400",
              planning:
                "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-600 dark:text-yellow-400",
              completed:
                "bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400",
            };

            return (
              <motion.div
                key={project.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="glass-strong rounded-2xl p-6 hover:scale-105 transition-transform cursor-pointer"
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="p-3 rounded-lg bg-indigo-100 dark:bg-indigo-900/30">
                    <Folder className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-foreground mb-1">
                      {project.name}
                    </h3>
                    <span
                      className={`text-xs px-2 py-1 rounded ${
                        statusColors[
                          project.status as keyof typeof statusColors
                        ]
                      }`}
                    >
                      {project.status}
                    </span>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-4">
                  {project.description}
                </p>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    <span>{project.members}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    <span>{project.lastUpdated}</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>

        {mockProjects.length === 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="text-center py-12"
          >
            <Folder className="w-16 h-16 text-muted-foreground mx-auto mb-4 opacity-50" />
            <p className="text-muted-foreground mb-4">No projects yet</p>
            <Button>
              <FolderPlus className="w-4 h-4 mr-2" />
              Create Your First Project
            </Button>
          </motion.div>
        )}
      </div>
    </div>
  );
}
