"use client";

import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {createContext, useContext, useState, useMemo} from 'react';

import {formatPhoneNumber, getIdentifierType} from "@/lib/utils";
import {IdentifierSchema, ResetPasswordSchema} from "@/lib/validators";
import {useRequestPasswordReset, useConfirmPasswordResetWithOTP} from "@/features/auth/hooks/usePasswordReset";
import {useRouter} from 'next/navigation';

const STEPS = {
    REQUEST: "REQUEST",
    CONFIRM_OTP: "CONFIRM_OTP",
    INFO_SENT: "INFO_SENT",
};

const ForgotPasswordContext = createContext(null);

export const useForgotPasswordFlow = () => {
    const context = useContext(ForgotPasswordContext);
    if (!context) {
        throw new Error("useForgotPasswordFlow must be used within a ForgotPasswordProvider");
    }
    return context;
};

export const ForgotPasswordProvider = ({children}) => {
    const [step, setStep] = useState(STEPS.REQUEST);
    const [identifier, setIdentifier] = useState("");
    const [showPassword, setShowPassword] = useState(false);

    // --- Hooks ---
    const router = useRouter();
    const requestReset = useRequestPasswordReset();
    const confirmWithOtp = useConfirmPasswordResetWithOTP();

    // --- Forms ---
    const identifierForm = useForm({
        resolver: zodResolver(IdentifierSchema),
        defaultValues: {identifier: ""},
    });
    const confirmOtpForm = useForm({
        resolver: zodResolver(ResetPasswordSchema),
        defaultValues: {code: "", password: "", password2: ""},
        mode: "onTouched",
    });

    // --- Handlers ---
    const handleIdentifierSubmit = (data) => {
        const rawIdentifier = data.identifier;
        const identifierType = getIdentifierType(rawIdentifier);
        const formattedIdentifier = formatPhoneNumber(rawIdentifier);
        setIdentifier(rawIdentifier);

        requestReset.mutate(formattedIdentifier, {
            onSuccess: () => {
                if (identifierType === 'phone_number') {
                    setStep(STEPS.CONFIRM_OTP);
                } else {
                    setStep(STEPS.INFO_SENT);
                }
            },
        });
    };

    const handleConfirmOtpSubmit = (data) => {
        const formattedIdentifier = formatPhoneNumber(identifier);
        confirmWithOtp.mutate(
            {phone_number: formattedIdentifier, code: data.code, password: data.password},
            {
                onSuccess: () => {
                    router.push('/login');
                },
                onError: (error) => {
                    confirmOtpForm.setError("code", {type: "server", message: error.response?.data?.detail || "Invalid code or password issue."})
                }
            }
        );
    };

    const tryDifferentAddress = () => {
        setStep(STEPS.REQUEST);
        identifierForm.reset();
        confirmOtpForm.reset();
    };


    const value = useMemo(() => ({
        steps: STEPS,
        step,
        setStep,
        identifier,
        showPassword,
        setShowPassword,
        identifierForm,
        confirmOtpForm,
        requestReset,
        confirmWithOtp,
        handleIdentifierSubmit,
        handleConfirmOtpSubmit,
        tryDifferentAddress
    }), [step, identifier, showPassword]);

    return (
        <ForgotPasswordContext.Provider value={value}>
            {children}
        </ForgotPasswordContext.Provider>
    );
};
