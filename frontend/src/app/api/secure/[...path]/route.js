import axios from 'axios';
import {cookies} from 'next/headers';
import {NextResponse} from 'next/server';
import {joinUrlParts} from '@/lib/utils';

const BASE_API_URL = process.env.NEXT_PUBLIC_API_URL;

async function handler(req) {
    const url = new URL(req.url);
    const path = url.pathname.replace('/api/secure/', '');

    // Change how the cookie is read to be more explicit.
    const {get} = cookies();
    const refreshToken = get('refreshToken')?.value;

    if (!refreshToken) {
        return NextResponse.json({message: 'Not authenticated'}, {status: 401});
    }

    try {
        const refreshUrl = joinUrlParts(BASE_API_URL, '/auth/token/refresh/');
        const refreshResponse = await axios.post(refreshUrl, {
            refresh: refreshToken,
        });
        const {access: accessToken} = refreshResponse.data;

        if (!accessToken) {
            throw new Error('Failed to obtain access token');
        }

        const body = req.method !== 'GET' && req.method !== 'DELETE' ? await req.json() : undefined;
        const apiUrl = joinUrlParts(BASE_API_URL, path) + (path.endsWith('/') ? '' : '/');

        const headers = {
            'Authorization': `Bearer ${accessToken}`,
        };
        if (req.method !== 'GET' && req.method !== 'DELETE') {
            headers['Content-Type'] = 'application/json';
        }

        const apiResponse = await axios({
            method: req.method,
            url: apiUrl,
            data: body,
            headers: headers,
        });

        return NextResponse.json(apiResponse.data, {status: apiResponse.status});

    } catch (error) {
        console.error("[SECURE PROXY ERROR]:", error.response?.data || error.message);
        const status = error.response?.status || 500;
        const data = error.response?.data || {message: 'An unexpected error occurred while proxying the request.'};
        return NextResponse.json(data, {status});
    }
}

export {handler as GET, handler as POST, handler as PATCH, handler as PUT, handler as DELETE};