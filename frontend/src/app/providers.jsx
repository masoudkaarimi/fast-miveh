'use client';

import {useState} from 'react';
import {NextIntlClientProvider} from 'next-intl';
import {ReactQueryDevtools} from '@tanstack/react-query-devtools';
import {QueryClient, QueryClientProvider} from '@tanstack/react-query';

import {Toaster} from "@/components/ui/sonner"

export default async function Providers({children, messages, locale}) {
    const [queryClient] = useState(() => new QueryClient());

    return (
        <NextIntlClientProvider locale={locale} messages={messages}>
            <QueryClientProvider client={queryClient}>
                {children}
                <Toaster closeButton />
                <ReactQueryDevtools initialIsOpen={false}/>
            </QueryClientProvider>
        </NextIntlClientProvider>
    );
}