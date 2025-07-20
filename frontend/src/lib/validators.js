import * as z from "zod";

// --- Schemas for data validation ---
// Schema for email or phone number identifier
export const IdentifierSchema = z.object({
    identifier: z.union([
        z.string().email({message: "Please enter a valid email address."}),
        z.string().regex(/^09\d{9}$/, {message: "Please enter a valid 11-digit mobile number starting with 09."})
    ], {
        errorMap: () => ({message: "Please enter a valid email or phone number."})
    })
});

// Schema for a 6-digit OTP code
export const OtpSchema = z.object({
    code: z.string().min(6, "Code must be 6 digits.")
});

// Schema for login password input
export const LoginPasswordSchema = z.object({
    password: z.string().min(8, "Password must be at least 8 characters.")
});

// Schema for creating/resetting a new, strong password with confirmation
export const NewPasswordSchema = z.object({
    password: z.string()
        .min(8, "Must be at least 8 characters")
        .regex(/[A-Z]/, "Must contain at least one uppercase letter")
        .regex(/[a-z]/, "Must contain at least one lowercase letter")
        .regex(/[0-9]/, "Must contain at least one number")
        .regex(/[!@#$%^&*(),.?":{}|<>]/, "Must contain at least one special character"),
    password2: z.string()
}).refine((data) => data.password === data.password2, {
    message: "Passwords don't match",
    path: ["password2"],
});

// Schema for the password reset form (OTP code + new password)
export const ResetPasswordSchema = NewPasswordSchema.extend({
    code: z.string().min(6, "Code must be 6 digits")
});

// --- Data for UI presentation ---
// Password criteria for UI feedback
export const passwordCriteria = [
    {text: "At least 8 characters", regex: /.{8,}/},
    {text: "At least one uppercase letter", regex: /[A-Z]/},
    {text: "At least one lowercase letter", regex: /[a-z]/},
    {text: "At least one number", regex: /[0-9]/},
    {text: "At least one special character", regex: /[!@#$%^&*(),.?":{}|<>]/},
];