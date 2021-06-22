mkdir itmp
while IFS= read -r line; do
    echo "$line"
    mkdir -p itmp/$(dirname $line)
    cp -r $line itmp/$line
done < learner-translation.txt
#docker-compose run --rm learning-circles /opt/django-venv/bin/python manage.py makemessages -a -i venv -i node_modules --settings=learnwithpeople.settings
docker run -it --rm --volume $(pwd)/itmp:/opt/app p2pu/learning-circles:local /opt/django-venv/bin/python manage.py makemessages -a  --keep-pot
rm -r locale
cp -r itmp/locale locale
