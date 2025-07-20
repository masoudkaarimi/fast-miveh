"use client";

import {useEffect} from "react";
import {useRouter, usePathname} from "next/navigation";

import {FullPageSpinner} from "@/components/shared/FullPageSpinner";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";

export default function UserLayout({children}) {
    // --- Hooks ---
    const router = useRouter();
    const pathname = usePathname();
    const {data: userData, isLoading} = useUserProfile();
    const user = userData?.data ?? null;

    useEffect(() => {
        if (isLoading || !user) return; // Wait until user data is loaded

        // User has NO password. They MUST go to the set-password page
        if (!user.has_password && !pathname.includes('/user/set-password')) {
            router.push('/user/set-password');
        }
    }, [isLoading, user, router, pathname]);

    // Show a spinner while checking the user status
    if (isLoading || !user) {
        return <FullPageSpinner/>;
    }

    // If the user has no password and is not on the set-password page, show a spinner
    if (!user.has_password && !pathname.includes('/user/set-password')) {
        return <FullPageSpinner/>;
    }

    return children;
}
