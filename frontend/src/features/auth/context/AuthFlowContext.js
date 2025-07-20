"use client";

import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {createContext, useContext, useState, useMemo, useEffect} from 'react';

import {formatPhoneNumber, getErrorMessage, getIdentifierType} from "@/lib/utils";
import {IdentifierSchema, OtpSchema, LoginPasswordSchema} from "@/lib/validators";
import {useCheckIdentifierStatus, useRequestOtp, useVerifyOtpAndLogin, useLoginWithPassword} from "@/features/auth/hooks/useAuth";

const STEPS = {
    IDENTIFIER_INPUT: "IDENTIFIER_INPUT",
    OTP_INPUT: "OTP_INPUT",
    PASSWORD_INPUT: "PASSWORD_INPUT",
};

const AuthFlowContext = createContext(null);

export const useAuthFlow = () => {
    const context = useContext(AuthFlowContext);
    if (!context) {
        throw new Error("useAuthFlow must be used within an AuthFlowProvider");
    }
    return context;
};

export const AuthFlowProvider = ({children}) => {
    const [step, setStep] = useState(STEPS.IDENTIFIER_INPUT);
    const [identifier, setIdentifier] = useState("");
    const [resendTimer, setResendTimer] = useState(0);
    const [showPassword, setShowPassword] = useState(false);

    // --- Timer logic ---
    useEffect(() => {
        if (resendTimer === 0) return;
        const intervalId = setInterval(() => setResendTimer((prev) => (prev > 0 ? prev - 1 : 0)), 1000);
        return () => clearInterval(intervalId);
    }, [resendTimer]);

    // --- Hooks ---
    const checkStatus = useCheckIdentifierStatus();
    const requestOtp = useRequestOtp();
    const verifyOtp = useVerifyOtpAndLogin();
    const loginWithPassword = useLoginWithPassword();

    // --- Forms ---
    const identifierForm = useForm({
        resolver: zodResolver(IdentifierSchema),
        defaultValues: {identifier: ""}
    });
    const otpForm = useForm({
        resolver: zodResolver(OtpSchema),
        defaultValues: {code: ""}
    });
    const passwordForm = useForm({
        resolver: zodResolver(LoginPasswordSchema),
        defaultValues: {password: ""}
    });

    // --- Handlers ---
    const startTimer = (seconds) => setResendTimer(seconds);

    const goBackToIdentifier = () => {
        setResendTimer(0);
        passwordForm.reset();
        otpForm.reset();
        setStep(STEPS.IDENTIFIER_INPUT);
    };

    const handleResendOtp = async (rawIdentifier) => {
        if (resendTimer > 0 || requestOtp.isPending) return;
        // requestOtp.mutate(formatPhoneNumber(rawIdentifier), {
        //     onSuccess: (response) => {
        //         startTimer(response.data.otp_lifetime_seconds);
        //     },
        // });
        try {
            const response = await requestOtp.mutateAsync(formatPhoneNumber(rawIdentifier));
            startTimer(response.data.otp_lifetime_seconds);
        } catch (error) {
            const errorData = error.response?.data;
            if (errorData?.cooldown_remaining_seconds) {
                startTimer(errorData.cooldown_remaining_seconds);
            }
        }
    };

    const handleIdentifierSubmit = async (data) => {
        const rawIdentifier = data.identifier;
        setIdentifier(rawIdentifier);
        checkStatus.mutate(formatPhoneNumber(rawIdentifier), {
            onSuccess: (response) => {
                const {has_password, user_exists} = response.data;
                const identifierType = getIdentifierType(rawIdentifier);

                if (identifierType === 'phone_number') {
                    if (has_password) setStep(STEPS.PASSWORD_INPUT);
                    else {
                        handleResendOtp(rawIdentifier);
                        setStep(STEPS.OTP_INPUT);
                    }
                } else if (identifierType === 'email') {
                    if (user_exists) setStep(STEPS.PASSWORD_INPUT);
                    else identifierForm.setError("identifier", {type: "server", message: "No account found with this email. Please register by phone number."});
                }
            },
            onError: (error) => identifierForm.setError("identifier", {type: "server", message: getErrorMessage(error)}),
        });
    };

    const handleOtpSubmit = (data) => {
        verifyOtp.mutate({phone_number: formatPhoneNumber(identifier), code: data.code}, {
            onError: (error) => otpForm.setError("code", {type: "server", message: error.response?.data?.detail || "Invalid code."}),
        });
    };

    const handlePasswordSubmit = (data) => {
        loginWithPassword.mutate({identifier: formatPhoneNumber(identifier), password: data.password}, {
            onError: (error) => passwordForm.setError("password", {type: "server", message: error.response?.data?.message || "Incorrect password."}),
        });
    };

    // Memoize the context value to prevent unnecessary re-renders
    const value = useMemo(() => ({
        steps: STEPS,
        step,
        setStep,
        identifier,
        resendTimer,
        showPassword,
        setShowPassword,
        checkStatus,
        requestOtp,
        verifyOtp,
        loginWithPassword,
        identifierForm,
        otpForm,
        passwordForm,
        handleIdentifierSubmit,
        handleResendOtp,
        handleOtpSubmit,
        handlePasswordSubmit,
        goBackToIdentifier
    }), [step, identifier, resendTimer, showPassword, setStep]);

    return (
        <AuthFlowContext.Provider value={value}>
            {children}
        </AuthFlowContext.Provider>
    );
};
