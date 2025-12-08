#!/bin/bash
case "$1" in
    start)
        docker-compose up -d
        ;;
    stop)
        docker-compose down
        ;;
    restart)
        docker-compose restart
        ;;
    logs)
        docker-compose logs -f
        ;;
    migrate)
        docker-compose exec web python manage.py migrate
        ;;
    createsuperuser)
        docker-compose exec web python manage.py createsuperuser
        ;;
    shell)
        docker-compose exec web python manage.py shell
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|logs|migrate|createsuperuser|shell}"
        exit 1
        ;;
esac