import {toast} from 'sonner';
import axios from '@/lib/axios';
import {useRouter} from "next/navigation";
import {useQuery, useMutation, useQueryClient} from '@tanstack/react-query';

import {getErrorMessage, getSuccessMessage} from "@/lib/utils";

// --- Fetches the current user's profile data ---
export const useUserProfile = () => {
    return useQuery({
        queryKey: ['userProfile'],
        queryFn: async () => axios.get('/secure/profile/me'),
        retry: 1,
        staleTime: 1000 * 60 * 5, // 5 minutes
    });
};

// --- Update the user's profile (first name, last name, etc.) ---
export const useUpdateUserProfile = () => {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (profileData) => axios.patch('/secure/profile/me/', profileData),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "Profile updated successfully."));
            queryClient.invalidateQueries({queryKey: ['userProfile']});
        },
        onError: (error) => {
            toast.error(getErrorMessage(error, error.response?.data?.message || "Failed to update profile."));
        }
    });
};

// --- User to set their password for the first time ---
export const useSetPassword = () => {
    const queryClient = useQueryClient();
    const router = useRouter();

    return useMutation({
        mutationFn: (passwords) => axios.post('/secure/profile/set-password/', passwords),
        onSuccess: (response) => {
            toast.success(getSuccessMessage(response, "Password set successfully."));
            toast.info("Please complete your profile.");
            queryClient.invalidateQueries({queryKey: ['userProfile']});
            router.push('/user/welcome?source=set-password');
        },
        onError: (error) => {
            toast.error(getErrorMessage(error));
        }
    });
};

// --- Existing user to change their password ---
export const useChangePassword = () => {
    return useMutation({
        mutationFn: (passwords) => axios.post('/secure/profile/change-password/', passwords),
        onSuccess: () => {
            toast.success("Password changed successfully.");
        },
        onError: (error) => {
            toast.error(error.response?.data?.old_password?.[0] || error.response?.data?.message || "Failed to change password.");
        }
    });
};

// --- Add or change a user's email address ---
export const useAddEmail = () => {
    return useMutation({
        mutationFn: (data) => axios.post('/secure/profile/email/add/', data),
        onSuccess: () => {
            toast.success("Verification email sent. Please check your inbox.");
        },
        onError: (error) => {
            toast.error(error.response?.data?.email?.[0] || "Failed to add email address.");
        }
    });
};

// --- Verify a new email address with an OTP ---
export const useVerifyEmail = () => {
    const queryClient = useQueryClient();
    return useMutation({
        mutationFn: (data) => axios.post('/secure/profile/email/verify/', data),
        onSuccess: () => {
            toast.success("Email address verified successfully!");
            queryClient.invalidateQueries({queryKey: ['userProfile']});
        },
        onError: (error) => {
            toast.error(error.response?.data?.message || "Email verification failed.");
        }
    });
};
