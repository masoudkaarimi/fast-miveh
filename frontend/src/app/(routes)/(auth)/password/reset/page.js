"use client";

import Link from "next/link";
import {toast} from "sonner";
import {useForm} from "react-hook-form";
import {useEffect, useState} from "react";
import {useSearchParams} from "next/navigation";
import {zodResolver} from "@hookform/resolvers/zod";
import {ChevronLeft, Eye, EyeOff} from "lucide-react";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {NewPasswordSchema} from "@/lib/validators";
import {Heading} from "@/components/shared/Heading";
import {useConfirmPasswordReset} from "@/features/auth/hooks/usePasswordReset";
import {PasswordStrengthIndicator} from "@/components/shared/PasswordStrengthIndicator";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";

export default function ConfirmPasswordResetPage() {
    const [showPassword, setShowPassword] = useState(false);

    // --- Hooks ---
    const searchParams = useSearchParams();
    const confirmReset = useConfirmPasswordReset();

    // --- Extracting uidb64 and token from search params ---
    const uidb64 = searchParams.get('uidb64');
    const token = searchParams.get('token');

    // --- Forms ---
    const form = useForm({
        resolver: zodResolver(NewPasswordSchema),
        defaultValues: {password: "", password2: ""},
        mode: "onTouched"
    });
    const passwordValue = form.watch("password");

    useEffect(() => {
        if (!uidb64 || !token) {
            toast.error("Invalid password reset link.");
        }
    }, [uidb64, token]);

    // --- Handlers ---
    const handleSubmit = (data) => {
        if (!uidb64 || !token) return;

        confirmReset.mutate({uidb64: uidb64, token: token, password: data.password});
    };

    if (!uidb64 || !token) {
        return (
            <div className="flex flex-col gap-6 text-center">
                <Heading
                    title="Invalid Link"
                    subtitle="This password reset link is invalid or has expired. Please request a new one."
                    action={
                        <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                            <Link href="/">
                                <ChevronLeft className="size-4"/>
                                Back to Home
                            </Link>
                        </Button>
                    }
                />
                <Button asChild variant="link">
                    <Link href="/password/forgot">
                        Request New Password Reset
                    </Link>
                </Button>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-6">
            <Heading
                title="Create a New Password"
                subtitle="Please enter a new password for your account."
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/login">
                            <ChevronLeft className="size-4"/>
                            Back to Login
                        </Link>
                    </Button>
                }
            />
            <Form {...form}>
                <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
                    <FormField control={form.control} name="password" render={({field}) => (
                        <FormItem>
                            <FormLabel>New Password</FormLabel>
                            <div className="relative">
                                <FormControl><Input autoFocus type={showPassword ? "text" : "password"} {...field} /></FormControl>
                                <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground"
                                     onClick={() => setShowPassword((prev) => !prev)}>
                                    {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                </div>
                            </div>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <PasswordStrengthIndicator passwordValue={passwordValue}/>
                    <FormField control={form.control} name="password2" render={({field}) => (
                        <FormItem>
                            <FormLabel>Confirm New Password</FormLabel>
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
                    <Button type="submit" className="w-full" disabled={confirmReset.isPending}>
                        {confirmReset.isPending ? "Saving New Password..." : "Reset Password"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
