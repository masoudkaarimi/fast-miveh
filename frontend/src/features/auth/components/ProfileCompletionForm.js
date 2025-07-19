"use client";

import * as z from "zod";
import {useForm} from "react-hook-form";
import {useRouter} from "next/navigation";
import {zodResolver} from "@hookform/resolvers/zod";

import {Input} from "@/components/ui/input";
import {Button} from "@/components/ui/button";
import {Heading} from "@/components/shared/Heading";
import {useUpdateUserProfile} from "@/features/user/profile/hooks/useProfile";
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from "@/components/ui/form";
import Link from "next/link";
import {ChevronLeft} from "lucide-react";

// --- Zod Schemas ---
const profileSchema = z.object({
    first_name: z.string().max(50).optional(),
    last_name: z.string().max(50).optional(),
    // Todo: Add more fields as needed
});

export function ProfileCompletionForm() {
    // --- Hooks ---
    const router = useRouter();
    const updateUserProfile = useUpdateUserProfile();

    // --- Forms ---
    const form = useForm({
        resolver: zodResolver(profileSchema),
        defaultValues: {first_name: "", last_name: ""},
    });

    // --- Handlers ---
    const handleSubmit = (data) => {
        updateUserProfile.mutate(data, {
            onSuccess: () => router.push('/user'),
        });
    };

    return (
        <div className="flex flex-col gap-6">
            <Heading
                title="Complete Your Profile"
                subtitle="This step is optional. You can add your details now or do it later from your dashboard."
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
                    <FormField name="first_name" control={form.control} render={({field}) => (
                        <FormItem>
                            <FormLabel>First Name</FormLabel>
                            <FormControl>
                                <Input autoFocus placeholder="John" {...field} />
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <FormField name="last_name" control={form.control} render={({field}) => (
                        <FormItem>
                            <FormLabel>Last Name</FormLabel>
                            <FormControl>
                                <Input placeholder="Doe" {...field} />
                            </FormControl>
                            <FormMessage/>
                        </FormItem>
                    )}/>
                    <div className="flex flex-col-reverse sm:flex-row flex-wrap gap-2">
                        <Button type="button" variant="outline" onClick={() => router.push('/user')}>
                            Skip for Now
                        </Button>
                        <Button type="submit" disabled={updateUserProfile.isPending} className="flex-grow">
                            {updateUserProfile.isPending ? "Saving..." : "Save and Continue"}
                        </Button>
                    </div>
                </form>
            </Form>
        </div>
    );
}
