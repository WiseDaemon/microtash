with open('c:/LLM/deepstash_microlearning/app/templates/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

target = '<!-- Export to Obsidian Markdown -->'
repl = '''<!-- Restack to Substack Notes -->
              <button onclick="openRestackModal()" class="w-9 h-9 rounded-full bg-[#ff6719]/15 border border-[#ff6719]/40 flex items-center justify-center text-[#ff6719] hover:bg-[#ff6719] hover:text-white transition shadow-sm" title="Restack to Substack Notes">
                <span class="material-symbols-outlined text-[18px]">repeat</span>
              </button>
              <!-- Export to Obsidian Markdown -->'''

if target in c:
    c = c.replace(target, repl, 1)
    with open('c:/LLM/deepstash_microlearning/app/templates/index.html', 'w', encoding='utf-8') as f:
        f.write(c)
    print("Restack button injected on card!")
else:
    print("Target not found")
