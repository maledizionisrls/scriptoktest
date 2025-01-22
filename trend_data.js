// trend_data.js
class TrendAnalyzer {
    constructor() {
        // Verifica che i dati siano disponibili
        if (typeof window.videos === 'undefined') {
            console.error('Dati video non disponibili');
            this.videos = [];
            return;
        }
        this.videos = window.videos;
        this.processedData = this.processData();
    }

    processData() {
        if (!this.videos.length) {
            return {
                wordCloud: [],
                keywords: [],
                categories: []
            };
        }

        const wordWeights = {};
        const keywordCounts = {};
        const categoryStats = {};

        this.videos.forEach(video => {
            try {
                // Gestione sicura delle visualizzazioni
                const views = parseInt((video.views || '0').replace(/\./g, '')) || 0;
                
                // Gestione sicura delle keywords
                if (Array.isArray(video.keywords)) {
                    video.keywords.forEach(keyword => {
                        if (keyword && keyword !== 'N/A') {
                            if (!wordWeights[keyword]) wordWeights[keyword] = 0;
                            wordWeights[keyword] += views;
                            
                            if (!keywordCounts[keyword]) keywordCounts[keyword] = 0;
                            keywordCounts[keyword]++;
                        }
                    });
                }

                // Gestione sicura delle categorie
                if (Array.isArray(video.categories)) {
                    video.categories.forEach(category => {
                        if (category && category !== 'N/A') {
                            if (!categoryStats[category]) {
                                categoryStats[category] = {
                                    totalViews: 0,
                                    count: 0
                                };
                            }
                            categoryStats[category].totalViews += views;
                            categoryStats[category].count++;
                        }
                    });
                }
            } catch (e) {
                console.error('Errore nel processamento del video:', e);
            }
        });

        return {
            wordCloud: this.prepareWordCloudData(wordWeights),
            keywords: this.prepareKeywordsData(keywordCounts),
            categories: this.prepareCategoriesData(categoryStats)
        };
    }

    prepareWordCloudData(weights) {
        try {
            return Object.entries(weights)
                .map(([text, value]) => ({
                    text,
                    size: this.calculateFontSize(value, Object.values(weights)),
                    weight: value
                }))
                .sort((a, b) => b.weight - a.weight)
                .slice(0, 40);
        } catch (e) {
            console.error('Errore nella preparazione word cloud:', e);
            return [];
        }
    }

    calculateFontSize(value, allValues) {
        try {
            const max = Math.max(...allValues);
            const min = Math.min(...allValues);
            const range = max - min;
            if (range === 0) return 24; // valore di default
            const normalized = (value - min) / range;
            return Math.floor(12 + normalized * 36); // da 12px a 48px
        } catch (e) {
            console.error('Errore nel calcolo font size:', e);
            return 24; // valore di default
        }
    }

    prepareKeywordsData(counts) {
        try {
            const total = Object.values(counts).reduce((sum, count) => sum + count, 0);
            if (total === 0) return [];

            return Object.entries(counts)
                .map(([keyword, count]) => ({
                    keyword,
                    count,
                    percentage: ((count / total) * 100).toFixed(1)
                }))
                .sort((a, b) => b.count - a.count)
                .slice(0, 10);
        } catch (e) {
            console.error('Errore nella preparazione keywords:', e);
            return [];
        }
    }

    prepareCategoriesData(stats) {
        try {
            return Object.entries(stats)
                .map(([category, data]) => ({
                    category,
                    avgViews: Math.round(data.totalViews / data.count),
                    totalVideos: data.count
                }))
                .sort((a, b) => b.avgViews - a.avgViews)
                .slice(0, 8);
        } catch (e) {
            console.error('Errore nella preparazione categorie:', e);
            return [];
        }
    }

    getData() {
        return this.processedData;
    }

    static formatNumber(num) {
        try {
            return new Intl.NumberFormat('it-IT').format(num);
        } catch (e) {
            return num.toString();
        }
    }
}

// Rendi disponibile globalmente
window.TrendAnalyzer = TrendAnalyzer;
