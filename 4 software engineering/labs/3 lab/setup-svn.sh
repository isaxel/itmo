set -e

REPO_WIN="C:/svn-repo/lab3"
WC_WIN="C:/svn-wc/lab3"
REPO_SH="/c/svn-repo/lab3"
WC_SH="/c/svn-wc/lab3"
URL="file:///$REPO_WIN/trunk"
REVISIONS=4

export MSYS_NO_PATHCONV=1

if [ ! -f build.xml ]; then
    echo "Запустите скрипт из корня проекта (рядом с build.xml)"
    exit 1
fi
if [ -e "$REPO_SH" ]; then
    echo "Каталог $REPO_SH уже существует. Удалите его или поменяйте REPO_WIN/REPO_SH в скрипте."
    exit 1
fi

PROJECT_SH="$(pwd)"

mkdir -p "$(dirname "$REPO_SH")" "$(dirname "$WC_SH")"
rm -rf "$WC_SH"

echo "создание репозитория"
svnadmin create "$REPO_WIN"
svn mkdir "$URL" -m "create trunk"

echo "рабочая копия"
svn checkout "$URL" "$WC_WIN"

echo "копирование проекта"
cp -r "$PROJECT_SH/src" "$WC_SH/"
cp "$PROJECT_SH/build.xml" "$PROJECT_SH/build.properties" "$WC_SH/"

cd "$WC_SH"
svn add --force . >/dev/null
svn commit -m "project sources and ant script"

echo "доп ревизии"
i=2
while [ "$i" -le "$REVISIONS" ]; do
    echo "revision $i" >> notes.txt
    svn add --force notes.txt >/dev/null 2>&1 || true
    svn commit -m "revision $i"
    i=$((i + 1))
done

echo "--- последние $REVISIONS ревизий:"
svn log -q -l "$REVISIONS" "$URL"
