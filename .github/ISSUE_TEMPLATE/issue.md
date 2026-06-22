---
name: ISSUE
about: Describe this issue template's purpose here.
title: ''
labels: ''
assignees: ''

---

name: 🐞 баг-репорт
description: сообщить об ошибке в аланаторе
title: "[БАГ] "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        спасибо, что сообщаете об ошибке! это поможет сделать аланатор лучше.
  - type: input
    id: version
    attributes:
      label: версия аланатора
      description: напиши версию (например, v0.9.0)
      placeholder: v0.9.0
    validations:
      required: true
  - type: dropdown
    id: os
    attributes:
      label: операционная система
      options:
        - windows 10
        - windows 11
        - другая
    validations:
      required: true
  - type: textarea
    id: what-happened
    attributes:
      label: что произошло
      description: опиши, что случилось
      placeholder: например, "при открытии aln с паролем не запрашивает пароль"
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: как воспроизвести
      description: по шагам
      placeholder: |
        1. создал архив с паролем
        2. открыл его через аланатор
        3. архив открылся без пароля
    validations:
      required: true
  - type: textarea
    id: expected
    attributes:
      label: ожидаемое поведение
      description: что должно было произойти
      placeholder: должен был запросить пароль
    validations:
      required: true
  - type: textarea
    id: screenshots
    attributes:
      label: скриншоты (если есть)
      description: прикрепи скриншот
      placeholder: перетащи сюда картинку
    validations:
      required: false
  - type: textarea
    id: logs
    attributes:
      label: логи (если есть)
      description: если есть файл с логами — вставь сюда
      render: shell
    validations:
      required: false
