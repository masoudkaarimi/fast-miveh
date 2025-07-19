"use client";

import * as z from "zod";
import Link from "next/link";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {CheckCircle2, Circle, ChevronLeft, Eye, EyeOff} from "lucide-react";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {useSetPassword} from "@/features/user/profile/hooks/useProfile";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";

// --- Zod Schemas ---
const passwordSetSchema = z.object({
    password: z.string()
        .min(8, "Must be at least 8 characters")
        .regex(/[A-Z]/, "Must contain at least one uppercase letter")
        .regex(/[a-z]/, "Must contain at least one lowercase letter")
        .regex(/[0-9]/, "Must contain at least one number"),
    password2: z.string()
}).refine((data) => data.password === data.password2, {
    message: "Passwords don't match",
    path: ["password2"],
});

// --- Password Criteria ---
const passwordCriteria = [
    {text: "At least 8 characters", regex: /.{8,}/},
    {text: "At least one uppercase letter", regex: /[A-Z]/},
    {text: "At least one lowercase letter", regex: /[a-z]/},
    {text: "At least one number", regex: /[0-9]/},
];

export function PasswordSetForm() {
    const [showPassword, setShowPassword] = useState(false);

    // --- Hooks ---
    const setPassword = useSetPassword();

    // --- Forms ---
    const form = useForm({
        resolver: zodResolver(passwordSetSchema),
        defaultValues: {password: "", password2: ""},
        mode: "onTouched",
    });
    const passwordValue = form.watch("password"); // Watch the password field for real-time feedback

    // --- Handlers ---
    const handleSubmit = (data) => {
        setPassword.mutate(data);
    };

    return (
        <div className="flex flex-col gap-6">
            <Heading
                title="Set Your Password"
                subtitle="To access your dashboard, you must set a password for your account."
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/">
                            <ChevronLeft className="size-4"/>
                            Back to Home
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

                    {/* Real-time Password Strength Indicator */}
                    <div className="space-y-2">
                        {passwordCriteria.map((criterion, index) => {
                            const isMet = criterion.regex.test(passwordValue || "");
                            return (
                                <div key={index} className="flex items-center text-sm">
                                    {isMet ? (
                                        <CheckCircle2 className="size-4 mr-2 text-green-500"/>
                                    ) : (
                                        <Circle className="size-4 mr-2 text-muted-foreground"/>
                                    )}
                                    <span className={isMet ? "text-foreground" : "text-muted-foreground"}>{criterion.text}</span>
                                </div>
                            );
                        })}
                    </div>

                    <FormField
                        control={form.control}
                        name="password2"
                        render={({field}) => (
                            <FormItem>
                                <FormLabel>Confirm New Password</FormLabel>
                                <div className="relative">
                                    <FormControl>
                                        <Input type={showPassword ? "text" : "password"} {...field} />
                                    </FormControl>
                                    <div className="absolute inset-y-0 right-0 flex cursor-pointer items-center p-3 text-muted-foreground"
                                         onClick={() => setShowPassword((prev) => !prev)}>
                                        {showPassword ? <EyeOff className="size-4"/> : <Eye className="size-4"/>}
                                    </div>
                                </div>
                                <FormMessage/>
                            </FormItem>
                        )}
                    />

                    <Button type="submit" disabled={setPassword.isPending} className="w-full">
                        {setPassword.isPending ? "Setting Password..." : "Set Password and Continue"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
