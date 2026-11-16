import { z } from "zod";
import { parseApiErrorMessage } from "./errors";

/** An API error that keeps the HTTP status, so callers can tell 401 (signed out) apart. */
export class ApiError extends Error {
	constructor(message: string, readonly status: number) {
		super(message);
	}
}

export function isSignedOutError(error: unknown) {
	return error instanceof ApiError && error.status === 401;
}

export async function apiFetch(path: string, init: RequestInit = {}) {
	const response = await fetch(`${process.env.NEXT_PUBLIC_API_ORIGIN}${path}`, {
		...init,
		headers: { "Content-Type": "application/json", ...init.headers },
		credentials: "include",
	});

	const data = await response.json().catch(() => null);

	if (!response.ok) {
		throw new ApiError(parseApiErrorMessage(data), response.status);
	}

	return data;
}

const profileSchema = z.object({
	email: z.string(),
	name: z.string(),
});

export type Profile = z.infer<typeof profileSchema>;

/** Shared by the signed-in layout (to check the session) and the profile page. */
export async function fetchProfile(): Promise<Profile> {
	return profileSchema.parse(await apiFetch("/v1/profile"));
}

export async function logout() {
	await apiFetch("/v1/auth/logout", { method: "POST" });
}
