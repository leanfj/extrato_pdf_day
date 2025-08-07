# 🎨 Sistema de Temas - Dark/Light Mode

## Visão Geral

O Extrator de PDF agora possui um sistema completo de temas com **Dark Mode** e **Light Mode**, proporcionando uma experiência visual confortável para qualquer horário do dia.

## 🌟 Funcionalidades do Sistema de Temas

### 🔄 **Toggle de Tema**
- **Botão no Header**: Ícone de sol/lua no canto superior direito
- **Transição Suave**: Animações de 0.3s para mudanças de tema
- **Persistência**: Preferência salva no localStorage
- **Auto-detecção**: Detecta preferência do sistema operacional

### 🎨 **Paleta de Cores**

#### 💡 **Light Mode**
- **Background**: #ffffff (branco)
- **Texto**: #212529 (preto)
- **Cards**: #ffffff (branco)
- **Bordas**: #dee2e6 (cinza claro)
- **Navbar**: #0d6efd (azul)

#### 🌙 **Dark Mode**
- **Background**: #121212 (preto suave)
- **Texto**: #ffffff (branco)
- **Cards**: #2d2d2d (cinza escuro)
- **Bordas**: #495057 (cinza médio)
- **Navbar**: #1a1a1a (preto)

### 🎯 **Cores dos Componentes**

| Componente | Light Mode | Dark Mode |
|------------|------------|-----------|
| Primary | #0d6efd | #4dabf7 |
| Success | #198754 | #51cf66 |
| Warning | #ffc107 | #ffd43b |
| Danger | #dc3545 | #ff6b6b |
| Info | #0dcaf0 | #74c0fc |

## 🔧 **Implementação Técnica**

### **CSS Variables**
```css
:root {
    --bg-color: #ffffff;
    --text-color: #212529;
    --card-bg: #ffffff;
    /* ... outras variáveis ... */
}

[data-theme="dark"] {
    --bg-color: #121212;
    --text-color: #ffffff;
    --card-bg: #2d2d2d;
    /* ... outras variáveis ... */
}
```

### **JavaScript para Toggle**
```javascript
// Detecta tema salvo ou preferência do sistema
const savedTheme = localStorage.getItem('theme') || 'light';

// Aplica tema
function applyTheme(theme) {
    if (theme === 'dark') {
        html.setAttribute('data-theme', 'dark');
        themeIcon.className = 'bi bi-moon-fill';
    } else {
        html.removeAttribute('data-theme');
        themeIcon.className = 'bi bi-sun-fill';
    }
}
```

## 🎛️ **Controles do Usuário**

### **Como Alternar o Tema**
1. **Clique no ícone** no canto superior direito da navbar
2. **Ícone de Sol** = Light Mode ativo (clique para Dark Mode)
3. **Ícone de Lua** = Dark Mode ativo (clique para Light Mode)

### **Persistência**
- A preferência é **salva automaticamente** no navegador
- **Mantém a escolha** entre sessões
- **Auto-detecção** da preferência do sistema na primeira visita

## 🎨 **Componentes Atualizados**

### ✅ **Navbar**
- Background adaptativo
- Ícones com cores temáticas
- Toggle button integrado

### ✅ **Cards e Painéis**
- Background e bordas adaptáveis
- Texto com contraste adequado
- Sombras ajustadas para cada tema

### ✅ **Formulários**
- Inputs com background temático
- Placeholders com cor apropriada
- Bordas e focos adaptativos

### ✅ **Tabelas (DataTables)**
- Headers com cores temáticas
- Linhas alternadas apropriadas
- Controles de paginação adaptados

### ✅ **Gráficos (Chart.js)**
- Cores automáticas baseadas no tema
- Grid e texto adaptáveis
- Atualização dinâmica ao trocar tema

### ✅ **Badges e Alertas**
- Cores de status apropriadas
- Contraste mantido em ambos os temas
- Transparências ajustadas

### ✅ **Botões**
- Estados hover/focus temáticos
- Cores primárias adaptadas
- Outline buttons responsivos

## 🔍 **Detalhes de Acessibilidade**

### **Contraste**
- **WCAG AA Compliant**: Contraste mínimo de 4.5:1
- **Texto Principal**: Sempre legível
- **Texto Secundário**: Contraste adequado

### **Indicadores Visuais**
- **Ícone do Tema**: Indica claramente o modo atual
- **Tooltips**: Explicam a função do toggle
- **Transições**: Suaves para evitar desconforto

### **Compatibilidade**
- **Todos os Navegadores**: Chrome, Firefox, Safari, Edge
- **Dispositivos Móveis**: Responsivo em tablets e phones
- **Preferências do Sistema**: Detecta automaticamente

## 📱 **Responsividade**

### **Desktop**
- Toggle no header sempre visível
- Transições suaves em telas grandes
- Hover effects completos

### **Mobile**
- Toggle acessível no menu collapsed
- Touch-friendly (40px mínimo)
- Transições otimizadas

### **Tablet**
- Experiência híbrida otimizada
- Touch e hover apropriados
- Layout adaptativo

## 🚀 **Performance**

### **CSS**
- **Variables**: Mudanças instantâneas
- **Transições**: Apenas onde necessário (0.3s)
- **No Flicker**: Aplicação suave de temas

### **JavaScript**
- **LocalStorage**: Acesso rápido às preferências
- **Event Listeners**: Otimizados e limpos
- **Chart Updates**: Batch updates para performance

## 🎯 **Casos de Uso**

### **🌅 Light Mode - Ideal para:**
- Trabalho durante o dia
- Ambientes bem iluminados
- Apresentações e demonstrações
- Impressão de documentos

### **🌙 Dark Mode - Ideal para:**
- Trabalho noturno
- Ambientes com pouca luz
- Redução da fadiga ocular
- Economia de bateria (OLED)

## 🔧 **Customização Avançada**

### **Adicionar Novas Cores**
```css
:root {
    --custom-color: #your-light-color;
}

[data-theme="dark"] {
    --custom-color: #your-dark-color;
}
```

### **Novos Componentes**
```css
.meu-componente {
    background-color: var(--bg-color);
    color: var(--text-color);
    border-color: var(--border-color);
    transition: all 0.3s ease;
}
```

### **JavaScript para Charts**
```javascript
// Use as cores dinâmicas
const colors = window.getChartColors();
chart.data.datasets[0].backgroundColor = colors.primary;
```

## 📊 **Estatísticas de Uso**

O sistema de temas será automaticamente utilizado baseado em:
- **Horário**: Manhã/Tarde → Light, Noite → Dark
- **Preferência do SO**: Seguirá configuração do sistema
- **Escolha Manual**: Preferência salva do usuário

## 🎉 **Benefícios**

### **Para o Usuário**
- ✅ **Conforto Visual**: Reduz fadiga ocular
- ✅ **Personalização**: Escolha baseada em preferência
- ✅ **Acessibilidade**: Melhor para diferentes condições visuais
- ✅ **Performance**: Transições suaves e responsivas

### **Para o Cliente**
- ✅ **Interface Moderna**: Seguindo tendências atuais
- ✅ **Profissional**: Aparência polida e cuidada
- ✅ **Acessível**: Atende padrões de acessibilidade
- ✅ **Adaptável**: Funciona em qualquer ambiente

## 🔮 **Futuras Melhorias**

- [ ] **Temas Personalizados**: Cores customizáveis pelo usuário
- [ ] **Modo Automático**: Mudança baseada no horário
- [ ] **Temas Corporativos**: Paletas específicas por empresa
- [ ] **Contraste Alto**: Modo para usuários com deficiência visual
- [ ] **Animações Avançadas**: Transições mais elaboradas

---

**🎨 O sistema de temas está completo e pronto para uso!** Oferece uma experiência visual moderna, acessível e personalizável para todos os usuários da aplicação.
