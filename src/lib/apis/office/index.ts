// Office module — frontend half of the SSO bridge.
//
// `getOfficeExchangeToken` fetches a 5-min HS256 JWT from Gnos3's
// `/api/v1/auths/office/exchange-token` endpoint (caller must be
// authenticated to Gnos3 with `token`, and hold `modules.office.read`).
// The embed component then loads `${OFFICE_BASE_URL}/sso?gnos3_token=<jwt>`
// inside the module iframe; the module verifies the token and starts a session.

import { WEBUI_API_BASE_URL } from '$lib/constants';

export interface OfficeExchangeTokenResponse {
	token: string;
	expires_at: number;
}

/** Mint a short-lived (5 min) Gnos3 JWT that the Office module SSO bridge accepts.
 *
 * Requires an existing Gnos3 session token (`token`). Throws on non-2xx —
 * callers should wrap in try/catch and surface a friendly error.
 */
export const getOfficeExchangeToken = async (
	token: string
): Promise<OfficeExchangeTokenResponse> => {
	if (!token) {
		throw new Error('not authenticated to Gnos3');
	}
	const res = await fetch(`${WEBUI_API_BASE_URL}/auths/office/exchange-token`, {
		method: 'POST',
		headers: {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		}
	});
	if (!res.ok) {
		const body = await res.text().catch(() => '');
		throw new Error(
			`Office exchange-token failed: HTTP ${res.status}${body ? ` — ${body.slice(0, 200)}` : ''}`
		);
	}
	return (await res.json()) as OfficeExchangeTokenResponse;
};
