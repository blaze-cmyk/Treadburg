import CredentialsProvider from "next-auth/providers/credentials"
import { NextAuthOptions } from "next-auth";
import { supabase } from "@/lib/supabase";

export const authOptions:NextAuthOptions = {
    providers: [
        CredentialsProvider({
            name: "Email",
            credentials: {
                email: { label: "Email", type: "email", placeholder: "Email" },
                password: { label: "Password", type: "password" },
            },
            async authorize(credentials) {
                if (!credentials?.email || !credentials.password) {
                    return null;
                }

                try {
                    // Sign in with Supabase
                    const { data, error } = await supabase.auth.signInWithPassword({
                        email: credentials.email,
                        password: credentials.password,
                    });

                    if (error || !data.user) {
                        console.error("Supabase auth error:", error);
                        return null;
                    }

                    // Return the user data in the format NextAuth expects
                    return {
                        id: data.user.id,
                        email: data.user.email,
                        name: data.user.user_metadata?.name || data.user.email?.split('@')[0],
                        image: data.user.user_metadata?.avatar_url,
                    };
                } catch (e) {
                    console.error("Error during Supabase authentication:", e);
                    return null;
                }
            },
        }),
    ],
    session: {
        strategy: "jwt"
    },
    callbacks: {
        async jwt({ token, user, account }:any) {
            if (user) {
                token.id = user.id;
                token.email = user.email;
                token.name = user.name;
            }
            return token;
        },
        async session({ session, token }:any) {
            if (token) {
                session.user.id = token.id as string;
                session.user.email = token.email;
                session.user.name = token.name;
            }
            return session;
        },
        async signIn({ user, account, profile }:any) {
            // Save user to Supabase when they sign in
            try {
                const { data, error } = await supabase
                    .from('profiles')
                    .upsert({
                        id: user.id,
                        email: user.email,
                        name: user.name,
                        avatar_url: user.image,
                        updated_at: new Date().toISOString()
                    }, {
                        onConflict: 'email'
                    });

                if (error) {
                    console.error('Error saving user to Supabase:', error);
                }
                return true;
            } catch (error) {
                console.error('Error in signIn callback:', error);
                return true; // Still allow sign in even if Supabase fails
            }
        },
    },

    secret: process.env.NEXTAUTH_SECRET

}

