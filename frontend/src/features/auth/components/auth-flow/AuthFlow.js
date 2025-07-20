"use client";

import {OtpStep} from './steps/OtpStep';
import {PasswordStep} from './steps/PasswordStep';
import {IdentifierStep} from './steps/IdentifierStep';
import {AuthFlowProvider, useAuthFlow} from '@/features/auth/context/AuthFlowContext';

function AuthFlowContent() {
    const {steps, step} = useAuthFlow();

    switch (step) {
        case steps.IDENTIFIER_INPUT:
            return <IdentifierStep/>;
        case steps.OTP_INPUT:
            return <OtpStep/>;
        case steps.PASSWORD_INPUT:
            return <PasswordStep/>;
        default:
            return <IdentifierStep/>;
    }
}

export function AuthFlow() {
    return (
        <AuthFlowProvider>
            <div className="flex flex-col gap-6">
                <AuthFlowContent/>
            </div>
        </AuthFlowProvider>
    );
}