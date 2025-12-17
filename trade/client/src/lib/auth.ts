import GoogleProvider from "next-auth/providers/google"
import { NextAuthOptions } from "next-auth";

export const authOptions:NextAuthOptions = {
    providers: [
        GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID || "",
            clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
            authorization: {
                params: {
                    prompt: "consent",
                    access_type: "offline",
                    response_type: "code"
                }
            }
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
                token.picture = user.image;
            }
            return token;
        },
        async session({ session, token }:any) {
            if (token) {
                session.user.id = token.id as string;
                session.user.email = token.email;
                session.user.name = token.name;
                session.user.image = token.picture;
            }
            return session;
        },
        async signIn({ user, account, profile }:any) {
            // Save user to backend database
            try {
                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
                
                const response = await fetch(`${apiUrl}/api/auth/save-user`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        id: user.id,
                        email: user.email,
                        name: user.name,
                        picture: user.image,
                    }),
                });

                if (!response.ok) {
                    console.error('Failed to save user to backend');
                }
                return true;
            } catch (error) {
                console.error('Error in signIn callback:', error);
                return true; // Still allow sign in even if backend fails
            }
        },
    },

    secret: process.env.NEXTAUTH_SECRET,
    
    pages: {
        signIn: '/login',
        error: '/auth/error',
    }

}

