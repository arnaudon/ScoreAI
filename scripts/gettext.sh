pybabel extract -o locales/strings.pot .
pybabel update -i locales/strings.pot -d locales
pybabel compile -d locales
