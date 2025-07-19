import axios from 'axios';
import {NextResponse} from 'next/server';
import {joinUrlParts} from '@/lib/utils';

const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL;


async function handler(req) {
    const url = new URL(req.url);
    const path = url.pathname.replace('/api/public/', '');
    const isLoginOrVerify = path.startsWith('auth/otp/verify') || path.startsWith('auth/login');

    try {
        const body = req.method !== 'GET' && req.method !== 'DELETE' ? await req.json() : undefined;

        const apiUrl = joinUrlParts(BASE_API_URL, path) + (path.endsWith('/') ? '' : '/');

        const apiResponse = await axios({
            method: req.method,
            url: apiUrl,
            data: body,
            headers: {
                'Content-Type': 'application/json',
            },
        });

        const responseData = apiResponse.data;
        const status = apiResponse.status;

        const response = NextResponse.json(responseData, {status});

        if (isLoginOrVerify && responseData && responseData.refresh_token) {
            response.cookies.set('refreshToken', responseData.refresh_token, {
                httpOnly: true,
                secure: process.env.NODE_ENV === 'production',
                maxAge: 60 * 60 * 24 * 30, // 30 days
                path: '/',
                sameSite: 'lax',
            });
        }

        return response;

    } catch (error) {
        console.error("Proxy Error:", error.response?.data || error.message);
        const status = error.response?.status || 500;
        const data = error.response?.data || {message: 'An unexpected error occurred.'};
        return NextResponse.json(data, {status});
    }
}

export {handler as GET, handler as POST, handler as PATCH, handler as PUT, handler as DELETE};