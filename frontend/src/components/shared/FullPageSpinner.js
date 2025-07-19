import {Logo} from "@/components/shared/Logo";

export function FullPageSpinner() {
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
            <div className="flex flex-col items-center gap-6">
                <Logo size={60} link="/"/>

                <div className="flex space-x-2">
                    <div
                        className="w-3 h-3 rounded-full bg-primary animate-pulse-dot"
                        style={{animationDelay: '-0.32s'}}
                    ></div>
                    <div
                        className="w-3 h-3 rounded-full bg-primary animate-pulse-dot"
                        style={{animationDelay: '-0.16s'}}
                    ></div>
                    <div
                        className="w-3 h-3 rounded-full bg-primary animate-pulse-dot"
                    ></div>
                </div>

                <p className="text-lg font-medium text-muted-foreground animate-[fade-in-out_2s_ease-in-out_infinite]">
                    Loading...
                </p>
            </div>
        </div>
    );
}