// The Notes graph: a force layout (d3-force) drawn on a canvas, themed from the design system's
// tokens. Wheel or pinch zooms, dragging the background pans, dragging a node moves it, hovering
// lights up a node and its neighbours, clicking opens it.

import {
	forceCenter,
	forceCollide,
	forceLink,
	forceManyBody,
	forceSimulation,
	forceX,
	forceY,
	type Simulation
} from 'd3-force';

export interface GNode {
	id: string;
	kind: 'note' | 'ghost' | 'entity' | 'tag';
	title: string;
	color?: string | null; // a design token name (chart-3) or null
	degree?: number;
	focus?: boolean;
	x?: number;
	y?: number;
	vx?: number;
	vy?: number;
	fx?: number | null;
	fy?: number | null;
}

export interface GLink {
	source: string | GNode;
	target: string | GNode;
	kind: string;
}

export interface GraphOptions {
	linkDistance: number;
	repel: number;
	centerForce: number;
	nodeSize: number;
	linkWidth: number;
	showArrows: boolean;
	labelZoom: number; // labels appear from this zoom level
	onOpen: (node: GNode, event: MouseEvent) => void;
	onHover?: (node: GNode | null) => void;
}

const DEFAULTS: Omit<GraphOptions, 'onOpen'> = {
	linkDistance: 60,
	repel: 160,
	centerForce: 0.06,
	nodeSize: 1,
	linkWidth: 1,
	showArrows: false,
	labelZoom: 0.9
};

interface Palette {
	background: string;
	foreground: string;
	muted: string;
	border: string;
	primary: string;
	tokens: Map<string, string>;
}

const nodeId = (end: string | GNode) => (typeof end === 'string' ? end : end.id);

export class ForceGraph {
	private canvas: HTMLCanvasElement;
	private ctx: CanvasRenderingContext2D;
	private options: GraphOptions;
	private nodes: GNode[] = [];
	private links: GLink[] = [];
	private neighbours = new Map<string, Set<string>>();
	private simulation: Simulation<GNode, undefined> | null = null;
	private palette: Palette | null = null;
	private transform = { x: 0, y: 0, k: 1 };
	private hovered: GNode | null = null;
	private dragging: GNode | null = null;
	private panning = false;
	private moved = false;
	private last = { x: 0, y: 0 };
	private width = 0;
	private height = 0;
	private frame = 0;
	private resizeObserver: ResizeObserver;
	private themeObserver: MutationObserver;
	private probe: HTMLSpanElement;
	private fitted = false;
	private pointers = new Map<number, { x: number; y: number }>();
	private pinchStart: { distance: number; k: number } | null = null;

	constructor(
		canvas: HTMLCanvasElement,
		options: Partial<GraphOptions> & Pick<GraphOptions, 'onOpen'>
	) {
		this.canvas = canvas;
		this.ctx = canvas.getContext('2d')!;
		this.options = { ...DEFAULTS, ...options };
		this.probe = document.createElement('span');
		this.probe.style.display = 'none';
		canvas.parentElement?.appendChild(this.probe);
		this.readPalette();
		this.resizeObserver = new ResizeObserver(() => this.resize());
		this.resizeObserver.observe(canvas.parentElement ?? canvas);
		this.themeObserver = new MutationObserver(() => {
			this.readPalette();
			this.draw();
		});
		this.themeObserver.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ['class']
		});
		this.resize();
		this.bind();
	}

	// --- data -----------------------------------------------------------------

	setData(nodes: GNode[], links: GLink[]) {
		const old = new Map(this.nodes.map((n) => [n.id, n]));
		this.nodes = nodes.map((n) => {
			const previous = old.get(n.id);
			return previous
				? { ...n, x: previous.x, y: previous.y, vx: previous.vx, vy: previous.vy }
				: { ...n };
		});
		const ids = new Set(this.nodes.map((n) => n.id));
		this.links = links
			.filter((l) => ids.has(nodeId(l.source)) && ids.has(nodeId(l.target)))
			.map((l) => ({ ...l, source: nodeId(l.source), target: nodeId(l.target) }));
		this.neighbours = new Map(this.nodes.map((n) => [n.id, new Set<string>()]));
		for (const l of this.links) {
			this.neighbours.get(nodeId(l.source))?.add(nodeId(l.target));
			this.neighbours.get(nodeId(l.target))?.add(nodeId(l.source));
		}
		for (const n of this.nodes) n.degree = this.neighbours.get(n.id)?.size ?? 0;
		this.fitted = this.fitted && old.size > 0;
		this.restart(old.size === 0 ? 1 : 0.3);
	}

	setOptions(options: Partial<GraphOptions>) {
		this.options = { ...this.options, ...options };
		this.restart(0.5);
	}

	private restart(alpha: number) {
		this.simulation?.stop();
		const o = this.options;
		this.simulation = forceSimulation<GNode>(this.nodes)
			.force(
				'link',
				forceLink<GNode, any>(this.links)
					.id((d: GNode) => d.id)
					.distance(o.linkDistance)
					.strength(0.5)
			)
			.force('charge', forceManyBody<GNode>().strength(-o.repel).distanceMax(600))
			.force('center', forceCenter(0, 0))
			.force('x', forceX<GNode>(0).strength(o.centerForce))
			.force('y', forceY<GNode>(0).strength(o.centerForce))
			.force(
				'collide',
				forceCollide<GNode>().radius((d) => this.radius(d) + 3)
			)
			.alpha(alpha)
			.alphaDecay(0.03)
			.on('tick', () => this.schedule())
			.on('end', () => {
				if (!this.fitted) {
					this.fitted = true;
					this.zoomToFit(300);
				}
			});
		// Lay out a little before the first paint so the graph does not explode on screen.
		if (alpha >= 1) {
			this.simulation.tick(60);
			this.zoomToFit(0);
		}
	}

	// --- view -----------------------------------------------------------------

	zoomToFit(duration = 250) {
		if (!this.nodes.length || !this.width) return;
		let minX = Infinity,
			minY = Infinity,
			maxX = -Infinity,
			maxY = -Infinity;
		for (const n of this.nodes) {
			minX = Math.min(minX, n.x ?? 0);
			minY = Math.min(minY, n.y ?? 0);
			maxX = Math.max(maxX, n.x ?? 0);
			maxY = Math.max(maxY, n.y ?? 0);
		}
		const pad = 60;
		const k = Math.min(
			2.5,
			Math.max(
				0.1,
				Math.min(this.width / (maxX - minX + pad * 2), this.height / (maxY - minY + pad * 2))
			)
		);
		const target = {
			k,
			x: this.width / 2 - ((minX + maxX) / 2) * k,
			y: this.height / 2 - ((minY + maxY) / 2) * k
		};
		this.animateTo(target, duration);
	}

	centerOn(id: string, duration = 300) {
		const n = this.nodes.find((x) => x.id === id);
		if (!n) return;
		const k = Math.max(this.transform.k, 1.2);
		this.animateTo(
			{ k, x: this.width / 2 - (n.x ?? 0) * k, y: this.height / 2 - (n.y ?? 0) * k },
			duration
		);
	}

	zoomBy(factor: number) {
		this.zoomAt(this.width / 2, this.height / 2, factor);
	}

	private animateTo(target: { x: number; y: number; k: number }, duration: number) {
		if (duration <= 0) {
			this.transform = target;
			this.draw();
			return;
		}
		const start = { ...this.transform };
		const t0 = performance.now();
		const step = (now: number) => {
			const t = Math.min(1, (now - t0) / duration);
			const e = 1 - Math.pow(1 - t, 3);
			this.transform = {
				x: start.x + (target.x - start.x) * e,
				y: start.y + (target.y - start.y) * e,
				k: start.k + (target.k - start.k) * e
			};
			this.draw();
			if (t < 1) requestAnimationFrame(step);
		};
		requestAnimationFrame(step);
	}

	private zoomAt(sx: number, sy: number, factor: number) {
		const k = Math.min(6, Math.max(0.05, this.transform.k * factor));
		const real = k / this.transform.k;
		this.transform = {
			k,
			x: sx - (sx - this.transform.x) * real,
			y: sy - (sy - this.transform.y) * real
		};
		this.schedule();
	}

	private resize() {
		const box = (this.canvas.parentElement ?? this.canvas).getBoundingClientRect();
		const ratio = window.devicePixelRatio || 1;
		const first = !this.width;
		this.width = Math.max(1, box.width);
		this.height = Math.max(1, box.height);
		this.canvas.width = Math.round(this.width * ratio);
		this.canvas.height = Math.round(this.height * ratio);
		this.canvas.style.width = `${this.width}px`;
		this.canvas.style.height = `${this.height}px`;
		this.ctx.setTransform(ratio, 0, 0, ratio, 0, 0);
		if (first) this.transform = { x: this.width / 2, y: this.height / 2, k: 1 };
		this.draw();
	}

	// --- colours --------------------------------------------------------------

	private resolve(css: string) {
		this.probe.style.color = '';
		this.probe.style.color = css;
		return getComputedStyle(this.probe).color || css;
	}

	private readPalette() {
		this.palette = {
			background: this.resolve('var(--background)'),
			foreground: this.resolve('var(--foreground)'),
			muted: this.resolve('var(--muted-foreground)'),
			border: this.resolve('var(--border)'),
			primary: this.resolve('var(--primary)'),
			tokens: new Map()
		};
	}

	private token(name: string) {
		const p = this.palette!;
		if (!p.tokens.has(name)) p.tokens.set(name, this.resolve(`var(--${name})`));
		return p.tokens.get(name)!;
	}

	private colorOf(n: GNode) {
		const p = this.palette!;
		if (n.color) return this.token(n.color);
		if (n.kind === 'ghost') return p.muted;
		if (n.kind === 'tag') return this.token('chart-7');
		return p.muted;
	}

	// --- drawing --------------------------------------------------------------

	private radius(n: GNode) {
		const base = n.kind === 'note' ? 4 : n.kind === 'tag' ? 3.5 : 4;
		return (base + Math.sqrt(n.degree ?? 0) * 1.6) * this.options.nodeSize;
	}

	private schedule() {
		if (this.frame) return;
		this.frame = requestAnimationFrame(() => {
			this.frame = 0;
			this.draw();
		});
	}

	private draw() {
		const { ctx, palette: p } = this;
		if (!p) return;
		const { x, y, k } = this.transform;
		ctx.save();
		ctx.clearRect(0, 0, this.width, this.height);
		ctx.translate(x, y);
		ctx.scale(k, k);

		const active = this.hovered;
		const near = active ? (this.neighbours.get(active.id) ?? new Set()) : null;
		const lit = (id: string) => !active || id === active.id || near!.has(id);

		// Links
		for (const l of this.links) {
			const s = l.source as GNode;
			const t = l.target as GNode;
			if (s.x === undefined || t.x === undefined) continue;
			const on = active && (s.id === active.id || t.id === active.id);
			ctx.globalAlpha = active ? (on ? 0.9 : 0.08) : 0.45;
			ctx.strokeStyle = on ? p.primary : p.muted;
			ctx.lineWidth = ((on ? 1.6 : 1) * this.options.linkWidth) / Math.max(0.6, k);
			ctx.setLineDash(
				l.kind === 'property'
					? [4 / k, 3 / k]
					: l.kind === 'tag' || l.kind === 'entity'
						? [1.5 / k, 2.5 / k]
						: []
			);
			ctx.beginPath();
			ctx.moveTo(s.x, s.y!);
			ctx.lineTo(t.x, t.y!);
			ctx.stroke();
			if (this.options.showArrows) {
				const r = this.radius(t) + 2;
				const angle = Math.atan2(t.y! - s.y!, t.x - s.x);
				const ax = t.x - Math.cos(angle) * r;
				const ay = t.y! - Math.sin(angle) * r;
				const size = 4 / Math.max(0.6, k);
				ctx.setLineDash([]);
				ctx.beginPath();
				ctx.moveTo(ax, ay);
				ctx.lineTo(ax - size * Math.cos(angle - 0.45), ay - size * Math.sin(angle - 0.45));
				ctx.lineTo(ax - size * Math.cos(angle + 0.45), ay - size * Math.sin(angle + 0.45));
				ctx.closePath();
				ctx.fillStyle = on ? p.primary : p.muted;
				ctx.fill();
			}
		}
		ctx.setLineDash([]);

		// Nodes
		for (const n of this.nodes) {
			if (n.x === undefined) continue;
			const r = this.radius(n);
			const color = this.colorOf(n);
			ctx.globalAlpha = lit(n.id) ? 1 : 0.15;
			ctx.beginPath();
			if (n.kind === 'entity') {
				ctx.rect(n.x - r, n.y! - r, r * 2, r * 2);
			} else if (n.kind === 'tag') {
				ctx.moveTo(n.x, n.y! - r * 1.2);
				ctx.lineTo(n.x + r * 1.2, n.y!);
				ctx.lineTo(n.x, n.y! + r * 1.2);
				ctx.lineTo(n.x - r * 1.2, n.y!);
				ctx.closePath();
			} else {
				ctx.arc(n.x, n.y!, r, 0, Math.PI * 2);
			}
			if (n.kind === 'ghost') {
				ctx.fillStyle = p.background;
				ctx.fill();
				ctx.lineWidth = 1.2 / Math.max(0.6, k);
				ctx.strokeStyle = color;
				ctx.setLineDash([2 / k, 2 / k]);
				ctx.stroke();
				ctx.setLineDash([]);
			} else {
				ctx.fillStyle = color;
				ctx.fill();
			}
			if (n.focus || n === active) {
				ctx.lineWidth = 2 / Math.max(0.6, k);
				ctx.strokeStyle = p.primary;
				ctx.beginPath();
				ctx.arc(n.x, n.y!, r + 3 / Math.max(0.6, k), 0, Math.PI * 2);
				ctx.stroke();
			}
		}

		ctx.restore();

		// Labels, drawn in screen space at a whole pixel size (text scaled by the zoom transform
		// renders with uneven letter spacing): when zoomed in enough, for the hovered node and its
		// neighbours, and for the focused note.
		ctx.save();
		ctx.font = '11px Geist, ui-sans-serif, system-ui, sans-serif';
		ctx.textAlign = 'center';
		ctx.textBaseline = 'top';
		ctx.lineJoin = 'round';
		for (const n of this.nodes) {
			if (n.x === undefined) continue;
			const show = k >= this.options.labelZoom || (active && lit(n.id)) || n.focus;
			if (!show) continue;
			const sx = Math.round(n.x * k + x);
			const sy = Math.round((n.y! + this.radius(n)) * k + y + 3);
			if (sx < -200 || sx > this.width + 200 || sy < -20 || sy > this.height + 20) continue;
			ctx.globalAlpha = lit(n.id) ? (n.kind === 'ghost' ? 0.7 : 0.95) : 0.12;
			const label = n.title.length > 40 ? n.title.slice(0, 39) + '…' : n.title;
			ctx.lineWidth = 3;
			ctx.strokeStyle = p.background;
			ctx.strokeText(label, sx, sy);
			ctx.fillStyle = n.kind === 'ghost' ? p.muted : p.foreground;
			ctx.fillText(label, sx, sy);
		}
		ctx.restore();
		ctx.globalAlpha = 1;
	}

	// --- input ----------------------------------------------------------------

	private toWorld(sx: number, sy: number) {
		return {
			x: (sx - this.transform.x) / this.transform.k,
			y: (sy - this.transform.y) / this.transform.k
		};
	}

	private nodeAt(sx: number, sy: number): GNode | null {
		const { x, y } = this.toWorld(sx, sy);
		let best: GNode | null = null;
		let bestD = Infinity;
		for (const n of this.nodes) {
			if (n.x === undefined) continue;
			const d = Math.hypot(n.x - x, n.y! - y);
			const reach = this.radius(n) + 4 / this.transform.k;
			if (d <= reach && d < bestD) {
				best = n;
				bestD = d;
			}
		}
		return best;
	}

	private local(e: PointerEvent | WheelEvent | MouseEvent) {
		const rect = this.canvas.getBoundingClientRect();
		return { x: e.clientX - rect.left, y: e.clientY - rect.top };
	}

	private onWheel = (e: WheelEvent) => {
		e.preventDefault();
		const { x, y } = this.local(e);
		const factor = Math.exp(-e.deltaY * (e.ctrlKey ? 0.01 : 0.0015));
		this.zoomAt(x, y, factor);
	};

	private onPointerDown = (e: PointerEvent) => {
		this.canvas.setPointerCapture(e.pointerId);
		const pos = this.local(e);
		this.pointers.set(e.pointerId, pos);
		if (this.pointers.size === 2) {
			const [a, b] = [...this.pointers.values()];
			this.pinchStart = { distance: Math.hypot(a.x - b.x, a.y - b.y), k: this.transform.k };
			this.dragging = null;
			this.panning = false;
			return;
		}
		this.moved = false;
		this.last = pos;
		const hit = this.nodeAt(pos.x, pos.y);
		if (hit) {
			this.dragging = hit;
			hit.fx = hit.x;
			hit.fy = hit.y;
			this.simulation?.alphaTarget(0.25).restart();
		} else {
			this.panning = true;
		}
	};

	private onPointerMove = (e: PointerEvent) => {
		const pos = this.local(e);
		if (this.pointers.has(e.pointerId)) this.pointers.set(e.pointerId, pos);
		if (this.pinchStart && this.pointers.size === 2) {
			const [a, b] = [...this.pointers.values()];
			const distance = Math.hypot(a.x - b.x, a.y - b.y);
			const k = this.pinchStart.k * (distance / this.pinchStart.distance);
			this.zoomAt((a.x + b.x) / 2, (a.y + b.y) / 2, k / this.transform.k);
			return;
		}
		if (Math.hypot(pos.x - this.last.x, pos.y - this.last.y) > 3) this.moved = true;
		if (this.dragging) {
			const w = this.toWorld(pos.x, pos.y);
			this.dragging.fx = w.x;
			this.dragging.fy = w.y;
			return;
		}
		if (this.panning) {
			this.transform = {
				...this.transform,
				x: this.transform.x + pos.x - this.last.x,
				y: this.transform.y + pos.y - this.last.y
			};
			this.last = pos;
			this.schedule();
			return;
		}
		const hit = this.nodeAt(pos.x, pos.y);
		if (hit !== this.hovered) {
			this.hovered = hit;
			this.canvas.style.cursor = hit ? 'pointer' : 'grab';
			this.options.onHover?.(hit);
			this.schedule();
		}
	};

	private onPointerUp = (e: PointerEvent) => {
		this.pointers.delete(e.pointerId);
		if (this.pointers.size < 2) this.pinchStart = null;
		if (this.dragging) {
			const node = this.dragging;
			this.dragging = null;
			node.fx = null;
			node.fy = null;
			this.simulation?.alphaTarget(0);
			if (!this.moved) this.options.onOpen(node, e);
		}
		this.panning = false;
	};

	private onLeave = () => {
		if (this.hovered) {
			this.hovered = null;
			this.options.onHover?.(null);
			this.schedule();
		}
	};

	private bind() {
		this.canvas.style.cursor = 'grab';
		this.canvas.style.touchAction = 'none';
		this.canvas.addEventListener('wheel', this.onWheel, { passive: false });
		this.canvas.addEventListener('pointerdown', this.onPointerDown);
		this.canvas.addEventListener('pointermove', this.onPointerMove);
		this.canvas.addEventListener('pointerup', this.onPointerUp);
		this.canvas.addEventListener('pointercancel', this.onPointerUp);
		this.canvas.addEventListener('pointerleave', this.onLeave);
	}

	destroy() {
		this.simulation?.stop();
		this.resizeObserver.disconnect();
		this.themeObserver.disconnect();
		if (this.frame) cancelAnimationFrame(this.frame);
		this.canvas.removeEventListener('wheel', this.onWheel);
		this.canvas.removeEventListener('pointerdown', this.onPointerDown);
		this.canvas.removeEventListener('pointermove', this.onPointerMove);
		this.canvas.removeEventListener('pointerup', this.onPointerUp);
		this.canvas.removeEventListener('pointercancel', this.onPointerUp);
		this.canvas.removeEventListener('pointerleave', this.onLeave);
		this.probe.remove();
	}
}
