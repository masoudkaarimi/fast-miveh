"use client";

import Link from "next/link";
import {ChevronLeft, Eye, EyeOff} from "lucide-react";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {InputOTP, InputOTPGroup, InputOTPSlot} from "@/components/ui/input-otp";
import {useForgotPasswordFlow} from "@/features/auth/context/ForgotPasswordContext";
import {PasswordStrengthIndicator} from "@/components/shared/PasswordStrengthIndicator";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import {useWatch} from "react-hook-form";

export function ConfirmOtpStep() {
    const {
        identifier,
        confirmOtpForm,
        handleConfirmOtpSubmit,
        confirmWithOtp,
        showPassword,
        setShowPassword,
    } = useForgotPasswordFlow();

    // Watch the password field for real-time feedback
    const passwordValue = useWatch({
        control: confirmOtpForm.control,
        name: "password"
    });

    return (
        <>
            <Heading
                title="Reset Your Password"
                subtitle={`We've sent a code to ${identifier}. Enter it below and choose a new password.`}
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/login">
                            <ChevronLeft className="size-4"/>
                            Back to Login
                        </Link>
                    </Button>
                }
            />
            <Form {...confirmOtpForm}>
                <form onSubmit={confirmOtpForm.handleSubmit(handleConfirmOtpSubmit)} className="space-y-4">
                    <FormField control={confirmOtpForm.control} name="code" render={({field}) => (
                        <FormItem className="flex flex-col items-center justify-center">
                            <FormLabel>Verification Code</FormLabel>
                            <FormControl>
                                <InputOTP autoFocus maxLength={6} {...field}>
                                    <InputOTPGroup>
                                        {[...Array(6)].map((_, i) => <InputOTPSlot key={i} index={i}/>)}
                                    </InputOTPGroup>
                                </InputOTP>
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <FormField control={confirmOtpForm.control} name="password" render={({field}) => (
                        <FormItem>
                            <FormLabel>New Password</FormLabel>
                            <div className="relative">
                                <FormControl><Input type={showPassword ? "text" : "password"} {...field} /></FormControl>
                                <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground" onClick={() => setShowPassword(p => !p)}>
                                    {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                </div>
                            </div>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <PasswordStrengthIndicator passwordValue={passwordValue}/>
                    <FormField control={confirmOtpForm.control} name="password2" render={({field}) => (
                        <FormItem>
                            <FormLabel>Confirm New Password</FormLabel>
                            <div className="relative">
                                <FormControl><Input type={showPassword ? "text" : "password"} {...field} /></FormControl>
                                <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground" onClick={() => setShowPassword(p => !p)}>
                                    {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                </div>
                            </div>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <Button type="submit" className="w-full" disabled={confirmWithOtp.isPending}>
                        {confirmWithOtp.isPending ? "Resetting..." : "Reset Password"}
                    </Button>
                </form>
            </Form>
        </>
    );
}
