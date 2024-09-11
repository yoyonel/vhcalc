# Changelog
## 0.6.0 (2024-09-11)

### Feat

- **vhcalc**: add an option '--decompress' to main API entry 'imghash' for decompressing binary images hashes to hexadecimal representation

## 0.5.0 (2024-09-09)

### Feat

- **vhcalc**: add in CLI command an option to specify which image hashing function we want to use
- **imghash**: parametrize image hash function usage

## 0.4.0 (2024-09-04)

### Feat

- **application**: allow to use stdin for providing binary data (media/video)

### Refactor

- **services**: regroup API for generating images hashes from Path|str media filename or directly from buffered reader (like return from open())
- **tools**: move all forked tools (click-path, click-default-group and imageio-ffmpeg:io) to a 'tools/forked' dedicated directory

## 0.3.0 (2024-09-03)

### Feat

- **app.py**: default CLI group to a simpler entrypoint for generating images hashes from media filename input

## 0.2.9 (2024-09-02)

### Fix

- **github-actions**: fix on 'Set up Python' step
- **style**: add .tox to exclude directory for style.flake8

### Refactor

- **invoke**: typo + deprecated call for poetry install (without dev dependancies)

## 0.2.8 (2024-08-30)

### Fix

- **click-path**: remove package click-path and transfert click_path.GlobPath implementation into our tool

## 0.2.7 (2024-08-29)

### Fix

- **style.py**: fix task style commit check (using commitizen)

### Refactor

- refactoring on services, tools. add more utests, more comments. update some pre-commit hooks

## 0.2.6 (2022-05-29)

### Fix

- **docker**: Fix docker stage (build, entrypoint/command)
- **docker**: Fix docker stage (build, entrypoint/command)

## 0.2.5 (2022-05-28)

### Fix

- Dockerfile to reduce vulnerabilities

## 0.2.4 (2022-05-28)

### Fix

- requirements.txt to reduce vulnerabilities

## 0.2.3 (2022-05-12)

### Fix

- **pre-commit**: deactivate pre-commit (ymlparser) on mkdocs.yml
- **click**: downgrade click version (mypy issue) + remove mkdocs-click extension (poetry graph resolution issue)

## 0.2.2 (2022-04-02)

### Fix

- **coverage**: fix ci coverage step

## 0.2.1 (2022-04-01)

### Fix

- ci - docker build&publish image

## 0.2.0 (2022-03-28)

### Fix

- **utest**: fix utest on cli(ck) version request

### Feat

- **CLI**: Enhance cli support (entrypoint, utest, doc)
- **CLI**: Add cli command 'export_imghash_from_media' + functionnalities + unittest

## 0.1.0 (2022-03-04)

### Feat

- Initial commit
