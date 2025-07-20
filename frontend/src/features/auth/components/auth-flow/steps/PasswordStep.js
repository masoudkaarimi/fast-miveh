"use client";

import Link from "next/link";
import {ChevronLeft, ChevronRight, Eye, EyeOff} from "lucide-react";
import {useAuthFlow} from "@/features/auth/context/AuthFlowContext";
import {Button} from "@/components/ui/button";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import {Heading} from "@/components/shared/Heading";
import {Input} from "@/components/ui/input";
import {getIdentifierType} from "@/lib/utils";

export function PasswordStep() {
    const {
        passwordForm,
        handlePasswordSubmit,
        loginWithPassword,
        identifier,
        showPassword,
        setShowPassword,
        handleResendOtp,
        goBackToIdentifier,
        setStep
    } = useAuthFlow();

    return (
        <>
            <Heading
                title="Enter Your Password"
                subtitle={`Welcome back! Please enter your password for ${identifier}.`}
                action={
                    <Button variant="ghost" size="sm" onClick={goBackToIdentifier} className="ps-0 py-0">
                        <ChevronLeft className="size-4"/>Back
                    </Button>
                }
            />
            <Form {...passwordForm}>
                <form onSubmit={passwordForm.handleSubmit(handlePasswordSubmit)} className="space-y-4">
                    <FormField control={passwordForm.control} name="password" render={({field}) => (
                        <FormItem>
                            <FormLabel>Password</FormLabel>
                            <div className="relative">
                                <FormControl>
                                    <Input autoFocus type={showPassword ? "text" : "password"} {...field} />
                                </FormControl>
                                <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground"
                                     onClick={() => setShowPassword((prev) => !prev)}>
                                    {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                </div>
                            </div>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <div className="flex flex-col items-start">
                        {getIdentifierType(identifier) === 'phone_number' && (
                            <Button
                                type="button"
                                variant="link"
                                size="sm"
                                className="ps-0 py-0"
                                onClick={() => {
                                    handleResendOtp(identifier);
                                    setStep('OTP_INPUT');
                                }}>
                                Login with OTP instead
                                <ChevronRight className="size-4"/>
                            </Button>
                        )}
                        <Button asChild type="button" variant="link" size="sm" className="ps-0 py-0">
                            <Link href="/password/forgot">
                                Forgot password
                                <ChevronRight className="size-4"/>
                            </Link>
                        </Button>
                    </div>
                    <Button type="submit" disabled={loginWithPassword.isPending} className="w-full">
                        {loginWithPassword.isPending ? "Logging in..." : "Login"}
                    </Button>
                </form>
            </Form>
        </>
    );
}
