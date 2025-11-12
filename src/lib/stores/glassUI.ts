import { writable } from 'svelte/store';

export interface GlassUISettings {
	enabled: boolean;
	blur: boolean;
	overlay: boolean;
	backgroundImage: string;
	opacity: number;
	blurAmount: number;
}

const defaultSettings: GlassUISettings = {
	enabled: false,
	blur: true,
	overlay: true,
	backgroundImage: 'gradient', // 'gradient', 'landscape', 'abstract', 'custom'
	opacity: 0.15,
	blurAmount: 12
};

// Load from localStorage
const loadSettings = (): GlassUISettings => {
	if (typeof window !== 'undefined') {
		const stored = localStorage.getItem('glassUISettings');
		if (stored) {
			try {
				return { ...defaultSettings, ...JSON.parse(stored) };
			} catch (e) {
				console.error('Failed to parse glass UI settings:', e);
			}
		}
	}
	return defaultSettings;
};

// Create the store
export const glassUISettings = writable<GlassUISettings>(loadSettings());

// Save to localStorage whenever it changes
if (typeof window !== 'undefined') {
	glassUISettings.subscribe((value) => {
		localStorage.setItem('glassUISettings', JSON.stringify(value));
	});
}

// Helper functions
export const toggleGlassUI = () => {
	glassUISettings.update((s) => ({ ...s, enabled: !s.enabled }));
};

export const toggleBlur = () => {
	glassUISettings.update((s) => ({ ...s, blur: !s.blur }));
};

export const toggleOverlay = () => {
	glassUISettings.update((s) => ({ ...s, overlay: !s.overlay }));
};

export const setBackgroundImage = (image: string) => {
	glassUISettings.update((s) => ({ ...s, backgroundImage: image }));
};

export const setOpacity = (opacity: number) => {
	glassUISettings.update((s) => ({ ...s, opacity }));
};

export const setBlurAmount = (blurAmount: number) => {
	glassUISettings.update((s) => ({ ...s, blurAmount }));
};
