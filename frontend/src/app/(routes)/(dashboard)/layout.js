"use client";

import {useEffect} from "react";
import {useRouter, usePathname} from "next/navigation";

import {FullPageSpinner} from "@/components/shared/FullPageSpinner";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";

export default function UserLayout({children}) {
    const router = useRouter();
    const pathname = usePathname();
    const {data: userData, isLoading} = useUserProfile();
    const user = userData?.data ?? null;

    useEffect(() => {
        if (isLoading || !user) return; // Wait for data, or if no user, do nothing (proxy will handle redirect)

        const onSetPasswordPage = pathname.includes('/user/set-password');
        const onWelcomePage = pathname.includes('/user/welcome');

        // User has NO password. They MUST go to the set-password page
        if (!user.has_password && !onSetPasswordPage) {
            router.push('/user/set-password');
            return;
        }

        // User HAS password, but profile is INCOMPLETE. They must go to the welcome page
        // if (user.has_password && !user.is_profile_complete && !onWelcomePage && !onSetPasswordPage) {
        //     router.push('/user/welcome');
        //     return;
        // }

        // User HAS password AND profile is COMPLETE, but tries to access onboarding pages
        // if (user.has_password && user.is_profile_complete && (onSetPasswordPage || onWelcomePage)) {
        if (user.has_password && (onSetPasswordPage || !onWelcomePage)) {
            router.push('/user'); // Redirect them to the main dashboard
        }

    }, [isLoading, user, router, pathname]);

    // This logic decides what to show while checks are running
    if (isLoading || !user) {
        return <FullPageSpinner/>;
    }
    if (!user.has_password && !pathname.includes('/user/set-password')) {
        return <FullPageSpinner/>;
    }
    // if (user.has_password && !user.is_profile_complete && !pathname.includes('/user/welcome')) {
    //     return <FullPageSpinner/>;
    // }

    // If all checks pass, render the actual page
    return children;
}