"use client";

import Link from "next/link";
import {ChevronLeft} from "lucide-react";

import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {useForgotPasswordFlow} from "@/features/auth/context/ForgotPasswordContext";

export function InfoSentStep() {
    const {identifier, tryDifferentAddress} = useForgotPasswordFlow();

    return (
        <div className="text-center space-y-4">
            <Heading
                title="Check Your Inbox"
                subtitle={`If an account with that email exists, password reset instructions have been sent to ${identifier}.`}
                action={
                    <Button asChild variant="ghost" size="sm" className="ps-0 py-0">
                        <Link href="/">
                            <ChevronLeft className="size-4"/>
                            Back to Home
                        </Link>
                    </Button>
                }
            />
            <Button variant="link" onClick={tryDifferentAddress}>
                Try a different address
            </Button>
        </div>
    );
}
