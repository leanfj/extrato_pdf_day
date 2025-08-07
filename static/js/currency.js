// Formatação brasileira para valores monetários
function formatCurrencyBR(valor) {
    if (valor === 0 || valor === null || valor === undefined) {
        return "0,00";
    }
    
    // Converte para número se for string
    if (typeof valor === 'string') {
        valor = parseFloat(valor);
    }
    
    // Formata com 2 casas decimais
    const valorStr = valor.toFixed(2);
    
    // Separa parte inteira e decimal
    const partes = valorStr.split('.');
    let parteInteira = partes[0];
    const parteDecimal = partes[1];
    
    // Adiciona separadores de milhares
    if (parteInteira.length > 3) {
        let parteInteiraFormatada = "";
        for (let i = parteInteira.length - 1, j = 0; i >= 0; i--, j++) {
            if (j > 0 && j % 3 === 0) {
                parteInteiraFormatada = "." + parteInteiraFormatada;
            }
            parteInteiraFormatada = parteInteira[i] + parteInteiraFormatada;
        }
        parteInteira = parteInteiraFormatada;
    }
    
    return `${parteInteira},${parteDecimal}`;
}

// Formatação completa com símbolo R$
function formatCurrencyBRFull(valor) {
    return `R$ ${formatCurrencyBR(valor)}`;
}

// Configura Chart.js para usar formatação brasileira
if (typeof Chart !== 'undefined') {
    Chart.defaults.locale = 'pt-BR';
    
    // Plugin global para formatação brasileira
    Chart.register({
        id: 'currency-br-formatter',
        beforeInit: function(chart) {
            // Configura tooltips para usar formatação brasileira
            if (chart.options.plugins && chart.options.plugins.tooltip) {
                const originalCallbacks = chart.options.plugins.tooltip.callbacks || {};
                
                chart.options.plugins.tooltip.callbacks = {
                    ...originalCallbacks,
                    label: function(context) {
                        let label = context.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (context.parsed.y !== null) {
                            label += formatCurrencyBRFull(context.parsed.y);
                        }
                        return label;
                    }
                };
            }
            
            // Configura escalas para usar formatação brasileira
            if (chart.options.scales) {
                Object.keys(chart.options.scales).forEach(scaleKey => {
                    const scale = chart.options.scales[scaleKey];
                    if (scale.type === 'linear' || scale.type === 'logarithmic') {
                        scale.ticks = scale.ticks || {};
                        scale.ticks.callback = function(value, index, values) {
                            return formatCurrencyBRFull(value);
                        };
                    }
                });
            }
        }
    });
}

// Funções utilitárias para DataTables
function formatDataTableCurrency(data, type, row) {
    if (type === 'display' || type === 'type') {
        return formatCurrencyBRFull(data);
    }
    return data;
}

// Exporta as funções para uso global
window.formatCurrencyBR = formatCurrencyBR;
window.formatCurrencyBRFull = formatCurrencyBRFull;
window.formatDataTableCurrency = formatDataTableCurrency;
