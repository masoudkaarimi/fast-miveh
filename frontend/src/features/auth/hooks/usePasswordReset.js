"use client";

import {toast} from 'sonner';
import {useRouter} from 'next/navigation';
import {useMutation} from '@tanstack/react-query';

import axios from '@/lib/axios';
import {getErrorMessage, getSuccessMessage} from "@/lib/utils";

// --- Hook to request a password reset for an identifier (email or phone) ---
export const useRequestPasswordReset = () => {
    return useMutation({
        mutationFn: (identifier) => axios.post('/public/password-reset/request', {identifier}),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "If an account with that identifier exists, password reset instructions have been sent."));
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- Hook to confirm password reset using the token from an email link ---
export const useConfirmPasswordReset = () => {
    const router = useRouter();
    return useMutation({
        mutationFn: ({uidb64, token, password}) => axios.post('/public/password-reset/confirm', {uidb64, token, password}),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "Your password has been reset successfully! Please log in."));
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
        mutationFn: ({phone_number, code, password}) => axios.post('/public/password-reset/confirm-otp', {phone_number, code, password}),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "Your password has been reset successfully! Please log in."));
            router.push('/login');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};