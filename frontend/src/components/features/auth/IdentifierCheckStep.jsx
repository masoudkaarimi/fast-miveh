'use client';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { checkIdentifierStatus, requestOTP } from '@/lib/api';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

const checkAndRequestOtpMutation = async (identifier) => {
    const status = await checkIdentifierStatus(identifier);
    if (status.user_exists && status.has_password) {
        throw { isPasswordFlow: true, identifier };
    }
    await requestOTP(identifier);
    return identifier;
};

export const IdentifierCheckStep = ({ onOtpSent, onPasswordRequired }) => {
    const t = useTranslations('LoginPage');
    const tErrors = useTranslations('Errors');

    const formSchema = z.object({
        identifier: z.string().min(1, { message: tErrors('requiredField') }),
    });

    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: { identifier: "" },
    });

    const mutation = useMutation({
        mutationFn: checkAndRequestOtpMutation,
        onSuccess: onOtpSent,
        onError: (error) => {
            if (error?.isPasswordFlow) {
                onPasswordRequired(error.identifier);
            }
        },
    });

    function onSubmit(values) {
        mutation.mutate(values.identifier);
    }

    return (
        <div className="space-y-4">
            <div className="text-center">
                <h2 className="text-2xl font-bold">{t('title')}</h2>
                <p className="text-muted-foreground">{t('subtitle')}</p>
            </div>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                        control={form.control}
                        name="identifier"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t('identifierLabel')}</FormLabel>
                                <FormControl>
                                    <Input placeholder={t('identifierPlaceholder')} {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    <Button type="submit" className="w-full" disabled={mutation.isPending}>
                        {mutation.isPending ? t('loadingButton') : t('continueButton')}
                    </Button>
                </form>
            </Form>
        </div>
    );
};