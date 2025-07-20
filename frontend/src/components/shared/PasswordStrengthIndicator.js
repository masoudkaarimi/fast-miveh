"use client";

import {CheckCircle2, Circle} from "lucide-react";

import {passwordCriteria} from "@/lib/validators";

export function PasswordStrengthIndicator({passwordValue = ""}) {
    return (
        <div className="space-y-2 pt-2">
            {passwordCriteria.map((criterion, index) => {
                const isMet = criterion.regex.test(passwordValue);
                return (
                    <div key={index} className="flex items-center text-sm">
                        {isMet ? (
                            <CheckCircle2 className="size-4 mr-2 text-green-500"/>
                        ) : (
                            <Circle className="size-4 mr-2 text-muted-foreground"/>
                        )}
                        <span className={isMet ? "text-foreground" : "text-muted-foreground"}>
                            {criterion.text}
                        </span>
                    </div>
                );
            })}
        </div>
    );
}
