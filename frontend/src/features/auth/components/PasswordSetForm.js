"use client";

import Link from "next/link";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {ChevronLeft, Eye, EyeOff} from "lucide-react";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {NewPasswordSchema} from "@/lib/validators";
import {useSetPassword} from "@/features/user/profile/hooks/useProfile";
import {PasswordStrengthIndicator} from "@/components/shared/PasswordStrengthIndicator";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";


export function PasswordSetForm() {
    const [showPassword, setShowPassword] = useState(false);

    // --- Hooks ---
    const setPassword = useSetPassword();

    // --- Forms ---
    const form = useForm({
        resolver: zodResolver(NewPasswordSchema),
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
                    <PasswordStrengthIndicator passwordValue={passwordValue}/>
                    <FormField control={form.control} name="password2" render={({field}) => (
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
                    )}/>
                    <Button type="submit" disabled={setPassword.isPending} className="w-full">
                        {setPassword.isPending ? "Setting Password..." : "Set Password and Continue"}
                    </Button>
                </form>
            </Form>
        </div>
    );
}
