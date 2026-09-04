## запуск git_scr.sh:
```bash
./git_scr.sh
```

## запуск svn_scr.sh:

### 1. Убедитесь, что установлен Subversion
Проверьте установку:
```bash
svn --version
svnadmin --version
```

### 2. Создайте каталог с архивами коммитов
Скрипт ожидает, что в папке `../commits/` (относительно места запуска) лежат zip-архивы `commit0.zip`, `commit1.zip`, …, `commit14.zip`.  

архивы лежат на se.ifmo.ru. схема в варианте интерактивная. при нажатии на ревизию скачивается коммит 


### 3. Сделайте скрипт исполняемым
```bash
chmod +x script.sh
```
(Если вы не хотите менять права, можно запустить через `bash script.sh`.)

### 4. Запустите скрипт
```bash
./script.sh
```
или
```bash
bash script.sh
```

### 5. Наблюдайте за выводом
Скрипт будет выводить сообщения SVN (добавление файлов, коммиты, переключения, слияния).  
В какой-то момент откроется редактор `nano` для ручного разрешения конфликта в файлах (строка с `nano *.java`).  
Вам нужно будет:
- Внести изменения (или сохранить файл).
- Нажать `Ctrl+O` (сохранить), затем `Ctrl+X` (выйти).

После этого скрипт продолжит выполнение.

### 6. Проверьте результат
После завершения скрипта в текущей папке появятся:
- `repo/` — сам репозиторий SVN
- `wc/` — рабочая копия

Вы можете исследовать историю:
```bash
cd wc
svn log -v
svn info
svn status
```

# Вопросы 

1. Какие есть СКВ? в лекциях и презе:
    - на основе файловой системы
    - централизованные (svn)
    - распределенные (git). эта по управлению делится на централизованную, с интеграционными менеджерами и с диктатором и лейтинантами
2. Какие типы тегов существуют? [статья](https://timeweb.cloud/tutorials/git/rabota-s-git-tegami-sozdanie-udalenie-ispolzovanie)
3. Что находится в папке .git? [статья](https://www.git-tower.com/blog/exploring-the-git-directory)
4. В чем различя reset --soft, --hard, --mixed? [обсуждение](https://stackoverflow.com/questions/3528245/whats-the-difference-between-git-reset-mixed-soft-and-hard) 
--soft is discarding last commit, 
--mix is discarding last commit and add, 
--hard is discarding last commit,add and any changes you made on the codes which is the same with git checkout HEAD

