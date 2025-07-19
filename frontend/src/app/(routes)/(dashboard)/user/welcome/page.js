"use client";

import {useEffect} from "react";
import {useRouter} from "next/navigation";

import {FullPageSpinner} from "@/components/shared/FullPageSpinner";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";
import {ProfileCompletionForm} from "@/features/auth/components/ProfileCompletionForm";

export default function WelcomePage() {
    // --- Hooks ---
    const router = useRouter();
    const {data: user, isLoading} = useUserProfile();

    useEffect(() => {
        // If the user is loading or already has a complete profile, redirect them to the user dashboard
        if (!isLoading && user && user.is_profile_complete) {
            router.push('/user');
        }
    }, [isLoading, user, router]);

    // Show a spinner while checking the profile status
    if (isLoading || (user && user.is_profile_complete)) {
        return <FullPageSpinner/>;
    }

    // If the profile is not complete, show the form
    return (
        <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
            <div className="w-full max-w-sm">
                <ProfileCompletionForm/>
            </div>
        </div>
    );
}
