import {Logo} from "@/components/shared/Logo";

export function Heading({title, subtitle, action, has_logo = true}) {
    return (
        <div className="flex flex-col items-center gap-3 relative w-full mb-6">
            {action && <div className="absolute left-0 top-0">{action}</div>}
            {has_logo && <Logo size={60} link="/"/>}
            {title && <h1 className="text-xl font-bold text-center">{title}</h1>}
            {subtitle && <div className="text-center text-sm text-muted-foreground">{subtitle}</div>}
        </div>
    );
}
