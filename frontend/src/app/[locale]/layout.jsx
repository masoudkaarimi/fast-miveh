import {Inter} from "next/font/google";
import {notFound} from 'next/navigation';

import {hasLocale} from 'next-intl';
import {getMessages, getTranslations} from 'next-intl/server';

import {routing} from '@/i18n/routing';

import Providers from "../providers";

import "../globals.css";

// const t = await getTranslations('HomePage')


const inter = Inter({subsets: ["latin"]});

export const metadata = {
    // title: t('title'),
    // description: t('description'),
};

export default async function RootLayout({children, params}) {
    const messages = await getMessages();
    const {locale} = await params;
    if (!hasLocale(routing.locales, locale)) {
        notFound();
    }

    return (
        <html lang={locale} dir={locale === 'fa' ? 'rtl' : 'ltr'}>
        <body className={inter.className}>
        <Providers locale={locale} messages={messages}>
            <main>{children}</main>
        </Providers>
        </body>
        </html>
    );
}
