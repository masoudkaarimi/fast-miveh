"use client"

import Link from 'next/link';

export default function UserPage() {
    return (
        <div className="container mx-auto p-4">
            <h1 className="text-xl font-bold">User Page</h1>
            <ul className="my-10 text-lg divide-y divide-gray-300 list-group">
                <li className="py-3"><Link href="/">Home</Link></li>
                <li className="py-3"><Link href="/login">Login</Link></li>
                {/*<li className="py-3"}><Link href="/logout">Logout</Link></li>*/}
                <li className="py-3"><Link href="/password/forgot">Forgot Password</Link></li>
                <li className="py-3"><Link href="/password/reset">Forgot Reset</Link></li>
                <li className="py-3"><Link href="/user/">User</Link></li>
                <li className="py-3"><Link href="/user/set-password">Set Password</Link></li>
                <li className="py-3"><Link href="/user/welcome">Welcome</Link></li>
            </ul>
        </div>
    );
}