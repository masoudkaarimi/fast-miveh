'use client';

import {useEffect, useState} from 'react';
import {useLocale} from 'next-intl';
import {useRouter} from '@/i18n/navigation';

import {VerifyOtpStep} from '@/components/features/auth/VerifyOtpStep';
import {LoginPasswordStep} from '@/components/features/auth/LoginPasswordStep';
import {IdentifierCheckStep} from '@/components/features/auth/IdentifierCheckStep';

export default function LoginPage() {
    const [step, setStep] = useState('identifier_check');
    const [identifier, setIdentifier] = useState('');
    const router = useRouter();
    const locale = useLocale();

    const handleGoToOtp = (id) => {
        setIdentifier(id);
        setStep('otp_verify');
    };

    const handleGoToPassword = (id) => {
        setIdentifier(id);
        setStep('password_login');
    };

    const handleLoginSuccess = (data) => {
        console.log("Login successful!", data);
        router.push(`/${locale}/`);
    };

    const renderStep = () => {
        switch (step) {
            case 'identifier_check':
                return <IdentifierCheckStep onOtpSent={handleGoToOtp} onPasswordRequired={handleGoToPassword}/>;
            case 'otp_verify':
                return <VerifyOtpStep identifier={identifier} onLoginSuccess={handleLoginSuccess}/>;
            case 'password_login':
                return <LoginPasswordStep identifier={identifier} onLoginSuccess={handleLoginSuccess}/>;
            default:
                return <IdentifierCheckStep onOtpSent={handleGoToOtp} onPasswordRequired={handleGoToPassword}/>;
        }
    };

    return renderStep();
}