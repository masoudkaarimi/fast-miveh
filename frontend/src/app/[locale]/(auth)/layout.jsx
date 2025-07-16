import { Card, CardContent } from '@/components/ui/card';

export default function AuthLayout({ children }) {
    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-100 dark:bg-gray-900 p-4">
            <Card className="w-full max-w-md">
                <CardContent className="p-6 pt-6">
                    {children}
                </CardContent>
            </Card>
        </div>
    );
}
