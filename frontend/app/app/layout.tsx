"use client";

import { fetchProfile, isSignedOutError, logout } from "@/app/lib/api";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

const paths = {
	"/app/profile": "Profile",
	"/app/friends": "Friends",
};

export default function AppLayout({
	children,
}: Readonly<{ children: React.ReactNode }>) {
	const path = usePathname();
	const router = useRouter();
	const queryClient = useQueryClient();

	const currentPath = Object.keys(paths).find((key) => path.startsWith(key));

	// Every page under /app needs a signed-in user. The profile request doubles
	// as the session check; the profile page reads the same cached result.
	const { data: profile, error, fetchStatus } = useQuery({
		queryKey: ["profile"],
		queryFn: fetchProfile,
		retry: false,
	});

	const signedOut = isSignedOutError(error);

	useEffect(() => {
		// Wait until no request is in flight, so a stale cached 401 can't
		// redirect while a fresh check is still running.
		if (signedOut && fetchStatus === "idle") {
			queryClient.clear();
			router.replace("/login");
		}
	}, [signedOut, fetchStatus, queryClient, router]);

	const logoutMutation = useMutation({
		mutationFn: logout,
		onSuccess() {
			queryClient.clear();
			router.replace("/login");
		},
	});

	let content: React.ReactNode;
	if (profile) {
		content = children;
	} else if (error && !signedOut) {
		content = (
			<p className="text-white bg-red-500/25 p-2 rounded text-sm mt-4">
				{error.message}
			</p>
		);
	} else {
		content = <p className="text-sm text-slate-400">Loading...</p>;
	}

	return (
		<div className="w-full h-full flex flex-col items-center justify-center py-8">
			<div className="w-[600px] max-w-full h-full border border-slate-600 rounded-lg p-8 overflow-hidden flex flex-col gap-4">
				<nav className="flex gap-4 items-center">
					{Object.entries(paths).map(([key, value]) => (
						<Link key={key} href={key}>
							{key === currentPath ? (
								<span className="text-white font-semibold">{value}</span>
							) : (
								<span className="text-white hover:underline">{value}</span>
							)}
						</Link>
					))}
					{profile && (
						<button
							type="button"
							onClick={() => logoutMutation.mutate()}
							disabled={logoutMutation.isPending}
							className="ml-auto text-sm text-slate-300 hover:text-white hover:underline disabled:opacity-50"
						>
							Log out
						</button>
					)}
				</nav>
				{logoutMutation.error && (
					<p className="text-white bg-red-500/25 p-2 rounded text-sm">
						{logoutMutation.error.message}
					</p>
				)}
				<div className="flex flex-col flex-grow w-full h-full overflow-hidden">
					{content}
				</div>
			</div>
		</div>
	);
}
