# Hermes Evolutionary Self-Development Fork

**Проект:** Форк Hermes Agent с полноценным Evolutionary Self-Development Architecture — слоем мета-навыков и инструментов, который превращает нативный learning loop Hermes в системный, наблюдаемый и compounding процесс саморазвития.

## Цель проекта

Hermes уже обладает сильным нативным механизмом самоулучшения (автономное создание и эволюция навыков, persistent memory, Skills Hub).  
Этот форк добавляет **мета-слой**, который делает эволюцию:

- Более осознанной и структурированной (через OODA)
- Автоматической и умной (через `hermes-evolution-orchestrator` + `evolution-hook.py`)
- Аудируемой и улучшаемой (через `loop-auditor`)
- Анти-хрупкой и долгосрочной

---

## Что было создано

### Основные компоненты

| Компонент | Назначение | Расположение |
|-----------|------------|--------------|
| `hermes-evolution-orchestrator` | Центральный дирижёр эволюции. Связывает нативный loop Hermes с мета-навыками | `optional-skills/evolutionary-self-dev/` |
| `evolution-hook.py` | Умный детектор задач + анализ истории и паттернов. Решает, когда запускать оркестратор | `tools/` |
| `ooda-framework` | Структурирует улучшения по модели Observe → Orient → Decide → Act | `optional-skills/evolutionary-self-dev/` |
| `loop-auditor` (обновлённый) | Мета-аудит всего эволюционного цикла с фокусом на Hermes + orchestrator | `optional-skills/evolutionary-self-dev/` |
| `install-evolutionary-skills.sh` | Однокомандная установка всех навыков + `AGENTS.md` | Корень форка |
| `AGENTS.md` | Готовые инструкции, триггеры и описание системы для Hermes | Корень форка |
| `hermes-codebase-engineer` | Специализированный навык для программирования и интеграции в Hermes | `optional-skills/evolutionary-self-dev/` |

### Дополнительные мета-навыки

Также включены: `self-improver`, `mental-model-updater`, `experimenter`, `antifragility-builder`, `system-dynamics-thinker`, `value-clarifier`, `optimizer-philosopher`, `self-observer`, `crisis-manager`.

---

## Быстрый старт

```bash
git clone https://github.com/YOUR_USERNAME/hermes-evolutionary-self-dev.git
cd hermes-evolutionary-self-dev

chmod +x install-evolutionary-skills.sh
./install-evolutionary-skills.sh
```

После установки:
- Все мета-навыки появятся в `~/.hermes/skills/evolutionary-self-dev/`
- Файл `~/.hermes/AGENTS.md` будет содержать инструкции по использованию

---

## Как работает система

```
Hermes Native Learning Loop
        ↓ (после сложной задачи / создания навыка)
evolution-hook.py (анализирует контекст + историю)
        ↓ (решает запускать ли)
hermes-evolution-orchestrator
        ↓
ooda-framework → self-improver → mental-model-updater → ...
        ↓ (периодически)
loop-auditor (мета-аудит цикла)
```

**Ключевые принципы:**
- Неинвазивность (всё живёт в `optional-skills/` и `tools/`)
- Постепенная автоматизация (от ручных триггеров → `evolution-hook.py` → будущие нативные хуки)
- Итеративное улучшение самого процесса эволюции

---

## Текущий статус (Июль 2026)

**Готово:**
- `hermes-evolution-orchestrator`
- `evolution-hook.py` (с историей + анализом паттернов)
- `install-evolutionary-skills.sh`
- `AGENTS.md`
- `loop-auditor` (специально адаптирован под Hermes)
- `ooda-framework`
- `hermes-codebase-engineer`
- Полная структура форка + документация

Проект находится в состоянии, пригодном для реального использования и дальнейшего развития.

---

## Следующие шаги развития

- Реализовать нативную интеграцию `evolution-hook.py` как инструмента Hermes
- Добавить визуальные/структурированные отчёты эволюции
- Усилить использование паттернов из истории в принятии решений
- Провести реальные эксперименты на форке Hermes

---

**Стиль проекта:** Evolutionary Self-Development Architecture  
**Лицензия:** MIT (как у оригинального Hermes)

Готов к форку, использованию и дальнейшей эволюции.