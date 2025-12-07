"use client";

import { motion } from "framer-motion";
import { User, Mail, Calendar, Edit, Save, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useState, useEffect } from "react";
import { useMouseWheelScroll } from "@/hooks/use-mouse-wheel-scroll";
import { useUser } from "@/contexts/UserContext";

export default function ProfilePage() {
  const { profile, updateProfile, getInitials } = useUser();
  const [isEditing, setIsEditing] = useState(false);
  const [editedProfile, setEditedProfile] = useState(profile);

  // Update local state when profile changes
  useEffect(() => {
    setEditedProfile(profile);
  }, [profile]);

  const handleSave = () => {
    updateProfile(editedProfile);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProfile(profile); // Reset to original values
    setIsEditing(false);
  };

  const scrollRef = useMouseWheelScroll<HTMLDivElement>();

  return (
    <div
      ref={scrollRef}
      className="flex-1 flex flex-col h-full overflow-y-auto show-scrollbar-on-hover bg-background"
    >
      <div className="max-w-4xl mx-auto px-4 py-12 w-full">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-2xl font-semibold text-foreground">Profile</h1>
            {!isEditing ? (
              <Button onClick={() => setIsEditing(true)}>
                <Edit className="w-4 h-4 mr-2" />
                Edit Profile
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button variant="outline" onClick={handleCancel}>
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
                <Button onClick={handleSave}>
                  <Save className="w-4 h-4 mr-2" />
                  Save Changes
                </Button>
              </div>
            )}
          </div>
          <p className="text-muted-foreground">
            Manage your personal information and account settings.
          </p>
        </motion.div>

        {/* Profile Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="rounded-2xl p-8 mb-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_18px_40px_rgba(0,0,0,0.6)]"
        >
          <div className="flex items-center gap-6 mb-6">
            <div className="w-24 h-24 rounded-full bg-[var(--tradeberg-accent-color)] flex items-center justify-center text-white text-3xl font-bold shadow-[0_0_0_4px_rgba(16,163,127,0.25)]">
              {getInitials()}
            </div>
            <div className="flex-1">
              {isEditing ? (
                <Input
                  value={editedProfile.name}
                  onChange={(e) =>
                    setEditedProfile({ ...editedProfile, name: e.target.value })
                  }
                  className="text-2xl font-bold mb-2"
                />
              ) : (
                <h2 className="text-xl font-semibold text-foreground mb-2">
                  {profile.name}
                </h2>
              )}
              <div className="flex items-center gap-2 text-muted-foreground">
                <Mail className="w-4 h-4" />
                {isEditing ? (
                  <Input
                    value={editedProfile.email}
                    onChange={(e) =>
                      setEditedProfile({
                        ...editedProfile,
                        email: e.target.value,
                      })
                    }
                    type="email"
                    className="flex-1"
                  />
                ) : (
                  <span>{profile.email}</span>
                )}
              </div>
            </div>
          </div>

          {isEditing ? (
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Bio
                </label>
                <Input
                  value={editedProfile.bio}
                  onChange={(e) =>
                    setEditedProfile({ ...editedProfile, bio: e.target.value })
                  }
                  placeholder="Tell us about yourself"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Location
                </label>
                <Input
                  value={editedProfile.location}
                  onChange={(e) =>
                    setEditedProfile({
                      ...editedProfile,
                      location: e.target.value,
                    })
                  }
                  placeholder="Your location"
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  Website
                </label>
                <Input
                  value={editedProfile.website}
                  onChange={(e) =>
                    setEditedProfile({
                      ...editedProfile,
                      website: e.target.value,
                    })
                  }
                  placeholder="https://yourwebsite.com"
                />
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-foreground">{profile.bio}</p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <span>{profile.location}</span>
                <span>•</span>
                {profile.website && (
                  <a
                    href={profile.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--tradeberg-accent-color)] hover:underline"
                  >
                    {profile.website}
                  </a>
                )}
              </div>
            </div>
          )}
        </motion.div>

        {/* Account Information */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="rounded-2xl p-6 mb-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_16px_32px_rgba(0,0,0,0.55)]"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Account Information
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between py-2 border-b border-border">
              <div className="flex items-center gap-3">
                <User className="w-5 h-5 text-muted-foreground" />
                <span className="text-foreground">Account Type</span>
              </div>
              <span className="text-muted-foreground">Free</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border">
              <div className="flex items-center gap-3">
                <Calendar className="w-5 h-5 text-muted-foreground" />
                <span className="text-foreground">Member Since</span>
              </div>
              <span className="text-muted-foreground">{profile.joinDate}</span>
            </div>
            <div className="flex items-center justify-between py-2">
              <div className="flex items-center gap-3">
                <Mail className="w-5 h-5 text-muted-foreground" />
                <span className="text-foreground">Email Verified</span>
              </div>
              <span className="text-[var(--tradeberg-accent-color)]">Verified</span>
            </div>
          </div>
        </motion.div>

        {/* Preferences */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="rounded-2xl p-6 bg-[var(--tradeberg-card-bg)] border border-[var(--tradeberg-card-border)] shadow-[0_14px_28px_rgba(0,0,0,0.5)]"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">
            Preferences
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-foreground font-medium">
                  Email Notifications
                </p>
                <p className="text-sm text-muted-foreground">
                  Receive email updates about your account
                </p>
              </div>
              <input type="checkbox" defaultChecked className="toggle" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-foreground font-medium">Marketing Emails</p>
                <p className="text-sm text-muted-foreground">
                  Receive updates about new features
                </p>
              </div>
              <input type="checkbox" className="toggle" />
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
