/** Gnos3's two tiers above `user`: `admin` (data) and `superadmin` (platform). Most "admins may
 *  do this" checks mean both; platform settings use `isSuperadmin` from the stores instead. */
export const isAdminRole = (role?: string | null) => role === 'admin' || role === 'superadmin';
