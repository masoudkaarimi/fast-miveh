"use client";

import * as z from "zod";
import {useEffect, useState} from "react";
import {useForm} from "react-hook-form";
import {useSearchParams} from "next/navigation";
import {zodResolver} from "@hookform/resolvers/zod";
import {toast} from "sonner";
import {Eye, EyeOff} from "lucide-react";

import {useConfirmPasswordReset} from "@/features/auth/hooks/usePasswordReset";
import {Button} from "@/components/ui/button";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import {Input} from "@/components/ui/input";
import {Heading} from "@/components/shared/Heading";

const passwordSchema = z.object({
    password: z.string().min(8, "Password must be at least 8 characters"),
});

export default function ConfirmPasswordResetPage() {
    const searchParams = useSearchParams();
    const confirmReset = useConfirmPasswordReset();
    const [showPassword, setShowPassword] = useState(false);

    const uid = searchParams.get('uidb64');
    const token = searchParams.get('token');

    const form = useForm({
        resolver: zodResolver(passwordSchema),
        defaultValues: {password: ""},
    });

    useEffect(() => {
        if (!uid || !token) {
            toast.error("Invalid password reset link.");
        }
    }, [uid, token]);

    const handleSubmit = (data) => {
        if (!uid || !token) return;
        confirmReset.mutate({uidb64: uid, token: token, password: data.password});
    };

    if (!uid || !token) {
        return (
            <Heading title="Invalid Link" subtitle="This password reset link is invalid or has expired. Please request a new one."/>
        );
    }

    return (
        <div className="flex flex-col gap-6">
            <Heading title="Create a New Password" subtitle="Please enter a new password for your account."/>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
                    <FormField control={form.control} name="password" render={({field}) => (
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
                    <Button type="submit" className="w-full" disabled={confirmReset.isPending}>
                        {confirmReset.isPending ? "Saving New Password..." : "Reset Password"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
