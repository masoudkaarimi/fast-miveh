"use client";

import {useMutation} from '@tanstack/react-query';
import {useRouter} from 'next/navigation';
import {toast} from 'sonner';
import axios from '@/lib/axios';
import {getErrorMessage, getSuccessMessage} from "@/lib/utils";

// --- Hook to request a password reset for an identifier (email or phone) ---
export const useRequestPasswordReset = () => {
    return useMutation({
        mutationFn: (identifier) => axios.post('/public/password-reset/request', {identifier}),
        // onSuccess: (response) => {
        //     toast.success(getSuccessMessage(response, ""));
        // },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- Hook to confirm password reset using the token from an email link ---
export const useConfirmPasswordReset = () => {
    const router = useRouter();
    return useMutation({
        mutationFn: (data) => axios.post('/public/password-reset/confirm', data),
        onSuccess: () => {
            toast.success("Your password has been reset successfully! Please log in.");
            router.push('/login');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- Hook to confirm password reset using an OTP from SMS ---
export const useConfirmPasswordResetWithOTP = () => {
    const router = useRouter();
    return useMutation({
        mutationFn: (data) => axios.post('/public/password-reset/confirm-otp', data),
        onSuccess: () => {
            toast.success("Your password has been reset successfully! Please log in.");
            router.push('/login');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};