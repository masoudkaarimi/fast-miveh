"use client";

import Link from "next/link";
import {ChevronLeft} from "lucide-react";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {useAuthFlow} from "@/features/auth/context/AuthFlowContext";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";

export function IdentifierStep() {
    const {identifierForm, handleIdentifierSubmit, checkStatus} = useAuthFlow();

    return (
        <>
            <Heading
                title="Welcome to Fast Miveh"
                subtitle="Enter your email or phone number to continue."
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/"><ChevronLeft className="size-4"/>Back</Link>
                    </Button>
                }
            />
            <Form {...identifierForm}>
                <form onSubmit={identifierForm.handleSubmit(handleIdentifierSubmit)} className="space-y-4">
                    <FormField control={identifierForm.control} name="identifier" render={({field}) => (
                        <FormItem>
                            <FormLabel>Email or Phone Number</FormLabel>
                            <FormControl>
                                <Input autoFocus placeholder="example@domain.com or 0912..." {...field} />
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <Button type="submit" disabled={checkStatus.isPending} className="w-full">
                        {checkStatus.isPending ? "Checking..." : "Continue"}
                    </Button>
                </form>
            </Form>

            {/* Todo: Login with social media like google */}
        </>
    );
}
