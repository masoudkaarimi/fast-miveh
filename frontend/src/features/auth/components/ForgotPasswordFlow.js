// features/auth/components/ForgotPasswordFlow.jsx
"use client";

import * as z from "zod";
import {useState} from "react";
import Link from "next/link";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {Eye, EyeOff, ChevronLeft} from "lucide-react";

import {formatPhoneNumber, getIdentifierType} from "@/lib/utils";
import {useRequestPasswordReset, useConfirmPasswordResetWithOTP} from "@/features/auth/hooks/usePasswordReset";
import {Button} from "@/components/ui/button";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import {Input} from "@/components/ui/input";
import {Heading} from "@/components/shared/Heading";
import {InputOTP, InputOTPGroup, InputOTPSlot} from "@/components/ui/input-otp";

// Schemas
const identifierSchema = z.object({
    identifier: z.union([
        z.string().email({message: "Please enter a valid email address."}),
        z.string().regex(/^09\d{9}$/, {message: "Please enter a valid 11-digit mobile number."})
    ], {errorMap: () => ({message: "Please enter a valid email or phone number."})})
});

const confirmOtpSchema = z.object({
    code: z.string().min(6, "Code must be 6 digits"),
    password: z.string()
        .min(8, "Must be at least 8 characters")
        .regex(/[A-Z]/, "Must contain at least one uppercase letter")
        .regex(/[a-z]/, "Must contain at least one lowercase letter")
        .regex(/[0-9]/, "Must contain at least one number"),
    password2: z.string(),
}).refine((data) => data.password === data.password2, {
    message: "Passwords don't match",
    path: ["password2"],
});

const STEPS = {
    REQUEST: "REQUEST",
    CONFIRM_OTP: "CONFIRM_OTP",
    INFO_SENT: "INFO_SENT",
};

export function ForgotPasswordFlow() {
    const [step, setStep] = useState(STEPS.REQUEST);
    const [identifier, setIdentifier] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);

    const requestReset = useRequestPasswordReset();
    const confirmWithOtp = useConfirmPasswordResetWithOTP();

    const identifierForm = useForm({
        resolver: zodResolver(identifierSchema),
        defaultValues: {identifier: ""},
    });
    const confirmOtpForm = useForm({
        resolver: zodResolver(confirmOtpSchema),
        defaultValues: {code: "", password: "", password2: ""},
    });

    const handleIdentifierSubmit = (data) => {
        const id = data.identifier;
        setIdentifier(id);
        const idType = getIdentifierType(id);
        const formattedIdentifier = formatPhoneNumber(id);

        requestReset.mutate(formattedIdentifier, {
            onSuccess: () => {
                if (idType === 'phone_number') {
                    setStep(STEPS.CONFIRM_OTP);
                } else {
                    setStep(STEPS.INFO_SENT);
                }
            },
        });
    };

    const handleConfirmOtpSubmit = (data) => {
        const formattedIdentifier = formatPhoneNumber(identifier);
        confirmWithOtp.mutate({phone_number: formattedIdentifier, code: data.code, password: data.password});
    };

    if (step === STEPS.INFO_SENT) {
        return (
            <div className="text-center space-y-4">
                <Heading title="Check Your Inbox" subtitle={`If an account with that email exists, password reset instructions have been sent to ${identifier}.`}/>
                <Button variant="link" onClick={() => setStep(STEPS.REQUEST)}>Try a different address</Button>
            </div>
        );
    }

    // ResetPasswordForm
    if (step === STEPS.CONFIRM_OTP) {
        return (
            <div className="flex flex-col gap-6">
                <Heading title="Reset Your Password" subtitle={`We've sent a code to ${identifier}. Enter it below and choose a new password.`}/>
                <Form {...confirmOtpForm} key="confirm-password-form">
                    <form onSubmit={confirmOtpForm.handleSubmit(handleConfirmOtpSubmit)} className="space-y-4">
                        <FormField
                            control={confirmOtpForm.control}
                            name="code"
                            render={({field}) => (
                                <FormItem className="flex flex-col items-center justify-center">
                                    <FormLabel>Verification Code</FormLabel>
                                    <FormControl>
                                        <InputOTP maxLength={6} {...field}>
                                            <InputOTPGroup>
                                                <InputOTPSlot index={0}/>
                                                <InputOTPSlot index={1}/>
                                                <InputOTPSlot index={2}/>
                                                <InputOTPSlot index={3}/>
                                                <InputOTPSlot index={4}/>
                                                <InputOTPSlot index={5}/>
                                            </InputOTPGroup>
                                        </InputOTP>
                                    </FormControl>
                                    <FormMessage/>
                                </FormItem>
                            )}
                        />
                        <FormField control={confirmOtpForm.control} name="password" render={({field}) => (
                            <FormItem>
                                <FormLabel>New Password</FormLabel>
                                <div className="relative">
                                    <FormControl><Input type={showPassword ? "text" : "password"} {...field} /></FormControl>
                                    <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground"
                                         onClick={() => setShowPassword((prev) => !prev)}>
                                        {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                    </div>
                                </div>
                                <FormMessage/>
                            </FormItem>
                        )}/>

                        <FormField control={confirmOtpForm.control} name="password2" render={({field}) => (
                            <FormItem>
                                <FormLabel>Confirm New Password</FormLabel>
                                <div className="relative">
                                    <FormControl><Input type={showConfirmPassword ? "text" : "password"} {...field} /></FormControl>
                                    <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground"
                                         onClick={() => setShowConfirmPassword((prev) => !prev)}>
                                        {showConfirmPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                    </div>
                                </div>
                                <FormMessage/>
                            </FormItem>
                        )}/>

                        <Button type="submit" className="w-full" disabled={confirmWithOtp.isPending}>
                            {confirmWithOtp.isPending ? "Resetting..." : "Reset Password"}
                        </Button>
                        <div className="text-center mt-4">
                            <Button asChild variant="link">
                                <Link href="/login">
                                    Cancel and return to Login
                                </Link>
                            </Button>
                        </div>
                    </form>
                </Form>
            </div>
        );
    }

    // ForgotPasswordForm
    return (
        <div className="flex flex-col gap-6">
            <Heading
                title="Forgot Password?"
                subtitle="Enter your email or phone number to reset your password."
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/login">
                            <ChevronLeft className="size-4"/>
                            Back to Login
                        </Link>
                    </Button>
                }
            />
            <Form {...identifierForm} key="forgot-password-form">
                <form onSubmit={identifierForm.handleSubmit(handleIdentifierSubmit)} className="space-y-4">
                    <FormField control={identifierForm.control} name="identifier" render={({field}) => (
                        <FormItem>
                            <FormLabel>Email or Phone Number</FormLabel>
                            <FormControl><Input placeholder="example@domain.com or 0912..." {...field} /></FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <Button type="submit" className="w-full" disabled={requestReset.isPending}>
                        {requestReset.isPending ? "Sending Instructions..." : "Continue"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
