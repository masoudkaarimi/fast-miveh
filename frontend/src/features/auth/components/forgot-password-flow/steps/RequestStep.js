"use client";

import Link from "next/link";
import { ChevronLeft } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Heading } from "@/components/shared/Heading";
import { useForgotPasswordFlow } from "@/features/auth/context/ForgotPasswordContext";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";

export function RequestStep() {
    const { identifierForm, handleIdentifierSubmit, requestReset } = useForgotPasswordFlow();

    return (
        <>
            <Heading
                title="Forgot Password?"
                subtitle="Enter your email or phone number to reset your password."
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/login">
                            <ChevronLeft className="size-4" />
                            Back to Login
                        </Link>
                    </Button>
                }
            />
            <Form {...identifierForm}>
                <form onSubmit={identifierForm.handleSubmit(handleIdentifierSubmit)} className="space-y-4">
                    <FormField control={identifierForm.control} name="identifier" render={({ field }) => (
                        <FormItem>
                            <FormLabel>Email or Phone Number</FormLabel>
                            <FormControl><Input autoFocus placeholder="example@domain.com or 0912..." {...field} /></FormControl>
                            <FormMessage />
                        </FormItem>
                    )} />
                    <Button type="submit" className="w-full" disabled={requestReset.isPending}>
                        {requestReset.isPending ? "Sending Instructions..." : "Continue"}
                    </Button>
                </form>
            </Form>
        </>
    );
}
