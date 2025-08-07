// Sistema simplificado e estável para ícones
let iconsChecked = false;

document.addEventListener('DOMContentLoaded', function() {
    // Verifica apenas uma vez quando a página carrega
    if (!iconsChecked) {
        setTimeout(checkIconsOnce, 2000); // Aguarda tempo suficiente para CSS carregar
    }
});

function checkIconsOnce() {
    if (iconsChecked) return; // Evita múltiplas execuções
    iconsChecked = true;
    
    // Verifica se Bootstrap Icons está carregado verificando uma propriedade específica
    const testElement = document.createElement('i');
    testElement.className = 'bi bi-house-fill';
    testElement.style.position = 'absolute';
    testElement.style.left = '-9999px';
    testElement.style.visibility = 'hidden';
    document.body.appendChild(testElement);
    
    // Aguarda um pouco para o estilo ser aplicado
    setTimeout(() => {
        const computedStyle = window.getComputedStyle(testElement, '::before');
        const content = computedStyle.getPropertyValue('content');
        
        document.body.removeChild(testElement);
        
        // Se o conteúdo for "none" ou vazio, Bootstrap Icons não carregou
        if (!content || content === 'none' || content === '""') {
            console.warn('Bootstrap Icons não detectado. Ativando fallback estático...');
            activateStaticFallback();
        } else {
            console.log('Bootstrap Icons funcionando corretamente!');
        }
    }, 500);
}

function activateStaticFallback() {
    // Adiciona classe uma única vez
    document.body.classList.add('icons-fallback');
    console.log('Fallback de ícones ativado (modo estático)');
}

// Função simplificada para teste manual (sem interferir no sistema automático)
function forceIconFallback() {
    if (document.body.classList.contains('icons-fallback')) {
        // Remove fallback
        document.body.classList.remove('icons-fallback');
        console.log('Fallback desativado - voltando para Bootstrap Icons');
    } else {
        // Ativa fallback
        document.body.classList.add('icons-fallback');
        console.log('Fallback ativado manualmente - usando emojis Unicode');
    }
}
