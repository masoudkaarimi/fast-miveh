"use client";

import {useEffect} from "react";
import {useRouter, useSearchParams} from "next/navigation";

import {FullPageSpinner} from "@/components/shared/FullPageSpinner";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";
import {ProfileCompletionForm} from "@/features/auth/components/ProfileCompletionForm";

export default function WelcomePage() {
    // --- Hooks ---
    const router = useRouter();
    const searchParams = useSearchParams();
    const {data: userData, isLoading} = useUserProfile();
    const user = userData?.data ?? null;

    useEffect(() => {
        if (isLoading || !user) return; // Wait until user data is loaded

        // Check if the user came from the set-password flow
        const source = searchParams.get('source');
        if (source === 'set-password') {
            return;
        }

        // If the user already has a complete profile, redirect them to the user dashboard
        if (user.is_profile_complete) {
            router.push('/user');
        }
    }, [isLoading, user, router, searchParams]);

    // Show a spinner while checking the user status
    if (isLoading || !user) {
        return <FullPageSpinner/>;
    }

    // If the user is already complete and not coming from set-password, show a spinner while redirecting
    const source = searchParams.get('source');
    if (user.is_profile_complete && source !== 'set-password') {
        return <FullPageSpinner/>; // Show spinner while redirecting
    }

    // If the user is not complete, show the profile completion form
    return (
        <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
            <div className="w-full max-w-sm">
                <ProfileCompletionForm/>
            </div>
        </div>
    );
}
