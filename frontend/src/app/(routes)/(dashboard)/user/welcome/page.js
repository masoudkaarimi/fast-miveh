"use client";

import {useEffect} from "react";
import {useRouter} from "next/navigation";

import {FullPageSpinner} from "@/components/shared/FullPageSpinner";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";
import {ProfileCompletionForm} from "@/features/auth/components/ProfileCompletionForm";

export default function WelcomePage() {
    // --- Hooks ---
    const router = useRouter();
    const {data: userData, isLoading} = useUserProfile();
    const user = userData?.data ?? null;

    useEffect(() => {
        if (isLoading || !user) return; // Wait until user data is loaded

        // If the user is loading or has a complete profile, redirect them to the user dashboard
        if (!isLoading && user && user.is_profile_complete) {
            router.push('/user');
        }
    }, [isLoading, user, router]);

    // Show a spinner while checking the user status
    if (isLoading || (user && user.is_profile_complete)) {
        return <FullPageSpinner/>;
    }

    // If the user has an incomplete profile, show the profile completion form
    return (
        <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
            <div className="w-full max-w-sm">
                <ProfileCompletionForm/>
            </div>
        </div>
    );
}
