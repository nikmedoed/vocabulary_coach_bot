## Инструкция по работе с окружениями

### Разработка в `dev_env_inside`

В директории `dev_env_inside` настроено окружение для работы с таблицей разработки (DEV). Предполагается, что во время разработки вы работаете с таблицей DEV. Когда разработка завершена, используйте команду:

```bash
clasp pull
```

Эта команда получит изменения для хранения локально.

### DEPLOY

Чтобы обновить таблицу диплоя (DEPLOY), выполните команду из корневой директории, где находится этот документ:

```bash
clasp push
```

### Логика

Вся логика работы построена на использовании одного и того же кода для двух разных таблиц за счёт двух разных конфигураций, ссылающихся на один код:
- Окружение в корневой директории предназначено для диплоя (DEPLOY).
- Окружение в директории `dev_env_inside` используется для разработки (DEV).

При необходимости процесс можно автоматизировать, но это не является обязательным.

---

## Environment Workflow Guide

### Development in `dev_env_inside`

The `dev_env_inside` directory is set up for working with the DEV table. It is assumed that during development, you will work with the DEV table. When development is complete, use the command:

```bash
clasp pull
```

This command will fetch the changes locally.

### DEPLOY

To update the deploy table (DEPLOY), run the command from the root directory where this document is located:

```bash
clasp push
```

### Logic

The entire workflow is based on using the same code for two different tables by utilizing two different configurations pointing to the same code:
- The environment in the root directory is for deployment (DEPLOY).
- The environment in the `dev_env_inside` directory is for development (DEV).

Automation can be set up if needed, but it is not mandatory.