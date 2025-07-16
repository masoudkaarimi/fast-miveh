'use client';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { loginWithPassword } from '@/lib/api';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';

export const LoginPasswordStep = ({ identifier, onLoginSuccess }) => {
    const t = useTranslations('LoginPage');
    const tErrors = useTranslations('Errors');

    const formSchema = z.object({
        password: z.string().min(1, { message: tErrors('requiredField') }),
    });

    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: { password: "" },
    });

    const mutation = useMutation({
        mutationFn: (password) => loginWithPassword({ identifier, password }),
        onSuccess: onLoginSuccess,
    });

    function onSubmit(values) {
        mutation.mutate(values.password);
    }

    return (
        <div className="space-y-4">
            <div className="text-center">
                <h2 className="text-2xl font-bold">{t('passwordTitle')}</h2>
                <p className="text-muted-foreground">{t('passwordSubtitle', { identifier })}</p>
            </div>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                        control={form.control}
                        name="password"
                        render={({ field }) => (
                            <FormItem>
                                <FormLabel>{t('passwordLabel')}</FormLabel>
                                <FormControl>
                                    <Input type="password" {...field} />
                                </FormControl>
                                <FormMessage />
                            </FormItem>
                        )}
                    />
                    {mutation.isError && <p className="text-sm text-destructive">{tErrors('invalidCredentials')}</p>}
                    <Button type="submit" className="w-full" disabled={mutation.isPending}>
                        {mutation.isPending ? t('loadingButton') : t('passwordLoginButton')}
                    </Button>
                </form>
            </Form>
        </div>
    );
};