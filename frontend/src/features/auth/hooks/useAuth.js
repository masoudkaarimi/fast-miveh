import {useRouter} from 'next/navigation';
import {useMutation, useQueryClient} from '@tanstack/react-query';
import {toast} from 'sonner';

import axios from '@/lib/axios';
import {getErrorMessage, getSuccessMessage} from "@/lib/utils";

// --- Check the status of an identifier (email or phone number) ---
export const useCheckIdentifierStatus = () => {
    return useMutation({
        mutationFn: (identifier) => axios.post('/public/auth/status', {identifier}),
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- Request an OTP for a given phone number ---
export const useRequestOtp = () => {
    return useMutation({
        mutationFn: (phone_number) => axios.post('/public/auth/otp/request', {phone_number}),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "A new OTP has been sent."));
        },
        onError: (error) => {
            const errorData = error.response?.data;
            if (errorData?.cooldown_remaining_seconds) {
                toast.error(errorData.detail);
            } else {
                toast.error(getErrorMessage(error));
            }
        },
    });
};

// --- Verify the OTP and log in the user ---
export const useVerifyOtpAndLogin = () => {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: ({phone_number, code}) => axios.post('/public/auth/otp/verify', {phone_number, code}),
        onSuccess: (response) => {
            const {is_new_user} = response.data;
            toast.success({is_new_user} ? "Welcome! Let's set up your account." : "Welcome back!");
            queryClient.invalidateQueries({queryKey: ['userProfile']});
            router.push('/user');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- User login with identifier and password ---
export const useLoginWithPassword = () => {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: ({identifier, password}) => axios.post('/public/auth/login', {identifier, password}),
        onSuccess: () => {
            toast.success("Successfully logged in!");
            queryClient.invalidateQueries({queryKey: ['userProfile']});
            router.push('/user');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};


export const useLogout = () => {
// Todo
}