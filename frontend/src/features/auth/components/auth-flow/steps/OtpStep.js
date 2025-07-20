"use client";

import {ChevronLeft} from "lucide-react";

import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {useAuthFlow} from "@/features/auth/context/AuthFlowContext";
import {InputOTP, InputOTPGroup, InputOTPSlot} from "@/components/ui/input-otp";
import {Form, FormControl, FormField, FormItem, FormMessage} from "@/components/ui/form";

export function OtpStep() {
    const {otpForm, handleOtpSubmit, verifyOtp, identifier, resendTimer, handleResendOtp, requestOtp, goBackToIdentifier} = useAuthFlow();

    return (
        <>
            <Heading
                title="Enter the confirmation code"
                subtitle={`We sent a code to ${identifier}. Please enter it below to verify your identity.`}
                action={
                    <Button variant="ghost" size="sm" onClick={goBackToIdentifier} className="ps-0 py-0">
                        <ChevronLeft className="size-4"/>Back
                    </Button>
                }
            />
            <Form {...otpForm}>
                <form onSubmit={otpForm.handleSubmit(handleOtpSubmit)} className="space-y-4">
                    <FormField control={otpForm.control} name="code" render={({field}) => (
                        <FormItem className="flex flex-col items-center justify-center">
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
                    <div className="text-center text-sm">
                        {resendTimer > 0 ? (
                            <p className="text-muted-foreground">Resend code in {resendTimer} seconds</p>
                        ) : (
                            <Button type="button" variant="link" size="sm" className="p-0 h-auto" onClick={() => handleResendOtp(identifier)} disabled={requestOtp.isPending}>
                                {requestOtp.isPending ? "Sending..." : "Resend code"}
                            </Button>
                        )}
                    </div>
                    <Button type="submit" disabled={verifyOtp.isPending} className="w-full">
                        {verifyOtp.isPending ? "Verifying..." : "Verify & Login"}
                    </Button>
                </form>
            </Form>
        </>
    );
}
