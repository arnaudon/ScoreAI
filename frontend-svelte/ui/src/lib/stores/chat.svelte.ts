type HistoryMessage = {
	question: string;
	[key: string]: any;
};

function createHistoryStore() {
	let history = $state<HistoryMessage[]>([]);
	let rawHistory = $state<any[]>([]);

	return {
		get history() {
			return history;
		},
		set history(value: HistoryMessage[]) {
			history = value;
		},

		get rawHistory() {
			return rawHistory;
		},
		set rawHistory(value: any[]) {
			rawHistory = value;
		},

		clear() {
			history = [];
			rawHistory = [];
		}
	};
}

export const mainAgentHistoryStore = createHistoryStore();
export const imslpAgentHistoryStore = createHistoryStore();
