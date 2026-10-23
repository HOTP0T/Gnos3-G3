<script lang="ts" module>
	import { type VariantProps, tv } from "tailwind-variants";

	export const badgeVariants = tv({
		base: "inline-flex w-fit shrink-0 items-center justify-center gap-1 overflow-hidden rounded-md border border-transparent px-2 py-0.5 text-xs font-medium whitespace-nowrap transition-[color,box-shadow] focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 aria-invalid:border-destructive [&>svg]:pointer-events-none [&>svg]:size-3",
		variants: {
			variant: {
				default: "bg-primary text-primary-foreground [a&]:hover:bg-primary/90",
				secondary: "bg-secondary text-secondary-foreground [a&]:hover:bg-secondary/90",
				destructive: "bg-destructive text-white dark:bg-destructive/60 [a&]:hover:bg-destructive/90",
				outline: "border-border text-foreground [a&]:hover:bg-accent [a&]:hover:text-accent-foreground",
				// lifecycle status: outline, muted text, a 14px icon that may carry the tone (Status map)
				status: "border-border text-muted-foreground pl-1.5 [&>svg]:size-3.5",
				// soft tones for problems and scores: text is the tone mixed 80/20 with foreground (>= 5.4:1)
				success: "border-success/20 bg-success/10 text-success-foreground",
				warning: "border-warning/20 bg-warning/10 text-warning-foreground",
				info: "border-info/20 bg-info/10 text-info-foreground",
				danger: "border-destructive/20 bg-destructive/10 text-danger-foreground",
				count: "min-w-5 h-5 rounded-full px-1.5 tabular-nums bg-secondary text-secondary-foreground",
			},
		},
		defaultVariants: {
			variant: "default",
		},
	});

	export type BadgeVariant = VariantProps<typeof badgeVariants>["variant"];
</script>

<script lang="ts">
	import { cn, type WithElementRef } from "$lib/utils/shadcn.js";
	import type { HTMLAnchorAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		href,
		class: className,
		variant = "default",
		children,
		...restProps
	}: WithElementRef<HTMLAnchorAttributes> & {
		variant?: BadgeVariant;
	} = $props();
</script>

<svelte:element
	this={href ? "a" : "span"}
	bind:this={ref}
	data-slot="badge"
	{href}
	class={cn(badgeVariants({ variant }), className)}
	{...restProps}
>
	{@render children?.()}
</svelte:element>
