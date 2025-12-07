"use client";

import { motion } from "framer-motion";
import {
  Users,
  UserPlus,
  Crown,
  Shield,
  Mail,
  MoreVertical,
} from "lucide-react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useUser } from "@/contexts/UserContext";

export default function TeamPage() {
  const { profile, getInitials } = useUser();
  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  const mockTeamMembers = [
    {
      id: "1",
      name: profile.name,
      email: profile.email,
      role: "Owner",
      avatar: getInitials(),
      status: "active",
      joined: profile.joinDate,
    },
    {
      id: "2",
      name: "John Doe",
      email: "john@example.com",
      role: "Admin",
      avatar: "J",
      status: "active",
      joined: "Feb 2024",
    },
    {
      id: "3",
      name: "Jane Smith",
      email: "jane@example.com",
      role: "Member",
      avatar: "J",
      status: "active",
      joined: "Mar 2024",
    },
  ];

  const getRoleIcon = (role: string) => {
    switch (role) {
      case "Owner":
        return Crown;
      case "Admin":
        return Shield;
      default:
        return Users;
    }
  };

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
              Team
            </h1>
            <p className="text-muted-foreground">
              Manage your trading team members, share portfolios, and
              collaborate on market analysis.
            </p>
          </div>
          <Button>
            <UserPlus className="w-4 h-4 mr-2" />
            Invite Member
          </Button>
        </motion.div>

        {/* Team Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6"
        >
          <div className="glass-strong rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <Users className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm text-muted-foreground">
                Total Members
              </span>
            </div>
            <p className="text-2xl font-semibold text-foreground">
              {mockTeamMembers.length}
            </p>
          </div>
          <div className="glass-strong rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <Shield className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm text-muted-foreground">Admins</span>
            </div>
            <p className="text-2xl font-semibold text-foreground">
              {mockTeamMembers.filter((m) => m.role === "Admin").length}
            </p>
          </div>
          <div className="glass-strong rounded-2xl p-6">
            <div className="flex items-center gap-3 mb-2">
              <Crown className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
              <span className="text-sm text-muted-foreground">Owners</span>
            </div>
            <p className="text-2xl font-semibold text-foreground">
              {mockTeamMembers.filter((m) => m.role === "Owner").length}
            </p>
          </div>
        </motion.div>

        {/* Team Members List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="glass-strong rounded-2xl p-6"
        >
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Team Members
          </h2>
          <div className="space-y-4">
            {mockTeamMembers.map((member, index) => {
              const RoleIcon = getRoleIcon(member.role);
              return (
                <motion.div
                  key={member.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.1 }}
                  className="flex items-center justify-between p-4 rounded-lg border border-border glass-light hover:bg-opacity-50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-indigo-600 flex items-center justify-center text-white font-bold">
                      {member.avatar}
                    </div>
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold text-foreground">
                          {member.name}
                        </h3>
                        <div className="flex items-center gap-1">
                          <RoleIcon className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                          <span className="text-xs bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 px-2 py-1 rounded">
                            {member.role}
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Mail className="w-3 h-3" />
                        <span>{member.email}</span>
                        <span>•</span>
                        <span>Joined {member.joined}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 px-2 py-1 rounded">
                      {member.status}
                    </span>
                    <button className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg">
                      <MoreVertical className="w-4 h-4 text-muted-foreground" />
                    </button>
                  </div>
                </motion.div>
              );
            })}
          </div>
        </motion.div>

        {/* Invite Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="glass-strong rounded-2xl p-6 mt-6"
        >
          <h2 className="text-lg font-semibold text-foreground mb-4">
            Invite Team Members
          </h2>
          <p className="text-muted-foreground mb-4">
            Invite colleagues to collaborate on your projects. They'll receive
            an email invitation.
          </p>
          <Button>
            <UserPlus className="w-4 h-4 mr-2" />
            Send Invitation
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
