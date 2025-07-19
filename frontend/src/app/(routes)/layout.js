import {Inter} from "next/font/google";

import {routing} from "@/i18n/routing";
import AppProviders from "@/providers/AppProviders";

import "@/styles/globals.css";

const inter = Inter({subsets: ["latin"]});

export function generateStaticParams() {
    return routing.locales.map((locale) => ({locale}));
}

export async function generateMetadata({params}) {
    return {
        title: "Fast Miveh",
        description: "Welcome to Fast Miveh"
    };
}

export default async function RootLayout({children, params}) {
    return (
        <html>
            <body className={inter.className}>
                <AppProviders>
                    {children}
                </AppProviders>
            </body>
        </html>
    );
}