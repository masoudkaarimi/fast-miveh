"use client";

import {RequestStep} from "./steps/RequestStep";
import {InfoSentStep} from "./steps/InfoSentStep";
import {ConfirmOtpStep} from "./steps/ConfirmOtpStep";
import {ForgotPasswordProvider, useForgotPasswordFlow} from "@/features/auth/context/ForgotPasswordContext";

function ForgotPasswordContent() {
    const {step, steps} = useForgotPasswordFlow();

    switch (step) {
        case steps.REQUEST:
            return <RequestStep/>;
        case steps.CONFIRM_OTP:
            return <ConfirmOtpStep/>;
        case steps.INFO_SENT:
            return <InfoSentStep/>;
        default:
            return <RequestStep/>;
    }
}

export function ForgotPasswordFlow() {
    return (
        <ForgotPasswordProvider>
            <div className="flex flex-col gap-6">
                <ForgotPasswordContent/>
            </div>
        </ForgotPasswordProvider>
    );
}
