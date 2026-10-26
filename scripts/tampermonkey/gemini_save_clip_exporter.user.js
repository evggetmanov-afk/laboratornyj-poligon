// ==UserScript==
// @name         Gemini Save Clip Exporter
// @namespace    https://local.poligon/
// @version      1.0.0
// @description  Быстрая выгрузка блоков ### FILE: из чата Gemini в буфер macOS для утилиты save
// @author       Оператор
// @match        https://gemini.google.com/*
// @grant        GM_setClipboard
// @run-at       document-idle
// ==/UserScript==

(function() {
    'use strict';

    const MARKER = '### FILE:';
    const BTN_CLASS = 'save-clip-export-btn';

    function addExportButtons() {
        // Ищем все блоки с форматированным кодом/текстом в ответах
        const blocks = document.querySelectorAll('pre:not([data-save-clip-processed="true"])');

        blocks.forEach(block => {
            const rawText = block.innerText || block.textContent;

            if (rawText.includes(MARKER)) {
                block.setAttribute('data-save-clip-processed', 'true');
                block.style.position = 'relative';

                const btn = document.createElement('button');
                btn.className = BTN_CLASS;
                btn.type = 'button';
                btn.textContent = '📋 Скопировать для save';
                btn.style.position = 'absolute';
                btn.style.top = '6px';
                btn.style.right = '40px';
                btn.style.zIndex = '1000';
                btn.style.padding = '4px 8px';
                btn.style.fontSize = '12px';
                btn.style.fontWeight = '600';
                btn.style.color = '#ffffff';
                btn.style.backgroundColor = '#1a73e8';
                btn.style.border = 'none';
                btn.style.borderRadius = '4px';
                btn.style.cursor = 'pointer';

                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();

                    // Вырезаем ровно фрагмент от маркера ### FILE:
                    const startIndex = rawText.indexOf(MARKER);
                    const cleanText = rawText.substring(startIndex).trim();

                    if (typeof GM_setClipboard !== 'undefined') {
                        GM_setClipboard(cleanText);
                    } else {
                        navigator.clipboard.writeText(cleanText);
                    }

                    btn.textContent = '✅ Скопировано!';
                    btn.style.backgroundColor = '#1e8e3e';
                    setTimeout(() => {
                        btn.textContent = '📋 Скопировать для save';
                        btn.style.backgroundColor = '#1a73e8';
                    }, 2000);
                });

                block.appendChild(btn);
            }
        });
    }

    // Наблюдатель за потоковым появлением сообщений в DOM
    const observer = new MutationObserver(() => {
        addExportButtons();
    });

    observer.observe(document.body, {
        childList: true,
        subtree: true
    });

    addExportButtons();
})();