"use client";

import {PasswordSetForm} from "@/features/auth/components/PasswordSetForm";
import {useUserProfile} from "@/features/user/profile/hooks/useProfile";
import {useRouter} from "next/navigation";
import {useEffect} from "react";
import {FullPageSpinner} from "@/components/shared/FullPageSpinner";

export default function SetPasswordPage() {
    // --- Hooks ---
    const router = useRouter();
    const {data: userData, isLoading} = useUserProfile();
    const user = userData?.data ?? null;

    useEffect(() => {
        if (isLoading || !user) return; // Wait until user data is loaded

        // If the user is loading or already has a password, redirect them to the user dashboard
        if (!isLoading && user && user.has_password) {
            router.push('/user');
        }
    }, [isLoading, user, router]);

    // Show a spinner while checking the user status
    if (isLoading || (user && user.has_password)) {
        return <FullPageSpinner/>;
    }

    // If the user has no password, show the set password form
    return (
        <div className="bg-background flex min-h-svh flex-col items-center justify-center gap-6 p-6 md:p-10">
            <div className="w-full max-w-sm">
                <PasswordSetForm/>
            </div>
        </div>
    );
}
