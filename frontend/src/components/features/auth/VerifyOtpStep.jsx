'use client';
import {useForm} from 'react-hook-form';
import {z} from 'zod';
import {zodResolver} from '@hookform/resolvers/zod';
import {useMutation} from '@tanstack/react-query';
import {verifyOtpAndLogin} from '@/lib/api';
import {useTranslations} from 'next-intl';
import {Button} from '@/components/ui/button';
import {Input} from '@/components/ui/input';
import {Form, FormControl, FormField, FormItem, FormLabel, FormMessage} from '@/components/ui/form';

export const VerifyOtpStep = ({identifier, onLoginSuccess}) => {
    const t = useTranslations('LoginPage');
    const tErrors = useTranslations('Errors');

    const formSchema = z.object({
        code: z.string().min(6, {message: tErrors('invalidOtp')}).max(6),
    });

    const form = useForm({
        resolver: zodResolver(formSchema),
        defaultValues: {code: ""},
    });

    const mutation = useMutation({
        mutationFn: (code) => verifyOtpAndLogin({phone_number: identifier, code}),
        onSuccess: onLoginSuccess,
    });

    function onSubmit(values) {
        mutation.mutate(values.code);
    }

    return (
        <div className="space-y-4">
            <div className="text-center">
                <h2 className="text-2xl font-bold">{t('otpTitle')}</h2>
                <p className="text-muted-foreground">{t('otpSubtitle', {identifier})}</p>
            </div>
            <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                    <FormField
                        control={form.control}
                        name="code"
                        render={({field}) => (
                            <FormItem>
                                <FormLabel>{t('otpInputLabel')}</FormLabel>
                                <FormControl>
                                    <Input placeholder="123456" {...field} />
                                </FormControl>
                                <FormMessage/>
                            </FormItem>
                        )}
                    />
                    <Button type="submit" className="w-full" disabled={mutation.isPending}>
                        {mutation.isPending ? t('loadingButton') : t('otpVerifyButton')}
                    </Button>
                </form>
            </Form>
        </div>
    );
};