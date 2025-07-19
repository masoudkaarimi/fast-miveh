import {NextResponse} from 'next/server';

const protectedRoutes = [
    '/user',
];
const guestRoutes = [
    '/login',
    // '/password/forgot',
    // '/password/reset'
];

export function middleware(req) {
    const refreshToken = req.cookies.get('refreshToken')?.value;
    const {pathname} = req.nextUrl;


    // Redirect authenticated users from guest routes
    if (refreshToken && guestRoutes.some(path => pathname.startsWith(path))) {
        return NextResponse.redirect(new URL('/user', req.url));
    }

    // Redirect unauthenticated users from protected routes
    if (!refreshToken && protectedRoutes.some(path => pathname.startsWith(path))) {
        return NextResponse.redirect(new URL('/login', req.url));
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        // Match all routes except for static assets and API routes
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ]
};
