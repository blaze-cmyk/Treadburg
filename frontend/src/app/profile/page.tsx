"use client";

import React, { useState, useEffect } from "react";
import { useUser } from "@/contexts/UserContext";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea-fix";
import { Separator } from "@/components/ui/separator";
import { useRouter } from "next/navigation";

export default function ProfilePage() {
  const { user, profile, isLoading, isAuthenticated, updateProfile } = useUser();
  const router = useRouter();
  
  const [formData, setFormData] = useState({
    full_name: "",
    bio: "",
    country: "",
    phone: "",
  });
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  // Update form data when profile loads
  useEffect(() => {
    if (profile) {
      setFormData({
        full_name: profile.full_name || "",
        bio: profile.bio || "",
        country: profile.country || "",
        phone: profile.phone || "",
      });
    }
  }, [profile]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    
    try {
      await updateProfile(formData);
      setIsEditing(false);
    } catch (error) {
      console.error("Error updating profile:", error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="container max-w-4xl mx-auto px-4 py-8">
      <div className="bg-card rounded-xl shadow-lg p-6">
        {/* Debug Button */}
        <div className="mb-4 text-right">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              console.log("Current User:", user);
              console.log("Current Profile:", profile);
              alert("Auth & Profile data logged to console. Please check developer tools.");
            }}
          >
            Debug User Info
          </Button>
        </div>
        
        <div className="flex flex-col md:flex-row items-center md:items-start gap-8">
          {/* Profile Avatar */}
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32 rounded-full overflow-hidden border-4 border-primary/20">
              {profile?.avatar_url ? (
                <Image
                  src={profile.avatar_url}
                  alt={profile.full_name || "User avatar"}
                  fill
                  className="object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-primary/30 to-primary/10 text-4xl font-bold text-primary">
                  {profile?.full_name?.charAt(0) || "U"}
                </div>
              )}
            </div>
            
            <div className="text-center mt-4">
              <div className="text-xs text-muted-foreground">Member since</div>
              <div>
                {profile?.created_at 
                  ? new Date(profile.created_at).toLocaleDateString("en-US", { year: "numeric", month: "long" })
                  : "Unknown"}
              </div>
            </div>
          </div>

          {/* Profile Info */}
          <div className="flex-1">
            {isEditing ? (
              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium mb-1">
                    Full Name
                  </label>
                  <Input
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="bio" className="block text-sm font-medium mb-1">
                    Bio
                  </label>
                  <Textarea
                    id="bio"
                    name="bio"
                    value={formData.bio}
                    onChange={handleInputChange}
                    rows={3}
                  />
                </div>
                
                <div>
                  <label htmlFor="country" className="block text-sm font-medium mb-1">
                    Country
                  </label>
                  <Input
                    id="country"
                    name="country"
                    value={formData.country}
                    onChange={handleInputChange}
                  />
                </div>
                
                <div>
                  <label htmlFor="phone" className="block text-sm font-medium mb-1">
                    Phone
                  </label>
                  <Input
                    id="phone"
                    name="phone"
                    type="tel"
                    value={formData.phone}
                    onChange={handleInputChange}
                    placeholder="+1 (123) 456-7890"
                  />
                </div>
                
                <div className="flex justify-end gap-2 pt-4">
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setIsEditing(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isSaving}>
                    {isSaving ? "Saving..." : "Save Changes"}
                  </Button>
                </div>
              </form>
            ) : (
              <div>
                <div className="flex justify-between items-center">
                  <h1 className="text-2xl font-bold">{profile?.full_name}</h1>
                  <Button onClick={() => setIsEditing(true)}>Edit Profile</Button>
                </div>
                
                <div className="text-muted-foreground mb-4">{profile?.email}</div>
                
                <Separator className="my-4" />
                
                <div className="space-y-4">
                  {profile?.bio && (
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Bio</h3>
                      <p className="mt-1">{profile.bio}</p>
                    </div>
                  )}
                  
                  {profile?.country && (
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Country</h3>
                      <p className="mt-1">{profile.country}</p>
                    </div>
                  )}
                  
                  {profile?.phone && (
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Phone</h3>
                      <p className="mt-1">{profile.phone}</p>
                    </div>
                  )}
                  
                  {profile?.subscription_tier && (
                    <div>
                      <h3 className="text-sm font-medium text-muted-foreground">Subscription</h3>
                      <p className="mt-1 capitalize">{profile.subscription_tier}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
